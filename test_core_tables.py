#!/usr/bin/env python
import requests

def test_core_tables():
    """Test avec les nouvelles tables core_"""
    
    print('=== TEST AVEC TABLES CORE_ ===')
    
    # 1. Authentification
    login_response = requests.post('http://127.0.0.1:8000/api/auth/login/', 
                                 json={'email': 'test@xamila.com', 'password': 'test123'})
    if login_response.status_code != 200:
        print(f'Login failed: {login_response.status_code}')
        return
    
    token = login_response.json()['tokens']['access']
    headers = {'Authorization': f'Bearer {token}'}
    print('OK Authentication successful')
    
    # 2. Test compte d'épargne
    account_response = requests.get('http://127.0.0.1:8000/api/savings/account/', headers=headers)
    print(f'Account Status: {account_response.status_code}')
    
    if account_response.status_code == 200:
        account_data = account_response.json()
        balance = account_data.get('solde_actuel', 'N/A')
        print(f'Current Balance: {balance} FCFA')
    
    # 3. Test nouveau dépôt
    deposit_data = {
        'montant': 15000,
        'methode_depot': 'bank',
        'banque': 'NSIA',
        'description': 'Test avec table core_savingsdeposit'
    }
    
    deposit_response = requests.post('http://127.0.0.1:8000/api/savings/deposit/', 
                                   json=deposit_data, headers=headers)
    print(f'New Deposit Status: {deposit_response.status_code}')
    
    if deposit_response.status_code == 200:
        deposit_resp_data = deposit_response.json()
        print(f'Deposit Reference: {deposit_resp_data.get("reference", "N/A")}')
        print(f'New Balance: {deposit_resp_data.get("nouveau_solde", "N/A")} FCFA')
    else:
        print(f'Deposit Error: {deposit_response.text[:200]}')
    
    print('\n=== VERIFICATION DANS PHPMYADMIN ===')
    print('Maintenant, vérifiez dans phpMyAdmin:')
    print('- Table: core_savingsdeposit')
    print('- Vous devriez voir le nouveau dépôt de 15000 FCFA')

if __name__ == "__main__":
    test_core_tables()
