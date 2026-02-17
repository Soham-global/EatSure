// ============================================================
//  AllergyGuard — Service Worker
//  Handles caching, offline fallback, and background sync
// ============================================================

const CACHE_NAME      = 'allergyguard-v1';
const OFFLINE_URL     = '/offline';

// Files to cache immediately on install (app shell)
const STATIC_ASSETS = [
    '/',
    '/login',
    '/register',
    '/profile',
    '/analyse',
    '/static/style.css',
    '/static/manifest.json',
    '/offline',
];

// ── Install ──────────────────────────────────────────────────
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_ASSETS);
        }).then(() => self.skipWaiting())
    );
});

// ── Activate ─────────────────────────────────────────────────
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys
                    .filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            )
        ).then(() => self.clients.claim())
    );
});

// ── Fetch ────────────────────────────────────────────────────
self.addEventListener('fetch', event => {
    // Skip non-GET and POST requests (like form submissions)
    if (event.request.method !== 'GET') return;

    // Skip chrome-extension and non-http requests
    if (!event.request.url.startsWith('http')) return;

    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) {
                // Serve from cache, update in background
                fetch(event.request).then(networkResponse => {
                    if (networkResponse && networkResponse.status === 200) {
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, networkResponse.clone());
                        });
                    }
                }).catch(() => {});
                return cachedResponse;
            }

            // Not in cache — try network
            return fetch(event.request).then(networkResponse => {
                // Cache successful responses for static assets
                if (networkResponse && networkResponse.status === 200) {
                    const url = event.request.url;
                    if (url.includes('/static/') || url.endsWith('.css') || url.endsWith('.js')) {
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, networkResponse.clone());
                        });
                    }
                }
                return networkResponse;
            }).catch(() => {
                // Network failed — show offline page for navigation requests
                if (event.request.mode === 'navigate') {
                    return caches.match(OFFLINE_URL);
                }
            });
        })
    );
});