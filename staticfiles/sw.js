// ============================================================
// Service Worker لتطبيق متابعة الخريجين (PWA + Push Notifications)
// ============================================================

const CACHE_NAME = 'alumni-pwa-v1';
const OFFLINE_URL = '/offline/';  // صفحة مخصصة عند عدم الاتصال

// الملفات التي سيتم تخزينها في الكاش
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/images/icons/apple-touch-icon.png',
    '/static/images/icons/android-chrome-192x192.png',
    '/static/images/icons/android-chrome-512x512.png',
    OFFLINE_URL,
];

// ============================================================
// ✅ 1. تثبيت Service Worker
// ============================================================
self.addEventListener('install', event => {
    console.log('📦 Service Worker installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('✅ Caching files...');
                return cache.addAll(urlsToCache);
            })
            .then(() => self.skipWaiting())
            .catch(err => console.error('❌ Cache error:', err))
    );
});

// ============================================================
// ✅ 2. جلب الملفات (من الكاش أولاً، ثم من الشبكة)
// ============================================================
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // إذا وجد في الكاش، أعده
                if (response) {
                    return response;
                }
                // وإلا، جلب من الشبكة
                return fetch(event.request)
                    .then(networkResponse => {
                        // تخزين النسخة الجديدة في الكاش (للزيارات المستقبلية)
                        if (networkResponse && networkResponse.status === 200) {
                            const responseClone = networkResponse.clone();
                            caches.open(CACHE_NAME)
                                .then(cache => cache.put(event.request, responseClone));
                        }
                        return networkResponse;
                    })
                    .catch(() => {
                        // إذا تعذر الجلب، عرض صفحة "غير متصل"
                        return caches.match(OFFLINE_URL);
                    });
            })
    );
});

// ============================================================
// ✅ 3. تنشيط Service Worker (حذف الكاش القديم)
// ============================================================
self.addEventListener('activate', event => {
    console.log('🔄 Service Worker activated');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cache => {
                    if (cache !== CACHE_NAME) {
                        console.log(`🗑️ Deleting old cache: ${cache}`);
                        return caches.delete(cache);
                    }
                })
            );
        })
        .then(() => self.clients.claim()) // السيطرة على الصفحات المفتوحة فوراً
    );
});

// ============================================================
// ✅ 4. استقبال الإشعارات (Push Notifications)
// ============================================================
self.addEventListener('push', function(event) {
    let data = {};
    
    // محاولة تحليل البيانات المرسلة
    try {
        data = event.data.json();
    } catch (e) {
        data = {
            title: '📢 إشعار جديد',
            body: event.data ? event.data.text() : 'لديك إشعار جديد',
            url: '/'
        };
    }

    const options = {
        body: data.body || 'لديك إشعار جديد',
        icon: data.icon || '/static/favicon.ico',
        badge: '/static/favicon.ico',
        vibrate: [200, 100, 200],
        data: {
            url: data.url || '/',
            id: data.id || null,
        },
        actions: [
            { action: 'open', title: '📖 عرض' },
            { action: 'close', title: '❌ إغلاق' },
        ],
        requireInteraction: true,
        tag: data.tag || 'default',
    };

    event.waitUntil(
        self.registration.showNotification(
            data.title || '📢 إشعار جديد',
            options
        )
    );
});

// ============================================================
// ✅ 5. النقر على الإشعار
// ============================================================
self.addEventListener('notificationclick', function(event) {
    event.notification.close();

    // إذا تم النقر على زر مخصص
    if (event.action === 'close') {
        return;
    }

    const urlToOpen = event.notification.data?.url || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(windowClients => {
                // إذا كانت هناك نافذة مفتوحة، انتقل إليها
                for (let client of windowClients) {
                    if (client.url === urlToOpen && 'focus' in client) {
                        return client.focus();
                    }
                }
                // وإلا افتح نافذة جديدة
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

// ============================================================
// ✅ 6. إغلاق الإشعار (اختياري)
// ============================================================
self.addEventListener('notificationclose', function(event) {
    console.log('🔕 Notification closed:', event.notification.data);
});

// ============================================================
// ✅ 7. التعامل مع الأخطاء
// ============================================================
self.addEventListener('error', function(event) {
    console.error('❌ Service Worker error:', event.message);
});

console.log('✅ Service Worker loaded successfully!');