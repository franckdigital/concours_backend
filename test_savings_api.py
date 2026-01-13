#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Utilisateur
from rest_framework_simplejwt.tokens import RefreshToken

def test_savings_api():
    """Test les endpoints de l'API Ma Caisse"""
    
    # Récupérer l'utilisateur de test
    user = Utilisateur.objects.get(email="test@xamila.com")
    
    # Générer un token JWT pour l'utilisateur
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    base_url = 'http://127.0.0.1:8000/api'
    
    print(f"Testing API with user: {user.nom_complet} (ID: {user.id})")
    print(f"Token: {access_token[:50]}...")
    print("-" * 50)
    
    # Test 1: GET /api/savings/account/
    print("1. Test GET /api/savings/account/")
    try:
        response = requests.get(f'{base_url}/savings/account/', headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Solde: {data['solde_actuel']} FCFA")
            print(f"   Objectif: {data['objectif_mensuel']} FCFA")
            print(f"   Progression: {data['progression_mensuelle']:.1f}%")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # Test 2: POST /api/savings/deposit/
    print("2. Test POST /api/savings/deposit/")
    deposit_data = {
        'montant': 10000,
        'methode_depot': 'home'
    }
    try:
        response = requests.post(f'{base_url}/savings/deposit/', 
                               headers=headers, 
                               data=json.dumps(deposit_data))
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Message: {data['message']}")
            print(f"   Nouveau solde: {data['nouveau_solde']} FCFA")
            print(f"   Référence: {data['reference']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # Test 3: GET /api/savings/transactions/
    print("3. Test GET /api/savings/transactions/")
    try:
        response = requests.get(f'{base_url}/savings/transactions/', headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Nombre de transactions: {len(data['transactions'])}")
            if data['transactions']:
                last_tx = data['transactions'][0]
                print(f"   Dernière transaction: {last_tx['type']} de {last_tx['amount']} FCFA")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_savings_api()
