import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Utilisateur

# Get the user and set a simple test password
user = Utilisateur.objects.get(telephone='0709638208')
user.set_password('test123')
user.save()
print(f"Password set to 'test123' for user {user.nom_complet}")

# Verify the password works
is_valid = user.check_password('test123')
print(f"Password 'test123' is valid: {is_valid}")
