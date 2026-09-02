// 餃木 GYOZA WOOD — service worker
// Precaches the app shell for offline use, then serves navigations/assets
// cache-first with a network fallback (and a background revalidation so
// the cache doesn't go stale forever).

const CACHE_VERSION = 'gyoza-wood-v1';
const APP_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './assets/hero-poster.jpg',
  './assets/icons/icon-192.png',
  './assets/icons/icon-512.png',
  './assets/icons/icon-maskable-192.png',
  './assets/icons/icon-maskable-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then((cache) => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((key) => key !== CACHE_VERSION).map((key) => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Only handle same-origin GET requests; let the browser deal with
  // everything else (CDN scripts, fonts, cross-origin APIs, POSTs...).
  if (request.method !== 'GET' || new URL(request.url).origin !== self.location.origin) {
    return;
  }

  event.respondWith(
    caches.match(request).then((cached) => {
      const network = fetch(request)
        .then((response) => {
          if (response && response.ok) {
            const clone = response.clone();
            caches.open(CACHE_VERSION).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => cached || caches.match('./index.html'));

      // Cache-first for instant loads; refresh the cache in the background.
      return cached || network;
    })
  );
});
