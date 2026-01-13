#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import ContenuPedagogique

def fix_inactive_contenus():
    """Active tous les contenus pédagogiques inactifs"""
    
    # Trouver tous les contenus inactifs
    contenus_inactifs = ContenuPedagogique.objects.filter(active=False)
    
    print(f"Contenus pedagogiques inactifs trouves: {contenus_inactifs.count()}")
    
    for contenu in contenus_inactifs:
        print(f"- ID {contenu.id}: {contenu.titre} (Matiere: {contenu.matiere.nom})")
    
    if contenus_inactifs.exists():
        # Activer tous les contenus inactifs
        count = contenus_inactifs.count()
        contenus_inactifs.update(active=True)
        print(f"\nOK {count} contenus pedagogiques actives avec succes!")
        
        # Vérification
        still_inactive = ContenuPedagogique.objects.filter(active=False).count()
        print(f"Contenus encore inactifs: {still_inactive}")
    else:
        print("Tous les contenus sont deja actifs!")

if __name__ == '__main__':
    fix_inactive_contenus()
