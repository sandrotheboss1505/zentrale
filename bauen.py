#!/usr/bin/env python3
"""
ZENTRALE · PWA bauen
Die Oberfläche liegt in Teilen im Ordner app/ (ein Unterordner pro Bereich, CSS und JS getrennt).
bauen.py setzt sie nach der Liste SEITEN zu AppSeite.html, ChiefSeite.html und SensiSeite.html im Hauptordner zusammen
(die braucht die alte Web App doGet, clasp schickt sie zu Google) und macht daraus web/index.html für GitHub Pages.
Die drei Seiten sind erzeugt: nie von Hand ändern, Änderungen immer in app/.
Aufruf: python3 web/bauen.py        (Live Seite web/index.html)
        python3 web/bauen.py test   (Testseite web/test/ mit Spieldaten, spricht nie mit Google)
"""
import io, json, os, re, sys, time

HIER = os.path.dirname(os.path.abspath(__file__))
API = 'https://script.google.com/macros/s/AKfycby_mlOvm6veeRy8tqW0SyjI4XqaZJRVt_dUFyv5VV2n9KsCfKVsX45EeMVUHlcNyV0FXA/exec'
VERSION = time.strftime('%Y%m%d%H%M')
NAME = os.environ.get('ZENTRALE_NAME', '').strip()   # aus bereitstellen.sh, zum Beispiel "V80 Beschreibung"
TEST = len(sys.argv) > 1 and sys.argv[1] == 'test'
ZIEL = os.path.join(HIER, 'test') if TEST else HIER

# ── Oberfläche: Teile aus app/ in fester Reihenfolge ──
# Jede Seite ist eine Liste. Ein .html Teil wird so eingesetzt, wie er ist.
# Eine Liste von .css Dateien wird ein <style> Block, eine Liste von .js Dateien ein <script> Block.
# Die Reihenfolge zählt: CSS gilt von oben nach unten, JS läuft von oben nach unten.
# Im Browser laufen die Blöcke von Chief und Sensi vor dem Hauptteil (AppSeite setzt sie vor ihren <script> Block).
# Neue Datei in app/: hier eintragen, sonst bricht bauen.py ab.
# SEITEN Anfang
SEITEN = [
    ('AppSeite.html', [
        'basis/kopf.html',                # Kopf der Seite bis vor <style>
        [
            'basis/basis.css',            # Farben, Schrift, Kopf, Karte, Bedienelemente, Leiste, Meldung, Tipp Animation
            'koeoe/koeoe.css',            # Köö: Zeiten, Ringe grau außer Körper, Kästchen, Sport
            'woche/woche.css',            # Karte Woche im Tag, Liste Letzte 14 Tage
            'geld/geld.css',              # Posten (Ausgaben, Konten), Geld Karte letzte 7 Tage
            'tag/tag.css',                # Check ins, Termine, Blöcke, Heute Karte, Planen, Neu Fenster, Tasks vormerken
            'basis/mac.css',              # Mac: breites Layout, Wechsel der Ansicht
            'tag/erledigt.css',           # Ringe, Erledigt, Taskpunkte, Plus fliegt
        ],
        'basis/seite.html',               # Gerüst: Kopfleiste, Inhalt, Leiste, Chief und Sensi (Apps Script Einschub)
        [
            'basis/kern.js',              # Einstellungen, Zustand, kleine Hilfen, Serveraufruf, Abfragen
            'basis/hilfen.js',            # Farben aus Ziele, Hilfen, Zeichnen, Tipp Animation, Wechsel
            'koeoe/koeoe.js',             # Köö: Zuordnung der Felder, Sport, Rauchen, Nikotin, Drinks
            'tag/tag.js',                 # Tag zeichnen, Version
            'woche/woche.js',             # Karte Woche im Tag, Ansicht Letzte 14 Tage
            'tag/felder.js',              # Felder, Bildschirm Balken, Check ins, Mehrfach, Termine, Tasks
            'geld/geld.js',               # Listen aus Zellnotizen, Posten, Geld Karte letzte 7 Tage
            'tag/tageswert.js',           # Fokuspunkte, Tageswert wie in Tage, Fokuszeit, Blöcke
            'tag/ringe.js',               # Ringe um die Tageszahl, Plus fliegt
            'tag/heute.js',               # Heute: Jetzt, Später, Dran, Los, Erledigt, Stufen
            'tag/tasks.js',               # Für heute, Tasks Vorrat, Tasks vormerken und bearbeiten, Block bewerten
            'tag/planen.js',              # Planen: Block oder Task, Lücke, Tagesleiste
            'basis/aktionen.js',          # Aktionen: Speichern, Rückgängig, Einträge, Blättern, Aktualisieren
            'basis/start.js',             # Mac Layout und Tasten, Ort, Start, Abfragen im Takt, Räder
        ],
        'basis/ende.html',                # Ende der Seite
    ]),
    ('ChiefSeite.html', [
        [
            'chief/chief.css',            # Kästchen, Seite Chief, Projekt, Ziehen, Woche am Mac, Blätter
            'chief/fokus.css',            # Fokus im Tag: Balken, Liste nach Uhrzeit, Tasks, Leiste am Mac
        ],
        'chief/blatt.html',               # Platz für das Blatt
        [
            'chief/zustand.js',           # Zustand, Laden, Ändern mit Rückweg
            'chief/rechnen.js',           # Rechnen, Kästchen, Block läuft, Als Nächstes
            'chief/seite.js',             # Seite Chief: Übersicht, Projekt, Woche am Mac
            'chief/blaetter.js',          # Blätter: Schritt, Projekt, Etappe, Zerlegen
            'chief/ziehen.js',            # Ziehen am Griff (Rang, Schritte)
            'chief/fokus.js',             # Tag: Fokus Karte, Liste nach Uhrzeit, Balken
            'chief/vornehmen.js',         # Heute vornehmen, Vergessen, Einplanen, Blatt Wann
            'chief/plus.js',              # Blatt Plus, Karte Tasks
            'chief/mac.js',               # Mac: Tag als Leiste
            'chief/runde.js',             # Wochenrunde, Mittwochsrunde, Einhängen
        ],
    ]),
    ('SensiSeite.html', [
        [
            'sensi/sensi.css',            # Tiefe, Lesen, Gesehen, Handy, Blatt
        ],
        'sensi/blatt.html',               # Platz für das Blatt
        [
            'sensi/sensi.js',             # Zustand, Laden, Rechnen, Zeichnen, Lesen, Rückgängig
            'sensi/blaetter.js',          # Blätter (Buch, Film, Seite), Einhängen
        ],
    ]),
]
# SEITEN Ende

APP = os.path.join(HIER, '..', 'app')

def teile_bauen():
    benutzt = set()
    def lies(name):
        p = os.path.join(APP, name)
        if not os.path.isfile(p):
            sys.exit('bauen.py: Teil fehlt: app/' + name)
        t = io.open(p, encoding='utf-8').read()
        if not t.endswith('\n'):
            sys.exit('bauen.py: app/' + name + ' muss mit einem Zeilenumbruch enden')
        benutzt.add(name)
        return t
    for seite, liste in SEITEN:
        out = ''
        for t in liste:
            if isinstance(t, str):
                out += lies(t)
                continue
            art = 'style' if t[0].endswith('.css') else 'script'
            if any(not x.endswith('.css' if art == 'style' else '.js') for x in t):
                sys.exit('bauen.py: CSS und JS gemischt in einem Block von ' + seite)
            out += '<' + art + '>\n' + ''.join(lies(x) for x in t) + '</' + art + '>\n'
        ziel = os.path.join(HIER, '..', seite)
        alt = io.open(ziel, encoding='utf-8').read() if os.path.exists(ziel) else None
        if alt != out:
            io.open(ziel, 'w', encoding='utf-8').write(out)
    for ordner, _, dateien in os.walk(APP):
        for d in dateien:
            if d.startswith('.'):
                continue
            name = os.path.relpath(os.path.join(ordner, d), APP).replace(os.sep, '/')
            if name not in benutzt:
                sys.exit('bauen.py: app/' + name + ' steht nicht in SEITEN (web/bauen.py)')

teile_bauen()

s = io.open(os.path.join(HIER, '..', 'AppSeite.html'), encoding='utf-8').read()

def ersetze(alt, neu):
    global s
    if s.count(alt) != 1:
        sys.exit('bauen.py: Stelle nicht gefunden oder doppelt: ' + alt[:60])
    s = s.replace(alt, neu)

# Kopf: kein Apps Script Rahmen, dafür App Angaben für den Home Bildschirm
ersetze('<base target="_top">\n', '''<title>Zentrale</title>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Zentrale">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#073763">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
''')

# Chief of Staff: eigene Datei ChiefSeite.html, hier fest in die Seite gesetzt (in der alten Web App macht das Apps Script)
ersetze("<?!= HtmlService.createHtmlOutputFromFile('ChiefSeite').getContent() ?>",
        io.open(os.path.join(HIER, '..', 'ChiefSeite.html'), encoding='utf-8').read())

# Sensi: eigene Datei SensiSeite.html, genauso eingesetzt
ersetze("<?!= HtmlService.createHtmlOutputFromFile('SensiSeite').getContent() ?>",
        io.open(os.path.join(HIER, '..', 'SensiSeite.html'), encoding='utf-8').read())

# Startdaten kommen in der PWA aus dem Handyspeicher, nicht vom Server
ersetze('const START = <?!= start ?>;', 'const START = null;')

# Schnittstelle, Schlüssel und Service Worker vor dem eigentlichen Code
ersetze('<script>\n/* ── Einstellungen ── */', '''<script>
/* ── PWA (aus web/bauen.py) ── */
const ZENTRALE_API = '%s';
const PWA_VERSION = '%s';
const PWA_NAME = %s;
const SCHLUESSEL_SPEICHER = 'zentrale_k';
(function () {
  // Einmal mit https://…/#k=SCHLUESSEL öffnen, dann ist er auf dem Gerät gespeichert
  const m = location.hash.match(/k=([0-9a-f]{32})/);
  if (m) { try { localStorage.setItem(SCHLUESSEL_SPEICHER, m[1]); } catch (e) { /* egal */ } history.replaceState(null, '', location.pathname); }
})();
function schluessel() { try { return localStorage.getItem(SCHLUESSEL_SPEICHER) || ''; } catch (e) { return ''; } }
function schluesselFragen(falsch) {
  if (falsch) { try { localStorage.removeItem(SCHLUESSEL_SPEICHER); } catch (e) { /* egal */ } }
  if (document.getElementById('schluessel')) return;
  const d = document.createElement('div');
  d.id = 'schluessel';
  d.innerHTML = '<div class="sk-innen"><b>Zentrale</b><p>' + (falsch ? 'Der Schlüssel stimmt nicht.' : 'Einmal den Schlüssel eingeben.') +
    '</p><input type="text" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" placeholder="Schlüssel"><button>Los</button></div>';
  d.querySelector('button').onclick = () => {
    // Großbuchstaben, Leerzeichen und Umbrüche vom Einsetzen nicht übel nehmen
    const roh = d.querySelector('input').value, k = roh.toLowerCase().replace(/[^0-9a-f]/g, '');
    if (k.length !== 32) { d.querySelector('p').textContent = 'Eingesetzt sind ' + k.length + ' passende Zeichen, der Schlüssel hat 32 (Zahlen und a bis f).'; return; }
    try { localStorage.setItem(SCHLUESSEL_SPEICHER, k); } catch (e) { /* egal */ }
    location.reload();
  };
  document.body.appendChild(d);
}
document.addEventListener('DOMContentLoaded', () => { if (!schluessel()) schluesselFragen(false); });
if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register('sw.js', { updateViaCache: 'none' }).catch(() => {}));
</script>
<style>
  #schluessel { position: fixed; inset: 0; z-index: 99; background: var(--bg); display: grid; place-items: center; padding: 24px; }
  #schluessel .sk-innen { width: 100%%; max-width: 320px; display: grid; gap: 12px; text-align: center; }
  #schluessel b { font: italic 800 34px/1 Inter, -apple-system, sans-serif; color: var(--akzent); }
  #schluessel input { height: 46px; border-radius: 12px; border: 1px solid var(--linie); padding: 0 14px; font-size: 16px; background: var(--karte); color: var(--text); }
  #schluessel button { height: 46px; border-radius: 12px; background: #073763; color: #fff; font-weight: 600; }
</style>
<script>
/* ── Einstellungen ── */''' % ('spielwelt' if TEST else API, VERSION, json.dumps('Test' if TEST and not NAME else NAME, ensure_ascii=False).replace('</', '<\\/')))

if '<?' in s:
    sys.exit('bauen.py: Es steht noch Apps Script Vorlagen Code in der Seite.')

if TEST:
    # Testseite: eigener Name, eigenes Icon, rotes TEST Band. Daten aus der Spielwelt im Browser (tests/testseite.js), nie von Google
    T = os.path.join(HIER, '..', 'tests')
    lies = lambda *p: io.open(os.path.join(*p), encoding='utf-8').read()
    welt = lies(T, 'testseite.js')
    for marke, teil in (('__MOCK__', lies(T, 'mock.js')), ('__SENSIMOCK__', lies(T, 'sensi_mock.js')), ('__SPIELDATEN__', lies(T, 'spieldaten.js'))):
        if '</script' in teil:
            sys.exit('bauen.py: </script in ' + marke)
        welt = welt.replace(marke, teil)
    welt = welt.replace('__CHIEF__', json.dumps(lies(HIER, '..', 'Chief.js'), ensure_ascii=False).replace('</', '<\\/'))
    welt = welt.replace('__SENSI__', json.dumps(lies(HIER, '..', 'Sensi.js') + '\n' + lies(HIER, '..', 'Koerper.js'), ensure_ascii=False).replace('</', '<\\/'))   # V81: Körper braucht Sensi
    ersetze('<script>\n/* ── Einstellungen ── */', '<script>\n' + welt + '</script>\n<script>\n/* ── Einstellungen ── */')
    ersetze('<title>Zentrale</title>', '<title>Zentrale Test</title>')
    ersetze('<meta name="apple-mobile-web-app-title" content="Zentrale">', '<meta name="apple-mobile-web-app-title" content="Test">')
    # Band zeigt die Uhrzeit des Bauens, damit man sieht, welcher Stand auf der Testseite liegt
    ersetze('</body>', '''<div id="testband">TEST ''' + time.strftime('%H:%M') + '''</div>
<style>#testband { position: fixed; top: calc(8px + env(safe-area-inset-top)); left: 12px; z-index: 60; pointer-events: none;
  background: #C62828; color: #fff; font: 700 11px/1 -apple-system, sans-serif; letter-spacing: .08em; padding: 5px 9px; border-radius: 999px; }</style>
</body>''')
    os.makedirs(ZIEL, exist_ok=True)
    io.open(os.path.join(ZIEL, 'manifest.webmanifest'), 'w', encoding='utf-8').write('''{
  "name": "Zentrale Test",
  "short_name": "Test",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "background_color": "#F4F3EF",
  "theme_color": "#C62828",
  "icons": [
    { "src": "icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
  ]
}
''')
    # Icons: das normale Icon mit rotem Band unten (nur wenn noch keins da ist)
    if not os.path.exists(os.path.join(ZIEL, 'icon-512.png')):
      try:
          from PIL import Image, ImageDraw, ImageFont
          for g in (180, 192, 512):
              im = Image.open(os.path.join(HIER, 'icon-%d.png' % g)).convert('RGB')
              d = ImageDraw.Draw(im)
              h = int(g * 0.26)
              d.rectangle([0, g - h, g, g], fill=(198, 40, 40))
              try:
                  ft = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', int(h * 0.62))
              except Exception:
                  ft = ImageFont.load_default()
              x0, y0, x1, y1 = d.textbbox((0, 0), 'TEST', font=ft)
              d.text(((g - (x1 - x0)) / 2 - x0, g - h + (h - (y1 - y0)) / 2 - y0), 'TEST', fill=(255, 255, 255), font=ft)
              im.save(os.path.join(ZIEL, 'icon-%d.png' % g))
      except ImportError:
          import shutil
          for g in (180, 192, 512):
              shutil.copy(os.path.join(HIER, 'icon-%d.png' % g), os.path.join(ZIEL, 'icon-%d.png' % g))

io.open(os.path.join(ZIEL, 'index.html'), 'w', encoding='utf-8').write(s)

# Service Worker bekommt die Version, damit das Handy die neue Seite holt
sw = io.open(os.path.join(HIER, 'sw.vorlage.js'), encoding='utf-8').read().replace('__VERSION__', VERSION)
sw = sw.replace('__VORSILBE__', 'zentrale-test-' if TEST else 'zentrale-')
io.open(os.path.join(ZIEL, 'sw.js'), 'w', encoding='utf-8').write(sw)
print(('Testseite' if TEST else 'PWA') + ' gebaut, Version ' + VERSION)
