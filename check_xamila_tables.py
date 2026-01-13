#!/usr/bin/env python
import pymysql

def check_xamila_tables():
    """Vérifier les tables dans la base xamila"""
    
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        port=3306,
        database='xamila'
    )
    
    cursor = connection.cursor()
    
    # Tables utilisateur
    cursor.execute("SHOW TABLES LIKE '%user%'")
    user_tables = cursor.fetchall()
    print('Tables utilisateur dans xamila:')
    for table in user_tables:
        print(f'  - {table[0]}')
    
    # Tables core
    cursor.execute("SHOW TABLES LIKE 'core%'")
    core_tables = cursor.fetchall()
    print('\nTables core dans xamila:')
    for table in core_tables:
        print(f'  - {table[0]}')
    
    # Vérifier structure de core_user si elle existe
    cursor.execute("SHOW TABLES LIKE 'core_user'")
    if cursor.fetchone():
        cursor.execute("DESCRIBE core_user")
        columns = cursor.fetchall()
        print('\nStructure de core_user:')
        for col in columns:
            print(f'  - {col[0]}: {col[1]}')
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    check_xamila_tables()
