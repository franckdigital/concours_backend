#!/usr/bin/env python
"""
Script pour créer des données d'exemple pour tester la structure ENA
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Cycle, Matiere, Lecon, ContenuPedagogique, SessionZoomLive
from django.utils import timezone
from datetime import timedelta

def create_ena_test_data():
    print("Creation des donnees d'exemple pour la structure ENA...")
    
    # 1. Créer un cycle pour le second tour
    cycle_ena, created = Cycle.objects.get_or_create(nom="Cycle ENA 2025")
    if created:
        print(f"[OK] Cycle cree : {cycle_ena.nom}")
    else:
        print(f"[INFO] Cycle existant : {cycle_ena.nom}")
    
    # 2. Créer des matières pour chaque tour ENA
    
    # PREMIER TOUR - Matières sans cycle
    matieres_premier_tour = [
        "Culture Générale",
        "Mathématiques", 
        "Français",
        "Histoire",
        "Géographie"
    ]
    
    for nom_matiere in matieres_premier_tour:
        matiere, created = Matiere.objects.get_or_create(
            nom=nom_matiere,
            choix_concours='ENA',
            tour_ena='premier_tour',
            cycle=None  # Pas de cycle pour le premier tour
        )
        if created:
            print(f"[OK] Matiere Premier Tour creee : {matiere.nom}")
        else:
            print(f"[INFO] Matiere Premier Tour existante : {matiere.nom}")
    
    # SECOND TOUR - Matières avec cycle
    matieres_second_tour = [
        "Droit Constitutionnel",
        "Économie Politique",
        "Relations Internationales",
        "Administration Publique"
    ]
    
    for nom_matiere in matieres_second_tour:
        matiere, created = Matiere.objects.get_or_create(
            nom=nom_matiere,
            choix_concours='ENA',
            tour_ena='second_tour',
            cycle=cycle_ena  # Cycle obligatoire pour le second tour
        )
        if created:
            print(f"[OK] Matiere Second Tour creee : {matiere.nom}")
        else:
            print(f"[INFO] Matiere Second Tour existante : {matiere.nom}")
    
    # ORAL - Matières sans cycle
    matieres_oral = [
        "Entretien de Motivation",
        "Analyse de Cas Pratique",
        "Présentation Orale"
    ]
    
    for nom_matiere in matieres_oral:
        matiere, created = Matiere.objects.get_or_create(
            nom=nom_matiere,
            choix_concours='ENA',
            tour_ena='oral',
            cycle=None  # Pas de cycle pour l'oral
        )
        if created:
            print(f"[OK] Matiere Oral creee : {matiere.nom}")
        else:
            print(f"[INFO] Matiere Oral existante : {matiere.nom}")
    
    # 3. Créer des leçons (catégories) pour le premier tour
    print("\nCreation des lecons pour le Premier Tour...")
    
    # Culture Générale - Catégories
    culture_generale = Matiere.objects.get(nom="Culture Générale", tour_ena='premier_tour')
    categories_culture = [
        ("Sport", "Questions sur le sport et les événements sportifs"),
        ("Science", "Sciences et découvertes scientifiques"),
        ("Art", "Arts, littérature et culture artistique"),
        ("Histoire", "Événements historiques marquants"),
        ("Société", "Questions de société contemporaine")
    ]
    
    for nom, description in categories_culture:
        lecon, created = Lecon.objects.get_or_create(
            nom=nom,
            matiere=culture_generale,
            defaults={
                'description': description,
                'ordre': len(categories_culture)
            }
        )
        if created:
            print(f"  [OK] Lecon creee : {lecon.nom} ({culture_generale.nom})")
    
    # Mathématiques - Catégories
    mathematiques = Matiere.objects.get(nom="Mathématiques", tour_ena='premier_tour')
    categories_maths = [
        ("Algèbre", "Équations et systèmes algébriques"),
        ("Géométrie", "Géométrie plane et dans l'espace"),
        ("Probabilités", "Calculs de probabilités et statistiques"),
        ("Analyse", "Fonctions et dérivées")
    ]
    
    for nom, description in categories_maths:
        lecon, created = Lecon.objects.get_or_create(
            nom=nom,
            matiere=mathematiques,
            defaults={
                'description': description,
                'ordre': len(categories_maths)
            }
        )
        if created:
            print(f"  [OK] Lecon creee : {lecon.nom} ({mathematiques.nom})")
    
    # 4. Créer des contenus pédagogiques pour le second tour
    print("\nCreation des contenus pedagogiques pour le Second Tour...")
    
    droit_constit = Matiere.objects.get(nom="Droit Constitutionnel", tour_ena='second_tour')
    contenus_droit = [
        ("Constitution de la Ve République", "pdf", "Cours complet sur la Constitution"),
        ("Les Institutions Françaises", "video", "Vidéo explicative des institutions"),
        ("Le Conseil Constitutionnel", "pdf", "Rôle et fonctionnement du Conseil"),
        ("Séparation des Pouvoirs", "video", "Principe de séparation des pouvoirs")
    ]
    
    for titre, type_contenu, description in contenus_droit:
        contenu, created = ContenuPedagogique.objects.get_or_create(
            titre=titre,
            matiere=droit_constit,
            type_contenu=type_contenu,
            defaults={
                'description': description,
                'ordre': len(contenus_droit)
            }
        )
        if created:
            print(f"  [OK] Contenu cree : {contenu.titre} ({type_contenu.upper()})")
    
    # 5. Créer des sessions Zoom pour l'oral
    print("\nCreation des sessions Zoom pour l'Oral...")
    
    entretien_motivation = Matiere.objects.get(nom="Entretien de Motivation", tour_ena='oral')
    
    # Sessions programmées pour les prochains jours
    sessions_zoom = [
        ("Préparation Entretien - Session 1", timezone.now() + timedelta(days=1, hours=14)),
        ("Simulation Entretien - Session 2", timezone.now() + timedelta(days=3, hours=10)),
        ("Conseils et Techniques - Session 3", timezone.now() + timedelta(days=5, hours=16)),
    ]
    
    for titre, date_session in sessions_zoom:
        session, created = SessionZoomLive.objects.get_or_create(
            titre=titre,
            matiere=entretien_motivation,
            date_session=date_session,
            defaults={
                'description': f"Session de préparation pour {entretien_motivation.nom}",
                'url_zoom': f"https://zoom.us/j/123456789{len(sessions_zoom)}",
                'meeting_id': f"123 456 78{len(sessions_zoom)}",
                'mot_de_passe': "ENA2025",
                'duree_minutes': 90,
                'statut': 'programmee'
            }
        )
        if created:
            print(f"  [OK] Session Zoom creee : {session.titre}")
            print(f"     Date : {session.date_session.strftime('%d/%m/%Y %H:%M')}")
    
    print("\nDonnees d'exemple creees avec succes !")
    print("\nStructure creee :")
    print("[1] Premier Tour (sans cycle) :")
    print("   - Culture Generale -> Sport, Science, Art, Histoire, Societe")
    print("   - Mathematiques -> Algebre, Geometrie, Probabilites, Analyse")
    print("[2] Second Tour (avec cycle) :")
    print("   - Droit Constitutionnel -> PDF et Videos")
    print("[3] Oral (sans cycle) :")
    print("   - Entretien de Motivation -> Sessions Zoom programmees")

if __name__ == "__main__":
    create_ena_test_data()
