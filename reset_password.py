#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Utilisateur

# Trouver l'utilisateur
user = Utilisateur.objects.filter(telephone='0709638208').first()

if user:
    print(f'User found: {user.nom_complet}')
    print(f'Email: {user.email}')
    print(f'Telephone: {user.telephone}')
    
    # Réinitialiser le mot de passe
    user.set_password('manager$2025')
    user.save()
    
    print('Password reset to: manager$2025')
    
    # Vérifier que ça marche
    if user.check_password('manager$2025'):
        print('✅ Password verification successful')
    else:
        print('❌ Password verification failed')
else:
    print('❌ User not found')
