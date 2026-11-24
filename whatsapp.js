/**
 * NATIVA · Widget de WhatsApp
 * Mensaje y globo según la página, recuerda la página anterior de la sesión.
 * Seguridad: sin innerHTML con datos dinámicos, número validado, textos saneados,
 * sessionStorage protegido con try/catch. Compatible con la CSP (solo script 'self').
 */
(function () {
  'use strict';

  function iniciar() {
    // ---- Utilidades ----
    const limpiar = (s, max) =>
      String(s == null ? '' : s).replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, max);
    const leer = (k) => { try { return sessionStorage.getItem(k) || ''; } catch (e) { return ''; } };
    const guardar = (k, v) => { try { sessionStorage.setItem(k, v); } catch (e) { /* almacenamiento bloqueado */ } };

    // Número: solo dígitos (país + número, 10 a 15). Si la config no es válida, se usa el de Nativa.
    const cfg = window.NATIVA_CONFIG && window.NATIVA_CONFIG.NATIVA_WHATSAPP;
    const numero = /^\d{10,15}$/.test(String(cfg || '')) ? String(cfg) : '573214645550';

    // 1. Datos de la página actual
    const ruta = window.location.pathname;
    const archivo = ruta.substring(ruta.lastIndexOf('/') + 1).toLowerCase();
    const pagina = archivo.replace('.html', '');
    const h1 = document.querySelector('h1');
    const tituloReal = h1 ? limpiar(h1.textContent, 80) : '';

    const formatearSlug = (slug) =>
      slug.split('-').map((p) => p.charAt(0).toUpperCase() + p.slice(1)).join(' ');

    // 2. Historial de sesión para dar contexto
    const paginaAnterior = limpiar(leer('nativa_ultima_pagina'), 80);
    guardar('nativa_ultima_pagina', tituloReal || pagina || 'Inicio');

    // 3. Mensaje base y texto del globo
    let mensajeActual = 'Hola Nativa, vengo de su sitio web y me gustaría recibir asesoría.';
    let textoGlobo = '¿Necesitas ayuda? Escríbenos';

    if (pagina === '' || pagina === 'index') {
      mensajeActual = 'Hola Nativa, estoy explorando su página principal y quiero conocer sus experiencias.';
      textoGlobo = '¡Hola! ¿Buscas una ruta o producto?';
    } else if (pagina.startsWith('aliado-')) {
      const nombre = tituloReal || formatearSlug(pagina.replace('aliado-', ''));
      mensajeActual = `Hola Nativa, estoy viendo el perfil de *${nombre}* y me gustaría conectar o reservar.`;
      textoGlobo = `¿Preguntas sobre ${nombre}?`;
    } else if (pagina.startsWith('producto-')) {
      const nombre = tituloReal || formatearSlug(pagina.replace('producto-', ''));
      mensajeActual = `Hola Nativa, me interesa adquirir *${nombre}*. ¿Me confirman disponibilidad y envío?`;
      textoGlobo = `¿Quieres pedir ${nombre}?`;
    } else if (pagina.startsWith('ruta-')) {
      const nombre = tituloReal || `Ruta ${formatearSlug(pagina.replace('ruta-', ''))}`;
      mensajeActual = `Hola Nativa, quiero información sobre fechas y cupos para *${nombre}*.`;
      textoGlobo = '¿Te gustaría vivir esta ruta?';
    } else if (pagina === 'rutas') {
      mensajeActual = 'Hola Nativa, estoy viendo sus rutas y quiero ayuda para elegir la ideal para mí.';
      textoGlobo = '¿Te ayudamos a elegir ruta?';
    } else if (pagina === 'directorio') {
      mensajeActual = 'Hola Nativa, estoy explorando el directorio y busco recomendaciones.';
      textoGlobo = '¿Buscas algún aliado en especial?';
    }

    if (paginaAnterior && paginaAnterior !== (tituloReal || pagina)) {
      mensajeActual += ` (Vengo de ver: ${paginaAnterior}).`;
    }

    // 4. Contenedor, globo y botón (todo con DOM seguro: textContent, nunca innerHTML con datos)
    const contenedor = document.createElement('div');
    contenedor.className = 'whatsapp-widget';

    const globo = document.createElement('div');
    globo.className = 'whatsapp-tooltip';
    const textoEl = document.createElement('span');
    textoEl.textContent = limpiar(textoGlobo, 90);
    const cerrar = document.createElement('button');
    cerrar.type = 'button';
    cerrar.className = 'wa-close';
    cerrar.setAttribute('aria-label', 'Cerrar mensaje');
    cerrar.textContent = '\u00d7';
    globo.appendChild(textoEl);
    globo.appendChild(cerrar);

    const enlace = document.createElement('a');
    enlace.target = '_blank';
    enlace.rel = 'noopener noreferrer';
    enlace.setAttribute('aria-label', 'Contactar a Nativa por WhatsApp (se abre en una pestaña nueva)');
    enlace.className = 'whatsapp-float';
    // SVG estático (constante, sin datos dinámicos)
    enlace.innerHTML =
      '<svg width="30" height="30" viewBox="0 0 32 32" fill="currentColor" aria-hidden="true" focusable="false">' +
      '<path d="M16.004 3.2c-7.06 0-12.8 5.74-12.8 12.8 0 2.256.59 4.46 1.71 6.404L3.2 28.8l6.56-1.72a12.74 12.74 0 0 0 6.244 1.62h.006c7.058 0 12.796-5.74 12.796-12.8 0-3.42-1.332-6.636-3.75-9.054A12.716 12.716 0 0 0 16.004 3.2zm0 23.34h-.004a10.61 10.61 0 0 1-5.41-1.48l-.388-.23-3.892 1.02 1.04-3.794-.252-.4a10.596 10.596 0 0 1-1.626-5.656c0-5.86 4.768-10.628 10.632-10.628 2.84 0 5.508 1.106 7.516 3.114a10.56 10.56 0 0 1 3.112 7.518c0 5.862-4.768 10.636-10.628 10.636z"/>' +
      '</svg>';

    // Función global para actualizar el mensaje desde cualquier parte de la web
    window.actualizarWhatsApp = function (nuevoMensaje, nuevoGlobo) {
      if (typeof nuevoMensaje !== 'string') return;
      enlace.href = 'https://wa.me/' + numero + '?text=' + encodeURIComponent(limpiar(nuevoMensaje, 600));
      if (typeof nuevoGlobo === 'string' && nuevoGlobo) {
        textoEl.textContent = limpiar(nuevoGlobo, 90);
        globo.classList.add('visible');
      }
    };
    window.actualizarWhatsApp(mensajeActual);

    // 5. Filtros, categorías o pestañas: el mensaje se adapta
    document.addEventListener('click', function (e) {
      const origen = e.target;
      const filtro = origen && origen.closest
        ? origen.closest('[data-filter], .filter-btn, .tab-btn, .categoria-btn') : null;
      if (!filtro) return;
      const nombreFiltro = limpiar(filtro.textContent, 40);
      if (nombreFiltro && nombreFiltro.toLowerCase() !== 'todos') {
        window.actualizarWhatsApp(
          `Hola Nativa, estoy filtrando por *${nombreFiltro}* en ${tituloReal || pagina} y me gustaría asesoría.`,
          `¿Te ayudo con ${nombreFiltro}?`
        );
      }
    });

    // El globo aparece a los 4 s, salvo que la persona ya lo haya cerrado
    setTimeout(function () {
      if (!leer('wa_globo_cerrado')) globo.classList.add('visible');
    }, 4000);

    function cerrarGlobo() {
      globo.classList.remove('visible');
      guardar('wa_globo_cerrado', 'true');
    }
    cerrar.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      cerrarGlobo();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && globo.classList.contains('visible')) cerrarGlobo();
    });

    contenedor.appendChild(globo);
    contenedor.appendChild(enlace);
    document.body.appendChild(contenedor);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
