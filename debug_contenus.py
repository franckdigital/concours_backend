#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import ContenuPedagogique, Matiere

def debug_contenus():
    """Debug les contenus pédagogiques et leur visibilité"""
    
    print("=== DEBUG CONTENUS PEDAGOGIQUES ===\n")
    
    # Lister tous les contenus
    all_contenus = ContenuPedagogique.objects.all().order_by('-date_creation')
    print(f"Total contenus pedagogiques: {all_contenus.count()}")
    
    for contenu in all_contenus:
        print(f"ID {contenu.id}: {contenu.titre}")
        print(f"  - Matiere: {contenu.matiere.nom} (ID: {contenu.matiere.id})")
        print(f"  - Cycle: {contenu.matiere.cycle.nom if contenu.matiere.cycle else 'Aucun'}")
        print(f"  - Tour ENA: {contenu.matiere.tour_ena}")
        print(f"  - Active: {contenu.active}")
        print(f"  - Date creation: {contenu.date_creation}")
        print()
    
    # Vérifier les matières du second tour
    print("=== MATIERES SECOND TOUR ===\n")
    matieres_second_tour = Matiere.objects.filter(
        choix_concours='ENA',
        tour_ena='second_tour'
    ).order_by('cycle', 'nom')
    
    for matiere in matieres_second_tour:
        contenus_count = ContenuPedagogique.objects.filter(matiere=matiere, active=True).count()
        print(f"Matiere: {matiere.nom} (ID: {matiere.id})")
        print(f"  - Cycle: {matiere.cycle.nom if matiere.cycle else 'Aucun'}")
        print(f"  - Contenus actifs: {contenus_count}")
        print()

if __name__ == '__main__':
    debug_contenus()
