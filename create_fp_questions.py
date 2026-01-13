#!/usr/bin/env python
"""
Script pour créer des questions de test pour la Fonction Publique
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Matiere, Lecon, Question, Choix

def create_fp_test_questions():
    """
    Crée des questions de test pour la Fonction Publique
    """
    print("=== CREATION QUESTIONS TEST FONCTION PUBLIQUE ===")
    
    try:
        # Récupérer la matière Culture Générale FP
        matiere_cg = Matiere.objects.get(nom='fp - Culture Generale', choix_concours='fonction_publique')
        lecon_histoire = Lecon.objects.get(nom='fp - Histoire de France', matiere=matiere_cg)
        
        print(f"Matiere: {matiere_cg.nom}")
        print(f"Lecon: {lecon_histoire.nom}")
        
        # Questions de test variées
        questions_test = [
            {
                'texte': 'En quelle année a eu lieu la Révolution française ?',
                'type': 'choix_unique',
                'explication': 'La Révolution française a commencé en 1789 avec la prise de la Bastille.',
                'choix': [
                    {'texte': '1789', 'correct': True},
                    {'texte': '1792', 'correct': False},
                    {'texte': '1804', 'correct': False},
                    {'texte': '1815', 'correct': False}
                ]
            },
            {
                'texte': 'Quels sont les symboles de la République française ?',
                'type': 'choix_multiple',
                'explication': 'Les principaux symboles de la République française sont Marianne, le coq gaulois et le drapeau tricolore.',
                'choix': [
                    {'texte': 'Marianne', 'correct': True},
                    {'texte': 'Le coq gaulois', 'correct': True},
                    {'texte': 'La fleur de lys', 'correct': False},
                    {'texte': 'Le drapeau tricolore', 'correct': True}
                ]
            },
            {
                'texte': 'Citez un roi de France célèbre :',
                'type': 'texte_court',
                'explication': 'Plusieurs rois de France sont célèbres, notamment Louis XIV (le Roi-Soleil), François Ier, ou Henri IV.',
                'reponse_attendue': 'Louis XIV,François Ier,Henri IV,Louis XVI,Charlemagne,Philippe Auguste'
            },
            {
                'texte': 'La Ve République française a été fondée en 1958.',
                'type': 'vrai_faux',
                'explication': 'Vrai. La Ve République française a été instaurée en 1958 sous Charles de Gaulle.',
                'choix': [
                    {'texte': 'Vrai', 'correct': True},
                    {'texte': 'Faux', 'correct': False}
                ]
            },
            {
                'texte': 'Expliquez brièvement le rôle du Président de la République française :',
                'type': 'texte_long',
                'explication': 'Le Président de la République est le chef de l\'État français. Il nomme le Premier ministre, promulgue les lois, et représente la France à l\'international.',
                'reponse_attendue': 'chef,état,gouvernement,lois,représente,France,pouvoir,exécutif'
            }
        ]
        
        questions_creees = 0
        
        for i, q_data in enumerate(questions_test):
            # Créer la question
            question, created = Question.objects.get_or_create(
                texte=q_data['texte'],
                matiere=matiere_cg,
                lecon=lecon_histoire,
                defaults={
                    'type_question': q_data['type'],
                    'explication': q_data['explication'],
                    'reponse_attendue': q_data.get('reponse_attendue'),
                    'correction_mode': 'exacte' if q_data['type'] in ['texte_court', 'texte_long'] else None,
                    'choix_concours': 'fonction_publique'
                }
            )
            
            if created:
                print(f"Question {i+1} creee: {q_data['texte'][:50]}...")
                questions_creees += 1
                
                # Créer les choix si c'est une question à choix
                if 'choix' in q_data:
                    choix_crees = 0
                    for choix_data in q_data['choix']:
                        Choix.objects.create(
                            question=question,
                            texte=choix_data['texte'],
                            est_correct=choix_data['correct']
                        )
                        choix_crees += 1
                    print(f"  -> {choix_crees} choix crees")
            else:
                print(f"Question {i+1} existe deja")
        
        print("")
        print("=== RESUME ===")
        questions_fp = Question.objects.filter(choix_concours='fonction_publique')
        print(f"Total questions FP: {questions_fp.count()}")
        print(f"Questions creees: {questions_creees}")
        
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    create_fp_test_questions()
