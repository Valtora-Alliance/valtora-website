# Website Valtora Alliance

Eén pagina in drie talen (NL, EN, DE), online gezet via Netlify.

- `index.html` – de website (gebouwd uit `ontwerp/Main.dc.html`, niet rechtstreeks bewerken)
- `bedankt.html` – pagina na het versturen van het contactformulier
- `img/` – logo, foto's, favicon
- `netlify.toml` – instellingen voor Netlify
- `ontwerp/` – het ontwerpbestand en het bouwscript

Opnieuw bouwen na een wijziging in het ontwerp:

    python3 ontwerp/build.py ontwerp/Main.dc.html .

Het contactformulier gebruikt Netlify Forms: inzendingen verschijnen in Netlify onder Forms → contact.
