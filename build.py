#!/usr/bin/env python3
"""Genera la web estática de PulsoTech en ./docs (carpeta que publica GitHub Pages) a partir de articulos/*.md y paginas/*.md.

Uso: python3 build.py   (necesita pandoc)
"""
import html, json, re, shutil, subprocess, unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
SITE = "https://www.pulsotech.es"
NAME = "PulsoTech"
TAGLINE = "Tecnología para entrenar mejor"
EMAIL = "delgado28alaminos@gmail.com"
GSC_VERIFICATION = "Yl6vsyT7Wm8YZBCkvP9fcp3DEsRIXIwle4AMyrHxQFc"  # Google Search Console
ADSENSE_CLIENT = "ca-pub-8344607375706556"  # ID de editor de AdSense

# Datos de cada artículo que no están en el .md
ARTICLES = {
    "01-apps-entrenar-futbol-solo.md": {"cat": "Fútbol", "date": "2026-10-19", "emoji": "⚽"},
    "02-fiabilidad-calorias-smartwatch.md": {"cat": "Relojes", "date": "2026-10-19", "emoji": "⌚"},
    "03-sincronizar-strava-reloj.md": {"cat": "Apps", "date": "2026-10-19", "emoji": "📲"},
    "04-pasos-al-dia-segun-edad.md": {"cat": "Salud", "date": "2026-10-20", "emoji": "👟"},
    "05-apps-controlar-sueno.md": {"cat": "Apps", "date": "2026-10-20", "emoji": "🌙"},
    "06-gps-futbol.md": {"cat": "Fútbol", "date": "2026-10-20", "emoji": "📡"},
    "07-medir-frecuencia-cardiaca-movil.md": {"cat": "Salud", "date": "2026-10-20", "emoji": "❤️"},
    "08-zonas-frecuencia-cardiaca.md": {"cat": "Entrenamiento", "date": "2026-10-20", "emoji": "📊"},
    "09-pulsometro-pecho-o-muneca.md": {"cat": "Relojes", "date": "2026-10-20", "emoji": "💓"},
    "10-que-es-vo2-max.md": {"cat": "Entrenamiento", "date": "2026-10-20", "emoji": "🫁"},
    "11-variabilidad-frecuencia-cardiaca.md": {"cat": "Entrenamiento", "date": "2026-10-20", "emoji": "📈"},
    "12-como-elegir-reloj-deportivo.md": {"cat": "Relojes", "date": "2026-10-20", "emoji": "⌚"},
    "13-alargar-bateria-reloj-deportivo.md": {"cat": "Relojes", "date": "2026-10-20", "emoji": "🔋"},
    "14-smartwatch-o-pulsera-actividad.md": {"cat": "Relojes", "date": "2026-10-20", "emoji": "⚖️"},
    "15-medir-velocidad-futbol.md": {"cat": "Fútbol", "date": "2026-10-20", "emoji": "⚡"},
    "16-calentamiento-futbol.md": {"cat": "Fútbol", "date": "2026-10-20", "emoji": "🔥"},
    "17-strava-entrenar-mejor.md": {"cat": "Apps", "date": "2026-10-20", "emoji": "🧡"},
    "18-limpiar-correa-reloj.md": {"cat": "Relojes", "date": "2026-10-20", "emoji": "🧼"},
    "19-auriculares-deporte.md": {"cat": "Entrenamiento", "date": "2026-10-20", "emoji": "🎧"},
    "20-configurar-garmin-primera-vez.md": {"cat": "Relojes", "date": "2026-10-20", "emoji": "⚙️"},
    "21-empezar-a-correr-con-app.md": {"cat": "Running", "date": "2026-10-20", "emoji": "🏃"},
    "22-apps-gimnasio.md": {"cat": "Apps", "date": "2026-10-20", "emoji": "🏋️"},
    "23-reloj-para-nadar.md": {"cat": "Relojes", "date": "2026-10-20", "emoji": "🏊"},
    "24-bascula-inteligente.md": {"cat": "Salud", "date": "2026-10-20", "emoji": "⚖️"},
    "25-ciclocomputador-o-movil-bici.md": {"cat": "Ciclismo", "date": "2026-10-20", "emoji": "🚴"},
    "26-apps-entrenar-en-casa.md": {"cat": "Entrenamiento", "date": "2026-10-20", "emoji": "🏠"},
    "27-cadencia-de-carrera.md": {"cat": "Running", "date": "2026-10-22", "emoji": "👣"},
    "28-oxigeno-en-sangre-reloj.md": {"cat": "Salud", "date": "2026-10-22", "emoji": "🩸"},
    "29-rodillo-inteligente.md": {"cat": "Ciclismo", "date": "2026-10-22", "emoji": "🚲"},
    "30-navegacion-mapas-reloj.md": {"cat": "Relojes", "date": "2026-10-26", "emoji": "🗺️"},
    "31-entrenamiento-intervalos-reloj.md": {"cat": "Entrenamiento", "date": "2026-10-26", "emoji": "⏱️"},
    "32-correr-de-noche-visible.md": {"cat": "Running", "date": "2026-10-26", "emoji": "🔦"},
}
MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre"]


def md_to_html(md):
    return subprocess.run(["pandoc", "-f", "markdown", "-t", "html", "--wrap=none"],
                          input=md, capture_output=True, text=True, check=True).stdout


def nice_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} de {MONTHS[d.month - 1]} de {d.year}"


def parse_article(path):
    text = path.read_text(encoding="utf-8")
    head, body = text.split("\n---\n", 1)
    title = re.search(r"^# (.+)$", head, re.M).group(1).strip()
    field = lambda k: re.search(rf"^- {k}: (.+)$", head, re.M).group(1).strip()
    words = len(re.findall(r"\w+", body))
    return {
        "title": title,
        "seo_title": field("Título SEO"),
        "slug": field("Slug").strip("/"),
        "description": field("Meta descripción"),
        "body": md_to_html(body),
        "minutes": max(1, round(words / 200)),
        **ARTICLES[path.name],
    }


def parse_page(path):
    text = path.read_text(encoding="utf-8")
    _, front, body = text.split("---\n", 2)
    meta = dict(line.split(": ", 1) for line in front.strip().splitlines())
    meta["body"] = md_to_html(body).replace("{{EMAIL}}", html.escape(EMAIL))
    return meta


def adsense_head():
    if not ADSENSE_CLIENT:
        return ""
    return (f'<meta name="google-adsense-account" content="{ADSENSE_CLIENT}">\n'
            f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" '
            'crossorigin="anonymous"></script>')


def layout(*, title, description, path, body, extra_head=""):
    url = f"{SITE}{path}"
    e = html.escape
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{url}">
<meta name="google-site-verification" content="{GSC_VERIFICATION}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="es_ES">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap">
<link rel="stylesheet" href="/estilos.css">
{adsense_head()}
{extra_head}
</head>
<body>
<a class="skip" href="#contenido">Saltar al contenido</a>
<header class="top">
  <div class="wrap top-in">
    <a class="logo" href="/" aria-label="{NAME}, inicio"><span class="logo-mark" aria-hidden="true"></span><span>Pulso<b>Tech</b></span></a>
    <nav aria-label="Principal">
      <a href="/#articulos">Artículos</a>
      <a href="/sobre/">Sobre</a>
      <a href="/contacto/">Contacto</a>
    </nav>
  </div>
</header>
<main id="contenido">
{body}
</main>
<footer class="foot">
  <div class="wrap foot-in">
    <div>
      <a class="logo logo-sm" href="/"><span class="logo-mark" aria-hidden="true"></span><span>Pulso<b>Tech</b></span></a>
      <p>{TAGLINE}. Guías claras sobre relojes deportivos, apps y gadgets, escritas desde Granada.</p>
    </div>
    <nav aria-label="Legal">
      <a href="/sobre/">Sobre PulsoTech</a>
      <a href="/contacto/">Contacto</a>
      <a href="/privacidad/">Privacidad y cookies</a>
    </nav>
  </div>
  <div class="wrap foot-copy">© {date.today().year} {NAME}</div>
</footer>
</body>
</html>
"""


def cat_slug(c):
    return unicodedata.normalize("NFKD", c).encode("ascii", "ignore").decode().lower().replace(" ", "-")


CAT_INFO = {
    "Fútbol": "Tecnología para jugadores de fútbol: GPS, velocidad, calentamiento y apps para entrenar con balón.",
    "Relojes": "Guías para elegir, configurar y cuidar relojes deportivos, smartwatches y pulseras de actividad.",
    "Apps": "Las mejores apps para entrenar, dormir mejor y sacar partido a tu reloj o tu móvil.",
    "Salud": "Pasos, pulso y hábitos medidos con tecnología, explicados de forma sencilla.",
    "Running": "Tecnología y apps para empezar a correr y mejorar tus carreras.",
    "Ciclismo": "Ciclocomputadores, relojes, sensores y apps para salir en bici con datos.",
    "Entrenamiento": "Cómo usar los datos de tu reloj para entrenar mejor: zonas de pulso, VO2 máx, HRV y más.",
}


def chips_html(cats, current=None):
    out = []
    for c in cats:
        cls = "chip chip-lg chip-on" if c == current else "chip chip-lg"
        out.append(f'<a class="{cls}" href="/categoria/{cat_slug(c)}/">{html.escape(c)}</a>')
    return "".join(out)


def card(a):
    e = html.escape
    return f"""<article class="card">
  <a href="/{a['slug']}/" class="card-link">
    <div class="card-art" data-cat="{e(a['cat'])}" aria-hidden="true"><span>{a['emoji']}</span></div>
    <div class="card-body">
      <p class="chip">{e(a['cat'])}</p>
      <h3>{e(a['title'])}</h3>
      <p class="card-desc">{e(a['description'])}</p>
      <p class="meta">{a['minutes']} min de lectura</p>
    </div>
  </a>
</article>"""


def toc(body):
    heads = re.findall(r'<h2 id="([^"]+)">(.+?)</h2>', body)
    if len(heads) < 4:
        return ""
    items = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in heads)
    return f'<nav class="toc" aria-label="Contenido"><p class="toc-title">En este artículo</p><ol>{items}</ol></nav>'


def article_page(a, others):
    e = html.escape
    ld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": a["title"], "description": a["description"],
        "datePublished": a["date"], "dateModified": a["date"],
        "author": {"@type": "Person", "name": "Fer"},
        "publisher": {"@type": "Organization", "name": NAME},
        "mainEntityOfPage": f"{SITE}/{a['slug']}/", "inLanguage": "es-ES",
    }
    related = "\n".join(card(o) for o in others)
    body = f"""<article class="post">
  <header class="post-head">
    <div class="wrap narrow">
      <p class="crumbs"><a href="/">Inicio</a> <span aria-hidden="true">/</span> <a href="/categoria/{cat_slug(a['cat'])}/">{e(a['cat'])}</a></p>
      <h1>{e(a['title'])}</h1>
      <p class="post-meta">Por <strong>Fer</strong> · {nice_date(a['date'])} · {a['minutes']} min de lectura</p>
    </div>
  </header>
  <div class="wrap narrow prose">
{toc(a['body'])}
{a['body']}
  </div>
</article>
<section class="wrap related" aria-labelledby="mas">
  <h2 id="mas">Sigue leyendo</h2>
  <div class="grid">
{related}
  </div>
</section>"""
    return layout(title=a["seo_title"], description=a["description"], path=f"/{a['slug']}/", body=body,
                  extra_head=f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')


def home_page(articles):
    cards = "\n".join(card(a) for a in articles)
    cats = sorted({a["cat"] for a in articles})
    chips = chips_html(cats)
    body = f"""<section class="hero">
  <div class="wrap hero-in">
    <div class="hero-text">
      <p class="eyebrow">Deporte + tecnología</p>
      <h1>Entrena mejor con la tecnología que ya llevas encima</h1>
      <p class="lead">Guías claras sobre relojes deportivos, pulseras de actividad y apps para entrenar. Sin tecnicismos y sin humo.</p>
      <div class="hero-chips">{chips}</div>
    </div>
    <div class="hero-pulse" aria-hidden="true">
      <svg viewBox="0 0 320 120" preserveAspectRatio="none"><polyline points="0,70 70,70 90,70 105,30 120,105 138,15 155,90 170,70 320,70" /></svg>
      <div class="hero-bpm"><span>148</span> ppm</div>
    </div>
  </div>
</section>
<section class="wrap" id="articulos" aria-labelledby="ult">
  <h2 id="ult" class="section-title">Últimos artículos</h2>
  <div class="grid">
{cards}
  </div>
</section>"""
    return layout(title=f"{NAME}: {TAGLINE.lower()}",
                  description="Guías y comparativas sobre relojes deportivos, pulseras de actividad, apps para entrenar y gadgets para deportistas.",
                  path="/", body=body)


def category_page(cat, items, cats):
    cards = "\n".join(card(a) for a in items)
    desc = CAT_INFO.get(cat, f"Artículos de {cat} en {NAME}.")
    body = f"""<section class="cat-head">
  <div class="wrap">
    <p class="crumbs"><a href="/">Inicio</a> <span aria-hidden="true">/</span> Categoría</p>
    <h1>{html.escape(cat)}</h1>
    <p class="lead">{html.escape(desc)}</p>
    <div class="hero-chips">{chips_html(cats, cat)}</div>
  </div>
</section>
<section class="wrap" aria-label="Artículos">
  <p class="meta">{len(items)} artículos</p>
  <div class="grid">
{cards}
  </div>
</section>"""
    return layout(title=f"{cat}: guías y artículos | {NAME}", description=desc, path=f"/categoria/{cat_slug(cat)}/", body=body)


def related_for(a, articles):
    same = [o for o in articles if o is not a and o["cat"] == a["cat"]]
    rest = [o for o in articles if o is not a and o["cat"] != a["cat"]]
    return (same + rest)[:3]


def static_page(p):
    body = f"""<article class="post">
  <header class="post-head">
    <div class="wrap narrow"><h1>{html.escape(p['title'])}</h1></div>
  </header>
  <div class="wrap narrow prose">
{p['body']}
  </div>
</article>"""
    return layout(title=f"{p['title']} | {NAME}", description=p["description"], path=f"/{p['slug']}/", body=body)


def write(rel, content):
    f = OUT / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "assets", OUT)
    articles = [parse_article(ROOT / "articulos" / n) for n in ARTICLES]
    articles = [a for _, a in sorted(enumerate(articles), key=lambda t: (t[1]["date"], t[0]), reverse=True)]
    pages = [parse_page(p) for p in sorted((ROOT / "paginas").glob("*.md"))]

    write("index.html", home_page(articles))
    for a in articles:
        write(f"{a['slug']}/index.html", article_page(a, related_for(a, articles)))
    cats = sorted({a["cat"] for a in articles})
    for c in cats:
        write(f"categoria/{cat_slug(c)}/index.html", category_page(c, [a for a in articles if a["cat"] == c], cats))
    for p in pages:
        write(f"{p['slug']}/index.html", static_page(p))
    write("404.html", layout(title=f"Página no encontrada | {NAME}", description="Esta página no existe.", path="/404.html",
                             body='<section class="wrap narrow prose" style="padding-block:80px"><h1>Esta página no existe</h1>'
                                  '<p>Puede que el enlace esté mal escrito o que el artículo se haya movido.</p>'
                                  '<p><a href="/">Volver al inicio</a></p></section>'))

    lastmod = {f"/{a['slug']}/": a["date"] for a in articles}
    lastmod["/"] = max(a["date"] for a in articles)
    urls = (["/"] + [f"/{a['slug']}/" for a in articles] + [f"/categoria/{cat_slug(c)}/" for c in cats]
            + [f"/{p['slug']}/" for p in pages])
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{SITE}{u}</loc>{f'<lastmod>{lastmod[u]}</lastmod>' if u in lastmod else ''}</url>\n" for u in urls)
          + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    write("CNAME", "www.pulsotech.es\n")
    if ADSENSE_CLIENT:
        write("ads.txt", f"google.com, {ADSENSE_CLIENT.replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n")
    print(f"OK: {len(articles)} artículos, {len(pages)} páginas -> {OUT}")


if __name__ == "__main__":
    main()
