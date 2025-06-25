#!/usr/bin/env python3
"""
Generate VAPID keys for push notifications using cryptography library
"""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

def generate_vapid_keys():
    """Generate VAPID keys for push notifications"""
    try:
        # Generate private key
        private_key = ec.generate_private_key(ec.SECP256R1())
        
        # Get public key
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Convert to base64 for VAPID
        private_key_b64 = base64.urlsafe_b64encode(private_pem).decode('utf-8').rstrip('=')
        public_key_b64 = base64.urlsafe_b64encode(public_pem).decode('utf-8').rstrip('=')
        
        print("VAPID Keys Generated Successfully!")
        print("=" * 50)
        print(f"Public Key: {public_key_b64}")
        print(f"Private Key: {private_key_b64}")
        print("=" * 50)
        print("\nCopy these keys to your Django settings.py file:")
        print(f"VAPID_PUBLIC_KEY = '{public_key_b64}'")
        print(f"VAPID_PRIVATE_KEY = '{private_key_b64}'")
        
        return public_key_b64, private_key_b64
        
    except Exception as e:
        print(f"Error generating VAPID keys: {e}")
        return None, None

if __name__ == "__main__":
    generate_vapid_keys() 