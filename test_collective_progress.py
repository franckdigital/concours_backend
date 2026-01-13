import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Utilisateur
from rest_framework_simplejwt.tokens import RefreshToken
import requests
import json

def test_collective_progress():
    """Test de l'API collective progress avec token Django"""
    # Obtenir un utilisateur existant
    user = Utilisateur.objects.first()
    if not user:
        print('Aucun utilisateur trouvé')
        return
    
    # Générer un token JWT pour cet utilisateur
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    print(f'Testing with user: {user.email}')
    
    # Test collective progress
    url = 'http://127.0.0.1:8000/api/savings/collective-progress/'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('=== PROGRESSION COLLECTIVE ===')
            print(f'Participants: {data["community_stats"]["total_participants"]}')
            print(f'Total epargne: {data["community_stats"]["total_saved"]:,.0f} FCFA')
            print(f'Niveau communaute: {data["community_stats"]["community_level"]}')
            print(f'Top epargnants: {len(data["top_savers"])}')
            if data["current_user"]:
                print(f'Position utilisateur: #{data["current_user"]["rank"]}')
                print(f'Montant utilisateur: {data["current_user"]["amount"]:,.0f} FCFA')
        else:
            print(f'Erreur: {response.text}')
            
    except Exception as e:
        print(f'Erreur: {e}')

if __name__ == '__main__':
    test_collective_progress()
