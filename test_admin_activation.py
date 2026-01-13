#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import ContenuPedagogique, Matiere

def test_admin_activation():
    """Test la création d'un contenu pédagogique pour vérifier l'activation automatique"""
    
    # Trouver une matière du second tour pour le test
    matiere = Matiere.objects.filter(
        choix_concours='ENA',
        tour_ena='second_tour'
    ).first()
    
    if not matiere:
        print("Aucune matière du second tour trouvée pour le test")
        return
    
    print(f"Test avec la matière: {matiere.nom} (ID: {matiere.id})")
    
    # Créer un nouveau contenu pédagogique
    nouveau_contenu = ContenuPedagogique.objects.create(
        titre="Test activation automatique",
        matiere=matiere,
        type_contenu="pdf",
        description="Test pour vérifier l'activation automatique"
    )
    
    print(f"Contenu créé - ID: {nouveau_contenu.id}")
    print(f"Titre: {nouveau_contenu.titre}")
    print(f"Active: {nouveau_contenu.active}")
    
    if nouveau_contenu.active:
        print("✓ SUCCESS: Le contenu est automatiquement activé!")
    else:
        print("✗ FAILED: Le contenu n'est pas activé automatiquement")
        # Activer manuellement pour le test
        nouveau_contenu.active = True
        nouveau_contenu.save()
        print("→ Contenu activé manuellement")

if __name__ == '__main__':
    test_admin_activation()
