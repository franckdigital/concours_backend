"""
Gestionnaire d'évaluations ENA avec gestion des questions uniques et quota hebdomadaire
"""
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from typing import List, Dict, Any
import random
import logging

from prepaconcours.models import Question, SessionQuiz, Tentative, Matiere, Lecon


class EvaluationManager:
    """Gestionnaire pour les évaluations ENA avec questions uniques"""
    
    MAX_EVALUATIONS_PER_WEEK = 50  # Augmenté pour les tests et le développement
    QUESTIONS_PER_EVALUATION = 30  # Maximum 30 questions par évaluation
    QUESTION_TIME_LIMIT = 60  # 1 minute par question
    
    def __init__(self, user: User):
        self.user = user
    
    def get_weekly_evaluation_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques d'évaluation de la semaine courante"""
        # Calculer le début de la semaine (lundi)
        today = timezone.now().date()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)
        
        # Compter les évaluations de cette semaine
        # Note: On utilise un critère différent car type_evaluation n'existe pas
        evaluations_this_week = SessionQuiz.objects.filter(
            utilisateur=self.user,
            date_debut__date__range=[week_start, week_end],
            choix_concours='ENA'
        ).count()
        
        # Plus besoin de tracker les questions utilisées (suppression de l'unicité)
        used_questions = []  # Liste vide car plus de contrainte d'unicité
        
        return {
            'evaluations_this_week': evaluations_this_week,
            'max_evaluations_per_week': self.MAX_EVALUATIONS_PER_WEEK,
            'used_questions': used_questions,
            'can_start_evaluation': evaluations_this_week < self.MAX_EVALUATIONS_PER_WEEK,
            'week_start': week_start,
            'week_end': week_end
        }
    
    def select_unique_questions(self, matiere_id: int, nb_questions: int) -> List[Question]:
        """Sélectionne des questions aléatoirement pour une évaluation par matière"""
        logger.info(f"🎲 Sélection aléatoire de {nb_questions} questions pour la matière {matiere_id}")
        
        # Récupérer uniquement les questions d'évaluation pour cette matière (tri aléatoire simple)
        all_questions = Question.objects.filter(
            lecon__matiere_id=matiere_id,
            lecon__matiere__choix_concours='ENA',
            type_source='evaluation'
        ).order_by('?')  # Ordre aléatoire
        
        total_available = all_questions.count()
        logger.info(f"📊 Total questions disponibles pour matière {matiere_id}: {total_available}")
        
        if total_available == 0:
            logger.warning(f"❌ Aucune question disponible pour la matière {matiere_id}")
            return []
        
        if total_available < nb_questions:
            # Ajuster le nombre de questions au maximum disponible
            nb_questions = total_available
            logger.info(f"⚠️ Nombre de questions ajusté à {nb_questions} (maximum disponible)")
        
        # Sélectionner aléatoirement le nombre de questions demandé
        selected_questions = list(all_questions[:nb_questions])
        logger.info(f"✅ {len(selected_questions)} questions sélectionnées aléatoirement")
        
        return selected_questions
    # Fonction get_available_questions_for_matiere supprimée (première occurrence)
    # Remplacée par le système de sélection aléatoire sans contrainte d'unicité
    
    def select_random_questions(self, matiere_id: int, nb_questions: int = None) -> List[Question]:
        """Sélectionne des questions aléatoirement parmi toutes les questions disponibles (plus d'unicité)"""
        logger = logging.getLogger(__name__)
        
        if nb_questions is None:
            nb_questions = self.QUESTIONS_PER_EVALUATION
        
        logger.info(f"🎲 Sélection aléatoire de {nb_questions} questions pour la matière {matiere_id}")
        
        # Récupérer uniquement les questions d'évaluation pour la matière (sans filtre d'unicité)
        all_questions = list(Question.objects.filter(
            lecon__matiere_id=matiere_id,
            lecon__matiere__choix_concours='ENA',
            type_source='evaluation'
        ).order_by('?'))  # Tri aléatoire au niveau de la base de données
        
        logger.info(f"📚 {len(all_questions)} questions totales disponibles pour la matière")
        
        if len(all_questions) == 0:
            raise ValueError(f"Aucune question disponible pour la matière {matiere_id}")
        
        # Ajuster le nombre de questions si nécessaire
        if len(all_questions) < nb_questions:
            nb_questions = len(all_questions)
            logger.info(f"⚠️ Nombre de questions ajusté à {nb_questions} (maximum disponible)")
        
        # Sélectionner les premières questions du tri aléatoire
        selected_questions = all_questions[:nb_questions]
        logger.info(f"✅ {len(selected_questions)} questions sélectionnées aléatoirement (sans contrainte d'unicité)")
        
        return selected_questions
    
    # Fonction get_available_questions_for_matiere supprimée
    # Plus nécessaire avec le nouveau système de sélection aléatoire
    
    def create_matiere_evaluation_session(self, matiere_id: int, nb_questions: int = None) -> SessionQuiz:
        """Crée une session d'évaluation pour une matière spécifique"""
        logger = logging.getLogger(__name__)
        
        if nb_questions is None:
            nb_questions = self.QUESTIONS_PER_EVALUATION
        
        logger.info(f"🚀 Démarrage création session - Matière: {matiere_id}, Questions: {nb_questions}")
        
        # Vérifier que la matière existe
        try:
            matiere = Matiere.objects.get(id=matiere_id, choix_concours='ENA')
            logger.info(f"✅ Matière validée: {matiere.nom}")
        except Matiere.DoesNotExist:
            logger.error(f"Matière ENA {matiere_id} introuvable")
            raise ValueError(f"Matière ENA {matiere_id} introuvable")
        
        # Sélectionner les questions aléatoirement (plus de contrainte d'unicité)
        try:
            logger.info(f"🎲 Sélection de {nb_questions} questions aléatoires...")
            selected_questions = self.select_random_questions(matiere_id, nb_questions)
            logger.info(f"✅ {len(selected_questions)} questions sélectionnées aléatoirement")
        except Exception as e:
            logger.error(f"Erreur sélection questions: {e}")
            raise
        
        # Trouver la leçon avec le plus de questions pour cette matière
        try:
            logger.info(f"🔍 Recherche de la leçon optimale pour {matiere.nom}...")
            lecon = Lecon.objects.filter(
                matiere=matiere
            ).annotate(
                nb_questions=models.Count('questions')
            ).order_by('-nb_questions').first()
            
            if not lecon:
                logger.error(f"Aucune leçon trouvée pour la matière {matiere.nom}")
                raise ValueError(f"Aucune leçon trouvée pour la matière {matiere.nom}")
            
            logger.info(f"✅ Leçon sélectionnée: {lecon.nom} ({lecon.nb_questions} questions)")
        except Exception as e:
            logger.error(f"Erreur recherche leçon: {e}")
            raise
        
        # Créer la session d'évaluation
        try:
            logger.info(f"📝 Création SessionQuiz pour {self.user.nom_complet}...")
            session = SessionQuiz.objects.create(
                utilisateur=self.user,
                matiere=matiere,
                lecon=lecon,
                nb_questions=nb_questions,
                choix_concours='ENA'
            )
            logger.info(f"✅ SessionQuiz créée - ID: {session.id}")
        except Exception as e:
            logger.error(f"Erreur création SessionQuiz: {e}")
            raise
        
        # Associer les questions sélectionnées à la session
        try:
            logger.info(f"🎯 Association de {len(selected_questions)} questions à la session...")
            session.questions.set(selected_questions)
            logger.info(f"✅ {len(selected_questions)} questions associées avec succès")
        except Exception as e:
            logger.error(f"Erreur association questions: {e}")
            raise
        
        return session
    
    def get_matiere_evaluation_stats(self, matiere_id: int) -> Dict[str, Any]:
        """Récupère les statistiques d'évaluation pour une matière spécifique"""
        stats = self.get_weekly_evaluation_stats()
        
        # 🎲 NOUVEAU SYSTÈME : Compter uniquement les questions d'évaluation (type_source='evaluation')
        available_questions = list(Question.objects.filter(
            lecon__matiere_id=matiere_id,
            lecon__matiere__choix_concours='ENA',
            type_source='evaluation'
        ))
        
        # Compter les évaluations déjà passées pour cette matière
        matiere_evaluations = SessionQuiz.objects.filter(
            utilisateur=self.user,
            matiere_id=matiere_id,
            choix_concours='ENA'
        ).count()
        
        return {
            **stats,
            'available_questions_count': len(available_questions),
            'matiere_evaluations_total': matiere_evaluations,
            'can_start_matiere_evaluation': (
                stats['can_start_evaluation'] and 
                len(available_questions) >= self.QUESTIONS_PER_EVALUATION
            )
        }


def get_evaluation_manager(user: User) -> EvaluationManager:
    """Factory function pour créer un gestionnaire d'évaluation"""
    return EvaluationManager(user)
