// طلب إذن الإشعارات
function requestNotificationPermission() {
    if ('Notification' in window) {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                console.log('✅ الإشعارات مفعلة');
                registerServiceWorker();
            }
        });
    }
}

// تسجيل Service Worker
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(reg => {
                console.log('✅ Service Worker registered', reg);
                // إرسال اشتراك للخادم
                reg.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array('YOUR_VAPID_PUBLIC_KEY')
                }).then(subscription => {
                    fetch('/webpush/save-subscription/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(subscription)
                    });
                });
            })
            .catch(err => console.error('❌ Service Worker error:', err));
    }
}

// تشغيل عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', requestNotificationPermission);