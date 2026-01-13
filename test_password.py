import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Utilisateur

# Get the user
user = Utilisateur.objects.get(telephone='0709638208')
print(f"User: {user.nom_complet}")
print(f"Email: {user.email}")
print(f"Phone: {user.telephone}")

# Test password
test_password = 'manager$2025'
is_valid = user.check_password(test_password)
print(f"Password 'manager$2025' is valid: {is_valid}")

# Set a new password for testing
user.set_password('manager$2025')
user.save()
print("Password set to 'manager$2025'")

# Test again
is_valid = user.check_password('manager$2025')
print(f"Password 'manager$2025' is now valid: {is_valid}")
