import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Utilisateur

# Check if user exists with phone number
try:
    user = Utilisateur.objects.get(telephone='0709638208')
    print(f"Found user by phone: {user.nom_complet} - {user.email}")
    print(f"User ID: {user.id}")
    print(f"Is active: {user.is_active}")
    print(f"Password set: {bool(user.password)}")
except Utilisateur.DoesNotExist:
    print("No user found with phone 0709638208")

# Check if user exists with email
try:
    user = Utilisateur.objects.get(email='0709638208')
    print(f"Found user by email: {user.nom_complet} - {user.email}")
except Utilisateur.DoesNotExist:
    print("No user found with email 0709638208")

# List all users
print("\nAll users in database:")
users = Utilisateur.objects.all()
for user in users:
    print(f"- {user.nom_complet} | {user.email} | {user.telephone} | Active: {user.is_active}")
