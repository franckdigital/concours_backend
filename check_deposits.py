#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import SavingsDeposit, SavingsAccount
from django.db import connection

def check_deposits():
    """Vérifier les dépôts dans la base de données"""
    
    # Vérifier les dépôts
    deposits = SavingsDeposit.objects.all()
    print(f'Nombre de dépôts: {deposits.count()}')
    
    for deposit in deposits:
        print(f'Dépôt ID: {deposit.id}, Montant: {deposit.montant}, Date: {deposit.date_creation}, Méthode: {deposit.methode_depot}')
    
    # Vérifier le nom de la table
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE '%deposit%'")
        tables = cursor.fetchall()
        print(f'Tables contenant deposit: {tables}')
        
        # Vérifier le contenu de la table
        cursor.execute("SELECT COUNT(*) FROM prepaconcours_savingsdeposit")
        count = cursor.fetchone()[0]
        print(f'Nombre d\'enregistrements dans prepaconcours_savingsdeposit: {count}')
        
        if count > 0:
            cursor.execute("SELECT id, montant, methode_depot, date_creation FROM prepaconcours_savingsdeposit ORDER BY date_creation DESC LIMIT 5")
            recent_deposits = cursor.fetchall()
            print('Derniers dépôts:')
            for dep in recent_deposits:
                print(f'  ID: {dep[0]}, Montant: {dep[1]}, Méthode: {dep[2]}, Date: {dep[3]}')

if __name__ == "__main__":
    check_deposits()
