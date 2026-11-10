/* ZENTRALE · Service Worker (aus sw.vorlage.js, Version setzt bauen.py)
 * Die Seite selbst: erst Netz, ohne Netz aus dem Speicher. So kommt jede neue Version sofort,
 * und offline öffnet die App trotzdem. Daten laufen nie über den Service Worker (POST an Apps Script). */
const VORSILBE = '__VORSILBE__';
const CACHE = VORSILBE + '__VERSION__';
const HUELLE = ['./', 'index.html', 'manifest.webmanifest', 'icon-180.png', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(HUELLE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(l => Promise.all(l.filter(k => k !== CACHE && new RegExp('^' + VORSILBE + '\\d+$').test(k)).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  e.respondWith(fetch(r).then(antwort => {
    const kopie = antwort.clone();
    caches.open(CACHE).then(c => c.put(r, kopie));
    return antwort;
  }).catch(() => caches.match(r).then(x => x || caches.match('index.html'))));
});
