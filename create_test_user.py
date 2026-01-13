#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Utilisateur, SavingsAccount
from decimal import Decimal

def create_test_user():
    """Crée un utilisateur de test pour Ma Caisse"""
    
    # Vérifier si l'utilisateur existe déjà
    email = "test@xamila.com"
    
    try:
        user = Utilisateur.objects.get(email=email)
        print(f"Utilisateur trouve: {user.nom_complet} ({user.email})")
    except Utilisateur.DoesNotExist:
        # Créer l'utilisateur
        user = Utilisateur.objects.create_user(
            email=email,
            nom_complet="Test User",
            telephone="+33123456789",
            password="testpassword123"
        )
        print(f"Utilisateur cree: {user.nom_complet} ({user.email})")
    
    # Vérifier/créer le compte d'épargne
    try:
        savings_account = SavingsAccount.objects.get(utilisateur=user)
        print(f"Compte d'epargne trouve: {savings_account.solde_actuel} FCFA")
    except SavingsAccount.DoesNotExist:
        # Créer le compte d'épargne
        savings_account = SavingsAccount.objects.create(
            utilisateur=user,
            solde_actuel=Decimal('85000.00'),
            objectif_mensuel=Decimal('25000.00')
        )
        print(f"Compte d'epargne cree: {savings_account.solde_actuel} FCFA")
    
    print(f"ID utilisateur: {user.id}")
    print(f"Solde actuel: {savings_account.solde_actuel} FCFA")
    print(f"Progression: {savings_account.calculer_progression_mensuelle():.1f}%")

if __name__ == "__main__":
    create_test_user()
