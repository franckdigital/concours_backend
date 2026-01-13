#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Utilisateur
from django.contrib.auth import authenticate

# Trouver l'utilisateur
user = Utilisateur.objects.filter(telephone='0709638208').first()

if user:
    print(f'User found: {user.nom_complet}')
    print(f'Email: {user.email}')
    print(f'Telephone: {user.telephone}')
    print(f'Is active: {user.is_active}')
    
    # Test direct password check
    print(f'Direct password check: {user.check_password("manager$2025")}')
    
    # Test Django authenticate
    auth_user = authenticate(username=user.email, password='manager$2025')
    print(f'Django authenticate result: {auth_user}')
    
    # Test with telephone as username
    auth_user2 = authenticate(username='0709638208', password='manager$2025')
    print(f'Django authenticate with phone: {auth_user2}')
    
    # Create a simple test password
    user.set_password('test123')
    user.save()
    print('Password changed to: test123')
    
    # Test again
    print(f'Password check with test123: {user.check_password("test123")}')
    auth_user3 = authenticate(username=user.email, password='test123')
    print(f'Django authenticate with test123: {auth_user3}')
    
else:
    print('User not found')
