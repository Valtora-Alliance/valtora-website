#!/usr/bin/env python3
"""Bouwt de losse website (index.html) uit het ontwerpbestand Main.dc.html.

Gebruik: python3 build.py <pad/naar/Main.dc.html> <uitvoermap>
"""
import re
import sys
from pathlib import Path

src_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
src = src_path.read_text(encoding="utf-8")

# Afbeeldingen uit de ontwerpomgeving vervangen door lokale bestanden
BLOBS = {
    "c7b00c059ce74998870b404607067b8e": "img/logo.png",
    "c5487935c9b179be327a7d9d63a6f5e6": "img/hero.jpg",
    "b032db994bfff244aad689652c38ed21": "img/andy.png",
    "a5f2dc03d7c3fd033239a8ffaa925a52": "img/marion.jpg",
}
for blob, path in BLOBS.items():
    src = src.replace("/_blob/" + blob, path)
assert "/_blob/" not in src, "onbekende afbeelding in ontwerp"

body = src[src.index("<x-dc>") + len("<x-dc>"): src.index("</x-dc>")]
helmet = re.search(r"<helmet>([\s\S]*?)</helmet>", body).group(1)
tpl = re.sub(r"<helmet>[\s\S]*?</helmet>", "", body).strip()
logic = re.search(r'<script type="text/x-dc"[^>]*>([\s\S]*?)</script>', src).group(1)

# Contactformulier laten werken via Netlify Forms
form_open = re.search(r"<form aria-label=\"\{\{ t\.formLabel \}\}\" style=\"", tpl)
assert form_open
tpl = tpl.replace(
    '<form aria-label="{{ t.formLabel }}" style="',
    '<form name="contact" method="POST" action="/bedankt.html" data-netlify="true" netlify-honeypot="bot-field" '
    'aria-label="{{ t.formLabel }}" style="', 1)
tpl = tpl.replace(
    'gap: 16px">\n<label for="naam"',
    'gap: 16px">\n<input type="hidden" name="form-name" value="contact">'
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
    if (p && p.lang) { try { localStorage.setItem('valtora-lang', p.lang); } catch (e) {} }
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
    document.documentElement.lang = v.lang || 'nl';
  }
  root.addEventListener('click', function (e) {
    var el = e.target.closest('[data-dc-click]');
    if (el) { fns[+el.getAttribute('data-dc-click')](e); }
  });
  window.__dcStart = function (Component) {
    comp = new Component({});
    var lang = null;
    try { lang = new URLSearchParams(location.search).get('lang') || localStorage.getItem('valtora-lang'); } catch (e) {}
    if (lang === 'nl' || lang === 'en' || lang === 'de') comp.state.lang = lang;
    draw();
    if (location.hash) { var t = document.getElementById(location.hash.slice(1)); if (t) t.scrollIntoView(); }
  };
})();
"""

html = f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Valtora Alliance – Begeleiding in Paraguay</title>
<meta name="description" content="Valtora Alliance begeleidt Belgische, Nederlandse en Duitse ondernemers bij verkenning, vestiging en investeringen in Paraguay.">
<link rel="canonical" href="https://www.valtora-alliance.com/">
<link rel="icon" type="image/png" href="img/favicon.png">
<link rel="apple-touch-icon" href="img/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:title" content="Valtora Alliance – Begeleiding in Paraguay">
<meta property="og:description" content="Uw volgende stap ligt buiten Europa. Verkenning, residentie, bank en investeringen in Paraguay, met één aanspreekpunt.">
<meta property="og:image" content="https://www.valtora-alliance.com/img/og.jpg">
<meta property="og:url" content="https://www.valtora-alliance.com/">
{helmet.strip()}
</head>
<body>
<div id="app"><noscript><p style="padding:24px;font-family:sans-serif">Deze website heeft JavaScript nodig. Contact: <a href="mailto:info@valtora-alliance.com">info@valtora-alliance.com</a></p></noscript></div>
<form name="contact" data-netlify="true" netlify-honeypot="bot-field" hidden>
<input name="naam"><input name="email"><input name="land"><textarea name="vraag"></textarea><input name="bot-field">
</form>
<script type="text/x-template" id="dc-template">
{tpl}
</script>
<script>{RUNTIME}</script>
<script>
{logic.strip()}
window.__dcStart(Component);
</script>
</body>
</html>
"""
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "index.html").write_text(html, encoding="utf-8")
print("index.html geschreven:", len(html), "tekens")
