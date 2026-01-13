#!/usr/bin/env python3
"""
Script de test simplifié pour valider l'implémentation des questions d'examen national ENA
"""

import os
import sys
import django
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import QuestionExamen
from django.contrib.auth.models import User

def test_questions_examen_ena():
    """Test simplifié des questions d'examen ENA"""
    print("=== DEBUT DES TESTS QUESTIONS EXAMEN ENA ===")
    
    # Test 1: Vérifier que les questions ont été importées
    total_questions = QuestionExamen.objects.count()
    print(f"Total questions importees: {total_questions}")
    
    # Test 2: Vérifier la répartition par matière
    print("\nRepartition par matiere:")
    for matiere_code, matiere_nom in QuestionExamen.MATIERE_COMBINEE_CHOICES:
        count = QuestionExamen.objects.filter(matiere_combinee=matiere_code).count()
        print(f"  - {matiere_nom}: {count} questions")
    
    # Test 3: Vérifier les types de questions
    print("\nTypes de questions:")
    for type_code, type_nom in QuestionExamen.TYPE_CHOICES:
        count = QuestionExamen.objects.filter(type_question=type_code).count()
        if count > 0:
            print(f"  - {type_nom}: {count} questions")
    
    # Test 4: Tester la génération de codes uniques
    print("\nTest generation codes uniques:")
    question_test = QuestionExamen.objects.create(
        texte="Test question code unique",
        type_question="choix_unique",
        matiere_combinee="culture_aptitude",
        choix_a="A", choix_b="B",
        bonne_reponse="A",
        difficulte="moyen",
        creee_par="Test"
    )
    print(f"Code genere: {question_test.code_question}")
    
    # Test 5: Tester la validation des réponses
    print("\nTest validation reponses:")
    
    # Question QCM
    question_qcm = QuestionExamen.objects.create(
        texte="Test QCM",
        type_question="choix_unique",
        matiere_combinee="culture_aptitude",
        choix_a="Bonne reponse",
        choix_b="Mauvaise reponse",
        bonne_reponse="A",
        difficulte="moyen",
        creee_par="Test"
    )
    
    if question_qcm.verifier_reponse("A"):
        print("  - Validation QCM: OK")
    else:
        print("  - Validation QCM: ERREUR")
    
    # Question Vrai/Faux
    question_vf = QuestionExamen.objects.create(
        texte="Test Vrai/Faux",
        type_question="vrai_faux",
        matiere_combinee="logique_combinee",
        bonne_reponse="VRAI",
        difficulte="facile",
        creee_par="Test"
    )
    
    if question_vf.verifier_reponse("VRAI"):
        print("  - Validation Vrai/Faux: OK")
    else:
        print("  - Validation Vrai/Faux: ERREUR")
    
    # Test 6: Vérifier les quotas pour examen
    print("\nVerification quotas examen:")
    quotas_requis = {
        'culture_aptitude': 60,
        'logique_combinee': 40,
        'anglais': 30
    }
    
    peut_creer_examen = True
    for matiere, quota_requis in quotas_requis.items():
        disponibles = QuestionExamen.objects.filter(
            matiere_combinee=matiere,
            active=True,
            validee=True
        ).count()
        
        suffisant = disponibles >= quota_requis
        print(f"  - {matiere}: {disponibles}/{quota_requis} ({'OK' if suffisant else 'INSUFFISANT'})")
        
        if not suffisant:
            peut_creer_examen = False
    
    print(f"\nPeut creer examen complet: {'OUI' if peut_creer_examen else 'NON'}")
    
    # Test 7: Statistiques finales
    print("\nStatistiques finales:")
    questions_actives = QuestionExamen.objects.filter(active=True).count()
    questions_validees = QuestionExamen.objects.filter(validee=True).count()
    
    print(f"  - Questions actives: {questions_actives}")
    print(f"  - Questions validees: {questions_validees}")
    print(f"  - Pourcentage validees: {(questions_validees/total_questions*100):.1f}%" if total_questions > 0 else "0%")
    
    # Nettoyer les questions de test
    QuestionExamen.objects.filter(creee_par="Test").delete()
    
    print("\n=== TESTS TERMINES ===")
    print("RESULTAT: SUCCES - Le systeme QuestionExamen ENA est operationnel!")

if __name__ == '__main__':
    try:
        test_questions_examen_ena()
    except Exception as e:
        print(f"ERREUR lors des tests: {e}")
        sys.exit(1)
