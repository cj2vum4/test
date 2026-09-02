// 餃木 GYOZA WOOD — service worker
// Network-first: always try to fetch the latest version first, only
// falling back to cache when offline/unreachable. This keeps deploys
// (like the checkout backend URL in index.html) taking effect immediately
// instead of getting stuck behind a stale cached copy — a previous
// cache-first version of this file caused exactly that bug.

const CACHE_VERSION = 'gyoza-wood-v2';
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
  // everything else (CDN scripts, fonts, cross-origin APIs, POSTs to the
  // GAS order endpoint...).
  if (request.method !== 'GET' || new URL(request.url).origin !== self.location.origin) {
    return;
  }

  event.respondWith(
    fetch(request)
      .then((response) => {
        if (response && response.ok) {
          const clone = response.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(request, clone));
        }
        return response;
      })
      .catch(() => caches.match(request).then((cached) => cached || caches.match('./index.html')))
  );
});
