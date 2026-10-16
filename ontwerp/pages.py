#!/usr/bin/env python3
"""Maakt de losse pagina's: privacyverklaring (3 talen), bedankpagina's, 404, robots.txt en sitemap.xml.

Gebruik: python3 ontwerp/pages.py .
"""
import sys
from pathlib import Path

out = Path(sys.argv[1])
SITE = "https://valtora-alliance.com"
UPDATED = {"nl": "16 oktober 2026", "en": "16 October 2026", "de": "16. Oktober 2026"}

CSS = """body{margin:0;background:#F7F6F2;color:#0B2545;font-family:'Source Sans 3','Segoe UI',sans-serif;font-size:17px;line-height:1.6}
main{max-width:720px;margin:0 auto;padding:56px 24px 72px}
.logo{height:52px;width:auto;margin-bottom:40px}
h1{font-family:'EB Garamond',Georgia,serif;font-weight:500;font-size:40px;line-height:1.15;margin:0 0 16px}
h2{font-family:'EB Garamond',Georgia,serif;font-weight:500;font-size:26px;line-height:1.2;margin:36px 0 8px}
p,li{color:#4A5C70}p{margin:0 0 12px}ul{margin:0 0 12px;padding-left:20px}
a{color:#0B2545}
.small{font-size:14px}
.lang{margin-top:40px;padding-top:20px;border-top:1px solid #E3E1DA;font-size:15px}
a.btn{display:inline-block;margin-top:24px;background:#0B2545;color:#fff;text-decoration:none;font-weight:600;padding:14px 22px;border-radius:4px}"""


def page(lang, title, body, robots=None, canonical=None, alternates=None):
    head = [f'<meta name="robots" content="{robots}">'] if robots else []
    if canonical:
        head.append(f'<link rel="canonical" href="{SITE}{canonical}">')
    for l, href in (alternates or {}).items():
        head.append(f'<link rel="alternate" hreflang="{l}" href="{SITE}{href}">')
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{chr(10).join(head)}
<link rel="icon" type="image/png" href="/img/favicon.png">
<link rel="stylesheet" href="/fonts/fonts.css">
<style>
{CSS}
</style>
</head>
<body>
<main>
<a href="{ {'nl': '/', 'en': '/en/', 'de': '/de/'}[lang] }"><img class="logo" src="/img/logo.png" alt="Valtora Alliance"></a>
{body}
</main>
</body>
</html>
"""


def write(rel, html):
    p = out / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
    print(p)


# ---------- Privacyverklaring ----------
PRIV_ALT = {"nl": "/privacy/", "en": "/en/privacy/", "de": "/de/datenschutz/"}

PRIV = {
"nl": ("Privacyverklaring – Valtora Alliance", f"""
<h1>Privacyverklaring</h1>
<p class="small">Laatst bijgewerkt op {UPDATED['nl']}</p>
<p>Valtora Alliance is een handelsnaam van a&amp;a-mmvp BV. In deze verklaring leest u welke persoonsgegevens wij verwerken wanneer u onze website bezoekt of contact met ons opneemt, waarom we dat doen en welke rechten u hebt.</p>
<h2>Wie is verantwoordelijk?</h2>
<p>a&amp;a-mmvp BV, Trekschurenstraat 92, 3500 Hasselt, België<br>Ondernemingsnummer 0840.525.883<br>E-mail: <a href="mailto:info@valtora-alliance.com">info@valtora-alliance.com</a> · Telefoon: +32 499 11 75 98</p>
<h2>Welke gegevens verwerken wij?</h2>
<ul>
<li>Wat u invult in het contactformulier: uw naam, e-mailadres, land en uw vraag. Ook de taal van de pagina waarop u het formulier invult, wordt meegestuurd.</li>
<li>Wat u ons zelf toestuurt per e-mail of telefoon.</li>
<li>Technische gegevens die elke webserver ontvangt, zoals uw IP-adres en het tijdstip van uw bezoek. Onze hostingpartner gebruikt die alleen om de website veilig en werkend te houden.</li>
</ul>
<h2>Waarvoor gebruiken wij uw gegevens?</h2>
<ul>
<li>Om uw vraag te beantwoorden en, als u dat wilt, een kennismakingsgesprek te plannen. Dat doen we omdat u ons daarom vraagt, met het oog op een mogelijke overeenkomst (artikel 6.1.b AVG).</li>
<li>Om een overeenkomst met u uit te voeren, als u klant wordt (artikel 6.1.b AVG).</li>
<li>Om te voldoen aan wettelijke verplichtingen, zoals onze boekhouding (artikel 6.1.c AVG).</li>
<li>Om onze website veilig te houden en misbruik van het formulier te voorkomen (gerechtvaardigd belang, artikel 6.1.f AVG).</li>
</ul>
<p>Wij sturen u geen nieuwsbrieven of reclame zonder uw toestemming. Wij verkopen uw gegevens nooit.</p>
<h2>Cookies en metingen</h2>
<p>Deze website plaatst geen cookies en gebruikt geen analyse- of advertentiediensten. Ook de lettertypes worden van onze eigen server geladen, niet van Google. Komt daar ooit verandering in, dan passen we deze verklaring aan en vragen we vooraf uw toestemming waar dat nodig is.</p>
<h2>Wie krijgt uw gegevens te zien?</h2>
<ul>
<li>Netlify, Inc. host de website en ontvangt de berichten van het contactformulier. Netlify is gevestigd in de Verenigde Staten. De doorgifte gebeurt op basis van het EU-VS-gegevensprivacykader en de standaardcontractbepalingen van de Europese Commissie.</li>
<li>Combell NV (België) verzorgt onze e-mail.</li>
<li>Wordt u klant, dan delen we enkel de gegevens die nodig zijn met partners die u helpen in Paraguay, zoals advocaten, notarissen en banken, en alleen nadat we dat met u hebben besproken.</li>
</ul>
<h2>Hoe lang bewaren wij uw gegevens?</h2>
<p>Berichten van wie geen klant wordt, verwijderen we uiterlijk twee jaar na ons laatste contact. Klantgegevens bewaren we zolang de samenwerking loopt en daarna zo lang als de wet het vraagt, bijvoorbeeld zeven jaar voor boekhoudkundige stukken.</p>
<h2>Uw rechten</h2>
<p>U kunt ons altijd vragen om uw gegevens in te zien, te verbeteren of te laten verwijderen. U kunt ook bezwaar maken tegen een verwerking, vragen om die te beperken of uw gegevens in een gangbaar formaat opvragen. Stuur daarvoor een e-mail naar <a href="mailto:info@valtora-alliance.com">info@valtora-alliance.com</a>. Wij antwoorden binnen een maand.</p>
<p>Bent u niet tevreden over hoe wij met uw gegevens omgaan, dan kunt u een klacht indienen bij de Gegevensbeschermingsautoriteit, Drukpersstraat 35, 1000 Brussel, <a href="https://www.gegevensbeschermingsautoriteit.be">www.gegevensbeschermingsautoriteit.be</a>.</p>
<p class="lang">Also in <a href="/en/privacy/">English</a> · Auch auf <a href="/de/datenschutz/">Deutsch</a></p>
"""),
"en": ("Privacy statement – Valtora Alliance", f"""
<h1>Privacy statement</h1>
<p class="small">Last updated on {UPDATED['en']}</p>
<p>Valtora Alliance is a trade name of a&amp;a-mmvp BV. This statement explains which personal data we process when you visit our website or contact us, why we do so and what your rights are.</p>
<h2>Who is responsible?</h2>
<p>a&amp;a-mmvp BV, Trekschurenstraat 92, 3500 Hasselt, Belgium<br>Company number 0840.525.883<br>Email: <a href="mailto:info@valtora-alliance.com">info@valtora-alliance.com</a> · Phone: +32 499 11 75 98</p>
<h2>What data do we process?</h2>
<ul>
<li>What you enter in the contact form: your name, email address, country and your question. The language of the page on which you fill in the form is sent along.</li>
<li>What you send us yourself by email or phone.</li>
<li>Technical data that every web server receives, such as your IP address and the time of your visit. Our hosting partner uses this only to keep the website secure and working.</li>
</ul>
<h2>Why do we use your data?</h2>
<ul>
<li>To answer your question and, if you wish, to schedule an introductory meeting. We do this at your request, with a view to a possible agreement (Article 6(1)(b) GDPR).</li>
<li>To perform an agreement with you if you become a client (Article 6(1)(b) GDPR).</li>
<li>To meet legal obligations, such as our accounting (Article 6(1)(c) GDPR).</li>
<li>To keep our website secure and prevent misuse of the form (legitimate interest, Article 6(1)(f) GDPR).</li>
</ul>
<p>We do not send newsletters or advertising without your consent. We never sell your data.</p>
<h2>Cookies and analytics</h2>
<p>This website sets no cookies and uses no analytics or advertising services. The fonts are also loaded from our own server, not from Google. If this ever changes, we will update this statement and ask for your consent in advance where required.</p>
<h2>Who sees your data?</h2>
<ul>
<li>Netlify, Inc. hosts the website and receives the messages from the contact form. Netlify is based in the United States. The transfer is based on the EU-US Data Privacy Framework and the European Commission’s standard contractual clauses.</li>
<li>Combell NV (Belgium) provides our email.</li>
<li>If you become a client, we share only the data that is needed with partners who help you in Paraguay, such as lawyers, notaries and banks, and only after discussing this with you.</li>
</ul>
<h2>How long do we keep your data?</h2>
<p>Messages from people who do not become clients are deleted no later than two years after our last contact. Client data is kept for as long as we work together and afterwards for as long as the law requires, for example seven years for accounting records.</p>
<h2>Your rights</h2>
<p>You can always ask us to access, correct or delete your data. You can also object to processing, ask us to restrict it, or request your data in a common format. To do so, email <a href="mailto:info@valtora-alliance.com">info@valtora-alliance.com</a>. We will reply within one month.</p>
<p>If you are not satisfied with how we handle your data, you can lodge a complaint with the Belgian Data Protection Authority, Drukpersstraat 35, 1000 Brussels, <a href="https://www.dataprotectionauthority.be">www.dataprotectionauthority.be</a>, or with the supervisory authority in your own country.</p>
<p class="lang">Ook in het <a href="/privacy/">Nederlands</a> · Auch auf <a href="/de/datenschutz/">Deutsch</a></p>
"""),
"de": ("Datenschutzerklärung – Valtora Alliance", f"""
<h1>Datenschutzerklärung</h1>
<p class="small">Zuletzt aktualisiert am {UPDATED['de']}</p>
<p>Valtora Alliance ist ein Handelsname der a&amp;a-mmvp BV. In dieser Erklärung erfahren Sie, welche personenbezogenen Daten wir verarbeiten, wenn Sie unsere Website besuchen oder uns kontaktieren, warum wir das tun und welche Rechte Sie haben.</p>
<h2>Wer ist verantwortlich?</h2>
<p>a&amp;a-mmvp BV, Trekschurenstraat 92, 3500 Hasselt, Belgien<br>Unternehmensnummer 0840.525.883<br>E-Mail: <a href="mailto:info@valtora-alliance.com">info@valtora-alliance.com</a> · Telefon: +32 499 11 75 98</p>
<h2>Welche Daten verarbeiten wir?</h2>
<ul>
<li>Ihre Angaben im Kontaktformular: Name, E-Mail-Adresse, Land und Ihre Frage. Die Sprache der Seite, auf der Sie das Formular ausfüllen, wird mitgesendet.</li>
<li>Was Sie uns selbst per E-Mail oder Telefon mitteilen.</li>
<li>Technische Daten, die jeder Webserver erhält, etwa Ihre IP-Adresse und der Zeitpunkt Ihres Besuchs. Unser Hosting-Partner nutzt diese nur, um die Website sicher und funktionsfähig zu halten.</li>
</ul>
<h2>Wofür verwenden wir Ihre Daten?</h2>
<ul>
<li>Um Ihre Frage zu beantworten und auf Wunsch ein Kennenlerngespräch zu vereinbaren. Das geschieht auf Ihre Anfrage hin, im Hinblick auf einen möglichen Vertrag (Art. 6 Abs. 1 lit. b DSGVO).</li>
<li>Um einen Vertrag mit Ihnen zu erfüllen, wenn Sie Kunde werden (Art. 6 Abs. 1 lit. b DSGVO).</li>
<li>Um gesetzliche Pflichten zu erfüllen, etwa unsere Buchhaltung (Art. 6 Abs. 1 lit. c DSGVO).</li>
<li>Um unsere Website sicher zu halten und Missbrauch des Formulars zu verhindern (berechtigtes Interesse, Art. 6 Abs. 1 lit. f DSGVO).</li>
</ul>
<p>Wir senden Ihnen ohne Ihre Einwilligung keine Newsletter oder Werbung. Wir verkaufen Ihre Daten niemals.</p>
<h2>Cookies und Analyse</h2>
<p>Diese Website setzt keine Cookies und nutzt keine Analyse- oder Werbedienste. Auch die Schriften werden von unserem eigenen Server geladen, nicht von Google. Sollte sich das ändern, passen wir diese Erklärung an und holen, wo nötig, vorher Ihre Einwilligung ein.</p>
<h2>Wer erhält Ihre Daten?</h2>
<ul>
<li>Netlify, Inc. hostet die Website und empfängt die Nachrichten aus dem Kontaktformular. Netlify hat seinen Sitz in den USA. Die Übermittlung erfolgt auf Grundlage des EU-US Data Privacy Framework und der Standardvertragsklauseln der Europäischen Kommission.</li>
<li>Combell NV (Belgien) stellt unsere E-Mail bereit.</li>
<li>Werden Sie Kunde, geben wir nur die nötigen Daten an Partner weiter, die Sie in Paraguay unterstützen, etwa Anwälte, Notare und Banken, und nur nach Absprache mit Ihnen.</li>
</ul>
<h2>Wie lange speichern wir Ihre Daten?</h2>
<p>Nachrichten von Personen, die nicht Kunde werden, löschen wir spätestens zwei Jahre nach dem letzten Kontakt. Kundendaten speichern wir für die Dauer der Zusammenarbeit und danach so lange, wie es das Gesetz verlangt, zum Beispiel sieben Jahre für Buchhaltungsunterlagen.</p>
<h2>Ihre Rechte</h2>
<p>Sie können jederzeit Auskunft über Ihre Daten verlangen sowie deren Berichtigung oder Löschung. Sie können der Verarbeitung auch widersprechen, ihre Einschränkung verlangen oder Ihre Daten in einem gängigen Format anfordern. Schreiben Sie dazu an <a href="mailto:info@valtora-alliance.com">info@valtora-alliance.com</a>. Wir antworten innerhalb eines Monats.</p>
<p>Sind Sie mit dem Umgang mit Ihren Daten nicht zufrieden, können Sie sich bei der belgischen Datenschutzbehörde beschweren (Drukpersstraat 35, 1000 Brüssel, <a href="https://www.dataprotectionauthority.be">www.dataprotectionauthority.be</a>) oder bei der Aufsichtsbehörde in Ihrem Land.</p>
<p class="lang">Ook in het <a href="/privacy/">Nederlands</a> · Also in <a href="/en/privacy/">English</a></p>
"""),
}
for lang, (title, body) in PRIV.items():
    write(PRIV_ALT[lang].strip("/") + "/index.html", page(lang, title, body, canonical=PRIV_ALT[lang], alternates=PRIV_ALT))

# ---------- Bedankpagina's ----------
THANKS = {
    "bedankt.html": ("nl", "Bedankt – Valtora Alliance", "Bedankt voor uw bericht.",
                     "We hebben uw vraag goed ontvangen en nemen binnen twee werkdagen contact met u op.", "/", "Terug naar de website"),
    "thank-you.html": ("en", "Thank you – Valtora Alliance", "Thank you for your message.",
                       "We have received your request and will get back to you within two working days.", "/en/", "Back to the website"),
    "danke.html": ("de", "Danke – Valtora Alliance", "Vielen Dank für Ihre Nachricht.",
                   "Wir haben Ihre Anfrage erhalten und melden uns innerhalb von zwei Werktagen bei Ihnen.", "/de/", "Zurück zur Website"),
}
for fn, (lang, title, h1, text, home, back) in THANKS.items():
    write(fn, page(lang, title, f'<h1>{h1}</h1>\n<p>{text}</p>\n<a class="btn" href="{home}">{back}</a>', robots="noindex"))

# ---------- 404 ----------
write("404.html", page("nl", "Pagina niet gevonden – Valtora Alliance", """
<h1>Deze pagina bestaat niet.</h1>
<p>Misschien is de link verouderd of zit er een tikfout in het adres.</p>
<a class="btn" href="/">Naar de homepage</a>
<div class="lang">
<p><strong>Page not found.</strong> This page does not exist. <a href="/en/">Go to the homepage</a></p>
<p><strong>Seite nicht gefunden.</strong> Diese Seite existiert nicht. <a href="/de/">Zur Startseite</a></p>
</div>
""", robots="noindex"))

# ---------- robots.txt en sitemap.xml ----------
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

HOME = {"nl": "/", "en": "/en/", "de": "/de/"}


def urlset(group):
    rows = []
    for href in group.values():
        alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{SITE}{h}"/>' for l, h in group.items())
        alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{group["nl"]}"/>'
        rows.append(f"  <url>\n    <loc>{SITE}{href}</loc>\n    <lastmod>2026-10-16</lastmod>{alts}\n  </url>")
    return rows


xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
       + "\n".join(urlset(HOME) + urlset(PRIV_ALT)) + "\n</urlset>\n")
write("sitemap.xml", xml)
