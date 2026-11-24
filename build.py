# -*- coding: utf-8 -*-
"""Genera las subpáginas estáticas de Nativa. Todo el texto pasa por html.escape."""
from html import escape as e
import os, re

OUT = os.environ.get("NATIVA_OUT", "/home/claude/site")
CSP = ("default-src 'none'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; "
       "font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; "
       "connect-src 'self' https://script.google.com https://script.googleusercontent.com; "
       "form-action 'self'; base-uri 'self'; object-src 'none'; upgrade-insecure-requests")
FONTS = ("https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@300;400;600;700&"
         "family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&display=swap")
MAIL = "nativaecoturismoycultura@gmail.com"
TEL_TXT, TEL = "321 464 55 50", "+573214645550"
SLUG = re.compile(r"^[a-z0-9-]+$")


def _leer_footer():
    """El footer vive solo en index.html; todas las páginas lo replican desde ahí."""
    with open(os.path.join(OUT, "index.html"), encoding="utf-8") as f:
        m = re.search(r'    <footer class="footer".*?</footer>', f.read(), re.S)
    assert m, "No se encontró el footer en index.html"
    return m.group(0)


FOOTER = _leer_footer()


def mail(subject):
    from urllib.parse import quote
    return "mailto:%s?subject=%s" % (MAIL, quote(subject))


def page(fname, title, desc, body, active):
    assert SLUG.match(fname[:-5])
    def nav(href, label, key):
        cls = ' class="active" aria-current="page"' if key == active else ""
        return '<li><a href="%s"%s>%s</a></li>' % (href, cls, label)
    html = """<!DOCTYPE html>
<html lang="es-CO">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="%(desc)s">
    <meta name="theme-color" content="#738678">
    <meta http-equiv="Content-Security-Policy" content="%(csp)s">
    <meta name="referrer" content="strict-origin-when-cross-origin">
    <title>%(title)s · Nativa</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="stylesheet" href="subpaginas.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="%(fonts)s" rel="stylesheet">
</head>
<body>
    <a href="#main-content" class="skip-link">Saltar al contenido principal</a>
    <header class="header" role="banner">
        <nav class="nav-container" aria-label="Navegación principal">
            <a class="nav-logo" href="index.html" aria-label="Nativa, ir al inicio">
                <img src="assets/icons/logo-zari.svg" alt="" width="50" height="50">
                <span class="nav-brand">NATIVA</span>
                <span class="nav-subtitle">Bogotá</span>
            </a>
            <button class="nav-toggle" aria-label="Abrir menú" aria-expanded="false"><span class="hamburger"></span></button>
            <ul class="nav-menu">
                %(n1)s%(n2)s%(n3)s%(n4)s
                <li><a href="index.html#reservas" class="nav-cta">Reserva tu ruta</a></li>
            </ul>
        </nav>
    </header>
    <main id="main-content">
%(body)s
    </main>
%(footer)s
    <script src="script.js" defer></script>
</body>
</html>
""" % dict(
        desc=e(desc, quote=True), csp=CSP, title=e(title), fonts=FONTS, body=body,
        footer=FOOTER, mail=MAIL, tel=TEL, teltxt=TEL_TXT,
        n1=nav("index.html", "Inicio", "inicio"),
        n2=nav("rutas.html", "Experiencias", "rutas"),
        n3=nav("marketplace.html", "Marketplace", "market"),
        n4=nav("directorio.html", "Directorio", "dir"))
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(html)


def crumbs(items):
    out = []
    for i, (label, href) in enumerate(items):
        if href:
            out.append('<li><a href="%s">%s</a></li>' % (href, e(label)))
        else:
            out.append('<li aria-current="page">%s</li>' % e(label))
    return '<nav class="crumbs" aria-label="Ruta de navegación"><ol>%s</ol></nav>' % "".join(out)


def ul(items, cls=""):
    c = ' class="%s"' % cls if cls else ""
    return "<ul%s>%s</ul>" % (c, "".join("<li>%s</li>" % e(i) for i in items))


def money(n):
    return "$" + format(n, ",").replace(",", ".")


# ---------------------------------------------------------------- RUTAS
COMUN_INCLUYE = ["Guianza local en español", "Refrigerio tradicional (bebida y alimento típico)",
                 "Póliza de asistencia médica"]
COMUN_LLEVAR = ["Ropa impermeable: la ruta se hace con lluvia o con sol",
                "Zapatos cómodos y cerrados", "Agua para hidratarte", "Gorra",
                "Bloqueador solar", "Bicicleta en buen estado y casco (pregúntanos si necesitas alquilarlos)"]
COMUN_NORMAS = [
    "Llega a la hora acordada y no te alejes del grupo.",
    "Escucha con atención y trata con respeto a guías, comunidad y compañeros.",
    "Detente solo en las paradas designadas.",
    "No arrojes residuos, ni siquiera orgánicos.",
    "No extraigas material vegetal ni animal.",
    "Mantén un volumen de voz moderado y evita parlantes: protegen la fauna.",
    "Si te sientes mal, avísale directamente al guía.",
    "No consumas alcohol ni sustancias psicoactivas durante la experiencia.",
]

RUTAS = [
    dict(
        id="rios", slug="ruta-rios", nombre="Entre Ríos", tag="💧 Agua y biodiversidad",
        img="assets/images/ruta-rios.jpg",
        alt="Garza junto a vegetación exuberante en Briceño, Colombia",
        resumen="Una travesía entre canales, aves y relatos de restauración alrededor de los humedales de Suba.",
        km="12 km", horas="4 horas", base=75000, grupal=70000,
        dificultad="Fácil, sin ascensos", encuentro="Parque El Virrey, Cra. 15 # 88-00, barrio La Cabrera (Chapinero)",
        sentido="Nororiente a noroccidente", zona="Chapinero, Barrios Unidos y Suba",
        unico=[
            "Pedaleas por el canal del Río Negro y llegas al punto donde se encuentran el río Neuque (Arzobispo o Salitre) y el Río Negro.",
            "Conoces la historia de Aguas Calientes, el manantial termal que inspiró al actual Club Los Lagartos y que fue parte de la chupkua Tibabuyes.",
            "Terminas en el humedal Tibabuyes, el más grande de Bogotá (cerca de 222 hectáreas), hogar de la tingua bogotana, ave en peligro de extinción.",
            "Es el único humedal de Bogotá donde se registra el musgo de pantano.",
            "Vivencia de avistamiento de aves, fotografía y reseña histórica de la lucha comunitaria por proteger el humedal.",
        ],
        tramos=[
            ("Parque El Virrey a la Autopista Norte", "600 m · 15 min",
             "Corredor verde con más de 700 especies de plantas y árboles y 75 de fauna. Sus aguas vienen de la quebrada El Chicó."),
            ("Ciclorruta hasta el canal Río Negro", "1,5 km · 20 min",
             "Cruzas los puentes de la calle 92 y llegas por el barrio La Castellana a la Escuela Militar de Cadetes."),
            ("Entre Ríos, calle 80 con carrera 68", "1,3 km · 15 min + 15 min de pausa",
             "Parada para ver la unión de los ríos Neuque y Negro, caminar el puente peatonal e hidratarte."),
            ("Hacia Los Lagartos y la Av. Ciudad de Cali", "1,7 km · 30 min",
             "Pasas por Titán Plaza, cruzas la Av. Boyacá y conoces la historia de Aguas Calientes."),
            ("Humedal Tibabuyes", "1,45 km · 15 min + 45 min de actividad",
             "Refrigerio, reconocimiento del territorio, avistamiento de aves y relato de la lucha por el humedal."),
        ],
        extra_rec=["Lleva binoculares o cámara si quieres aprovechar el avistamiento de aves (opcional).",
                   "Hay dos descensos de la bicicleta para cruzar puentes peatonales: usa calzado cómodo para caminar."],
    ),
    dict(
        id="sabana", slug="ruta-sabana", nombre="Ruta Ancestral: de la Chupkua a la montaña",
        corto="Ruta Ancestral", tag="🔥 Memoria ancestral",
        img="assets/images/ruta-sabana.jpg", alt="Ritual cultural con fuego y música en Bogotá, Colombia",
        resumen="Una experiencia de interpretación cultural junto a memorias muiscas, caminos rurales y saberes de la sabana.",
        km="18 km", horas="5 horas", base=95000, grupal=90000,
        dificultad="Se confirma al reservar", encuentro="Se confirma al reservar",
        sentido="Vía Suba–Cota", zona="Suba rural y Cota",
        unico=[
            "Recorres la vía Suba–Cota, entre veredas campesinas y el borde de la Reserva Forestal Regional del Norte Thomas van der Hammen.",
            "Conoces la historia de la vereda Chorrillos: cerca de 2.000 habitantes que esperaron hasta 2021 la llegada del acueducto y hoy defienden su territorio rural.",
            "Aprendes por qué el río Bogotá se llamaba Funza («Varón Poderoso») y cómo los muiscas lo veneraban como fuente de vida y fertilidad.",
            "Escuchas las leyendas del páramo de Guacheneque y de la laguna que «brama», contadas desde la tradición oral.",
            "Miras hacia el cerro Majuy («dentro de ti»), territorio sagrado muisca con petroglifos y bosque alto andino.",
            "Incluye inmersión ancestral muisca con sabedores y guías de la comunidad.",
        ],
        tramos=[
            ("Vereda Chorrillos", "Parada de interpretación",
             "Agricultura, agua y defensa de la ruralidad en un ecosistema que aún no tiene figura de protección."),
            ("Reserva Thomas van der Hammen", "Parada de interpretación",
             "Conectividad ecológica entre los cerros orientales y el río Bogotá, y las amenazas que enfrenta."),
            ("Cota y el río Funza", "Parada de interpretación",
             "Significado del nombre Cota en lengua chibcha y la historia del río desde el páramo hasta la sabana."),
            ("Cerro Majuy y la montaña", "Cierre de la experiencia",
             "Mitos del Mohán y Huaika, petroglifos y el trabajo de las comunidades que cuidan el territorio."),
        ],
        tramos_nota="Las paradas y los tiempos exactos se confirman con Nativa al aceptar tu reserva.",
        extra_rec=["Lleva una chaqueta adicional: en la zona alta de la sabana el clima cambia rápido y refresca.",
                   "Es un recorrido de interpretación cultural: llega con disposición para escuchar y preguntar con respeto."],
    ),
    dict(
        id="cerro", slug="ruta-cerro", nombre="Ruta Cerro", tag="⛰️ Bosque y mirador",
        img="assets/images/ruta-cerro.jpg", alt="Vista del cerro con vegetación nativa en Suba, Bogotá",
        resumen="Un recorrido suave en bicicleta hacia el cerro para mirar la sabana desde lo alto, caminar entre bosque nativo y conversar sobre cómo se cuida este territorio.",
        km="5 km aprox.", horas="4 horas", base=75000, grupal=70000,
        dificultad="Fácil, con ascensos leves en el tramo urbano alto",
        encuentro="Entrada principal del humedal Tibabuyes (Av. Ciudad de Cali)",
        sentido="Noroccidente a noroccidente", zona="Av. Ciudad de Cali, Portal Suba, La Campiña, Plaza Fundacional y Cabildo Indígena",
        unico=[
            "Empiezas con una caminata interpretativa en la chupkua Tibabuyes, «tierra de labradores» en lengua muysccubun.",
            "Interpretas el mural del Portal Suba como memoria, fuerza e identidad del territorio.",
            "Llegas a la Plaza Fundacional de Suba y conoces su arquitectura de transición y su patrimonio colonial.",
            "Cierras con una inmersión en el Cabildo Indígena Muisca de Suba: ingreso regulado al Santuario y visita al Cusmuy (bohío ceremonial circular).",
            "Diálogo de saberes con guías de interpretación indígena y sabedores.",
            "Recibes un recordatorio artesanal hecho por artesanos de Suba.",
        ],
        tramos=[
            ("Humedal Tibabuyes (punto de encuentro)", "45 min",
             "Descenso de las bicicletas, caminata interpretativa, educación ambiental y avistamiento de aves."),
            ("Av. Ciudad de Cali al Portal Suba", "45 min",
             "Ciclorruta segura, historia de la localidad de Suba e interpretación del mural del Portal."),
            ("Portal Suba a la Plaza Fundacional", "45 min",
             "Ascenso leve por La Campiña, interpretación de la plaza y refrigerio tradicional."),
            ("Cabildo Muisca de Suba y el Cusmuy", "2 horas aprox.",
             "Ingreso regulado al Santuario, cosmología muisca y encuentro con prácticas tradicionales. Al final, encuesta de satisfacción y souvenir artesanal."),
        ],
        extra_rec=["Hay un ascenso leve hacia el centro histórico: dosifica el esfuerzo y avisa al guía si lo necesitas.",
                   "En el Santuario Muisca se ingresa de forma regulada y con acompañamiento: sigue siempre las indicaciones de los guías indígenas."],
    ),
]


def precio_html(r):
    return ('<p class="price-main"><strong>%s</strong> COP por persona</p>'
            '<p>Tarifa grupal (15 o más personas): %s COP por persona</p>') % (money(r["base"]), money(r["grupal"]))


def ruta_cards():
    out = []
    for r in RUTAS:
        out.append("""
                    <article class="route-card" data-route="%(id)s">
                        <div class="route-image">
                            <img src="%(img)s" alt="%(alt)s" loading="lazy" width="400" height="300">
                            <span class="route-tag">%(tag)s</span>
                        </div>
                        <div class="route-content">
                            <h2 class="route-title">%(nombre)s</h2>
                            <p class="route-description">%(resumen)s</p>
                            <div class="route-meta"><span>📍 %(km)s</span><span>⏱️ %(horas)s</span></div>
                            <div class="route-price">%(precio)s</div>
                            <div class="card-actions">
                                <a href="%(slug)s.html" class="btn btn-outline">Ver detalles</a>
                                <a href="index.html?ruta=%(id)s#reservas" class="btn btn-route">Reservar</a>
                            </div>
                        </div>
                    </article>""" % dict(
            id=r["id"], img=r["img"], alt=e(r["alt"], quote=True), tag=e(r["tag"]), nombre=e(r["nombre"]),
            resumen=e(r["resumen"]), km=e(r["km"]), horas=e(r["horas"]), precio=precio_html(r), slug=r["slug"]))
    return "".join(out)


def build_rutas():
    body = """
        <section class="sub-hero">
            <div class="container">
                %s
                <h1 class="sub-title">Experiencias Nativa</h1>
                <p class="sub-lead">Tres rutas guiadas en bicicleta. Elige una para ver sus paradas, lo que incluye y qué llevar.</p>
            </div>
        </section>
        <section class="routes">
            <div class="container">
                <div class="routes-grid">%s
                </div>
                <div class="sub-note"><p>Cada salida es de hasta 20 personas y se confirma al completar 7. Si no se completa, te proponemos otra fecha.</p></div>
            </div>
        </section>""" % (crumbs([("Inicio", "index.html"), ("Experiencias", None)]), ruta_cards())
    page("rutas.html", "Experiencias", "Rutas guiadas en bicicleta por los humedales, la sabana y los cerros de Suba, Bogotá.", body, "rutas")


def build_ruta(r):
    tramos = "".join(
        '<li><h3>%s</h3><p class="tramo-meta">%s</p><p>%s</p></li>' % (e(t[0]), e(t[1]), e(t[2])) for t in r["tramos"])
    nota = '<p class="sub-note-inline">%s</p>' % e(r["tramos_nota"]) if r.get("tramos_nota") else ""
    hechos = [("Distancia", r["km"]), ("Duración", r["horas"]), ("Dificultad", r["dificultad"]),
              ("Punto de encuentro", r["encuentro"]), ("Sentido", r["sentido"]), ("Zona", r["zona"]),
              ("Grupo por salida", "7 a 20 personas (reserva individual de 1 a 6 se une a una salida abierta)")]
    hechos_html = "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(k), e(v)) for k, v in hechos)
    body = """
        <section class="sub-hero">
            <div class="container">
                %(crumbs)s
                <p class="sub-tag">%(tag)s</p>
                <h1 class="sub-title">%(nombre)s</h1>
                <p class="sub-lead">%(resumen)s</p>
            </div>
        </section>
        <section class="detail">
            <div class="container detail-layout">
                <div class="detail-main">
                    <img class="detail-cover" src="%(img)s" alt="%(alt)s" width="800" height="600">

                    <h2>Lo que hace única esta ruta</h2>
                    %(unico)s

                    <h2>Paradas del recorrido</h2>
                    <ol class="tramos">%(tramos)s</ol>
                    %(nota)s

                    <h2>Qué incluye</h2>
                    %(incluye)s

                    <h2>Elementos indispensables</h2>
                    %(llevar)s

                    <h2>Recomendaciones</h2>
                    %(rec)s

                    <h2>Cuidemos el territorio</h2>
                    %(normas)s

                    <h2>Reserva y cancelación</h2>
                    <p>Puedes reservar hasta 48 horas antes. Una persona de Nativa confirma cupos, accesibilidad y opciones de pago. La cancelación es gratuita hasta 24 horas antes; con menos tiempo, si llegas tarde o no te presentas, no hay reembolso.</p>
                    <p>El recorrido se realiza con lluvia o con sol.</p>
                </div>
                <aside class="detail-aside" aria-label="Resumen y reserva">
                    <div class="aside-card">
                        <h2 class="aside-title">Datos de la ruta</h2>
                        <p class="price-main"><strong>%(base)s</strong> COP por persona</p>
                        <p class="price-note">Tarifa grupal (15 o más): %(grupal)s COP por persona</p>
                        <dl class="facts">%(hechos)s</dl>
                        <a href="index.html?ruta=%(id)s#reservas" class="btn btn-primary btn-block">Reservar esta ruta</a>
                        <a href="%(mail)s" class="btn btn-outline btn-block">Preguntar por correo</a>
                        <a href="rutas.html" class="back-link">Ver todas las rutas</a>
                    </div>
                </aside>
            </div>
        </section>""" % dict(
        crumbs=crumbs([("Inicio", "index.html"), ("Experiencias", "rutas.html"), (r.get("corto", r["nombre"]), None)]),
        tag=e(r["tag"]), nombre=e(r["nombre"]), resumen=e(r["resumen"]), img=r["img"], alt=e(r["alt"], quote=True),
        unico=ul(r["unico"], "check-list"), tramos=tramos, nota=nota,
        incluye=ul(COMUN_INCLUYE + (["Inmersión ancestral muisca con guías y sabedores indígenas"] if r["id"] == "sabana" else
                   ["Ingreso al Santuario Muisca, visita al Cusmuy y souvenir artesanal de Suba"] if r["id"] == "cerro" else []), "check-list"),
        llevar=ul(COMUN_LLEVAR, "check-list"), rec=ul(r["extra_rec"] + ["Llega a la hora acordada: la salida no espera."], "plain-list"),
        normas=ul(COMUN_NORMAS, "plain-list"), base=money(r["base"]), grupal=money(r["grupal"]),
        hechos=hechos_html, id=r["id"], mail=mail("Pregunta sobre " + r["nombre"]))
    page(r["slug"] + ".html", r.get("corto", r["nombre"]), r["resumen"], body, "rutas")


# ---------------------------------------------------------------- MARKETPLACE
PRODUCTOS = [
    ("ceramica", "Cerámica de territorio", "ceramica.jpg", "Cerámicas artesanales coloridas",
     "Piezas inspiradas en las aguas, semillas y aves de la sabana.",
     ["Piezas hechas a mano por artesanos locales de Suba.", "Motivos que recuerdan el agua, las semillas y las aves de los humedales.", "Cada pieza es única: puede variar en forma y color."],
     "Lávala a mano con agua tibia y jabón suave. Envuélvela bien si la llevas en la bicicleta o en el equipaje."),
    ("canasta", "Canasta agroecológica", "canasta.jpg", "Mujer lleva canasta con verduras frescas",
     "Cosechas de huertas urbanas, frescas y cultivadas con cuidado.",
     ["Productos de huertas urbanas de la localidad.", "Cultivados con cuidado y sin prisa.", "Su contenido depende de la cosecha de cada temporada."],
     "Pídela con anticipación: el contenido cambia con la temporada y se prepara bajo solicitud. Consúmela fresca."),
    ("botanica", "Botánica local", "botanica.jpg", "Jabones orgánicos artesanales",
     "Jabones, ungüentos e infusiones de plantas de uso responsable.",
     ["Jabones, ungüentos e infusiones elaborados con plantas de uso responsable.", "Elaboración artesanal en pequeñas cantidades."],
     "Revisa los ingredientes de cada producto si tienes alergias o estás embarazada o en lactancia, y consulta a un profesional de la salud antes de usar infusiones o ungüentos."),
    ("tejidos", "Tejidos de memoria", "tejidos.jpg", "Bolso tejido artesanal de colores",
     "Accesorios tejidos que llevan color, oficio y relatos comunitarios.",
     ["Accesorios tejidos a mano.", "Cada pieza lleva color, oficio y relatos de la comunidad.", "Compras directamente a quienes los elaboran."],
     "Lávalos a mano y sécalos a la sombra para conservar los colores."),
    ("joyeria", "Joyería artesanal", "joyeria.jpg", "Mujer muestra collares artesanales",
     "Pequeñas piezas elaboradas a mano para celebrar el detalle.",
     ["Pequeñas piezas elaboradas a mano.", "Producción en poca cantidad, con atención al detalle."],
     "Guárdala lejos de la humedad y evita el contacto con perfumes y productos de limpieza."),
    ("cafe", "Café de origen", "cafe.jpg", "Granos de café colombiano",
     "Tostión local en pequeños lotes para acompañar cada conversación.",
     ["Tostión local en pequeños lotes.", "Pensado para acompañar la conversación después del recorrido."],
     "Guárdalo en un recipiente hermético, en un lugar fresco y oscuro, y muélelo justo antes de prepararlo."),
]


def build_market():
    cards = "".join("""
                    <article class="market-card">
                        <img src="assets/images/%s" alt="%s" loading="lazy" width="300" height="200">
                        <h2 class="market-title">%s</h2>
                        <p class="market-description">%s</p>
                        <a href="producto-%s.html" class="btn btn-market">Ver detalles</a>
                    </article>""" % (p[2], e(p[3], quote=True), e(p[1]), e(p[4]), p[0]) for p in PRODUCTOS)
    body = """
        <section class="sub-hero">
            <div class="container">
                %s
                <h1 class="sub-title">Marketplace turístico</h1>
                <p class="sub-lead">Productos artesanales, agroecológicos y botánicos elaborados por iniciativas locales de Suba.</p>
            </div>
        </section>
        <section class="marketplace">
            <div class="container">
                <div class="market-grid">%s
                </div>
            </div>
        </section>""" % (crumbs([("Inicio", "index.html"), ("Marketplace", None)]), cards)
    page("marketplace.html", "Marketplace", "Productos artesanales, agroecológicos y botánicos de iniciativas locales de Suba.", body, "market")
    for pid, nombre, img, alt, resumen, carac, cuidado in PRODUCTOS:
        otros = "".join('<li><a href="producto-%s.html">%s</a></li>' % (o[0], e(o[1])) for o in PRODUCTOS if o[0] != pid)
        b = """
        <section class="sub-hero">
            <div class="container">
                %(crumbs)s
                <p class="sub-tag">🛍️ Marketplace turístico</p>
                <h1 class="sub-title">%(nombre)s</h1>
                <p class="sub-lead">%(resumen)s</p>
            </div>
        </section>
        <section class="detail">
            <div class="container detail-layout">
                <div class="detail-main">
                    <img class="detail-cover" src="assets/images/%(img)s" alt="%(alt)s" width="800" height="600">
                    <h2>Características</h2>
                    %(carac)s
                    <h2>Recomendaciones de cuidado</h2>
                    <p>%(cuidado)s</p>
                    <h2>Cómo conseguirlo</h2>
                    <p>Escríbenos y una persona de Nativa te confirma disponibilidad, precio y entrega. También puedes pedirlo junto con tu reserva de ruta.</p>
                </div>
                <aside class="detail-aside" aria-label="Solicitar producto">
                    <div class="aside-card">
                        <h2 class="aside-title">Me interesa</h2>
                        <a href="%(mail)s" class="btn btn-primary btn-block">Solicitar por correo</a>
                        <a href="index.html#reservas" class="btn btn-outline btn-block">Reservar una ruta</a>
                        <h3 class="aside-sub">Otros productos</h3>
                        <ul class="plain-list">%(otros)s</ul>
                        <a href="marketplace.html" class="back-link">Ver todo el marketplace</a>
                    </div>
                </aside>
            </div>
        </section>""" % dict(
            crumbs=crumbs([("Inicio", "index.html"), ("Marketplace", "marketplace.html"), (nombre, None)]),
            nombre=e(nombre), resumen=e(resumen), img=img, alt=e(alt, quote=True), carac=ul(carac, "check-list"),
            cuidado=e(cuidado), mail=mail("Me interesa: " + nombre), otros=otros)
        page("producto-%s.html" % pid, nombre, resumen, b, "market")


# ---------------------------------------------------------------- DIRECTORIO
ALIADOS = [
    ("refugio-verde", "Refugio Verde", "🏠 Hospedaje aliado", "refugio-verde.jpg", "Casa de madera tipo refugio rodeada por bosque",
     "Alojamiento de escala pequeña para descansar cerca de la naturaleza.",
     ["Alojamiento de escala pequeña.", "Entorno natural, pensado para descansar después de pedalear."],
     "Pregunta por disponibilidad con anticipación, sobre todo si viajas en grupo."),
    ("casa-patio-suba", "Casa Patio Suba", "🏙️ Hospedaje urbano", "casa-patio.jpg", "Patio colonial con fuente en Bogotá",
     "Un punto de descanso con vegetación, historia y cercanía a la ciudad.",
     ["Punto de descanso con vegetación e historia.", "Cercano a la ciudad y a las rutas de Nativa."],
     "Pregunta por disponibilidad con anticipación y confirma el horario de llegada."),
    ("bici-barrio", "Bici Barrio", "🚲 Servicio turístico", "bici-barrio.jpg", "Bicicletas estacionadas frente a tienda de alquiler",
     "Apoyo para movilidad, ajustes y alquiler de bicicletas para visitantes.",
     ["Alquiler de bicicletas para visitantes.", "Ajustes y apoyo de movilidad."],
     "Si no tienes bicicleta para una ruta, pregunta con anticipación por el alquiler y reserva antes de tu fecha."),
    ("cocina-de-la-huerta", "Cocina de la Huerta", "🍲 Sabores locales", "cocina-huerta.jpg", "Vendedora sirve comida caliente en calle de Bogotá",
     "Preparaciones de temporada con ingredientes cercanos y conversación abierta.",
     ["Preparaciones de temporada.", "Ingredientes cercanos y conversación abierta con quien cocina."],
     "Avisa si tienes alergias o restricciones alimentarias al pedir."),
]
PLANES = [
    ("Plan Comunidad", "$50.000", ["Perfil activo en el directorio web de Nativa."], False),
    ("Plan Impulso", "$100.000", ["Todo lo del Plan Comunidad.", "1 publicación en todas las redes de Nativa."], True),
    ("Plan Visibilidad", "$200.000", ["Todo lo del Plan Impulso.", "1 reel promocional por mes.", "Publicación en las redes sociales de Nativa."], False),
]


def build_directorio():
    cards = "".join("""
                    <article class="directory-card">
                        <img src="assets/images/%s" alt="%s" loading="lazy" width="300" height="200">
                        <span class="directory-type">%s</span>
                        <h2 class="directory-title">%s</h2>
                        <p class="directory-description">%s</p>
                        <a href="aliado-%s.html" class="btn btn-outline card-link">Ver detalles</a>
                    </article>""" % (a[3], e(a[4], quote=True), e(a[2]), e(a[1]), e(a[5]), a[0]) for a in ALIADOS)
    planes = "".join("""
                    <article class="plan-card%s">
                        <h3 class="plan-name">%s</h3>
                        <p class="plan-price">%s <span>COP / 3 meses</span></p>
                        %s
                        <a href="%s" class="btn %s">Quiero este plan</a>
                    </article>""" % (" plan-featured" if f else "", e(n), p, ul(l, "plan-list"),
                                     mail(n + " Nativa"), "btn-primary" if f else "btn-outline") for n, p, l, f in PLANES)
    body = """
        <section class="sub-hero">
            <div class="container">
                %s
                <h1 class="sub-title">Directorio local</h1>
                <p class="sub-lead">Hospedajes, servicios y emprendimientos aliados para extender tu visita de forma consciente.</p>
            </div>
        </section>
        <section class="directory">
            <div class="container">
                <div class="directory-grid">%s
                </div>
                <h2 class="plans-title">Planes para aliados</h2>
                <p class="section-description">¿Tienes un restaurante, taller, hospedaje o iniciativa en Suba? Súmate al directorio. Cada plan dura 3 meses.</p>
                <div class="plans-grid">%s
                </div>
            </div>
        </section>""" % (crumbs([("Inicio", "index.html"), ("Directorio", None)]), cards, planes)
    page("directorio.html", "Directorio local", "Hospedajes, servicios y emprendimientos aliados de Nativa en Suba, Bogotá.", body, "dir")
    for aid, nombre, tipo, img, alt, resumen, carac, rec in ALIADOS:
        otros = "".join('<li><a href="aliado-%s.html">%s</a></li>' % (o[0], e(o[1])) for o in ALIADOS if o[0] != aid)
        b = """
        <section class="sub-hero">
            <div class="container">
                %(crumbs)s
                <p class="sub-tag">%(tipo)s</p>
                <h1 class="sub-title">%(nombre)s</h1>
                <p class="sub-lead">%(resumen)s</p>
            </div>
        </section>
        <section class="detail">
            <div class="container detail-layout">
                <div class="detail-main">
                    <img class="detail-cover" src="assets/images/%(img)s" alt="%(alt)s" width="800" height="600">
                    <h2>Qué ofrece</h2>
                    %(carac)s
                    <h2>Recomendaciones</h2>
                    <p>%(rec)s</p>
                    <h2>Cómo contactar</h2>
                    <p>Escríbenos y te ponemos en contacto con este aliado. Los precios y la disponibilidad los confirma cada aliado.</p>
                </div>
                <aside class="detail-aside" aria-label="Contacto">
                    <div class="aside-card">
                        <h2 class="aside-title">Contactar</h2>
                        <a href="%(mail)s" class="btn btn-primary btn-block">Escribir a Nativa</a>
                        <a href="tel:%(tel)s" class="btn btn-outline btn-block">Llamar al %(teltxt)s</a>
                        <h3 class="aside-sub">Otros aliados</h3>
                        <ul class="plain-list">%(otros)s</ul>
                        <a href="directorio.html" class="back-link">Ver todo el directorio</a>
                    </div>
                </aside>
            </div>
        </section>""" % dict(
            crumbs=crumbs([("Inicio", "index.html"), ("Directorio", "directorio.html"), (nombre, None)]),
            tipo=e(tipo), nombre=e(nombre), resumen=e(resumen), img=img, alt=e(alt, quote=True),
            carac=ul(carac, "check-list"), rec=e(rec), mail=mail("Quiero contactar a " + nombre),
            tel=TEL, teltxt=TEL_TXT, otros=otros)
        page("aliado-%s.html" % aid, nombre, resumen, b, "dir")


def sync_legal(fname):
    """politica-datos.html no se genera: se le aplica el mismo footer, color de marca y fuentes."""
    p = os.path.join(OUT, fname)
    with open(p, encoding="utf-8") as f:
        h = f.read()
    h = h.replace('content="#173f35"', 'content="#738678"')
    if "fonts.googleapis.com/css2" not in h:
        h = h.replace('<link rel="stylesheet" href="styles.css">',
                      '<link rel="stylesheet" href="styles.css">\n    <link rel="preconnect" href="https://fonts.googleapis.com">\n'
                      '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n    <link href="%s" rel="stylesheet">' % FONTS, 1)
    if "<footer" in h:
        h = re.sub(r"[ \t]*<footer.*?</footer>", lambda _m: FOOTER, h, count=1, flags=re.S)
    else:
        h = h.replace("</main>", "</main>\n" + FOOTER, 1)
    with open(p, "w", encoding="utf-8") as f:
        f.write(h)


build_rutas()
for r in RUTAS:
    build_ruta(r)
build_market()
build_directorio()
sync_legal("politica-datos.html")
print("ok")
