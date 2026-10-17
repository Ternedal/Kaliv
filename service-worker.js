const CACHE_PREFIX = 'kaliv-shell-';
const CACHE_NAME = `${CACHE_PREFIX}v60`;

const CORE_ASSETS = [
  './',
  './?lang=en',
  './brief.html',
  './brief.html?lang=en',
  './hub.html',
  './hub.html?lang=en',
  './dossier.css',
  './dossier.js',
  './proofs.html',
  './proofs.html?lang=en',
  './architecture.html',
  './architecture.html?lang=en',
  './progress.html',
  './progress.html?lang=en',
  './project.json',
  './llms.txt',
  './robots.txt',
  './offline.html',
  './404.html',
  './site.webmanifest',
  './assets/kaliv-favicon-32.png',
  './assets/kaliv-apple-touch-icon.png',
  './assets/kaliv-icon-192.png',
  './assets/kaliv-icon-512.png',
  './assets/kaliv-icon-maskable-512.png',
  './assets/kaliv-ankh-160.webp',
  './assets/kaliv-ankh-640.webp',
  './assets/kaliv-ankh-transparent.webp',
  './assets/modelrig-continuity-female-hair-mobile.webp',
  './assets/modelrig-continuity-female-hair-1920.webp',
  './assets/modelrig-continuity-female-hair-hires.webp'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => Promise.all(
        CORE_ASSETS.map(asset => cache.add(new Request(asset, { cache: 'reload' })))
      ))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(key => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME)
          .map(key => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response.ok) {
            const copy = response.clone();
            event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.put(request, copy)));
          }
          return response;
        })
        .catch(async () =>
          (await caches.match(request)) ||
          caches.match('./offline.html')
        )
    );
    return;
  }

  event.respondWith((async () => {
    const cached = await caches.match(request);
    const network = fetch(request)
      .then(response => {
        if (response.ok) {
          const copy = response.clone();
          event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.put(request, copy)));
        }
        return response;
      })
      .catch(() => null);

    return cached || (await network) || Response.error();
  })());
});
