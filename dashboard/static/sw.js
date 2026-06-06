// Service Worker لتطبيق متابعة الخريجين
const CACHE_NAME = 'alumni-pwa-v1';

// تثبيت Service Worker
self.addEventListener('install', event => {
    console.log('Service Worker installed');
    self.skipWaiting();
});

// جلب الملفات
self.addEventListener('fetch', event => {
    event.respondWith(fetch(event.request));
});

// تنشيط Service Worker
self.addEventListener('activate', event => {
    console.log('Service Worker activated');
});