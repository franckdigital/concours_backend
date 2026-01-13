#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import ContenuPedagogique, Lecon

def activate_all_contenus():
    """Active tous les contenus pédagogiques et leçons inactifs"""
    
    # Vérifier et activer les contenus pédagogiques inactifs
    contenus_inactifs = ContenuPedagogique.objects.filter(active=False)
    print(f'Contenus pédagogiques inactifs: {contenus_inactifs.count()}')
    
    for contenu in contenus_inactifs:
        print(f'- ID {contenu.id}: {contenu.titre} (Matière: {contenu.matiere.nom})')
    
    if contenus_inactifs.exists():
        count = contenus_inactifs.count()
        contenus_inactifs.update(active=True)
        print(f'OK {count} contenus pedagogiques actives')
    else:
        print('OK Tous les contenus pedagogiques sont deja actifs')
    
    # Vérifier et activer les leçons inactives
    lecons_inactives = Lecon.objects.filter(active=False)
    print(f'\nLecons inactives: {lecons_inactives.count()}')
    
    for lecon in lecons_inactives:
        print(f'- ID {lecon.id}: {lecon.nom} (Matiere: {lecon.matiere.nom})')
    
    if lecons_inactives.exists():
        count = lecons_inactives.count()
        lecons_inactives.update(active=True)
        print(f'OK {count} lecons activees')
    else:
        print('OK Toutes les lecons sont deja actives')

if __name__ == '__main__':
    activate_all_contenus()
