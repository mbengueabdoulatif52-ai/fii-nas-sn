const CACHE = 'fiinas-sn-v35';
const ASSETS = ['/', '/index.html', '/manifest.json', '/icon-192.png', '/icon-512.png', '/apple-touch-icon.png'];
// Librairies versionnées (ne changent jamais) : gardées en cache pour l'usage hors ligne
const LIBS = [
  'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js',
  'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(ASSETS).then(() => Promise.all(LIBS.map(u => c.add(u).catch(() => {})))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE).map(k => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

function cacheFirst(req) {
  return caches.match(req).then(cached => cached || fetch(req).then(res => {
    if (res.ok) { const clone = res.clone(); caches.open(CACHE).then(c => c.put(req, clone)); }
    return res;
  }));
}

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);

  // Code Firebase et librairies cdnjs : fichiers versionnés → cache d'abord
  if ((url.hostname === 'www.gstatic.com' && url.pathname.startsWith('/firebasejs/')) ||
      url.hostname === 'cdnjs.cloudflare.com') {
    e.respondWith(cacheFirst(e.request));
    return;
  }

  // Tout le reste qui n'est pas l'appli elle-même (Firestore, connexion Google…) : pas touché
  if (url.origin !== self.location.origin) return;
  // Serveur d'analyse : jamais en cache
  if (url.pathname.startsWith('/api/')) return;
  // Numéro de version en ligne : toujours demandé au serveur
  if (url.pathname === '/version.json') return;

  // Page de l'appli : réseau d'abord (toujours la dernière version), cache si hors ligne
  const isPage = e.request.mode === 'navigate' || url.pathname === '/' || url.pathname.endsWith('.html');
  if (isPage) {
    e.respondWith(
      fetch(e.request).then(res => {
        if (res.ok) { const clone = res.clone(); caches.open(CACHE).then(c => c.put(e.request, clone)); }
        return res;
      }).catch(() => caches.match(e.request).then(r => r || caches.match('/index.html')))
    );
    return;
  }

  // Icônes, manifeste… : cache d'abord, mis à jour en arrière-plan
  e.respondWith(
    caches.match(e.request).then(cached => {
      const network = fetch(e.request).then(res => {
        if (res.ok) { const clone = res.clone(); caches.open(CACHE).then(c => c.put(e.request, clone)); }
        return res;
      }).catch(() => cached);
      return cached || network;
    })
  );
});
