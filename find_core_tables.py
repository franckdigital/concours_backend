#!/usr/bin/env python
import pymysql

def find_core_tables():
    """Chercher les tables core_savings dans toutes les bases de données"""
    
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            port=3306
        )
        
        cursor = connection.cursor()
        
        # Lister toutes les bases de données
        cursor.execute('SHOW DATABASES')
        databases = cursor.fetchall()
        print('Bases de données disponibles:')
        for db in databases:
            print(f'  - {db[0]}')
        
        # Chercher les tables core_savings dans chaque base
        found_tables = False
        for db in databases:
            db_name = db[0]
            if db_name not in ['information_schema', 'performance_schema', 'mysql', 'sys']:
                cursor.execute(f'USE `{db_name}`')
                cursor.execute("SHOW TABLES LIKE 'core_savings%'")
                tables = cursor.fetchall()
                if tables:
                    print(f'\nTables core_savings* trouvées dans {db_name}:')
                    for table in tables:
                        print(f'  - {table[0]}')
                    found_tables = True
                    
                    # Vérifier le contenu de core_savingsdeposit si elle existe
                    cursor.execute("SHOW TABLES LIKE 'core_savingsdeposit'")
                    if cursor.fetchone():
                        cursor.execute('SELECT COUNT(*) FROM core_savingsdeposit')
                        count = cursor.fetchone()[0]
                        print(f'  Nombre d\'enregistrements dans core_savingsdeposit: {count}')
        
        if not found_tables:
            print('\nAucune table core_savings* trouvée dans aucune base de données.')
            print('Vérification des tables prepaconcours_savings*...')
            
            for db in databases:
                db_name = db[0]
                if db_name not in ['information_schema', 'performance_schema', 'mysql', 'sys']:
                    cursor.execute(f'USE `{db_name}`')
                    cursor.execute("SHOW TABLES LIKE 'prepaconcours_savings%'")
                    tables = cursor.fetchall()
                    if tables:
                        print(f'\nTables prepaconcours_savings* trouvées dans {db_name}:')
                        for table in tables:
                            print(f'  - {table[0]}')
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f'Erreur: {e}')

if __name__ == "__main__":
    find_core_tables()
