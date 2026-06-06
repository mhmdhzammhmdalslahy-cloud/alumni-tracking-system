// Service Worker لتطبيق متابعة الخريجين
const CACHE_NAME = 'alumni-pwa-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/images/icons/apple-touch-icon.png',
    '/static/images/icons/android-chrome-192x192.png',
    '/static/images/icons/android-chrome-512x512.png'
];

// تثبيت Service Worker
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
            .then(() => self.skipWaiting())
    );
});

// جلب الملفات من cache
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});

// تنشيط Service Worker
self.addEventListener('activate', event => {
    console.log('Service Worker activated');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cache => {
                    if (cache !== CACHE_NAME) {
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});