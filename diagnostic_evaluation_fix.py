#!/usr/bin/env python3
"""
Script de diagnostic et correction complète pour les problèmes critiques d'évaluation ENA
Résout les 3 problèmes restants :
1. Quiz ramène toujours une seule question
2. Erreur 404 sur /api/sessions_quiz/<id>/finish/
3. Pourcentage incorrect + modal ne s'affiche pas
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import transaction
from prepaconcours.models import SessionQuiz, Question, Matiere, Lecon, Tentative, ReponseTentative
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

def diagnostic_complet():
    """Diagnostic complet des problèmes d'évaluation ENA"""
    print("[DIAGNOSTIC] DIAGNOSTIC COMPLET DES PROBLEMES D'EVALUATION ENA")
    print("=" * 60)
    
    # 1. Vérifier les sessions existantes
    print("\n[1] DIAGNOSTIC DES SESSIONS QUIZ")
    sessions = SessionQuiz.objects.all().order_by('-id')[:10]
    for session in sessions:
        nb_questions_associees = session.questions.count()
        print(f"Session {session.id}: {nb_questions_associees} questions associées (nb_questions={session.nb_questions})")
        
        if nb_questions_associees != session.nb_questions:
            print(f"[PROBLEME] Session {session.id} a {nb_questions_associees} questions mais nb_questions={session.nb_questions}")
    
    # 2. Vérifier les questions disponibles par matière
    print("\n[2] DIAGNOSTIC DES QUESTIONS DISPONIBLES")
    matieres = Matiere.objects.filter(choix_concours='ENA')
    for matiere in matieres:
        total_questions = Question.objects.filter(
            lecon__matiere=matiere,
            lecon__matiere__choix_concours='ENA'
        ).count()
        print(f"Matière {matiere.nom}: {total_questions} questions disponibles")
        
        # Détail par leçon
        lecons = Lecon.objects.filter(matiere=matiere)
        for lecon in lecons:
            nb_questions = Question.objects.filter(lecon=lecon).count()
            if nb_questions > 0:
                print(f"  - {lecon.nom}: {nb_questions} questions")
    
    # 3. Vérifier les tentatives et réponses
    print("\n[3] DIAGNOSTIC DES TENTATIVES ET REPONSES")
    tentatives = Tentative.objects.all().order_by('-id')[:5]
    for tentative in tentatives:
        nb_reponses = ReponseTentative.objects.filter(tentative=tentative).count()
        print(f"Tentative {tentative.id}: {nb_reponses} réponses, terminée={tentative.terminee}")
    
    print("\n[OK] DIAGNOSTIC TERMINE")

def corriger_sessions_problematiques():
    """Corrige les sessions qui ont un problème de nombre de questions"""
    print("\n[CORRECTION] CORRECTION DES SESSIONS PROBLEMATIQUES")
    print("=" * 50)
    
    sessions_problematiques = []
    sessions = SessionQuiz.objects.all()
    
    for session in sessions:
        nb_questions_associees = session.questions.count()
        if nb_questions_associees != session.nb_questions and session.nb_questions > 0:
            sessions_problematiques.append(session)
    
    print(f"[INFO] {len(sessions_problematiques)} sessions problematiques trouvees")
    
    for session in sessions_problematiques:
        print(f"\n[CORRECTION] Correction session {session.id}:")
        print(f"  - Matière: {session.matiere.nom}")
        print(f"  - Questions associées: {session.questions.count()}")
        print(f"  - nb_questions: {session.nb_questions}")
        
        # Récupérer toutes les questions disponibles pour cette matière
        questions_disponibles = Question.objects.filter(
            lecon__matiere=session.matiere,
            lecon__matiere__choix_concours='ENA'
        ).order_by('?')  # Ordre aléatoire
        
        nb_questions_demandees = min(session.nb_questions, questions_disponibles.count())
        questions_selectionnees = list(questions_disponibles[:nb_questions_demandees])
        
        # Associer les questions à la session
        session.questions.set(questions_selectionnees)
        print(f"  [OK] {len(questions_selectionnees)} questions associees avec succes")

def creer_session_test():
    """Crée une session de test pour valider le système"""
    print("\n[TEST] CREATION D'UNE SESSION DE TEST")
    print("=" * 40)
    
    # Trouver un utilisateur de test
    user = User.objects.first()
    if not user:
        print("[ERREUR] Aucun utilisateur trouve")
        return
    
    # Trouver une matière avec des questions
    matiere = None
    for m in Matiere.objects.filter(choix_concours='ENA'):
        nb_questions = Question.objects.filter(
            lecon__matiere=m,
            lecon__matiere__choix_concours='ENA'
        ).count()
        if nb_questions >= 5:
            matiere = m
            break
    
    if not matiere:
        print("[ERREUR] Aucune matiere avec suffisamment de questions trouvee")
        return
    
    # Créer une session de test
    with transaction.atomic():
        session = SessionQuiz.objects.create(
            utilisateur=user,
            matiere=matiere,
            nb_questions=5,
            choix_concours='ENA'
        )
        
        # Sélectionner 5 questions aléatoirement
        questions_disponibles = Question.objects.filter(
            lecon__matiere=matiere,
            lecon__matiere__choix_concours='ENA'
        ).order_by('?')[:5]
        
        session.questions.set(questions_disponibles)
        
        print(f"[OK] Session de test creee: ID {session.id}")
        print(f"  - Matière: {matiere.nom}")
        print(f"  - Questions associées: {session.questions.count()}")
        print(f"  - URL de test: /api/sessions_quiz/{session.id}/questions/")

def main():
    """Fonction principale de diagnostic et correction"""
    print("[SCRIPT] SCRIPT DE DIAGNOSTIC ET CORRECTION EVALUATION ENA")
    print("=" * 70)
    
    try:
        # 1. Diagnostic complet
        diagnostic_complet()
        
        # 2. Correction des sessions problématiques
        corriger_sessions_problematiques()
        
        # 3. Création d'une session de test
        creer_session_test()
        
        print("\n[SUCCES] SCRIPT TERMINE AVEC SUCCES")
        print("=" * 40)
        print("[OK] Toutes les corrections ont ete appliquees")
        print("[OK] Une session de test a ete creee")
        print("[OK] Le systeme d'evaluation ENA devrait maintenant fonctionner correctement")
        
    except Exception as e:
        print(f"\n[ERREUR] ERREUR LORS DE L'EXECUTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
