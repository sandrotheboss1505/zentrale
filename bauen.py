#!/usr/bin/env python3
"""
ZENTRALE · PWA bauen
Macht aus ../AppSeite.html (der alten Web App) die Seite web/index.html für GitHub Pages.
Eine Quelle für beide: Änderungen immer in AppSeite.html, danach bauen (macht bereitstellen.sh).
Aufruf: python3 web/bauen.py        (Live Seite web/index.html)
        python3 web/bauen.py test   (Testseite web/test/, ändert nichts an Live)
"""
import io, os, re, sys, time

HIER = os.path.dirname(os.path.abspath(__file__))
API = 'https://script.google.com/macros/s/AKfycby_mlOvm6veeRy8tqW0SyjI4XqaZJRVt_dUFyv5VV2n9KsCfKVsX45EeMVUHlcNyV0FXA/exec'
VERSION = time.strftime('%Y%m%d%H%M')
TEST = len(sys.argv) > 1 and sys.argv[1] == 'test'
ZIEL = os.path.join(HIER, 'test') if TEST else HIER

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

# Startdaten kommen in der PWA aus dem Handyspeicher, nicht vom Server
ersetze('const START = <?!= start ?>;', 'const START = null;')

# Schnittstelle, Schlüssel und Service Worker vor dem eigentlichen Code
ersetze('<script>\n/* ── Einstellungen ── */', '''<script>
/* ── PWA (aus web/bauen.py) ── */
const ZENTRALE_API = '%s';
const PWA_VERSION = '%s';
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
if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
</script>
<style>
  #schluessel { position: fixed; inset: 0; z-index: 99; background: var(--bg); display: grid; place-items: center; padding: 24px; }
  #schluessel .sk-innen { width: 100%%; max-width: 320px; display: grid; gap: 12px; text-align: center; }
  #schluessel b { font: italic 800 34px/1 Inter, -apple-system, sans-serif; color: var(--akzent); }
  #schluessel input { height: 46px; border-radius: 12px; border: 1px solid var(--linie); padding: 0 14px; font-size: 16px; background: var(--karte); color: var(--text); }
  #schluessel button { height: 46px; border-radius: 12px; background: #073763; color: #fff; font-weight: 600; }
</style>
<script>
/* ── Einstellungen ── */''' % (API, VERSION))

if '<?' in s:
    sys.exit('bauen.py: Es steht noch Apps Script Vorlagen Code in der Seite.')

if TEST:
    # Testseite: eigener Name, eigenes Icon, rotes TEST Band. Daten und Schlüssel sind dieselben wie live
    ersetze('<title>Zentrale</title>', '<title>Zentrale Test</title>')
    ersetze('<meta name="apple-mobile-web-app-title" content="Zentrale">', '<meta name="apple-mobile-web-app-title" content="Test">')
    ersetze('</body>', '''<div id="testband">TEST</div>
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
