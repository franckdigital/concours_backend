"""
Vues pour les évaluations ENA par matière avec gestion des questions uniques
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
import logging

from prepaconcours.models import Matiere, SessionQuiz, Question
from prepaconcours.serializers import SessionQuizSerializer, QuestionSerializer
from .evaluation_manager import get_evaluation_manager

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def evaluation_stats(request):
    """Récupère les statistiques d'évaluation de l'utilisateur"""
    try:
        manager = get_evaluation_manager(request.user)
        stats = manager.get_weekly_evaluation_stats()
        
        return Response({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Erreur récupération stats évaluation: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def matiere_evaluation_stats(request, matiere_id):
    """Récupère les statistiques d'évaluation pour une matière spécifique"""
    try:
        manager = get_evaluation_manager(request.user)
        stats = manager.get_matiere_evaluation_stats(matiere_id)
        
        return Response({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Erreur récupération stats matière {matiere_id}: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_matiere_evaluation(request):
    """Crée une session d'évaluation pour une matière spécifique"""
    try:
        matiere_id = request.data.get('matiere_id')
        nb_questions = request.data.get('nb_questions', 30)
        
        logger.info(f"📝 Création évaluation - Données reçues: matiere_id={matiere_id}, nb_questions={nb_questions}")
        
        if not matiere_id:
            logger.warning("Erreur: matiere_id manquant")
            return Response({
                'success': False,
                'error': 'matiere_id est requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier que la matière existe
        try:
            matiere = get_object_or_404(Matiere, id=matiere_id, choix_concours='ENA')
            logger.info(f"✅ Matière trouvée: {matiere.nom}")
        except Exception as e:
            logger.error(f"Erreur récupération matière {matiere_id}: {e}")
            raise
        
        # Créer la session d'évaluation avec transaction
        try:
            logger.info(f"🔧 Début transaction - Création session pour {matiere.nom}")
            with transaction.atomic():
                manager = get_evaluation_manager(request.user)
                logger.info(f"✅ Manager d'évaluation créé pour utilisateur {request.user.nom_complet}")
                
                session = manager.create_matiere_evaluation_session(
                    matiere_id=matiere_id,
                    nb_questions=nb_questions
                )
                logger.info(f"✅ Session créée avec succès - ID: {session.id}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création de session: {type(e).__name__}: {e}")
            raise
        
        # Sérialiser la réponse
        serializer = SessionQuizSerializer(session)
        
        logger.info(f"Session d'évaluation créée: {session.id} pour matière {matiere.nom}")
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': f'Évaluation {matiere.nom} créée avec {nb_questions} questions uniques'
        })
        
    except ValueError as e:
        logger.warning(f"Erreur validation évaluation: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Erreur création évaluation matière: {e}")
        return Response({
            'success': False,
            'error': 'Erreur interne lors de la création de l\'évaluation'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_questions_count(request, matiere_id):
    """Récupère le nombre de questions disponibles pour une matière"""
    try:
        # 🎲 NOUVEAU SYSTÈME : Plus de filtre sur les questions utilisées
        # Compter directement toutes les questions disponibles pour la matière
        from prepaconcours.models import Question
        
        available_questions = list(Question.objects.filter(
            lecon__matiere_id=matiere_id,
            lecon__matiere__choix_concours='ENA'
        ))
        
        return Response({
            'success': True,
            'data': {
                'matiere_id': matiere_id,
                'available_questions': len(available_questions),
                'used_questions_this_week': len(stats['used_questions']),
                'can_start_evaluation': len(available_questions) >= 30
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur comptage questions matière {matiere_id}: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def matieres_with_evaluation_stats(request):
    """Récupère toutes les matières ENA avec leurs statistiques d'évaluation"""
    try:
        # Récupérer toutes les matières ENA
        matieres = Matiere.objects.filter(choix_concours='ENA')
        manager = get_evaluation_manager(request.user)
        
        matieres_data = []
        for matiere in matieres:
            try:
                stats = manager.get_matiere_evaluation_stats(matiere.id)
                
                matiere_data = {
                    'id': matiere.id,
                    'nom': matiere.nom,
                    'description': getattr(matiere, 'description', ''),
                    'available_questions': stats['available_questions_count'],
                    'can_start_evaluation': stats['can_start_matiere_evaluation'],
                    'total_evaluations': stats['matiere_evaluations_total']
                }
                
                # Ajouter toutes les matières ENA (le filtrage se fait côté frontend)
                matieres_data.append(matiere_data)
                    
            except Exception as e:
                logger.warning(f"Erreur stats pour matière {matiere.nom}: {e}")
                continue
        
        return Response({
            'success': True,
            'data': matieres_data,
            'evaluation_stats': manager.get_weekly_evaluation_stats()
        })
        
    except Exception as e:
        logger.error(f"Erreur récupération matières avec stats: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_weekly_evaluations(request):
    """Reset les évaluations hebdomadaires (pour les tests ou admin)"""
    try:
        # Cette fonction ne devrait être accessible qu'aux admins en production
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': 'Accès non autorisé'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Supprimer les sessions d'évaluation de cette semaine
        manager = get_evaluation_manager(request.user)
        stats = manager.get_weekly_evaluation_stats()
        
        sessions_deleted = SessionQuiz.objects.filter(
            utilisateur=request.user,
            date_debut__date__range=[stats['week_start'], stats['week_end']],
            choix_concours='ENA'
        ).delete()
        
        return Response({
            'success': True,
            'message': f'{sessions_deleted[0]} sessions d\'évaluation supprimées',
            'data': {
                'sessions_deleted': sessions_deleted[0],
                'week_range': [stats['week_start'], stats['week_end']]
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur reset évaluations: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
