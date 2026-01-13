#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Utilisateur, SavingsAccount
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal

def sync_user_from_frontend():
    """Synchronise l'utilisateur du frontend avec le backend concours"""
    
    # Données de l'utilisateur du frontend
    frontend_user_data = {
        'id': '37c1c8f9-4cda-4fab-9cf9-9ad47a67e792',
        'email': 'test@xamila.com',
        'first_name': 'Test',
        'last_name': 'User',
        'phone': '+33123456789'
    }
    
    try:
        # Vérifier si l'utilisateur existe déjà
        user = Utilisateur.objects.get(email=frontend_user_data['email'])
        print(f"Utilisateur existant trouve: {user.nom_complet}")
    except Utilisateur.DoesNotExist:
        # Créer l'utilisateur avec l'ID du frontend
        user = Utilisateur.objects.create_user(
            email=frontend_user_data['email'],
            nom_complet=f"{frontend_user_data['first_name']} {frontend_user_data['last_name']}",
            telephone=frontend_user_data['phone'],
            password='testpassword123'
        )
        print(f"Nouvel utilisateur cree: {user.nom_complet}")
    
    # Vérifier/créer le compte d'épargne
    try:
        savings_account = SavingsAccount.objects.get(utilisateur=user)
        print(f"Compte d'epargne existant: {savings_account.solde_actuel} FCFA")
    except SavingsAccount.DoesNotExist:
        savings_account = SavingsAccount.objects.create(
            utilisateur=user,
            solde_actuel=Decimal('85000.00'),
            objectif_mensuel=Decimal('25000.00')
        )
        print(f"Compte d'epargne cree: {savings_account.solde_actuel} FCFA")
    
    # Générer un token JWT pour ce serveur
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    print(f"\nInformations de connexion:")
    print(f"Email: {user.email}")
    print(f"ID utilisateur: {user.id}")
    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")
    
    print(f"\nPour tester l'API, utilisez:")
    print(f"Authorization: Bearer {access_token}")
    
    return {
        'user': user,
        'access_token': access_token,
        'refresh_token': refresh_token
    }

if __name__ == "__main__":
    sync_user_from_frontend()
