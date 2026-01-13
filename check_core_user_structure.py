#!/usr/bin/env python
import pymysql

def check_core_user_structure():
    """Vérifier la structure de core_user dans xamila"""
    
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        port=3306,
        database='xamila'
    )
    
    cursor = connection.cursor()
    cursor.execute('DESCRIBE core_user')
    columns = cursor.fetchall()
    print('Colonnes de core_user:')
    for col in columns:
        nullable = "NULL" if col[2] == "YES" else "NOT NULL"
        default = f"DEFAULT {col[4]}" if col[4] else ""
        print(f'  {col[0]}: {col[1]} {nullable} {default}')

    cursor.execute('SELECT COUNT(*) FROM core_user')
    count = cursor.fetchone()[0]
    print(f'\nNombre d\'utilisateurs: {count}')

    if count > 0:
        cursor.execute('SELECT id, username, email, first_name, last_name FROM core_user LIMIT 3')
        users = cursor.fetchall()
        print('\nPremiers utilisateurs:')
        for user in users:
            print(f'  {user[0]}: {user[1]} ({user[2]}) - {user[3]} {user[4]}')

    cursor.close()
    connection.close()

if __name__ == "__main__":
    check_core_user_structure()
