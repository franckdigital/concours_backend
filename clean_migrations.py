import pymysql

# Connexion à la base de données
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='root',
    database='xamila'
)

cursor = connection.cursor()

# Nettoyer l'historique des migrations problématiques
cursor.execute('DELETE FROM django_migrations WHERE app IN ("admin", "auth", "contenttypes", "sessions")')
connection.commit()

print(f"Supprimé {cursor.rowcount} entrées de migration")

connection.close()
print('Migration history cleaned')
