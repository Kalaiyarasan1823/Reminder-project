#!/usr/bin/env python3
"""
Generate VAPID keys for push notifications
"""
from pywebpush import WebPushException, webpush
from py_vapid import Vapid
import base64
import json

def generate_vapid_keys():
    """Generate VAPID keys for push notifications"""
    try:
        # Generate VAPID keys
        vapid = Vapid()
        vapid_key = vapid.generate_keys()
        
        print("VAPID Keys Generated Successfully!")
        print("=" * 50)
        print(f"Public Key: {vapid_key.public_key}")
        print(f"Private Key: {vapid_key.private_key}")
        print("=" * 50)
        print("\nCopy these keys to your Django settings.py file:")
        print("VAPID_PUBLIC_KEY = 'your_generated_public_key'")
        print("VAPID_PRIVATE_KEY = 'your_generated_private_key'")
        
        return vapid_key.public_key, vapid_key.private_key
        
    except Exception as e:
        print(f"Error generating VAPID keys: {e}")
        return None, None

if __name__ == "__main__":
    generate_vapid_keys() 