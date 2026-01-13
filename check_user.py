#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Utilisateur

# Chercher l'utilisateur par téléphone
user = Utilisateur.objects.filter(telephone='0709638208').first()
print(f'User found: {user}')

if user:
    print(f'Email: {user.email}')
    print(f'Telephone: {user.telephone}')
    print(f'Nom complet: {user.nom_complet}')
    print(f'Password check with "manager$2025": {user.check_password("manager$2025")}')
    
    # Tester différents mots de passe possibles
    test_passwords = ['manager$2025', 'Manager$2025', 'manager2025', 'password', '123456']
    for pwd in test_passwords:
        if user.check_password(pwd):
            print(f'✅ Correct password found: {pwd}')
            break
    else:
        print('❌ None of the test passwords work')
        
    # Afficher le hash du mot de passe pour debug
    print(f'Password hash: {user.password}')
else:
    print('❌ No user found with telephone 0709638208')
    
    # Lister tous les utilisateurs
    print('\nAll users in database:')
    for u in Utilisateur.objects.all():
        print(f'- {u.nom_complet} | {u.telephone} | {u.email}')
