#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Utilisateur

def test_user_password():
    try:
        user = Utilisateur.objects.get(email='test@xamila.com')
        print(f'User ID: {user.id}')
        print(f'User email: {user.email}')
        print(f'Password check test123: {user.check_password("test123")}')
        print(f'Password check testpassword123: {user.check_password("testpassword123")}')
        print(f'User is_active: {getattr(user, "is_active", "N/A")}')
        
        # Test de changement de mot de passe si nécessaire
        if not user.check_password("test123"):
            print("Setting password to test123...")
            user.set_password("test123")
            user.save()
            print("Password updated successfully")
            
    except Utilisateur.DoesNotExist:
        print("User not found")

if __name__ == "__main__":
    test_user_password()
