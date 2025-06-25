# Push Notifications Setup Guide

This guide will help you set up push notifications for your Reminder App.

## Prerequisites

1. **HTTPS Required**: Push notifications only work over HTTPS (except for localhost during development)
2. **Modern Browser**: Chrome, Firefox, Edge, or Safari
3. **Service Worker Support**: Your browser must support service workers

## Step 1: Generate VAPID Keys

VAPID (Voluntary Application Server Identification) keys are required for push notifications.

### Option A: Using the provided script
```bash
cd "C:\Users\lenovo\Desktop\Reminder project\Reminder"
python generate_vapid_keys.py
```

### Option B: Manual generation
```python
from py_vapid import Vapid01 as Vapid
v = Vapid()
print("Public:", v.public_key)
print("Private:", v.private_key)
```

## Step 2: Update Configuration Files

### 1. Update settings.py
Replace the placeholder values in `Reminder/Reminder/settings.py`:

```python
# Push Notification Settings (VAPID)
VAPID_PUBLIC_KEY = "YOUR_ACTUAL_PUBLIC_KEY_HERE"
VAPID_PRIVATE_KEY = "YOUR_ACTUAL_PRIVATE_KEY_HERE"
VAPID_EMAIL = "your-email@example.com"  # Replace with your email
```

### 2. Update push-notifications.js
Replace the placeholder in `Reminder/Reminder_app/static/js/push-notifications.js`:

```javascript
this.vapidPublicKey = 'YOUR_ACTUAL_PUBLIC_KEY_HERE';
```

## Step 3: Test Push Notifications

1. **Start the server**:
   ```bash
   python manage.py runserver
   ```

2. **Open your browser** and navigate to `http://localhost:8000`

3. **Login** to your account

4. **Enable push notifications**:
   - Click the "Notifications" dropdown in the navbar
   - Click "Enable Push Notifications"
   - Allow notifications when prompted by your browser

5. **Test the notification**:
   - Click "Test Notification" in the dropdown
   - You should see a browser notification

## Step 4: Automatic Notifications

The app includes a management command to send automatic notifications for due reminders:

```bash
# Send notifications for reminders due in the next 15 minutes (default)
python manage.py send_push_notifications

# Send notifications for reminders due in the next 30 minutes
python manage.py send_push_notifications --minutes 30
```

### Setting up automatic notifications (Windows Task Scheduler):

1. Open Task Scheduler
2. Create a new Basic Task
3. Set it to run every 5-15 minutes
4. Action: Start a program
5. Program: `C:\Users\lenovo\Desktop\Reminder project\venv\Scripts\python.exe`
6. Arguments: `manage.py send_push_notifications`
7. Start in: `C:\Users\lenovo\Desktop\Reminder project\Reminder`

## Troubleshooting

### Common Issues:

1. **"Push notifications are not supported"**
   - Make sure you're using HTTPS (or localhost)
   - Check that your browser supports service workers

2. **"Service Worker registration failed"**
   - Check that the service worker file exists at `/static/js/sw.js`
   - Make sure static files are being served correctly

3. **"Failed to subscribe to push notifications"**
   - Verify your VAPID keys are correct
   - Check the browser console for detailed error messages

4. **Notifications not appearing**
   - Check browser notification permissions
   - Make sure the site is allowed to send notifications

### Debug Mode:

Open browser developer tools (F12) and check the Console tab for detailed error messages.

## Security Notes

- **Never commit your VAPID private key** to version control
- Use environment variables for production:
  ```python
  import os
  VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY')
  ```

## Production Deployment

For production, make sure to:

1. Use HTTPS
2. Set up proper VAPID keys
3. Configure automatic notification sending
4. Monitor notification delivery rates
5. Handle failed subscriptions gracefully

## Browser Support

- ✅ Chrome 42+
- ✅ Firefox 44+
- ✅ Edge 17+
- ✅ Safari 16+ (macOS 13+)
- ❌ Internet Explorer (not supported)

## Additional Features

The push notification system includes:

- **Automatic subscription management**
- **Failed subscription cleanup**
- **Rich notifications with actions**
- **Background sync support**
- **Offline capability**

For more information, see the [Web Push Protocol documentation](https://tools.ietf.org/html/rfc8030). 