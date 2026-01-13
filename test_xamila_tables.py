#!/usr/bin/env python
import requests
import json

def test_xamila_tables():
    """Test avec les tables core_* dans la base xamila"""
    
    print('=== TEST AVEC TABLES CORE_* DANS XAMILA ===')
    
    # 1. Authentification
    login_response = requests.post('http://127.0.0.1:8000/api/auth/login/', 
                                 json={'email': 'test@xamila.com', 'password': 'test123'})
    
    print(f'Login Status: {login_response.status_code}')
    if login_response.status_code != 200:
        print(f'Login Error: {login_response.text[:200]}')
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
        print(f'OK Current Balance: {balance} FCFA')
    else:
        print(f'Account Error: {account_response.text[:200]}')
    
    # 3. Test nouveau dépôt
    deposit_data = {
        'montant': 25000,
        'methode_depot': 'bank',
        'banque': 'NSIA',
        'description': 'Test dépôt avec tables core_* dans xamila'
    }
    
    deposit_response = requests.post('http://127.0.0.1:8000/api/savings/deposit/', 
                                   json=deposit_data, headers=headers)
    print(f'Deposit Status: {deposit_response.status_code}')
    
    if deposit_response.status_code == 200:
        deposit_resp_data = deposit_response.json()
        print(f'OK Deposit Reference: {deposit_resp_data.get("reference", "N/A")}')
        print(f'OK New Balance: {deposit_resp_data.get("nouveau_solde", "N/A")} FCFA')
    else:
        print(f'Deposit Error: {deposit_response.text[:300]}')
    
    # 4. Test transactions
    transactions_response = requests.get('http://127.0.0.1:8000/api/savings/transactions/', headers=headers)
    print(f'Transactions Status: {transactions_response.status_code}')
    
    if transactions_response.status_code == 200:
        transactions_data = transactions_response.json()
        print(f'OK Number of transactions: {len(transactions_data)}')
    else:
        print(f'Transactions Error: {transactions_response.text[:200]}')
    
    print('\n=== VERIFICATION ===')
    print('Vérifiez dans phpMyAdmin:')
    print('- Base de données: xamila')
    print('- Table: core_savingsdeposit')
    print('- Nouveau dépôt de 25000 FCFA devrait être visible')

if __name__ == "__main__":
    test_xamila_tables()
