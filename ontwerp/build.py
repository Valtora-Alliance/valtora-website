#!/usr/bin/env python3
"""Bouwt de losse website uit het ontwerpbestand Main.dc.html.

Gebruik: python3 ontwerp/build.py ontwerp/Main.dc.html .

Resultaat: index.html (NL), en/index.html, de/index.html. Elke taal heeft een
eigen adres, eigen titel en beschrijving, hreflang-verwijzingen en vooraf
opgebouwde HTML (zodat zoekmachines de tekst zien zonder JavaScript).
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

src_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
src = src_path.read_text(encoding="utf-8")
SITE = "https://valtora-alliance.com"

# Afbeeldingen uit de ontwerpomgeving vervangen door lokale bestanden
BLOBS = {
    "c7b00c059ce74998870b404607067b8e": "/img/logo.png",
    "c5487935c9b179be327a7d9d63a6f5e6": "/img/hero.jpg",
    "b032db994bfff244aad689652c38ed21": "/img/andy.png",
    "a5f2dc03d7c3fd033239a8ffaa925a52": "/img/marion.jpg",
}
for blob, path in BLOBS.items():
    src = src.replace("/_blob/" + blob, path)
assert "/_blob/" not in src, "onbekende afbeelding in ontwerp"

body = src[src.index("<x-dc>") + len("<x-dc>"): src.index("</x-dc>")]
helmet = re.search(r"<helmet>([\s\S]*?)</helmet>", body).group(1)
tpl = re.sub(r"<helmet>[\s\S]*?</helmet>", "", body).strip()
logic = re.search(r'<script type="text/x-dc"[^>]*>([\s\S]*?)</script>', src).group(1)

# Lettertypes van de eigen server in plaats van Google (privacy)
helmet = re.sub(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*', "", helmet)
helmet, n = re.subn(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]*">',
                    '<link rel="stylesheet" href="/fonts/fonts.css">', helmet)
assert n == 1, "Google Fonts-link niet gevonden"

for _a, _b in (("fSend: 'Verstuur',", "fSend: 'Verstuur', formAction: '/bedankt.html',"),
               ("fSend: 'Send',", "fSend: 'Send', formAction: '/thank-you.html',"),
               ("fSend: 'Senden',", "fSend: 'Senden', formAction: '/danke.html',")):
    assert logic.count(_a) == 1, _a
    logic = logic.replace(_a, _b)

# Taalknoppen gaan naar het adres van die taal
_pick = "pick: () => this.setState({ lang: code })"
assert logic.count(_pick) == 1, "taalknop niet gevonden"
logic = logic.replace(_pick, "pick: () => window.__dcLang(code)")

# Contactformulier laten werken via Netlify Forms
assert '<form aria-label="{{ t.formLabel }}" style="' in tpl
tpl = tpl.replace(
    '<form aria-label="{{ t.formLabel }}" style="',
    '<form name="contact-{{ lang }}" method="POST" action="{{ t.formAction }}" '
    'aria-label="{{ t.formLabel }}" style="', 1)
assert 'gap: 16px">\n<label for="naam"' in tpl
tpl = tpl.replace(
    'gap: 16px">\n<label for="naam"',
    'gap: 16px">\n<input type="hidden" name="form-name" value="contact-{{ lang }}"><input type="hidden" name="taal" value="{{ lang }}">'
    '<p hidden><label>Laat leeg: <input name="bot-field"></label></p>\n<label for="naam"', 1)
for field in ('id="naam" name="naam" type="text"', 'id="email" name="email" type="email"'):
    assert field in tpl, field
    tpl = tpl.replace(field, field + " required", 1)
tpl = tpl.replace('id="vraag" name="vraag" rows="4"', 'id="vraag" name="vraag" rows="4" required', 1)
btn = '<button type="button" style="font: inherit; font-weight: 600; background: #C9A227'
assert btn in tpl
tpl = tpl.replace(btn, btn.replace('type="button"', 'type="submit"'), 1)
assert "</script" not in tpl.lower()

RUNTIME = r"""
(function () {
  var TPL = document.getElementById('dc-template').textContent;
  var root = document.getElementById('app');
  var fns = [];
  function get(path, ctx) {
    return path.trim().split('.').reduce(function (o, k) { return o == null ? undefined : o[k]; }, ctx);
  }
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function findClose(str, tag, from) {
    var depth = 1, re = new RegExp('<(/?)' + tag + '\\b[^>]*>', 'g'), m;
    re.lastIndex = from;
    while ((m = re.exec(str))) { depth += m[1] ? -1 : 1; if (!depth) return [m.index, re.lastIndex]; }
    throw new Error('unclosed ' + tag);
  }
  function render(str, ctx) {
    var out = '', i = 0, re = /<sc-(for|if)\b([^>]*)>/g, m;
    while ((m = re.exec(str))) {
      out += str.slice(i, m.index);
      var tag = 'sc-' + m[1], close = findClose(str, tag, re.lastIndex);
      var inner = str.slice(re.lastIndex, close[0]), attrs = m[2];
      if (m[1] === 'for') {
        var list = get(attrs.match(/list="\{\{([^}]*)\}\}"/)[1], ctx) || [];
        var as = attrs.match(/as="([^"]*)"/)[1];
        list.forEach(function (it, ix) {
          var c = Object.assign({}, ctx); c[as] = it; c.index = ix; out += render(inner, c);
        });
      } else if (get(attrs.match(/value="\{\{([^}]*)\}\}"/)[1], ctx)) {
        out += render(inner, ctx);
      }
      i = close[1]; re.lastIndex = close[1];
    }
    out += str.slice(i);
    out = out.replace(/\s(on[A-Z]\w*)="\{\{([^}]*)\}\}"/g, function (_, ev, p) {
      var fn = get(p, ctx);
      if (typeof fn !== 'function') return '';
      return ' data-dc-' + ev.slice(2).toLowerCase() + '="' + (fns.push(fn) - 1) + '"';
    });
    return out.replace(/\{\{([^}]*)\}\}/g, function (_, p) { var x = get(p, ctx); return x == null ? '' : esc(x); });
  }
  var pending = false;
  function DCLogic(props) { this.props = props || {}; this.state = {}; }
  DCLogic.prototype.setState = function (p) {
    Object.assign(this.state, p);
    if (!pending) { pending = true; requestAnimationFrame(draw); }
  };
  window.DCLogic = DCLogic;
  var comp;
  function draw() {
    pending = false;
    var saved = {};
    root.querySelectorAll('input[id], textarea[id], select[id]').forEach(function (el) { saved[el.id] = el.value; });
    fns = [];
    var v = comp.renderVals();
    root.innerHTML = render(TPL, v);
    Object.keys(saved).forEach(function (id) { var el = document.getElementById(id); if (el && saved[id]) el.value = saved[id]; });
  }
  var PATHS = { nl: '/', en: '/en/', de: '/de/' };
  window.__dcLang = function (code) {
    if (code === comp.state.lang) return;
    location.href = PATHS[code] + location.hash;
  };
  root.addEventListener('click', function (e) {
    var el = e.target.closest('[data-dc-click]');
    if (el) { fns[+el.getAttribute('data-dc-click')](e); }
  });
  root.addEventListener('submit', function (e) {
    var f = e.target;
    if (!/^contact-/.test(f.getAttribute('name') || '')) return;
    e.preventDefault();
    var btn = f.querySelector('button[type=submit]'); if (btn) btn.disabled = true;
    fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(new FormData(f)).toString() })
      .then(function (r) { if (!r.ok) throw new Error(r.status); location.href = f.getAttribute('action'); })
      .catch(function () { if (btn) btn.disabled = false; alert(document.documentElement.lang === 'de' ? 'Senden fehlgeschlagen. Bitte mailen Sie an info@valtora-alliance.com.' : document.documentElement.lang === 'en' ? 'Sending failed. Please email info@valtora-alliance.com.' : 'Verzenden mislukt. Mail ons gerust op info@valtora-alliance.com.'); });
  });
  window.__dcStart = function (Component, lang) {
    comp = new Component({});
    comp.state.lang = lang;
    draw();
    if (location.hash) { var t = document.getElementById(location.hash.slice(1)); if (t) t.scrollIntoView(); }
  };
})();
"""

META = {
    "nl": {
        "path": "/", "locale": "nl_BE",
        "title": "Valtora Alliance – Ondernemen en investeren in Paraguay",
        "desc": "Valtora Alliance begeleidt Belgische en Nederlandse ondernemers bij residentie, bank, vennootschap en investeringen in Paraguay. Eén aanspreekpunt, in uw eigen taal.",
        "ogdesc": "Uw volgende stap ligt buiten Europa. Verkenning, residentie, bank en investeringen in Paraguay, met één aanspreekpunt.",
        "noscript": "Deze website werkt het best met JavaScript. Contact:",
    },
    "en": {
        "path": "/en/", "locale": "en_GB",
        "title": "Valtora Alliance – Doing business and investing in Paraguay",
        "desc": "Valtora Alliance guides entrepreneurs from Belgium and the Netherlands through residency, banking, company formation and investment in Paraguay.",
        "ogdesc": "Your next step lies beyond Europe. Exploration, residency, banking and investment in Paraguay, with one point of contact.",
        "noscript": "This website works best with JavaScript. Contact:",
    },
    "de": {
        "path": "/de/", "locale": "de_DE",
        "title": "Valtora Alliance – Unternehmen und Investieren in Paraguay",
        "desc": "Valtora Alliance begleitet Unternehmer aus den Niederlanden und Belgien bei Aufenthalt, Bankkonto, Firmengründung und Investitionen in Paraguay.",
        "ogdesc": "Ihr nächster Schritt liegt außerhalb Europas. Erkundung, Aufenthalt, Bank und Investitionen in Paraguay, mit einem Ansprechpartner.",
        "noscript": "Diese Website funktioniert am besten mit JavaScript. Kontakt:",
    },
}

ORG = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "@id": SITE + "/#organisatie",
    "name": "Valtora Alliance",
    "legalName": "a&a-mmvp BV",
    "url": SITE + "/",
    "logo": SITE + "/img/logo.png",
    "image": SITE + "/img/og.jpg",
    "email": "info@valtora-alliance.com",
    "telephone": "+32 499 11 75 98",
    "taxID": "BE0840525883",
    "address": {"@type": "PostalAddress", "streetAddress": "Trekschurenstraat 92", "postalCode": "3500",
                "addressLocality": "Hasselt", "addressCountry": "BE"},
    "areaServed": [{"@type": "Country", "name": n} for n in ("Belgium", "Netherlands", "Paraguay")],
    "knowsLanguage": ["nl", "en", "de", "es"],
    "founder": [
        {"@type": "Person", "name": "Andy Schuurmans", "telephone": "+32 499 11 75 98"},
        {"@type": "Person", "name": "Marion Sterckx", "telephone": "+32 474 58 26 85"},
    ],
}


def prerender(lang):
    """Rendert de pagina in Node met dezelfde runtime als in de browser."""
    js = (
        "var TPL=" + json.dumps(tpl) + ";\n"
        "var root={innerHTML:'',querySelectorAll:function(){return[]},addEventListener:function(){}};\n"
        "global.window=global;global.document={getElementById:function(id){return id==='dc-template'?{textContent:TPL}:id==='app'?root:null},documentElement:{}};\n"
        "global.location={hash:'',search:''};global.requestAnimationFrame=function(){};\n"
        + RUNTIME + "\n" + logic + "\nwindow.__dcStart(Component," + json.dumps(lang) + ");\n"
        "process.stdout.write(root.innerHTML);\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(js)
    out = subprocess.run(["node", f.name], capture_output=True, text=True, check=True).stdout
    Path(f.name).unlink()
    assert len(out) > 20000, "prerender te kort"
    return out


hreflang = "\n".join(
    f'<link rel="alternate" hreflang="{l}" href="{SITE}{m["path"]}">' for l, m in META.items()
) + f'\n<link rel="alternate" hreflang="x-default" href="{SITE}/">'

# Eén verborgen formulier (alleen op de NL-pagina) registreert het formulier bij Netlify,
# met vaste Nederlandse veldnamen voor de meldingsmail, in welke taal de bezoeker ook invult.
LABELS = {
    "nl": ("Naam", "E-mail", "Land", "Waar kunnen we u mee helpen?", "Taal van de website", "Laat leeg"),
    "en": ("Name", "Email", "Country", "How can we help you?", "Website language", "Leave empty"),
    "de": ("Name", "E-Mail", "Land", "Wie können wir Ihnen helfen?", "Sprache der Website", "Leer lassen"),
}


def detect(lang):
    """Verborgen formulier waarmee Netlify het formulier van deze taal registreert,
    met veldnamen in die taal voor de meldingsmail."""
    l = LABELS[lang]
    return (f'<form name="contact-{lang}" data-netlify="true" netlify-honeypot="bot-field" hidden>\n'
            f'<label>{l[0]} <input name="naam"></label>\n<label>{l[1]} <input name="email"></label>\n'
            f'<label>{l[2]} <input name="land"></label>\n<label>{l[3]} <textarea name="vraag"></textarea></label>\n'
            f'<label>{l[4]} <input name="taal"></label>\n<label>{l[5]} <input name="bot-field"></label>\n</form>\n')


for lang, m in META.items():
    html = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{m["title"]}</title>
<meta name="description" content="{m["desc"]}">
<link rel="canonical" href="{SITE}{m["path"]}">
{hreflang}
<link rel="icon" type="image/png" href="/img/favicon.png">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Valtora Alliance">
<meta property="og:locale" content="{m["locale"]}">
<meta property="og:title" content="{m["title"]}">
<meta property="og:description" content="{m["ogdesc"]}">
<meta property="og:image" content="{SITE}/img/og.jpg">
<meta property="og:url" content="{SITE}{m["path"]}">
<script type="application/ld+json">{json.dumps(ORG, ensure_ascii=False)}</script>
{helmet.strip()}
</head>
<body>
<div id="app">{prerender(lang)}</div>
<noscript><p style="padding:24px;font-family:sans-serif">{m["noscript"]} <a href="mailto:info@valtora-alliance.com">info@valtora-alliance.com</a></p></noscript>
{detect(lang)}<script type="text/x-template" id="dc-template">
{tpl}
</script>
<script>{RUNTIME}</script>
<script>
{logic.strip()}
window.__dcStart(Component, {json.dumps(lang)});
</script>
</body>
</html>
"""
    target = out_dir / m["path"].strip("/") / "index.html" if m["path"] != "/" else out_dir / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    print(target, len(html), "tekens")
