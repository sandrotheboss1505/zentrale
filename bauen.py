#!/usr/bin/env python3
"""
ZENTRALE · PWA bauen
Macht aus ../AppSeite.html (der alten Web App) die Seite web/index.html für GitHub Pages.
Eine Quelle für beide: Änderungen immer in AppSeite.html, danach bauen (macht bereitstellen.sh).
Aufruf: python3 web/bauen.py
"""
import io, os, re, sys, time

HIER = os.path.dirname(os.path.abspath(__file__))
API = 'https://script.google.com/macros/s/AKfycby_mlOvm6veeRy8tqW0SyjI4XqaZJRVt_dUFyv5VV2n9KsCfKVsX45EeMVUHlcNyV0FXA/exec'
VERSION = time.strftime('%Y%m%d%H%M')

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
    '</p><input type="password" autocomplete="off" placeholder="Schlüssel"><button>Los</button></div>';
  d.querySelector('button').onclick = () => {
    const k = d.querySelector('input').value.trim();
    if (!/^[0-9a-f]{32}$/.test(k)) { d.querySelector('p').textContent = 'Das sieht nicht wie der Schlüssel aus.'; return; }
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
  #schluessel b { font: italic 800 34px/1 Inter, -apple-system, sans-serif; color: #073763; }
  #schluessel input { height: 46px; border-radius: 12px; border: 1px solid var(--linie); padding: 0 14px; font-size: 16px; background: var(--karte); color: var(--text); }
  #schluessel button { height: 46px; border-radius: 12px; background: #073763; color: #fff; font-weight: 600; }
</style>
<script>
/* ── Einstellungen ── */''' % (API, VERSION))

if '<?' in s:
    sys.exit('bauen.py: Es steht noch Apps Script Vorlagen Code in der Seite.')
io.open(os.path.join(HIER, 'index.html'), 'w', encoding='utf-8').write(s)

# Service Worker bekommt die Version, damit das Handy die neue Seite holt
sw = io.open(os.path.join(HIER, 'sw.vorlage.js'), encoding='utf-8').read().replace('__VERSION__', VERSION)
io.open(os.path.join(HIER, 'sw.js'), 'w', encoding='utf-8').write(sw)
print('PWA gebaut, Version ' + VERSION)
