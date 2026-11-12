const CACHE_PREFIX = 'kaliv-shell-';
const CACHE_NAME = `${CACHE_PREFIX}{{ build_version }}`;

const CORE_ASSETS = {{ core_assets | json }};

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
        .catch(async () => {
          const known = await caches.match(request, { ignoreSearch: true });
          if (known) return known;
          const language = url.pathname.startsWith('/en/') || url.searchParams.get('lang') === 'en' ? 'en' : 'da';
          const fallback = await caches.match(language === 'en' ? './en/offline.html' : './offline.html');
          if (!fallback) return Response.error();
          // A fallback answers this navigation rather than retaining a cached URL.
          const headers = new Headers(fallback.headers);
          for (const name of ['content-length', 'content-encoding', 'transfer-encoding']) headers.delete(name);
          headers.set('X-Kaliv-Offline-Language', language);
          return new Response(await fallback.arrayBuffer(), { status: fallback.status, statusText: fallback.statusText, headers });
        })
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
