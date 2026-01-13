import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SHOW TABLES LIKE 'prepaconcours%'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables prepaconcours:", tables)

if 'prepaconcours_utilisateur' in tables:
    cursor.execute("DESCRIBE prepaconcours_utilisateur")
    columns = cursor.fetchall()
    print("\nColumns in prepaconcours_utilisateur:")
    for col in columns:
        print(f"  {col[0]} - {col[1]}")
else:
    print("Table prepaconcours_utilisateur not found")
    
# Check for any user-related tables
cursor.execute("SHOW TABLES")
all_tables = [row[0] for row in cursor.fetchall()]
user_tables = [t for t in all_tables if 'user' in t.lower() or 'utilisateur' in t.lower()]
print(f"\nUser-related tables: {user_tables}")
