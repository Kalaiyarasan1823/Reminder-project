// Service Worker for Push Notifications
self.addEventListener('push', function(event) {
    console.log('Push event received:', event);
    
    let notificationData = {
        title: 'Reminder App',
        body: 'You have a new notification',
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/badge-72x72.png',
        data: {}
    };
    
    if (event.data) {
        try {
            const data = event.data.json();
            notificationData = {
                title: data.title || notificationData.title,
                body: data.body || notificationData.body,
                icon: data.icon || notificationData.icon,
                badge: data.badge || notificationData.badge,
                data: data.data || {}
            };
        } catch (e) {
            console.error('Error parsing push data:', e);
        }
    }
    
    const options = {
        body: notificationData.body,
        icon: notificationData.icon,
        badge: notificationData.badge,
        data: notificationData.data,
        requireInteraction: true,
        actions: [
            {
                action: 'view',
                title: 'View',
                icon: '/static/images/view-icon.png'
            },
            {
                action: 'dismiss',
                title: 'Dismiss',
                icon: '/static/images/dismiss-icon.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification(notificationData.title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    console.log('Notification clicked:', event);
    
    event.notification.close();
    
    if (event.action === 'view') {
        // Open the app when notification is clicked
        event.waitUntil(
            clients.openWindow('/')
        );
    } else if (event.action === 'dismiss') {
        // Just close the notification
        event.notification.close();
    } else {
        // Default action - open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

self.addEventListener('notificationclose', function(event) {
    console.log('Notification closed:', event);
});

// Handle background sync for offline functionality
self.addEventListener('sync', function(event) {
    console.log('Background sync event:', event);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

function doBackgroundSync() {
    // Implement background sync logic here
    console.log('Performing background sync...');
    return Promise.resolve();
}

// Install event - cache important resources
self.addEventListener('install', function(event) {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open('reminder-app-v1').then(function(cache) {
            return cache.addAll([
                '/',
                '/static/css/bootstrap.min.css',
                '/static/js/bootstrap.bundle.min.js',
                '/static/images/icon-192x192.png',
                '/static/images/badge-72x72.png'
            ]);
        })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', function(event) {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== 'reminder-app-v1') {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
}); 