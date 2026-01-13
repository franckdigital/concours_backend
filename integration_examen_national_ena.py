#!/usr/bin/env python3
"""
Script d'intégration des QuestionExamen avec le système d'examen national ENA existant
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import QuestionExamen, ExamenNational, SessionExamen, ParticipationExamen
from django.contrib.auth.models import User

class IntegrationExamenNationalENA:
    """Classe pour intégrer QuestionExamen avec le système d'examen national"""
    
    def __init__(self):
        self.repartition_questions = {
            'culture_aptitude': 60,    # Culture générale + Aptitude verbale
            'logique_combinee': 40,    # Logique + Raisonnement
            'anglais': 30              # Anglais
        }
        self.duree_par_matiere = {
            'culture_aptitude': 60,    # 60 minutes
            'logique_combinee': 60,    # 60 minutes  
            'anglais': 60              # 60 minutes
        }
    
    def verifier_stock_questions(self):
        """Vérifie si on a suffisamment de questions pour créer un examen"""
        print("=== VERIFICATION DU STOCK DE QUESTIONS ===")
        
        stock_suffisant = True
        details_stock = {}
        
        for matiere, quota_requis in self.repartition_questions.items():
            questions_disponibles = QuestionExamen.objects.filter(
                matiere_combinee=matiere,
                active=True,
                validee=True
            ).count()
            
            suffisant = questions_disponibles >= quota_requis
            details_stock[matiere] = {
                'disponibles': questions_disponibles,
                'requis': quota_requis,
                'suffisant': suffisant
            }
            
            matiere_nom = dict(QuestionExamen.MATIERE_COMBINEE_CHOICES)[matiere]
            status = "OK" if suffisant else "INSUFFISANT"
            print(f"  - {matiere_nom}: {questions_disponibles}/{quota_requis} ({status})")
            
            if not suffisant:
                stock_suffisant = False
        
        print(f"\nStock global: {'SUFFISANT' if stock_suffisant else 'INSUFFISANT'}")
        return stock_suffisant, details_stock
    
    def selectionner_questions_examen(self):
        """Sélectionne les questions pour un examen national"""
        print("\n=== SELECTION DES QUESTIONS POUR EXAMEN ===")
        
        questions_selectionnees = {}
        total_questions = 0
        
        for matiere, quota in self.repartition_questions.items():
            questions = list(QuestionExamen.objects.filter(
                matiere_combinee=matiere,
                active=True,
                validee=True
            ).order_by('?')[:quota])  # Sélection aléatoire
            
            questions_selectionnees[matiere] = questions
            total_questions += len(questions)
            
            matiere_nom = dict(QuestionExamen.MATIERE_COMBINEE_CHOICES)[matiere]
            print(f"  - {matiere_nom}: {len(questions)} questions sélectionnées")
        
        print(f"\nTotal questions sélectionnées: {total_questions}")
        return questions_selectionnees
    
    def creer_examen_national_mensuel(self, annee, mois):
        """Crée un examen national pour un mois donné"""
        print(f"\n=== CREATION EXAMEN NATIONAL {mois:02d}/{annee} ===")
        
        # Vérifier le stock
        stock_suffisant, details_stock = self.verifier_stock_questions()
        if not stock_suffisant:
            print("ERREUR: Stock de questions insuffisant!")
            return None
        
        # Sélectionner les questions
        questions_selectionnees = self.selectionner_questions_examen()
        
        # Créer l'examen national
        debut_examen = datetime(annee, mois, 1, 9, 0)  # 1er du mois à 9h
        fin_examen = debut_examen + timedelta(days=30)  # Fin du mois
        
        examen = ExamenNational.objects.create(
            titre=f"Examen National ENA - {mois:02d}/{annee}",
            description=f"Examen national mensuel pour {mois:02d}/{annee}",
            date_debut=debut_examen,
            date_fin=fin_examen,
            duree_totale_minutes=180,  # 3 heures
            
            # Durées par matière (60 minutes chacune)
            temps_culture_aptitude=self.duree_par_matiere['culture_aptitude'],
            temps_logique_combinee=self.duree_par_matiere['logique_combinee'],
            temps_anglais=self.duree_par_matiere['anglais'],
            
            # Débuts des sections (séquentiels)
            debut_culture_aptitude=0,
            debut_logique_combinee=60,
            debut_anglais=120,
            
            terminee=False
        )
        
        # Associer les questions à l'examen
        toutes_questions = []
        for matiere, questions in questions_selectionnees.items():
            toutes_questions.extend(questions)
        
        examen.questions.set(toutes_questions)
        
        print(f"Examen créé: {examen.titre}")
        print(f"  - ID: {examen.id}")
        print(f"  - Questions: {len(toutes_questions)}")
        print(f"  - Durée: {examen.duree_totale_minutes} minutes")
        
        return examen
    
    def corriger_participation_examen(self, participation):
        """Corrige une participation d'examen avec les nouvelles questions"""
        print(f"\n=== CORRECTION PARTICIPATION {participation.id} ===")
        
        score_total = 0
        questions_correctes = 0
        details_correction = {}
        
        # Récupérer les réponses de la participation
        reponses = participation.reponses_detaillees or {}
        
        for question_id, reponse_utilisateur in reponses.items():
            try:
                question = QuestionExamen.objects.get(id=question_id)
                
                # Utiliser la méthode de vérification de QuestionExamen
                est_correcte = question.verifier_reponse(reponse_utilisateur)
                
                if est_correcte:
                    questions_correctes += 1
                    score_total += 1
                
                details_correction[question_id] = {
                    'question': question.texte[:50] + "...",
                    'reponse_utilisateur': reponse_utilisateur,
                    'bonne_reponse': question.bonne_reponse or question.reponse_attendue,
                    'correcte': est_correcte,
                    'explication': question.explication
                }
                
                # Incrémenter le compteur d'utilisation
                question.nombre_utilisations += 1
                question.save()
                
            except QuestionExamen.DoesNotExist:
                print(f"Question {question_id} non trouvée")
                continue
        
        # Calculer le score final
        total_questions = len(reponses)
        score_pourcentage = (score_total / total_questions * 100) if total_questions > 0 else 0
        
        # Mettre à jour la participation
        participation.score = score_pourcentage
        participation.questions_correctes = questions_correctes
        participation.total_questions = total_questions
        participation.details_correction = details_correction
        participation.corrigee = True
        participation.save()
        
        print(f"Correction terminée:")
        print(f"  - Score: {score_pourcentage:.1f}%")
        print(f"  - Questions correctes: {questions_correctes}/{total_questions}")
        
        return participation
    
    def generer_classement_national(self, examen):
        """Génère le classement national pour un examen"""
        print(f"\n=== CLASSEMENT NATIONAL - {examen.titre} ===")
        
        participations = ParticipationExamen.objects.filter(
            examen=examen,
            corrigee=True
        ).order_by('-score', 'temps_total')
        
        classement = []
        for rang, participation in enumerate(participations, 1):
            classement.append({
                'rang': rang,
                'utilisateur': participation.utilisateur.username,
                'score': participation.score,
                'temps_total': participation.temps_total,
                'questions_correctes': participation.questions_correctes,
                'total_questions': participation.total_questions
            })
        
        print(f"Classement généré pour {len(classement)} participants:")
        for i, entry in enumerate(classement[:10]):  # Top 10
            print(f"  {entry['rang']:2d}. {entry['utilisateur']} - {entry['score']:.1f}% ({entry['questions_correctes']}/{entry['total_questions']})")
        
        return classement
    
    def statistiques_questions_utilisees(self):
        """Génère des statistiques sur l'utilisation des questions"""
        print("\n=== STATISTIQUES UTILISATION QUESTIONS ===")
        
        # Questions les plus utilisées
        questions_populaires = QuestionExamen.objects.filter(
            nombre_utilisations__gt=0
        ).order_by('-nombre_utilisations')[:10]
        
        print("Questions les plus utilisées:")
        for q in questions_populaires:
            print(f"  - {q.code_question}: {q.nombre_utilisations} utilisations")
        
        # Répartition par matière
        print("\nUtilisation par matière:")
        for matiere_code, matiere_nom in QuestionExamen.MATIERE_COMBINEE_CHOICES:
            total_utilisations = sum(
                q.nombre_utilisations for q in 
                QuestionExamen.objects.filter(matiere_combinee=matiere_code)
            )
            print(f"  - {matiere_nom}: {total_utilisations} utilisations")
        
        # Questions jamais utilisées
        questions_inutilisees = QuestionExamen.objects.filter(
            nombre_utilisations=0,
            active=True,
            validee=True
        ).count()
        
        print(f"\nQuestions validées non utilisées: {questions_inutilisees}")
    
    def rapport_integration_complete(self):
        """Génère un rapport complet de l'intégration"""
        print("\n" + "="*60)
        print("RAPPORT INTEGRATION QUESTIONEXAMEN - EXAMEN NATIONAL ENA")
        print("="*60)
        
        # Statistiques générales
        total_questions = QuestionExamen.objects.count()
        questions_actives = QuestionExamen.objects.filter(active=True).count()
        questions_validees = QuestionExamen.objects.filter(validee=True).count()
        
        print(f"Total questions: {total_questions}")
        print(f"Questions actives: {questions_actives}")
        print(f"Questions validées: {questions_validees}")
        
        # Stock par matière
        print(f"\nStock par matière:")
        for matiere_code, matiere_nom in QuestionExamen.MATIERE_COMBINEE_CHOICES:
            count = QuestionExamen.objects.filter(
                matiere_combinee=matiere_code,
                active=True,
                validee=True
            ).count()
            requis = self.repartition_questions[matiere_code]
            status = "OK" if count >= requis else "INSUFFISANT"
            print(f"  - {matiere_nom}: {count}/{requis} ({status})")
        
        # Examens nationaux existants
        examens_count = ExamenNational.objects.count()
        examens_actifs = ExamenNational.objects.filter(terminee=False).count()
        
        print(f"\nExamens nationaux:")
        print(f"  - Total: {examens_count}")
        print(f"  - Actifs: {examens_actifs}")
        
        # Participations
        participations_count = ParticipationExamen.objects.count()
        participations_corrigees = ParticipationExamen.objects.filter(corrigee=True).count()
        
        print(f"\nParticipations:")
        print(f"  - Total: {participations_count}")
        print(f"  - Corrigées: {participations_corrigees}")
        
        print("="*60)

def main():
    """Fonction principale d'intégration"""
    print("INTEGRATION QUESTIONEXAMEN AVEC EXAMEN NATIONAL ENA")
    print("="*60)
    
    integration = IntegrationExamenNationalENA()
    
    try:
        # 1. Vérifier le stock de questions
        stock_suffisant, details = integration.verifier_stock_questions()
        
        # 2. Générer des statistiques
        integration.statistiques_questions_utilisees()
        
        # 3. Rapport complet
        integration.rapport_integration_complete()
        
        # 4. Recommandations
        print("\nRECOMMANDATIONS:")
        if not stock_suffisant:
            print("  - Importer plus de questions via Excel pour atteindre les quotas")
            print("  - Valider les questions existantes non validées")
        else:
            print("  - Stock suffisant pour créer des examens nationaux")
            print("  - Système prêt pour la production")
        
        print("\nINTEGRATION TERMINEE AVEC SUCCES!")
        
    except Exception as e:
        print(f"ERREUR lors de l'intégration: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
