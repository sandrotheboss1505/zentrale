#!/usr/bin/env python3
"""
ZENTRALE · PWA bauen
Die Oberfläche liegt in Teilen im Ordner app/ (ein Unterordner pro Bereich, CSS und JS getrennt).
bauen.py setzt sie nach der Liste SEITEN zu AppSeite.html, ChiefSeite.html und SensiSeite.html im Hauptordner zusammen
(die braucht die alte Web App doGet, clasp schickt sie zu Google) und macht daraus web/index.html für GitHub Pages.
Die drei Seiten sind erzeugt: nie von Hand ändern, Änderungen immer in app/.
Aufruf: python3 web/bauen.py        (Live Seite web/index.html)
        python3 web/bauen.py test   (Testseite web/test/ mit Spieldaten, spricht nie mit Google)
        python3 web/bauen.py entwicklung   (nur für ui/entwicklung/vite.js: Testseite mit Spieldaten nach ui/.entwicklung/,
                                    React Teil als Modul vom Vite Server statt gebaut, schreibt sonst nichts)
"""
import io, json, os, re, sys, time

HIER = os.path.dirname(os.path.abspath(__file__))
API = 'https://script.google.com/macros/s/AKfycby_mlOvm6veeRy8tqW0SyjI4XqaZJRVt_dUFyv5VV2n9KsCfKVsX45EeMVUHlcNyV0FXA/exec'
VERSION = time.strftime('%Y%m%d%H%M')
NAME = os.environ.get('ZENTRALE_NAME', '').strip()   # aus bereitstellen.sh, zum Beispiel "V80 Beschreibung"
ENTW = len(sys.argv) > 1 and sys.argv[1] == 'entwicklung'   # Entwicklungsmodus: wie test, aber nur ui/.entwicklung/index.html
TEST = len(sys.argv) > 1 and sys.argv[1] == 'test' or ENTW
ZIEL = os.path.join(HIER, '..', 'ui', '.entwicklung') if ENTW else os.path.join(HIER, 'test') if TEST else HIER

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
        'ui:css',                         # Stufe 3: React Teil, Hilfsklassen (Tailwind aus ui/, nach dem CSS der App, damit sie gewinnen)
        'basis/seite.html',               # Gerüst: Plätze für Kopfleiste, Inhalt, Leiste, Fenster (React zeichnet hinein), Chief und Sensi (Apps Script Einschub)
        'ui:js',                          # Stufe 3: React Teil (ui/, window.ZentraleUI): zeichnet die ganze App. Läuft vor dem Hauptteil, Kopf und Leiste sofort
        [
            'basis/kern.js',              # Einstellungen, Zustand, kleine Hilfen, Serveraufruf, Abfragen
            'basis/hilfen.js',            # Farben aus Ziele, Hilfen, Zeichnen (Weiche zu React), Meldung, Tipp Animation, Wechsel
            'koeoe/koeoe.js',             # Köö: Zuordnung der Felder zu Tag, Köö, Sensi
            'tag/tag.js',                 # Kopfleiste für Tag und Köö
            'woche/woche.js',             # Woche öffnen, Farbe der Stufe
            'tag/felder.js',              # Felder: Farben am Mac, Check ins, Skala, Aufklappen
            'geld/geld.js',               # Geld Karte letzte 7 Tage aufklappen
            'tag/tageswert.js',           # Fokuspunkte, Tageswert wie in Tage, Fokuszeit, Blöcke
            'tag/ringe.js',               # Ringe um die Tageszahl rechnen und wachsen lassen, Plus fliegt
            'tag/heute.js',               # Fokus Karte: Dran, Los, Fertig, Stufen, heuteNeu (gezeichnet in React, ui/src/fokus/)
            'tag/tasks.js',               # Für heute, Tasks Vorrat, Tasks vormerken und bearbeiten, Block bewerten (gezeichnet in React)
            'tag/planen.js',              # Planen: Block oder Task, Lücke, Tagesleiste (gezeichnet in React, ui/src/planen/)
            'basis/aktionen.js',          # Aktionen: Speichern, Rückgängig, Einträge, Blättern, Aktualisieren
            'basis/start.js',             # Mac Layout und Tasten, Ort, Start, Abfragen im Takt, Räder
        ],
        'basis/ende.html',                # Ende der Seite
    ]),
    ('ChiefSeite.html', [
        [
            'chief/chief.css',            # Kästchen, Seite Chief, Projekt, Ziehen, Woche am Mac, Blätter
            'chief/fokus.css',            # Fokus im Tag: Balken, Liste nach Uhrzeit, Tasks, Leiste am Mac
            'chief/fokus_ac.css',         # Ac: Fokus Karte (Balken mit Feldern, Jetzt, To Do) und Heute Karte (Kalender)
            'chief/woche.css',            # V95 Heute vornehmen und Woche als Raster
            'chief/projekt.css',          # V98 Projektseite, Projektliste, Mac Reiter
        ],
        'chief/blatt.html',               # Platz für das Blatt
        [
            'chief/zustand.js',           # Zustand, Laden, Ändern mit Rückweg
            'chief/rechnen.js',           # Rechnen: Blöcke, Minuten, Kästchen der Projekte, Reihenfolge, Etappen, Einsammeln, Haken
            'chief/rechnen_tag.js',       # Stufe 3: Rechnen für den Tag (Plan, Termine, Startzeiten, Empfehlung, Gehalten, Fokus Daten)
            'chief/rechnen_woche.js',     # Stufe 3: Rechnen für die Woche (Raster, Joker, Serie)
            'chief/rechnen_kal.js',       # Ac: Heute Karte, Kalender gestaucht und Termine ab jetzt
            'chief/seite.js',             # Seite Chief: Woche jetzt, Status, Projekt öffnen, Wochenplan, fester Tag
            'chief/projekt.js',           # V98 Projektseite: Zahlen, Notiz, frei, Erledigt, Reiter ziehen
            'chief/woche.js',             # V95 Raster ändern: Zelle wählen, Mengen, Startzeit, Verteilen, Joker, Momente
            'chief/blaetter.js',          # Blätter: Schritt, Projekt, Zerlegen, Weiter bei (Handlungen, gezeichnet in React)
            'chief/ziehen.js',            # Ziehen am Griff mit Pointer Events (Rang), Pfeiltasten
            'chief/fokus.js',             # Fokus Karte: Merken, Termine fix oder flexibel, Anfangen, Los, Weiter +30
            'chief/vornehmen.js',         # Heute vornehmen, Vergessen, Einplanen, Verschieben, Blatt Wann (Handlungen)
            'chief/dochnicht.js',         # Doch nicht gemacht: geschafftes Kästchen raus, kurz Rückgängig
            'chief/plus.js',              # Blatt Plus, Task Wann, Was kommt rein (Handlungen)
            'chief/mac.js',               # Mac: Leiste ziehen und ablegen, Balken wachsen lassen
            'chief/runde.js',             # Wochenrunde, Mittwochsrunde, Einhängen
        ],
    ]),
    ('SensiSeite.html', [
        [
            'sensi/sensi.css',            # Tiefe, Lesen, Gesehen, Handy, Blatt
        ],
        'sensi/blatt.html',               # Platz für das Blatt
        [
            'sensi/sensi.js',             # Zustand, Laden, Rechnen, Lesen, Rückgängig (gezeichnet in React, ui/src/sensi/)
            'sensi/blaetter.js',          # Handlungen der Blätter (Buch, Film, Seite), Einhängen
        ],
    ]),
]
# SEITEN Ende

APP = os.path.join(HIER, '..', 'app')
STUFE3_NEU = {'chief/rechnen_tag.js', 'chief/rechnen_woche.js'}   # neu im Branch react, siehe lies()

# ── Stufe 3: React Teil aus ui/ (Vite, React, Tailwind) zu einer JS und einer CSS Datei bauen ──
# In SEITEN stehen dafür 'ui:css' und 'ui:js'. Einmalig vorher: cd ui && npm install
UI = os.path.join(HIER, '..', 'ui')
UI_TEILE = {}
# Was nur in den Entwicklungsmodus gehört und nie in einen Bau (Prüfung unten und am Ende)
NUR_ENTWICKLUNG = ('react-grab', '/@vite/client', '@react-refresh', 'entwicklung.jsx', '__vite_plugin_react_preamble')
def ui_bauen():
    import subprocess
    if ENTW:
        # Kein vite build: der Vite Server liefert den React Teil als Modul, CSS setzt Vite selbst ans Ende von <head> (wie ui:css).
        # Fast Refresh braucht den Vorspann vor React, dann der Vite Client, dann der Einstieg. Die Skriptblöcke danach setzt
        # ui/src/entwicklung.jsx der Reihe nach ein, sobald window.ZentraleUI steht (siehe unten, zentrale/spaeter).
        UI_TEILE['ui:css'] = ''
        UI_TEILE['ui:js'] = ('<script type="module">\nimport RefreshRuntime from "/@react-refresh"\nRefreshRuntime.injectIntoGlobalHook(window)\n'
                             'window.$RefreshReg$ = () => {}\nwindow.$RefreshSig$ = () => (type) => type\nwindow.__vite_plugin_react_preamble_installed__ = true\n</script>\n'
                             '<script type="module" src="/@vite/client"></script>\n<script type="module" src="/src/entwicklung.jsx"></script>\n')
        return
    # web/ ist ein eigenes Repository ohne Branches: auf einem Stand ohne ui/src (zum Beispiel main vor Stufe 3) fällt der React Teil weg
    if not os.path.isfile(os.path.join(UI, 'src', 'start.jsx')):
        for _, liste in SEITEN:
            liste[:] = [t for t in liste if not (isinstance(t, str) and t.startswith('ui:'))]
        return
    if not os.path.isdir(os.path.join(UI, 'node_modules')):
        sys.exit('bauen.py: React Teil nicht eingerichtet. Einmal: cd ui && npm install')
    r = subprocess.run(['npm', 'run', 'bauen'], cwd=UI, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('bauen.py: React Teil (ui/) baut nicht:\n' + r.stdout[-3000:] + r.stderr[-3000:])
    for art, datei in (('js', 'zentrale-ui.js'), ('css', 'zentrale-ui.css')):
        t = io.open(os.path.join(UI, 'dist', datei), encoding='utf-8').read()
        # Die Seite geht auch als Apps Script Vorlage zu Google: <? wäre dort Vorlagen Code, </script beendet den Block
        for verboten in ('</script', '</style', '<?') + NUR_ENTWICKLUNG:
            if verboten in t:
                sys.exit('bauen.py: ' + verboten + ' im React Teil (ui/dist/' + datei + ')')
        UI_TEILE['ui:' + art] = ('<script>\n/* ── React Teil (ui/, gebaut von web/bauen.py) ── */\n' if art == 'js' else '<style>\n') + t.rstrip('\n') + '\n' + ('</script>\n' if art == 'js' else '</style>\n')

ui_bauen()

SEITEN_TEXT = {}   # fertige AppSeite.html, ChiefSeite.html, SensiSeite.html
def teile_bauen():
    benutzt = set()
    # web/ hat keine Branches: auf einem Stand vor Stufe 3 Schritt 2 (main bis V100) gibt es diese Dateien noch nicht, dann fallen sie weg
    vor_stufe3 = not os.path.isfile(os.path.join(UI, 'src', 'chief', 'daten.js'))
    def lies(name):
        p = os.path.join(APP, name)
        if not os.path.isfile(p) and vor_stufe3 and name in STUFE3_NEU:
            return ''
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
            if isinstance(t, str) and t in UI_TEILE:
                out += UI_TEILE[t]
                continue
            if isinstance(t, str):
                out += lies(t)
                continue
            art = 'style' if t[0].endswith('.css') else 'script'
            if any(not x.endswith('.css' if art == 'style' else '.js') for x in t):
                sys.exit('bauen.py: CSS und JS gemischt in einem Block von ' + seite)
            if ENTW and art == 'style':
                # Entwicklungsmodus: ein <style> pro Datei (gleiche Reihenfolge, gleiche Wirkung), damit der Vite Server eine geänderte Datei ohne Neuladen tauscht
                out += ''.join('<style data-quelle="' + x + '">\n' + lies(x) + '</style>\n' for x in t)
                continue
            out += '<' + art + '>\n' + ''.join(lies(x) for x in t) + '</' + art + '>\n'
        SEITEN_TEXT[seite] = out
        if ENTW:
            continue   # Entwicklungsmodus schreibt nie in den Hauptordner (clasp schickt AppSeite.html zu Google)
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

s = SEITEN_TEXT['AppSeite.html']

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
        SEITEN_TEXT['ChiefSeite.html'])

# Sensi: eigene Datei SensiSeite.html, genauso eingesetzt
ersetze("<?!= HtmlService.createHtmlOutputFromFile('SensiSeite').getContent() ?>",
        SEITEN_TEXT['SensiSeite.html'])

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
/* Dialog zeichnet React (ui/src/basis/gerust.jsx), hier nur Prüfen und Speichern */
function schluesselFragen(falsch) {
  if (falsch) { try { localStorage.removeItem(SCHLUESSEL_SPEICHER); } catch (e) { /* egal */ } }
  if (document.getElementById('schluessel') || typeof ZentraleUI === 'undefined') return;
  ZentraleUI.kopf({ schluessel: { falsch: !!falsch, text: falsch ? 'Der Schlüssel stimmt nicht.' : 'Einmal den Schlüssel eingeben.' } });
}
/* Eingesetzter Schlüssel: Großbuchstaben, Leerzeichen und Umbrüche vom Einsetzen nicht übel nehmen. Gibt den Fehlertext zurück oder lädt neu */
function schluesselNehmen(roh) {
  const k = String(roh || '').toLowerCase().replace(/[^0-9a-f]/g, '');
  if (k.length !== 32) return 'Eingesetzt sind ' + k.length + ' passende Zeichen, der Schlüssel hat 32 (Zahlen und a bis f).';
  try { localStorage.setItem(SCHLUESSEL_SPEICHER, k); } catch (e) { /* egal */ }
  location.reload();
  return '';
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
    welt = welt.replace('__SENSI__', json.dumps(lies(HIER, '..', 'Sensi.js') + '\n' + (lies(HIER, '..', 'Spotify.js') + '\n' if os.path.exists(os.path.join(HIER, '..', 'Spotify.js')) else '') + (lies(HIER, '..', 'Handy.js') + '\n' if os.path.exists(os.path.join(HIER, '..', 'Handy.js')) else '') + lies(HIER, '..', 'Koerper.js'), ensure_ascii=False).replace('</', '<\\/'))   # V81: Körper braucht Sensi, V105: Spotify.js für Audio, Handy.js für Handyfrei
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

def entw_seite(t):
    # Entwicklungsmodus: kein Service Worker, eigenes Band. Alle klassischen Skriptblöcke nach dem React Einstieg warten, bis
    # ui/src/entwicklung.jsx window.ZentraleUI gesetzt hat, und laufen dann in derselben Reihenfolge wie im Bau (PWA, Spielwelt, Hauptteil).
    t = t.replace("if ('serviceWorker' in navigator)", "if (false)")
    t = re.sub(r'<div id="testband">TEST [0-9:]+</div>', '<div id="testband">ENTWICKLUNG</div>', t)
    i = t.index('<script type="module" src="/src/entwicklung.jsx"></script>')
    return t[:i] + re.sub(r'(?m)^<script>$', '<script type="zentrale/spaeter">', t[i:])

if not ENTW:
    for verboten in NUR_ENTWICKLUNG:
        if verboten in s:
            sys.exit('bauen.py: ' + verboten + ' (nur Entwicklungsmodus) steht in der Seite')

io.open(os.path.join(ZIEL, 'index.html'), 'w', encoding='utf-8').write(entw_seite(s) if ENTW else s)

# ── Stufe 2: Werkbank (nur Testseite) unter web/test/werkbank/ ──
# Dieselbe gebaute Seite wie die Testseite (gleiche CSS, gleiche JS, Spielwelt aus tests/spieldaten.js),
# dazu feste Uhr der Spielwelt (Do 19.11.2026 10:30), eigener Browserspeicher und die Werkbank aus tests/werkbank/.
# Die App in app/ bleibt unberührt, die Werkbank steht nicht in SEITEN.
WERKBANK = ['werkbank/uhr.js', 'werkbank/werkbank.css', 'werkbank/skala.js', 'werkbank/bauteile.js', 'werkbank/werkbank.js']
if TEST:
    T = os.path.join(HIER, '..', 'tests')
    wl = lambda n: io.open(os.path.join(T, n), encoding='utf-8').read()
    for n in WERKBANK:
        if '</script' in wl(n) or '</style' in wl(n):
            sys.exit('bauen.py: </script oder </style in tests/' + n)
    w = s
    def wers(alt, neu):
        global w
        if w.count(alt) != 1:
            sys.exit('bauen.py Werkbank: Stelle nicht gefunden oder doppelt: ' + alt[:60])
        w = w.replace(alt, neu)
    wers('<script>\n/* ── PWA (aus web/bauen.py) ── */', '<script>\n' + wl('werkbank/uhr.js') + '</script>\n<script>\n/* ── PWA (aus web/bauen.py) ── */')
    wers("if ('serviceWorker' in navigator)", "if (false)")
    wers('href="manifest.webmanifest"', 'href="../manifest.webmanifest"')
    wers('href="icon-180.png"', 'href="../icon-180.png"')
    wers("const VOR = 'zentrale_test:';", "const VOR = 'zentrale_werkbank:';")
    wers('<title>Zentrale Test</title>', '<title>Zentrale Werkbank</title>')
    # Quelltexte der App für die Skala (gezählt wie in tests/messen.js), in der Reihenfolge von SEITEN
    quellen = {}
    for _, liste in SEITEN:
        for t in liste:
            for n in ([t] if isinstance(t, str) else t):
                if not n.endswith('.html') and not n.startswith('ui:') and os.path.isfile(os.path.join(APP, n)):
                    quellen[n] = io.open(os.path.join(APP, n), encoding='utf-8').read()
    qjs = json.dumps(quellen, ensure_ascii=False).replace('</', '<\\/')
    # Teil 2: Vorher Nachher, Bilder aus tests/bilder/vergleich (basis, neu) verkleinert als JPEG (braucht Pillow, sonst ohne)
    vergleich = []
    try:
        from PIL import Image
        vq = os.path.join(T, 'bilder', 'vergleich')
        namen = [n[:-4] for n in os.listdir(os.path.join(vq, 'basis')) if n.endswith('.png') and os.path.exists(os.path.join(vq, 'neu', n))]
        rang = lambda l, x: l.index(x) if x in l else 9
        for teil in ('basis', 'neu'):
            os.makedirs(os.path.join(ZIEL, 'werkbank', 'vergleich', teil), exist_ok=True)
            for n in namen:
                q, z = os.path.join(vq, teil, n + '.png'), os.path.join(ZIEL, 'werkbank', 'vergleich', teil, n + '.jpg')
                if ENTW and os.path.exists(z) and os.path.getmtime(z) >= os.path.getmtime(q):
                    continue   # Entwicklungsmodus erzeugt die Seite bei jeder Änderung neu: Bilder nur, wenn sie neuer sind
                im = Image.open(os.path.join(vq, teil, n + '.png')).convert('RGB')
                b = 390 if im.size[0] <= 800 else 700
                im.resize((b, round(im.size[1] * b / im.size[0]))).save(os.path.join(ZIEL, 'werkbank', 'vergleich', teil, n + '.jpg'), quality=72)
        vergleich = sorted(namen, key=lambda n: (rang(['handy', 'mac', 'dunkel'], n.split('-')[0]), rang(['tag', 'chief', 'koe', 'sensi', 'woche'], n.split('-')[-1])))
    except Exception:
        vergleich = []
    wers('</body>', '<style id="wbStil">\n' + wl('werkbank/werkbank.css') + '</style>\n<script>\nwindow.__wbQuellen = ' + qjs + ';\nwindow.__wbVergleich = ' + json.dumps(vergleich) + ';\n' +
         ''.join(wl(n) for n in WERKBANK if n.endswith('.js') and n != 'werkbank/uhr.js') + '</script>\n</body>')
    os.makedirs(os.path.join(ZIEL, 'werkbank'), exist_ok=True)
    io.open(os.path.join(ZIEL, 'werkbank', 'index.html'), 'w', encoding='utf-8').write(entw_seite(w) if ENTW else w)

if ENTW:
    print('Entwicklungsseite und Werkbank gebaut')
    sys.exit(0)   # kein Service Worker

# Service Worker bekommt die Version, damit das Handy die neue Seite holt
sw = io.open(os.path.join(HIER, 'sw.vorlage.js'), encoding='utf-8').read().replace('__VERSION__', VERSION)
sw = sw.replace('__VORSILBE__', 'zentrale-test-' if TEST else 'zentrale-')
io.open(os.path.join(ZIEL, 'sw.js'), 'w', encoding='utf-8').write(sw)
print(('Testseite' if TEST else 'PWA') + ' gebaut, Version ' + VERSION)
