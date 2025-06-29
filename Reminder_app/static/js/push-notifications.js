// Push Notification Management
class PushNotificationManager {
    constructor() {
        this.isSupported = 'serviceWorker' in navigator && 'PushManager' in window;
        this.registration = null;
        this.subscription = null;
        this.vapidPublicKey = 'YOUR_VAPID_PUBLIC_KEY_HERE';
    }

    async init() {
        if (!this.isSupported) {
            console.log('Push notifications are not supported in this browser');
            return false;
        }

        try {
            // Register service worker
            this.registration = await navigator.serviceWorker.register('/static/js/sw.js');
            console.log('Service Worker registered successfully');

            // Check if already subscribed
            this.subscription = await this.registration.pushManager.getSubscription();
            
            // Update UI based on subscription status
            this.updateUI();
            
            return true;
        } catch (error) {
            console.error('Service Worker registration failed:', error);
            return false;
        }
    }

    async subscribe() {
        if (!this.isSupported || !this.registration) {
            console.error('Push notifications not supported or service worker not registered');
            return false;
        }

        try {
            // Convert VAPID public key to Uint8Array
            const vapidPublicKey = this.urlBase64ToUint8Array(this.vapidPublicKey);
            
            // Subscribe to push notifications
            this.subscription = await this.registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: vapidPublicKey
            });

            // Send subscription to server
            const response = await fetch('/push/subscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(this.subscription)
            });

            if (response.ok) {
                console.log('Successfully subscribed to push notifications');
                this.updateUI();
                this.showNotification('Success', 'Push notifications enabled!');
                return true;
            } else {
                throw new Error('Failed to save subscription to server');
            }
        } catch (error) {
            console.error('Failed to subscribe to push notifications:', error);
            this.showNotification('Error', 'Failed to enable push notifications');
            return false;
        }
    }

    async unsubscribe() {
        if (!this.subscription) {
            console.log('No active subscription to unsubscribe from');
            return false;
        }

        try {
            // Unsubscribe from push notifications
            await this.subscription.unsubscribe();

            // Notify server
            const response = await fetch('/push/unsubscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(this.subscription)
            });

            if (response.ok) {
                console.log('Successfully unsubscribed from push notifications');
                this.subscription = null;
                this.updateUI();
                this.showNotification('Success', 'Push notifications disabled');
                return true;
            } else {
                throw new Error('Failed to remove subscription from server');
            }
        } catch (error) {
            console.error('Failed to unsubscribe from push notifications:', error);
            this.showNotification('Error', 'Failed to disable push notifications');
            return false;
        }
    }

    async testNotification() {
        try {
            const response = await fetch('/push/test/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                this.showNotification('Success', 'Test notification sent!');
            } else {
                throw new Error('Failed to send test notification');
            }
        } catch (error) {
            console.error('Failed to send test notification:', error);
            this.showNotification('Error', 'Failed to send test notification');
        }
    }

    updateUI() {
        const subscribeBtn = document.getElementById('subscribe-push');
        const unsubscribeBtn = document.getElementById('unsubscribe-push');
        const testBtn = document.getElementById('test-push');
        const statusText = document.getElementById('push-status');

        if (this.subscription) {
            // User is subscribed
            if (subscribeBtn) subscribeBtn.style.display = 'none';
            if (unsubscribeBtn) unsubscribeBtn.style.display = 'inline-block';
            if (testBtn) testBtn.style.display = 'inline-block';
            if (statusText) statusText.textContent = 'Push notifications are enabled';
        } else {
            // User is not subscribed
            if (subscribeBtn) subscribeBtn.style.display = 'inline-block';
            if (unsubscribeBtn) unsubscribeBtn.style.display = 'none';
            if (testBtn) testBtn.style.display = 'none';
            if (statusText) statusText.textContent = 'Push notifications are disabled';
        }
    }

    showNotification(title, message) {
        // Show a simple notification using Bootstrap toast or alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${title === 'Success' ? 'success' : 'danger'} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize push notification manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.pushManager = new PushNotificationManager();
    window.pushManager.init();
});
