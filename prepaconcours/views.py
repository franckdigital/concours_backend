from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from rest_framework import status
import logging

from rest_framework import viewsets

# Configuration du logger
logger = logging.getLogger(__name__)

class DifficulteViewSet(viewsets.ViewSet):
    """Read-only endpoint for listing difficulty levels (niveaux)"""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        # Use Question.NIVEAU_CHOICES
        from .models import Question
        niveaux = [
            {"id": i+1, "name": n[0], "label": n[1]} for i, n in enumerate(Question.NIVEAU_CHOICES)
        ]
        return Response(niveaux)

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from .models import (
    Cycle, Matiere, Utilisateur, Question, Choix,
    Tentative, ReponseTentative, Certificat, ImportExcel, SessionQuiz,
    Lecon, ContenuPedagogique, SessionZoomLive,
    Evaluation, ExamenNational, SessionExamen, ParticipationExamen,
    QuestionExamen, SessionComposition, ReponseComposition
)
from .serializers import (
    CycleSerializer, MatiereSerializer, UtilisateurSerializer,
    QuestionSerializer, QuestionCreateUpdateSerializer, QuestionDetailSerializer, ChoixSerializer,
    TentativeSerializer, ReponseTentativeSerializer, CertificatSerializer, ImportExcelSerializer, SessionQuizSerializer,
    LeconSerializer, ContenuPedagogiqueSerializer, SessionZoomLiveSerializer,
    EvaluationSerializer, ExamenNationalSerializer, ClassementExamenSerializer,
    SessionExamenSerializer, ParticipationExamenSerializer, QuestionExamenSerializer, QuestionExamenDetailSerializer, QuestionExamenPublicSerializer,
    SessionCompositionSerializer, ReponseCompositionSerializer
)

from rest_framework.permissions import AllowAny, IsAdminUser
import random
from django.utils import timezone

# --- Vue API pour /api/profile/ ---
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    
    if request.method == 'GET':
        # Diviser le nom_complet en first_name et last_name pour compatibilité frontend
        nom_complet = getattr(user, "nom_complet", "")
        nom_parts = nom_complet.split(' ', 1) if nom_complet else ['', '']
        
        first_name = nom_parts[0] if len(nom_parts) > 0 else ""
        last_name = nom_parts[1] if len(nom_parts) > 1 else ""
        
        return Response({
            "id": user.id,
            "username": getattr(user, "email", ""),  # Utiliser email comme username
            "email": getattr(user, "email", ""),
            "first_name": first_name,
            "last_name": last_name,
            "nom_complet": nom_complet,
            "telephone": getattr(user, "telephone", ""),
            "cycle_id": getattr(user.cycle, "id", None) if getattr(user, "cycle", None) else None,
            "date_joined": user.date_inscription,
            "last_login": getattr(user, "last_login", None),
            "date_inscription": user.date_inscription,
        })
    
    elif request.method == 'PUT':
        # Mise à jour du profil utilisateur
        try:
            data = request.data
            
            # Reconstituer nom_complet à partir de first_name et last_name
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            
            if first_name or last_name:
                user.nom_complet = f"{first_name} {last_name}".strip()
            
            # Mettre à jour l'email si fourni
            if 'email' in data and data['email']:
                user.email = data['email'].strip()
            
            # Mettre à jour le téléphone si fourni
            if 'telephone' in data:
                user.telephone = data['telephone'].strip() if data['telephone'] else None
            
            user.save()
            
            # Retourner les données mises à jour
            nom_complet = user.nom_complet
            nom_parts = nom_complet.split(' ', 1) if nom_complet else ['', '']
            
            updated_first_name = nom_parts[0] if len(nom_parts) > 0 else ""
            updated_last_name = nom_parts[1] if len(nom_parts) > 1 else ""
            
            return Response({
                "id": user.id,
                "username": user.email,
                "email": user.email,
                "first_name": updated_first_name,
                "last_name": updated_last_name,
                "nom_complet": nom_complet,
                "telephone": user.telephone,
                "cycle_id": getattr(user.cycle, "id", None) if user.cycle else None,
                "date_joined": user.date_inscription,
                "last_login": getattr(user, "last_login", None),
                "date_inscription": user.date_inscription,
            })
            
        except Exception as e:
            return Response(
                {"error": f"Erreur lors de la mise à jour du profil: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    """Endpoint pour récupérer les statistiques dynamiques de l'utilisateur"""
    user = request.user
    
    try:
        # Récupérer toutes les tentatives de l'utilisateur
        tentatives = Tentative.objects.filter(utilisateur=user)
        tentatives_terminees = tentatives.filter(terminee=True)
        
        # Sessions quiz ENA
        sessions_quiz = SessionQuiz.objects.filter(utilisateur=user)
        
        # Calculs des statistiques
        total_quizzes = sessions_quiz.count()
        completed_quizzes = sessions_quiz.filter(
            tentatives__in=tentatives_terminees
        ).distinct().count()
        
        # Score moyen des tentatives terminées
        scores = tentatives_terminees.values_list('score', flat=True)
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Meilleur score
        best_score = max(scores) if scores else 0
        
        # Temps total passé (en secondes)
        total_time = sum(
            tentative.temps_total_en_secondes or 0 
            for tentative in tentatives_terminees
        )
        
        # Matière favorite (la plus jouée)
        matieres_count = {}
        for session in sessions_quiz:
            matiere_nom = session.matiere.nom if session.matiere else 'Inconnue'
            matieres_count[matiere_nom] = matieres_count.get(matiere_nom, 0) + 1
        
        favorite_subject = max(matieres_count, key=matieres_count.get) if matieres_count else 'Aucune'
        
        # Série actuelle (jours consécutifs avec au moins une tentative)
        from datetime import datetime, timedelta
        today = timezone.now().date()
        streak = 0
        current_date = today
        
        while True:
            if tentatives.filter(date_test__date=current_date).exists():
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        # Activité récente (5 dernières tentatives)
        recent_tentatives = tentatives_terminees.order_by('-date_test')[:5]
        recent_activity = []
        
        for tentative in recent_tentatives:
            session = tentative.session  # Utiliser la relation directe
            recent_activity.append({
                'date': tentative.date_test.strftime('%Y-%m-%d'),
                'score': tentative.score or 0,
                'subject': session.matiere.nom if session and session.matiere else 'Quiz général'
            })
        
        stats = {
            'totalQuizzes': total_quizzes,
            'completedQuizzes': completed_quizzes,
            'averageScore': round(average_score, 1),
            'totalTimeSpent': total_time,
            'favoriteSubject': favorite_subject,
            'bestScore': round(best_score, 1),
            'streak': streak,
            'recentActivity': recent_activity
        }
        
        return Response(stats)
        
    except Exception as e:
        logger.error(f'Erreur calcul statistiques utilisateur: {e}')
        return Response(
            {'error': 'Erreur lors du calcul des statistiques'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class SessionQuizViewSet(viewsets.ModelViewSet):
    queryset = SessionQuiz.objects.all()
    serializer_class = SessionQuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logger.info(f"[SESSION QUIZ CREATE] Données reçues: {request.data}")
        logger.info(f"[SESSION QUIZ CREATE] User: {request.user}")
        
        data = request.data.copy()
        choix_concours = data.get('choix_concours')
        if choix_concours == 'fonction_publique':
            data['cycle'] = None
        
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            logger.error(f"[SESSION QUIZ CREATE] Erreurs de validation: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        return qs.filter(utilisateur=user)

    def list(self, request, *args, **kwargs):
        import traceback
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            print('[SESSION QUIZ LIST ERROR]', e)
            print(traceback.format_exc())
            return Response({'detail': str(e), 'traceback': traceback.format_exc()}, status=500)

    def perform_create(self, serializer):
        import traceback
        try:
            user = self.request.user
            matiere = serializer.validated_data.get('matiere')
            lecon = serializer.validated_data.get('lecon')
            nb_questions = serializer.validated_data.get('nb_questions', 10)
            choix_concours = serializer.validated_data.get('choix_concours', 'ENA')
            
            logger.info(f"[SESSION QUIZ] Création session - matiere: {matiere}, lecon: {lecon}, nb_questions: {nb_questions}")
            
            # Pour ENA et FP, on filtre par leçon si spécifiée, sinon par matière
            if lecon:
                questions = list(Question.objects.filter(lecon=lecon))
                filter_desc = f"leçon {lecon.nom}"
                logger.info(f"[SESSION QUIZ] Filtrage par leçon '{lecon.nom}' (id={lecon.id}) - {len(questions)} questions trouvées")
            elif matiere:
                questions = list(Question.objects.filter(matiere=matiere))
                filter_desc = f"matière {matiere.nom}"
                logger.info(f"[SESSION QUIZ] Filtrage par matière '{matiere.nom}' (id={matiere.id}) - {len(questions)} questions trouvées")
            else:
                raise serializers.ValidationError({'detail': "Matière ou leçon requise pour créer une session."})
            
            # Debug: afficher les IDs des questions trouvées
            if questions:
                logger.info(f"[SESSION QUIZ] Questions disponibles: {[q.id for q in questions[:10]]}...")
            else:
                logger.warning(f"[SESSION QUIZ] AUCUNE question trouvée pour {filter_desc}")
                # Vérifier combien de questions existent au total pour cette matière
                if matiere:
                    total_matiere = Question.objects.filter(matiere=matiere).count()
                    logger.warning(f"[SESSION QUIZ] Total questions pour matière {matiere.nom}: {total_matiere}")
                if lecon:
                    total_lecon = Question.objects.filter(lecon=lecon).count()
                    questions_sans_lecon = Question.objects.filter(matiere=lecon.matiere, lecon__isnull=True).count()
                    logger.warning(f"[SESSION QUIZ] Questions avec leçon {lecon.nom}: {total_lecon}, sans leçon: {questions_sans_lecon}")
            
            if len(questions) < nb_questions:
                raise serializers.ValidationError({
                    'nb_questions': f"Pas assez de questions pour {filter_desc}. Disponibles: {len(questions)}, demandées: {nb_questions}"
                })
            
            # Sélectionner aléatoirement les questions
            selected = random.sample(questions, nb_questions)
            instance = serializer.save(utilisateur=user)
            instance.questions.set([q.id for q in selected])
            instance.save()
            
        except Exception as e:
            print('[SESSION QUIZ CREATE ERROR]', e)
            print(traceback.format_exc())
            from rest_framework.response import Response
            from rest_framework import status
            raise serializers.ValidationError({'detail': str(e), 'traceback': traceback.format_exc()})


    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        logger.debug(f"SessionQuizViewSet.questions - User ID: {getattr(request.user, 'id', None)}, SessionQuiz ID: {pk}")
        session = self.get_object()
        logger.debug(f"SessionQuiz found: {session.id} (utilisateur: {getattr(session, 'utilisateur', None)})")
        # Prefetch 'choix' for all questions in the session
        questions = session.questions.all().prefetch_related('choix')
        data = QuestionDetailSerializer(questions, many=True).data
        return Response(data)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        import traceback
        try:
            session = self.get_object()
            if session.statut != 'en_cours':
                return Response({'detail': 'Session déjà terminée ou réinitialisée.'}, status=400)
            reponses = request.data.get('reponses', {})
            corrections = []
            score_total = 0
            for question in session.questions.all():
                rep = reponses.get(str(question.id))
                bonne = False
                explication = question.explication
                # Correction selon le type
                if question.type_question == 'choix_unique':
                    bonne = any(c.est_correct and str(c.id) == str(rep) for c in question.choix.all())
                elif question.type_question == 'choix_multiple':
                    corrects = set(str(c.id) for c in question.choix.filter(est_correct=True))
                    donnes = set(rep or [])
                    bonne = corrects == donnes
                elif question.type_question == 'vrai_faux':
                    bonne = (str(rep).lower() == str(question.reponse_attendue).lower())
                elif question.type_question in ['texte_court', 'texte_long']:
                    if question.correction_mode == 'exacte':
                        bonne = (str(rep).strip().lower() == str(question.reponse_attendue).strip().lower())
                    elif question.correction_mode == 'mot_cle':
                        bonne = str(question.reponse_attendue).strip().lower() in str(rep).strip().lower()
                    elif question.correction_mode == 'regex':
                        import re
                        try:
                            bonne = re.search(str(question.reponse_attendue), str(rep), re.IGNORECASE) is not None
                        except Exception:
                            bonne = False
                corrections.append({
                    'question_id': question.id,
                    'bonne': bonne,
                    'votre_reponse': rep,
                    'explication': explication,
                    'reponse_attendue': question.reponse_attendue,
                    'type_question': question.type_question
                })
                if bonne:
                    score_total += 1
            score = round(100 * score_total / session.nb_questions, 2)
            session.score = score
            session.date_fin = timezone.now()
            session.statut = 'terminee'
            session.save()
            # Création automatique de la tentative
            from .models import Tentative
            Tentative.objects.create(
                utilisateur=session.utilisateur,
                matiere=session.matiere,
                session=session,
                score=session.score,
                date_test=session.date_fin or timezone.now(),
                terminee=True
            )
            return Response({'score': score, 'corrections': corrections})
        except Exception as e:
            return Response({'detail': 'Erreur interne', 'traceback': traceback.format_exc()}, status=500)

    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """
        Soumet une réponse individuelle pour une question dans une session de quiz ENA.
        Format attendu: 
        - Choix multiple: {"question_id": 1019, "reponse_choisie": "C", "temps_reponse": 14}
        - Texte libre: {"question_id": 1019, "reponse_texte": "facile", "temps_reponse": 14}
        """
        import traceback
        print(f'[SUBMIT_ANSWER] ========== REQUÊTE REÇUE ==========')
        print(f'[SUBMIT_ANSWER] Session PK: {pk}')
        print(f'[SUBMIT_ANSWER] Data: {request.data}')
        print(f'[SUBMIT_ANSWER] User: {request.user}')
        try:
            session = self.get_object()
            if session.statut != 'en_cours':
                return Response({'detail': 'Session déjà terminée ou réinitialisée.'}, status=400)
            
            question_id = request.data.get('question_id')
            reponse_choisie = request.data.get('reponse_choisie')  # Lettre A, B, C, D pour choix
            reponse_texte = request.data.get('reponse_texte')      # Texte libre pour questions texte
            temps_reponse = request.data.get('temps_reponse', 0)
            
            if not question_id:
                return Response({'detail': 'question_id est requis.'}, status=400)
            
            # Vérifier que la question fait partie de cette session
            try:
                question = session.questions.get(id=question_id)
            except Question.DoesNotExist:
                return Response({'detail': 'Question invalide pour cette session.'}, status=400)
            
            # Gérer selon le type de question
            if question.type_question in ['texte_court', 'texte_long']:
                # Questions à réponse textuelle libre
                if not reponse_texte:
                    return Response({'detail': 'reponse_texte est requis pour les questions texte.'}, status=400)
                
                # Évaluer la réponse textuelle avec support des réponses multiples
                est_correct = False
                if question.reponse_attendue:
                    # Support des réponses multiples séparées par des virgules
                    reponses_acceptees = [r.strip().lower() for r in question.reponse_attendue.split(',')]
                    reponse_utilisateur = reponse_texte.strip().lower()
                    
                    if question.correction_mode == 'exacte':
                        # Vérifier si la réponse utilisateur correspond à l'une des réponses acceptées
                        est_correct = reponse_utilisateur in reponses_acceptees
                    elif question.correction_mode == 'mot_cle':
                        # Vérifier si l'un des mots-clés est présent dans la réponse
                        est_correct = any(mot_cle in reponse_utilisateur for mot_cle in reponses_acceptees)
                    elif question.correction_mode == 'regex':
                        import re
                        # Tester chaque pattern regex
                        est_correct = any(bool(re.search(pattern, reponse_texte, re.IGNORECASE)) for pattern in reponses_acceptees)
                
                choix_selectionnes = []
                premier_choix = None
                
            else:
                # Questions à choix multiples (A, B, C, D)
                if not reponse_choisie:
                    return Response({'detail': 'reponse_choisie est requis pour les questions à choix.'}, status=400)
                
                # Gérer les réponses simples (A, B, C, D) et multiples (A,B,C)
                reponses_lettres = [r.strip() for r in reponse_choisie.split(',')]
                
                # Valider que toutes les lettres sont valides
                for lettre in reponses_lettres:
                    if lettre not in ['A', 'B', 'C', 'D']:
                        return Response({'detail': f'Réponse invalide: {lettre}. Doit être A, B, C ou D.'}, status=400)
                
                # Récupérer les choix de la question
                choix_list = list(question.choix.all().order_by('id'))
                print(f'[SUBMIT_ANSWER] Question {question.id}, Type: {question.type_question}')
                print(f'[SUBMIT_ANSWER] Choix: {[(i, c.texte[:20] if c.texte else "", c.est_correct) for i, c in enumerate(choix_list)]}')
                print(f'[SUBMIT_ANSWER] Réponse reçue: {reponses_lettres}')
                
                # Convertir les lettres en objets choix
                choix_selectionnes = []
                for lettre in reponses_lettres:
                    choix_index = ord(lettre) - ord('A')  # A=0, B=1, C=2, D=3
                    if choix_index >= len(choix_list):
                        return Response({'detail': f'Choix {lettre} invalide pour cette question.'}, status=400)
                    choix_selectionnes.append(choix_list[choix_index])
                
                # Déterminer si la réponse est correcte
                if question.type_question == 'choix_multiple':
                    # 🚀 OPTIMISATION: Éviter choix_list.index() coûteux (O(n²) → O(n))
                    # Créer directement les indices des bonnes réponses
                    choix_corrects_indices = {i for i, c in enumerate(choix_list) if c.est_correct}
                    reponses_indices = {ord(lettre) - ord('A') for lettre in reponses_lettres}
                    est_correct = choix_corrects_indices == reponses_indices
                    print(f'[SUBMIT_ANSWER] Multiple: corrects={choix_corrects_indices}, réponse={reponses_indices}, est_correct={est_correct}')
                else:
                    # Pour les choix uniques, vérifier le premier choix sélectionné
                    choix_selectionne = choix_selectionnes[0]
                    est_correct = choix_selectionne.est_correct
                    print(f'[SUBMIT_ANSWER] Unique: choix={choix_selectionne.texte[:20] if choix_selectionne.texte else ""}, est_correct={est_correct}')
                
                print(f'[SUBMIT_ANSWER] ====> RÉSULTAT: est_correct={est_correct}')
                premier_choix = choix_selectionnes[0] if choix_selectionnes else None
            
            # Trouver ou créer une Tentative pour cette SessionQuiz
            from .models import Tentative, ReponseTentative
            tentative, created = Tentative.objects.get_or_create(
                utilisateur=session.utilisateur,
                session=session,
                defaults={
                    'matiere': session.matiere,
                    'cycle': session.cycle,
                    'choix_concours': session.choix_concours,
                    'terminee': False
                }
            )
            
            # Créer ou mettre à jour la réponse (pour éviter les doublons)
            reponse, created = ReponseTentative.objects.get_or_create(
                tentative=tentative,
                question=question,
                defaults={
                    'choix': premier_choix,
                    'texte_reponse': reponse_texte if question.type_question in ['texte_court', 'texte_long'] else None,
                    'est_correct': est_correct,
                    'temps_question_en_secondes': temps_reponse
                }
            )
            
            if not created:
                # Mettre à jour si déjà existante
                reponse.choix = premier_choix
                reponse.texte_reponse = reponse_texte if question.type_question in ['texte_court', 'texte_long'] else None
                reponse.est_correct = est_correct
                reponse.temps_question_en_secondes = temps_reponse
                reponse.save()
            
            # Préparer la réponse selon le type de question
            response_data = {
                'success': True,
                'est_correct': est_correct,
                'explication': question.explication,
            }
            
            # Ajouter choix_correct seulement pour les questions à choix
            if question.type_question in ['choix_unique', 'choix_multiple', 'vrai_faux']:
                choix_list = list(question.choix.all().order_by('id'))
                response_data['choix_correct'] = next((i for i, c in enumerate(choix_list) if c.est_correct), None)
            
            return Response(response_data)
            
        except Exception as e:
            print(f'[SUBMIT_ANSWER ERROR] {e}')
            print(traceback.format_exc())
            return Response({'detail': 'Erreur interne', 'traceback': traceback.format_exc()}, status=500)

    @action(detail=True, methods=['post'])
    def reinit(self, request, pk=None):
        session = self.get_object()
        if session.statut == 'en_cours':
            session.statut = 'reinitialisee'
            session.date_fin = timezone.now()
           # Réinitialiser la session
        new_session = SessionQuiz.objects.create(
            utilisateur=session.utilisateur,
            cycle=session.cycle,
            choix_concours=session.choix_concours,
            matiere=session.matiere,
            lecon=session.lecon,
            nb_questions=session.nb_questions
        )
        
        # Copier les questions de l'ancienne session
        new_session.questions.set(session.questions.all())
        new_session.save()
        serializer = self.get_serializer(new_session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='finish')
    def finish_quiz(self, request, pk=None):
        """
        Termine un quiz : marque la tentative comme terminée, calcule le score final
        et met à jour le statut de la session.
        """
        session = self.get_object()
        
        try:
            # Récupérer la tentative associée à cette session
            from .models import Tentative, ReponseTentative
            tentative = Tentative.objects.filter(session=session, utilisateur=request.user).first()
            
            if not tentative:
                return Response(
                    {'detail': 'Aucune tentative trouvée pour cette session.'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if tentative.terminee:
                return Response(
                    {'detail': 'Cette tentative est déjà terminée.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculer le score final
            reponses = ReponseTentative.objects.filter(tentative=tentative)
            total_questions = reponses.count()
            bonnes_reponses = reponses.filter(est_correct=True).count()
            
            if total_questions > 0:
                score_final = (bonnes_reponses / total_questions) * 100
            else:
                score_final = 0
            
            # Calculer le temps total (somme des temps par question)
            temps_total = sum(
                reponse.temps_question_en_secondes or 0 
                for reponse in reponses
            )
            
            # Marquer la tentative comme terminée
            tentative.terminee = True
            tentative.score = score_final
            tentative.temps_total_en_secondes = temps_total
            tentative.save()
            
            # Mettre à jour la session
            session.statut = 'terminee'
            session.score = score_final
            session.date_fin = timezone.now()
            session.save()
            
            return Response({
                'success': True,
                'score_final': score_final,
                'bonnes_reponses': bonnes_reponses,
                'total_questions': total_questions,
                'temps_total': temps_total,
                'message': 'Quiz terminé avec succès !'
            })
            
        except Exception as e:
            logger.error(f'Erreur lors de la finalisation du quiz: {e}')
            return Response(
                {'detail': 'Erreur lors de la finalisation du quiz.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def reinit(self, request, pk=None):
        session = self.get_object()
        if session.statut == 'en_cours':
            session.statut = 'reinitialisee'
            session.date_fin = timezone.now()
           # Réinitialiser la session
        new_session = SessionQuiz.objects.create(
            utilisateur=session.utilisateur,
            cycle=session.cycle,
            choix_concours=session.choix_concours,
            matiere=session.matiere,
            lecon=session.lecon,
            nb_questions=session.nb_questions
        )
        
        # Copier les questions de l'ancienne session
        new_session.questions.set(session.questions.all())
        new_session.save()
        serializer = self.get_serializer(new_session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='finish')
    def finish_quiz(self, request, pk=None):
        """
        Termine un quiz : marque la tentative comme terminée, calcule le score final
        et met à jour le statut de la session.
        """
        session = self.get_object()
        
        try:
            # Récupérer la tentative associée à cette session
            from .models import Tentative, ReponseTentative
            tentative = Tentative.objects.filter(session=session, utilisateur=request.user).first()
            
            if not tentative:
                return Response(
                    {'detail': 'Aucune tentative trouvée pour cette session.'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if tentative.terminee:
                return Response(
                    {'detail': 'Cette tentative est déjà terminée.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculer le score final
            reponses = ReponseTentative.objects.filter(tentative=tentative)
            total_questions = reponses.count()
            bonnes_reponses = reponses.filter(est_correct=True).count()
            
            if total_questions > 0:
                score_final = (bonnes_reponses / total_questions) * 100
            else:
                score_final = 0
            
            # Calculer le temps total (somme des temps par question)
            temps_total = sum(
                reponse.temps_question_en_secondes or 0 
                for reponse in reponses
            )
            
            # Marquer la tentative comme terminée
            tentative.terminee = True
            tentative.score = score_final
            tentative.temps_total_en_secondes = temps_total
            tentative.save()
            
            # Mettre à jour la session
            session.statut = 'terminee'
            session.score = score_final
            session.date_fin = timezone.now()
            session.save()
            
            return Response({
                'success': True,
                'score_final': score_final,
                'bonnes_reponses': bonnes_reponses,
                'total_questions': total_questions,
                'temps_total': temps_total,
                'message': 'Quiz terminé avec succès !'
            })
            
        except Exception as e:
            logger.error(f'Erreur lors de la finalisation du quiz: {e}')
            return Response(
                {'detail': 'Erreur lors de la finalisation du quiz.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='corrections')
    def corrections(self, request, pk=None):
        """
        Retourne les corrections détaillées d'une session de quiz terminée.
        Format de réponse compatible avec le frontend CorrectionsQuizENA.
        """
        session = self.get_object()
        
        try:
            # Vérifier que la session est terminée
            if session.statut != 'terminee':
                return Response(
                    {'detail': 'Cette session n\'est pas encore terminée.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Récupérer la tentative associée à cette session
            from .models import Tentative, ReponseTentative
            tentative = Tentative.objects.filter(session=session, utilisateur=request.user).first()
            
            if not tentative:
                return Response(
                    {'detail': 'Aucune tentative trouvée pour cette session.'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Récupérer toutes les questions de la session ET leurs réponses
            questions_session = session.questions.all().order_by('id')
            
            corrections_data = []
            
            for question in questions_session:
                # Chercher la réponse pour cette question
                reponse = ReponseTentative.objects.filter(
                    tentative=tentative, 
                    question=question
                ).select_related('choix').first()
                
                # Préparer les choix pour les questions à choix multiples
                choix_list = []
                if question.type_question in ['choix_unique', 'choix_multiple', 'vrai_faux']:
                    for choix in question.choix.all().order_by('id'):
                        choix_list.append({
                            'lettre': chr(65 + len(choix_list)),  # A, B, C, D...
                            'texte': choix.texte
                        })
                
                # Déterminer la réponse correcte
                reponse_correcte = None
                if question.type_question in ['choix_unique', 'choix_multiple', 'vrai_faux']:
                    # Pour les questions à choix, trouver la lettre du bon choix
                    choix_correct = question.choix.filter(est_correct=True).first()
                    if choix_correct:
                        choix_index = list(question.choix.all().order_by('id')).index(choix_correct)
                        reponse_correcte = chr(65 + choix_index)  # A, B, C, D...
                else:
                    # Pour les questions texte, utiliser la réponse attendue
                    reponse_correcte = question.reponse_attendue or "Réponse libre"
                
                # Déterminer la réponse de l'utilisateur
                user_answer = None
                is_correct = False
                
                if reponse:
                    if reponse.choix:
                        # Pour les réponses à choix
                        choix_index = list(question.choix.all().order_by('id')).index(reponse.choix)
                        user_answer = chr(65 + choix_index)  # A, B, C, D...
                    elif reponse.texte_reponse:
                        # Pour les réponses texte
                        user_answer = reponse.texte_reponse
                    else:
                        user_answer = "Pas de réponse"
                    
                    is_correct = reponse.est_correct or False
                else:
                    # Aucune réponse donnée pour cette question
                    user_answer = "Pas de réponse"
                    is_correct = False
                
                # Construire l'objet correction
                correction_item = {
                    'question_id': question.id,
                    'question_text': question.texte,
                    'type_question': question.type_question,
                    'choix': choix_list,
                    'reponse_correcte': reponse_correcte,
                    'user_answer': user_answer,
                    'is_correct': is_correct,
                    'explication': question.explication or 'Pas d\'explication disponible.'
                }
                
                corrections_data.append(correction_item)
            
            # Logs pour debug
            logger.info(f'✅ [CORRECTIONS BACKEND] Session {pk}: {len(corrections_data)} corrections générées')
            logger.info(f'✅ [CORRECTIONS BACKEND] Première correction: {corrections_data[0] if corrections_data else "Aucune"}')
            
            return Response(corrections_data)
            
        except Exception as e:
            logger.error(f'❌ [CORRECTIONS BACKEND] Erreur lors de la récupération des corrections: {e}')
            return Response(
                {'detail': f'Erreur lors de la récupération des corrections: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CycleViewSet(viewsets.ModelViewSet):
    queryset = Cycle.objects.all()
    serializer_class = CycleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [permissions.IsAuthenticated()]

class MatiereViewSet(viewsets.ModelViewSet):
    queryset = Matiere.objects.all()
    serializer_class = MatiereSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        cycle_id = self.request.query_params.get('cycle')
        if cycle_id:
            qs = qs.filter(cycle_id=cycle_id)
        return qs

    @action(detail=False, methods=['get'], url_path='second-tour')
    def second_tour_matieres(self, request):
        """Récupère les matières du second tour ENA par cycle"""
        cycle_id = request.query_params.get('cycle')
        if not cycle_id:
            return Response({'detail': 'Le paramètre cycle est requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        matieres = Matiere.objects.filter(
            choix_concours='ENA',
            tour_ena='second_tour',
            cycle_id=cycle_id
        )
        serializer = self.get_serializer(matieres, many=True)
        return Response(serializer.data)

from rest_framework.decorators import action

class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [permissions.IsAdminUser()]

    @action(detail=True, methods=['post'], url_path='activer_desactiver')
    def activer_desactiver(self, request, pk=None):
        user = self.get_object()
        is_active = request.data.get('is_active')
        if is_active is None:
            return Response({'detail': 'Le champ is_active est requis.'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = bool(is_active)
        user.save(update_fields=['is_active'])
        return Response({'detail': f"Utilisateur {'activé' if user.is_active else 'désactivé'}.", 'is_active': user.is_active})


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().prefetch_related('choix')
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'detail':
            return QuestionDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return QuestionCreateUpdateSerializer
        return QuestionSerializer
        
    @action(detail=True, methods=['get'], url_path='detail')
    def question_detail(self, request, pk=None):
        """
        Vue détaillée d'une question avec ses choix (propositions).
        """
        try:
            print(f"Récupération de la question avec l'ID: {pk}")
            question = self.get_object()
            print(f"Question récupérée: {question}")
            serializer = self.get_serializer(question)
            print(f"Données sérialisées: {serializer.data}")
            return Response(serializer.data)
        except Exception as e:
            print(f"Erreur dans la vue détail: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"Erreur lors de la récupération de la question: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ChoixViewSet(viewsets.ModelViewSet):
    queryset = Choix.objects.all()
    serializer_class = ChoixSerializer
    permission_classes = [permissions.IsAuthenticated]

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from django.template.loader import render_to_string
from django.http import HttpResponse
import io
from reportlab.pdfgen import canvas

class TentativeViewSet(viewsets.ModelViewSet):
    queryset = Tentative.objects.all()
    serializer_class = TentativeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        choix_concours = data.get('choix_concours')
        if choix_concours == 'fonction_publique':
            data['cycle'] = None
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or getattr(user, 'is_admin', False):
            return Tentative.objects.all()
        return Tentative.objects.filter(utilisateur=user)

    def perform_create(self, serializer):
        # Lier automatiquement la session quiz si elle est passée dans les données
        session = serializer.validated_data.get('session', None)
        serializer.save(utilisateur=self.request.user, session=session)
    @action(detail=False, methods=['get'], url_path='stats_par_cycle')
    def stats_par_cycle(self, request):
        """
        Retourne les stats (nb tentatives, score moyen, score total, taux de réussite) par utilisateur pour chaque cycle.
        """
        from django.db.models import Avg, Sum
        result = []
        cycles = Cycle.objects.all()
        for cycle in cycles:
            cycle_data = {
                'cycle_id': cycle.id,
                'cycle_nom': cycle.nom,
                'utilisateurs': []
            }
            # Sélectionner tous les utilisateurs qui ont au moins une tentative terminée pour ce cycle
            tentatives_cycle = Tentative.objects.filter(session__cycle=cycle, terminee=True)
            utilisateurs_ids = tentatives_cycle.values_list('utilisateur', flat=True).distinct()
            for user_id in utilisateurs_ids:
                user = Utilisateur.objects.get(id=user_id)
                tentatives = tentatives_cycle.filter(utilisateur=user)
                nb_tentatives = tentatives.count()
                score_moyen = round(tentatives.aggregate(avg=Avg('score'))['avg'] or 0, 2)
                score_total = tentatives.aggregate(total=Sum('score'))['total'] or 0
                # Taux de réussite proportionnel au score moyen (score_moyen = taux_reussite)
                taux_reussite = round(score_moyen, 2)
                cycle_data['utilisateurs'].append({
                    'id': user.id,
                    'nom_complet': user.nom_complet,
                    'email': user.email,
                    'nb_tentatives': nb_tentatives,
                    'score_moyen': score_moyen,
                    'score_total': score_total,
                    'taux_reussite': taux_reussite
                })
            result.append(cycle_data)
        return Response(result)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Statistiques globales et utilisateur sur les QCM : score moyen, taux de réussite, nombre de tentatives.
        """
        user = request.user
        stats = {}
        # Global
        tentatives_all = Tentative.objects.filter(terminee=True)
        stats['global'] = {
            'nb_tentatives': tentatives_all.count(),
            'score_moyen': round(tentatives_all.aggregate(models.Avg('score'))['score__avg'] or 0, 2),
            'taux_reussite': round(100 * tentatives_all.filter(score__gte=50).count() / tentatives_all.count(), 2) if tentatives_all.exists() else 0.0
        }
        # Utilisateur
        if user.is_authenticated:
            tentatives_user = Tentative.objects.filter(utilisateur=user, terminee=True)
            stats['utilisateur'] = {
                'nb_tentatives': tentatives_user.count(),
                'score_moyen': round(tentatives_user.aggregate(models.Avg('score'))['score__avg'] or 0, 2),
                'taux_reussite': round(100 * tentatives_user.filter(score__gte=50).count() / tentatives_user.count(), 2) if tentatives_user.exists() else 0.0
            }
        return Response(stats)

    @action(detail=True, methods=['get'], url_path='generate_certificate')
    def generate_certificate(self, request, pk=None):
        """
        Génère un certificat PDF pour une tentative terminée et réussie (score >= 50%).
        """
        tentative = self.get_object()
        user = request.user
        if tentative.utilisateur != user and not user.est_admin:
            return Response({'detail': 'Accès refusé.'}, status=status.HTTP_403_FORBIDDEN)
        if not tentative.terminee:
            return Response({'detail': 'La tentative n\'est pas terminée.'}, status=status.HTTP_400_BAD_REQUEST)
        if tentative.score is None or tentative.score < 50:
            return Response({'detail': 'Score insuffisant pour obtenir un certificat.'}, status=status.HTTP_403_FORBIDDEN)
        # Générer un PDF simple
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica-Bold", 20)
        p.drawString(100, 750, "Certificat de Réussite")
        p.setFont("Helvetica", 14)
        p.drawString(100, 700, f"Décerné à : {tentative.utilisateur.email}")
        p.drawString(100, 670, f"QCM ID : {tentative.qcm_id}")
        p.drawString(100, 640, f"Score : {tentative.score:.2f} %")
        p.drawString(100, 610, f"Date : {tentative.date_fin.strftime('%d/%m/%Y') if tentative.date_fin else ''}")
        p.showPage()
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=certificat_{tentative.id}.pdf'
        return response

    @action(detail=False, methods=['get'], url_path='export_attempts')
    def export_attempts(self, request):
        """
        Exporter les tentatives terminées au format CSV (admin ou propriétaire).
        """
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Authentification requise.'}, status=status.HTTP_401_UNAUTHORIZED)
        if user.is_admin:
            tentatives = Tentative.objects.filter(terminee=True)
        else:
            tentatives = Tentative.objects.filter(utilisateur=user, terminee=True)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tentatives.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Utilisateur', 'QCM', 'Score', 'Date début', 'Date fin'])
        for t in tentatives:
            writer.writerow([
                t.id,
                t.utilisateur.email,
                t.qcm_id,
                t.score,
                t.date_debut,
                t.date_fin
            ])
        return response
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='start_attempt')
    def start_attempt(self, request):
        """
        Crée une nouvelle tentative pour l’utilisateur connecté et le QCM (questionnaire) spécifié.
        Copie la durée limite du QCM sur la tentative.
        """
        qcm_id = request.data.get('qcm_id')
        if not qcm_id:
            return Response({'detail': 'qcm_id requis.'}, status=status.HTTP_400_BAD_REQUEST)
        from .models import Question
        try:
            questions = Question.objects.filter(qcm_id=qcm_id)
            if not questions.exists():
                return Response({'detail': 'QCM introuvable ou vide.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'detail': 'Erreur lors de la récupération du QCM.'}, status=status.HTTP_400_BAD_REQUEST)
        # Optionnel : vérifier qu’il n’y a pas déjà une tentative non terminée pour ce QCM
        existing = Tentative.objects.filter(utilisateur=request.user, qcm_id=qcm_id, terminee=False)
        if existing.exists():
            return Response({'detail': 'Vous avez déjà une tentative en cours pour ce QCM.', 'tentative_id': existing.first().id}, status=status.HTTP_409_CONFLICT)
        # Copie du temps_limite du QCM (on prend la valeur sur la première question du QCM)
        temps_limite = questions.first().temps_limite if questions.first() else None
        from django.utils import timezone
        tentative = Tentative.objects.create(utilisateur=request.user, qcm_id=qcm_id, temps_limite=temps_limite)
        temps_restant = None
        if temps_limite:
            temps_restant = int(temps_limite * 60)
        return Response({'detail': 'Tentative créée.', 'tentative_id': tentative.id, 'temps_limite': temps_limite, 'temps_restant': temps_restant}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='submit_response')
    def submit_response(self, request, pk=None):
        """
        Soumettre une réponse à une question pour une tentative donnée (pk = tentative.id).
        Gère les types : choix unique, choix multiple, vrai/faux, texte court, texte long.
        Correction automatique uniquement pour les types à choix.
        """
        from .models import ReponseTentative, Question, Choix
        from django.utils import timezone
        tentative = self.get_object()
        if tentative.utilisateur != request.user:
            return Response({'detail': 'Accès interdit à cette tentative.'}, status=status.HTTP_403_FORBIDDEN)
        if tentative.terminee:
            return Response({'detail': 'Cette tentative est déjà terminée.'}, status=status.HTTP_400_BAD_REQUEST)
        # Contrôle du timer
        if tentative.temps_limite:
            elapsed = (timezone.now() - tentative.date_debut).total_seconds() / 60
            temps_restant = int(max(0, tentative.temps_limite * 60 - (timezone.now() - tentative.date_debut).total_seconds()))
            if elapsed > tentative.temps_limite:
                tentative.terminee = True
                tentative.date_fin = timezone.now()
                tentative.save(update_fields=['terminee', 'date_fin'])
                return Response({'detail': 'Temps écoulé. La tentative est terminée.', 'temps_restant': 0}, status=status.HTTP_403_FORBIDDEN)
        else:
            temps_restant = None
        question_id = request.data.get('question_id')
        if not question_id:
            return Response({'detail': 'question_id est requis.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            question = Question.objects.get(id=question_id, qcm_id=tentative.qcm_id)
        except Question.DoesNotExist:
            return Response({'detail': 'Question invalide pour ce QCM.'}, status=status.HTTP_400_BAD_REQUEST)
        # Vérifier que l’utilisateur n’a pas déjà répondu à cette question dans cette tentative
        if ReponseTentative.objects.filter(tentative=tentative, question_id=question_id).exists():
            return Response({'detail': 'Vous avez déjà répondu à cette question.'}, status=status.HTTP_409_CONFLICT)
        type_q = question.type_question
        # Gestion des types
        if type_q in ["choix_unique", "vrai_faux"]:
            choix_id = request.data.get('choix_id')
            if not choix_id:
                return Response({'detail': 'choix_id requis.'}, status=status.HTTP_400_BAD_REQUEST)
            # Vérifier que le choix fait partie des choix de la question
            if not Choix.objects.filter(id=choix_id, question_id=question_id).exists():
                return Response({'detail': 'Choix invalide pour cette question.'}, status=status.HTTP_400_BAD_REQUEST)
            # Correction automatique
            est_correct = Choix.objects.filter(id=choix_id, question_id=question_id, est_correct=True).exists()
            reponse = ReponseTentative.objects.create(
                tentative=tentative,
                question=question,
                choix_id=choix_id,
                est_correct=est_correct
            )
        elif type_q == "choix_multiple":
            choix_ids = request.data.get('choix_ids')
            if not isinstance(choix_ids, list) or not choix_ids:
                return Response({'detail': 'choix_ids (liste) requis.'}, status=status.HTTP_400_BAD_REQUEST)
            # Vérifier que tous les choix font partie de la question
            valides = list(Choix.objects.filter(id__in=choix_ids, question_id=question_id).values_list('id', flat=True))
            if set(valides) != set(choix_ids):
                return Response({'detail': 'Un ou plusieurs choix invalides.'}, status=status.HTTP_400_BAD_REQUEST)
            # Correction automatique : tous les bons choix doivent être sélectionnés, aucun mauvais
            bons = set(Choix.objects.filter(question_id=question_id, est_correct=True).values_list('id', flat=True))
            est_correct = set(choix_ids) == bons and len(bons) > 0
            # On crée une réponse pour chaque choix sélectionné
            for cid in choix_ids:
                ReponseTentative.objects.create(
                    tentative=tentative,
                    question=question,
                    choix_id=cid,
                    est_correct=est_correct if cid in bons else False
                )
            return Response({'detail': 'Réponses enregistrées.', 'est_correct': est_correct, 'temps_restant': temps_restant}, status=status.HTTP_201_CREATED)
        elif type_q in ["texte_court", "texte_long"]:
            texte = request.data.get('texte_reponse')
            if not texte:
                return Response({'detail': 'texte_reponse requis.'}, status=status.HTTP_400_BAD_REQUEST)
            # Correction automatique selon le mode choisi
            est_correct = None
            if question.reponse_attendue:
                mode = question.correction_mode or 'exacte'
                attendue = question.reponse_attendue.strip()
                reponse_util = texte.strip()
                if mode == 'exacte':
                    est_correct = reponse_util.lower() == attendue.lower()
                elif mode == 'mot_cle':
                    mots_cles = [m.strip().lower() for m in attendue.split(',') if m.strip()]
                    est_correct = any(m in reponse_util.lower() for m in mots_cles)
                elif mode == 'regex':
                    import re
                    try:
                        est_correct = bool(re.search(attendue, reponse_util, re.IGNORECASE))
                    except re.error:
                        est_correct = None  # Regex mal formée
            reponse = ReponseTentative.objects.create(
                tentative=tentative,
                question=question,
                texte_reponse=texte,
                est_correct=est_correct
            )
        else:
            return Response({'detail': 'Type de question non supporté.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Réponse enregistrée.', 'reponse_id': reponse.id, 'temps_restant': temps_restant}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='finish_attempt')
    def finish_attempt(self, request, pk=None):
        """
        Termine la tentative, calcule le score et empêche toute modification ultérieure.
        Bloque l'action si le temps est écoulé.
        """
        from .models import ReponseTentative, Choix, Question
        from django.utils import timezone
        tentative = self.get_object()
        if tentative.utilisateur != request.user:
            return Response({'detail': 'Accès interdit à cette tentative.'}, status=status.HTTP_403_FORBIDDEN)
        if tentative.terminee:
            return Response({'detail': 'Cette tentative est déjà terminée.'}, status=status.HTTP_400_BAD_REQUEST)
        # Contrôle du timer
        if tentative.temps_limite:
            elapsed = (timezone.now() - tentative.date_debut).total_seconds() / 60
            if elapsed > tentative.temps_limite:
                tentative.terminee = True
                tentative.date_fin = timezone.now()
                tentative.save(update_fields=['terminee', 'date_fin'])
                return Response({'detail': 'Temps écoulé. La tentative est terminée.'}, status=status.HTTP_403_FORBIDDEN)
        # Récupérer toutes les questions du QCM
        questions = Question.objects.filter(qcm_id=tentative.qcm_id)
        total = questions.count()
        if total == 0:
            return Response({'detail': 'Ce QCM ne contient aucune question.'}, status=status.HTTP_400_BAD_REQUEST)
        # Calcul du score
        bonnes_reponses = 0
        for question in questions:
            reponse = ReponseTentative.objects.filter(tentative=tentative, question=question).first()
            if reponse and Choix.objects.filter(id=reponse.choix_id, question=question, est_correct=True).exists():
                bonnes_reponses += 1
        score = bonnes_reponses / total * 100
        # Marquer la tentative comme terminée
        tentative.terminee = True
        tentative.score = score
        tentative.date_fin = timezone.now()
        tentative.save(update_fields=['terminee', 'score', 'date_fin'])
        return Response({'detail': 'Tentative terminée.', 'score': score, 'bonnes_reponses': bonnes_reponses, 'total_questions': total, 'temps_restant': temps_restant}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='result')
    def result(self, request, pk=None):
        """
        Retourne les résultats et corrections pour une tentative terminée.
        Pagination possible via ?page (DRF) et navigation question par question via ?question_id ou ?index.
        """
        from .models import ReponseTentative, Choix, Question
        tentative = self.get_object()
        if tentative.utilisateur != request.user:
            return Response({'detail': 'Accès interdit à cette tentative.'}, status=status.HTTP_403_FORBIDDEN)
        if not tentative.terminee:
            return Response({'detail': 'La tentative n\'est pas encore terminée.'}, status=status.HTTP_400_BAD_REQUEST)
        questions = Question.objects.filter(qcm_id=tentative.qcm_id).order_by('id')
        # Navigation question par question
        question_id = request.GET.get('question_id')
        index = request.GET.get('index')
        if question_id:
            questions = questions.filter(id=question_id)
        elif index is not None:
            try:
                idx = int(index)
                questions = questions[idx:idx+1]
            except Exception:
                return Response({'detail': 'Index invalide.'}, status=status.HTTP_400_BAD_REQUEST)
        # Pagination DRF
        page = self.paginate_queryset(questions)
        if page is not None:
            questions = page
        result = []
        for question in questions:
            choix_possibles = list(Choix.objects.filter(question=question).values('id', 'texte', 'est_correct'))
            reponse = ReponseTentative.objects.filter(tentative=tentative, question=question).first()
            user_choix_id = reponse.choix_id if reponse else None
            est_correct = None
            if reponse:
                est_correct = Choix.objects.filter(id=user_choix_id, question=question, est_correct=True).exists()
            result.append({
                'question_id': question.id,
                'texte': question.texte,
                'choix': choix_possibles,
                'user_choix_id': user_choix_id,
                'est_correct': est_correct
            })
        # Calcul du temps restant
        from django.utils import timezone
        if tentative.temps_limite:
            temps_restant = int(max(0, tentative.temps_limite * 60 - (timezone.now() - tentative.date_debut).total_seconds()))
        else:
            temps_restant = None
        data = {
            'score': tentative.score,
            'resultats': result,
            'total_questions': Question.objects.filter(qcm_id=tentative.qcm_id).count(),
            'temps_restant': temps_restant
        }
        if page is not None:
            return self.get_paginated_response(data)
        return Response(data, status=status.HTTP_200_OK)

class ReponseTentativeViewSet(viewsets.ModelViewSet):
    queryset = ReponseTentative.objects.all()
    serializer_class = ReponseTentativeSerializer
    permission_classes = [permissions.IsAuthenticated]

class CertificatViewSet(viewsets.ModelViewSet):
    queryset = Certificat.objects.all()
    serializer_class = CertificatSerializer
    permission_classes = [permissions.IsAdminUser]

class ImportExcelViewSet(viewsets.ModelViewSet):
    queryset = ImportExcel.objects.all()
    serializer_class = ImportExcelSerializer
    permission_classes = [permissions.IsAdminUser]
    
    from django.db import transaction
    
    @action(detail=False, methods=['post'], url_path='preview')
    def preview(self, request, *args, **kwargs):
        import sys
        print("[IMPORTS PREVIEW] Vue appelée", file=sys.stderr)
        print(f"[IMPORTS PREVIEW] Méthode: {request.method}", file=sys.stderr)
        print(f"[IMPORTS PREVIEW] Headers: {request.headers}", file=sys.stderr)
        print(f"[IMPORTS PREVIEW] Fichiers reçus: {request.FILES}", file=sys.stderr)
        return self.create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        from django.db.models import Count, F, Value, CharField
        from django.db.models.functions import Concat
        
        # Récupérer les imports avec les informations utilisateur
        imports = ImportExcel.objects.select_related('utilisateur').order_by('-date_import')
        
        # Pagination
        page = self.paginate_queryset(imports)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(imports, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        import sys
        print("[IMPORTS CREATE] Vue appelée", file=sys.stderr)
        from django.utils import timezone
        import pandas as pd
        from io import BytesIO
        import json
        
        print("\n=== DÉBUT IMPORT EXCEL ===", file=sys.stderr)
        print(f"Méthode: {request.method}", file=sys.stderr)
        print(f"Headers: {request.headers}", file=sys.stderr)
        print(f"Fichiers reçus: {request.FILES}", file=sys.stderr)
        
        # Vérifier si un fichier a été fourni
        if 'file' not in request.FILES:
            print("!!! ERREUR: Aucun fichier fourni", file=sys.stderr)
            return Response(
                {'detail': 'Aucun fichier fourni'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        file = request.FILES['file']
        print(f"Fichier reçu: {file.name}, Taille: {file.size} octets", file=sys.stderr)
        
        # Vérifier que c'est bien un fichier Excel
        if not file.name.endswith(('.xlsx', '.xls')):
            print(f"!!! ERREUR: Format de fichier non supporté: {file.name}", file=sys.stderr)
            return Response(
                {'detail': 'Le fichier doit être au format Excel (.xlsx ou .xls)'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        print("[IMPORTS CREATE] Début lecture du fichier Excel", file=sys.stderr)
        # Lire le fichier Excel avec le moteur openpyxl spécifié explicitement
        try:
            print("\n=== LECTURE DU FICHIER EXCEL ===")
            print("Tentative de lecture avec pandas...")
            
            # Sauvegarder le fichier temporairement pour le débogage
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                for chunk in file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name
            
            print(f"Fichier temporaire créé: {tmp_file_path}")
            print(f"Taille du fichier: {os.path.getsize(tmp_file_path)} octets")
            
            # Lire le fichier Excel
            df = pd.read_excel(tmp_file_path, engine='openpyxl')
            
            print("\n=== CONTENU DU FICHIER EXCEL ===")
            print(f"Colonnes: {df.columns.tolist()}")
            print("Premières lignes:")
            print(df.head().to_string())
            print("\nTypes de données:")
            print(df.dtypes)
            
            # Supprimer le fichier temporaire
            try:
                os.unlink(tmp_file_path)
                print(f"Fichier temporaire supprimé: {tmp_file_path}")
            except Exception as e:
                print(f"Attention: impossible de supprimer le fichier temporaire {tmp_file_path}: {e}")
        except Exception as e:
            import traceback
            error_msg = f'Erreur lors de la lecture du fichier Excel. Détail: {str(e)}'
            print(f"\n!!! ERREUR LECTURE EXCEL: {error_msg}")
            print("\n=== TRACEBACK COMPLET ===")
            traceback.print_exc()
            print("======================\n")
            
            # Essayer de lire le fichier comme fichier binaire pour le débogage
            try:
                file.seek(0)  # Remettre le curseur au début du fichier
                content = file.read(500)  # Lire les 500 premiers octets
                print(f"Début du contenu du fichier (hex): {content.hex()}")
            except Exception as read_error:
                print(f"Impossible de lire le contenu du fichier: {read_error}")
            
            return Response(
                {'detail': f'Erreur lors de la lecture du fichier Excel. Vérifiez le format du fichier. Détail: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        print("\n=== APRÈS LECTURE FICHIER ===", file=sys.stderr)
        print(f"request.data: {request.data}", file=sys.stderr)
        
        if 'import_type' in request.data:
            import_type = request.data.get('import_type', 'questions')
        else:
            import_type = 'questions'
        
        print(f"import_type déterminé: {import_type}", file=sys.stderr)
        print(f"Colonnes du fichier Excel: {df.columns.tolist()}", file=sys.stderr)
        
        try:
            # Vérifier le type MIME du fichier
            if not file.name.endswith(('.xlsx', '.xls')):
                return Response(
                    {'detail': 'Le fichier doit être au format Excel (.xlsx ou .xls)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifier si c'est une prévisualisation (soit via le paramètre preview, soit via l'URL)
            is_preview = (request.data.get('preview', 'false').lower() == 'true' or 
                         request.path.endswith('/preview/'))
            
            print(f"is_preview: {is_preview}", file=sys.stderr)
            
            if import_type == 'questions':
                # Vérifier les colonnes requises pour les questions ENA (avec leçons)
                required_columns = ['texte_question', 'matiere_nom', 'lecon_nom', 'type_question']
                print(f"Colonnes requises: {required_columns}", file=sys.stderr)
                missing_columns = [col for col in required_columns if col not in df.columns]
                print(f"Colonnes manquantes: {missing_columns}", file=sys.stderr)
                if missing_columns:
                    print(f"!!! ERREUR: Colonnes manquantes: {missing_columns}", file=sys.stderr)
                    return Response(
                        {'detail': f'Colonnes manquantes dans le fichier Excel: {", ".join(missing_columns)}. Colonnes présentes: {", ".join(df.columns.tolist())}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            elif import_type == 'lecons':
                # Vérifier les colonnes requises pour les leçons ENA
                required_columns = ['nom', 'matiere_nom']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    return Response(
                        {'detail': f'Colonnes manquantes dans le fichier Excel: {", ".join(missing_columns)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            elif import_type == 'contenus_pedagogiques':
                # Vérifier les colonnes requises pour les contenus pédagogiques ENA
                required_columns = ['titre', 'matiere_nom', 'type_contenu']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    return Response(
                        {'detail': f'Colonnes manquantes dans le fichier Excel: {", ".join(missing_columns)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            elif import_type == 'sessions_zoom':
                # Vérifier les colonnes requises pour les sessions Zoom ENA
                required_columns = ['titre', 'matiere_nom', 'date_session']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    return Response(
                        {'detail': f'Colonnes manquantes dans le fichier Excel: {", ".join(missing_columns)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif import_type == 'questions_examen_national':
                # Vérifier les colonnes requises pour les questions d'examen national ENA
                required_columns = ['texte', 'type_question', 'matiere_combinee']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    return Response(
                        {'detail': f'Colonnes manquantes dans le fichier Excel: {", ".join(missing_columns)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {'detail': f'Type d\'import non supporté: {import_type}. Types supportés: questions, questions_examen_national, lecons, contenus_pedagogiques, sessions_zoom'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if import_type == 'questions':
                
                # Convertir les données en format approprié
                questions_data = []
                print("\n=== TRAITEMENT DES LIGNES ===")
                for idx, row in df.iterrows():
                    print(f"\nLigne {idx + 2} (0-based: {idx}):")  # +2 car l'index commence à 0 et on a l'en-tête
                    # Nettoyer les valeurs NaN pour les champs texte
                    def clean_value(value, field_name=''):
                        if pd.isna(value) or (isinstance(value, (int, float)) and pd.isna(float(value))):
                            if field_name:
                                print(f"    - Champ '{field_name}': valeur manquante (NaN), remplacée par ''")
                            return ''
                        cleaned = str(value).strip()
                        if field_name:
                            print(f"    - Champ '{field_name}': '{value}' -> '{cleaned}'")
                        return cleaned
                    
                    # Préparer les données de la question ENA
                    print("  Préparation des données de la question ENA...")
                    question_data = {
                        'texte_question': clean_value(row.get('texte_question', ''), 'texte_question'),
                        'matiere_nom': clean_value(row.get('matiere_nom', ''), 'matiere_nom'),
                        'lecon_nom': clean_value(row.get('lecon_nom', ''), 'lecon_nom'),
                        'type_question': clean_value(row.get('type_question', 'choix_unique'), 'type_question'),
                        'explication': clean_value(row.get('explication', ''), 'explication'),
                        'temps_limite': int(row.get('temps_limite', 0)) if pd.notna(row.get('temps_limite', 0)) and str(row.get('temps_limite', '')).strip() else None,
                        'choix': []
                    }
                    
                    # Validation des champs obligatoires
                    if not question_data['texte_question'] or not question_data['matiere_nom'] or not question_data['lecon_nom']:
                        print(f"  [ERREUR] Champs obligatoires manquants à la ligne {idx + 2}")
                        continue
                    print("  Données nettoyées:", {k: v for k, v in question_data.items() if k != 'choix'})
                    
                    # Gestion des choix pour les QCM
                    if question_data['type_question'] in ['choix_unique', 'choix_multiple']:
                        print(f"  Recherche des choix pour une question de type {question_data['type_question']}...")
                        
                        # Récupérer la bonne réponse (format: A, B, C, D ou a, b, c, d)
                        bonne_reponse = clean_value(row.get('bonne_reponse', ''), 'bonne_reponse').upper().strip()
                        print(f"  - Bonne réponse indiquée: {bonne_reponse}")
                        
                        # Support pour format choix_a, choix_b, choix_c, choix_d
                        lettres = ['a', 'b', 'c', 'd', 'e']
                        for lettre in lettres:
                            choix_texte = row.get(f'choix_{lettre}')
                            if pd.notna(choix_texte) and str(choix_texte).strip():
                                print(f"  - Choix {lettre.upper()} trouvé: {str(choix_texte)[:50]}...")
                                explication = clean_value(row.get(f'choix_{lettre}_explication', ''), f'choix_{lettre}_explication')
                                
                                # Déterminer si ce choix est correct basé sur bonne_reponse
                                est_correct = (lettre.upper() == bonne_reponse)
                                
                                question_data['choix'].append({
                                    'texte': clean_value(choix_texte),
                                    'est_correct': est_correct,
                                    'explication': explication
                                })
                        
                        # Fallback: Support pour format choix_1, choix_2, etc. si aucun choix_a/b/c/d trouvé
                        if not question_data['choix']:
                            for i in range(1, 11):  # Jusqu'à 10 choix
                                choix_texte = row.get(f'choix_{i}')
                                if pd.notna(choix_texte) and str(choix_texte).strip():
                                    print(f"  - Choix {i} trouvé: {str(choix_texte)[:50]}...")
                                    explication = clean_value(row.get(f'choix_{i}_explication', ''), f'choix_{i}_explication')
                                    
                                    est_correct = False
                                    if question_data['type_question'] == 'choix_unique':
                                        est_correct = (i == 1 and not any(c.get('est_correct', False) for c in question_data['choix'])) or \
                                                    row.get(f'choix_{i}_correct', False) in [True, 'oui', 'Oui', 'OUI', 'vrai', 'Vrai', 'VRAI', '1', 1]
                                    else:
                                        est_correct = row.get(f'choix_{i}_correct', False) in [True, 'oui', 'Oui', 'OUI', 'vrai', 'Vrai', 'VRAI', '1', 1]
                                    
                                    question_data['choix'].append({
                                        'texte': clean_value(choix_texte),
                                        'est_correct': est_correct,
                                        'explication': explication
                                    })
                        
                        print(f"  - Total choix trouvés: {len(question_data['choix'])}")
                    
                    questions_data.append(question_data)
                
                # Si c'est une prévisualisation, retourner les données sans les enregistrer
                if is_preview:
                    # Récupérer toutes les matières ENA premier tour pour la correspondance par nom
                    matieres = {m.nom.lower(): m for m in Matiere.objects.filter(choix_concours='ENA', tour_ena='premier_tour')}
                    print("\n=== MODE PRÉVISUALISATION ENA ===")
                    print(f"{len(questions_data)} questions à importer")
                    print(f"Matières ENA premier tour existantes: {', '.join(matieres.keys())}")
                    
                    # Valider les matières et leçons
                    validation_errors = []
                    for idx, q in enumerate(questions_data):
                        matiere_nom = q.get('matiere_nom', '').lower()
                        lecon_nom = q.get('lecon_nom', '')
                        
                        if matiere_nom and matiere_nom not in matieres:
                            validation_errors.append(f"Ligne {idx + 2}: Matière '{q.get('matiere_nom')}' non trouvée pour le premier tour ENA")
                        elif matiere_nom and lecon_nom:
                            # Vérifier si la leçon existe
                            matiere = matieres[matiere_nom]
                            if not Lecon.objects.filter(nom__iexact=lecon_nom, matiere=matiere).exists():
                                validation_errors.append(f"Ligne {idx + 2}: Leçon '{lecon_nom}' non trouvée pour la matière '{q.get('matiere_nom')}'")
                    
                    return Response({
                        'detail': f'Prévisualisation: {len(questions_data)} questions ENA',
                        'preview_data': questions_data[:10],
                        'total_rows': len(questions_data),
                        'validation_errors': validation_errors,
                        'created': 0,
                        'errors': [{'ligne': i+2, 'erreur': err} for i, err in enumerate(validation_errors)]
                    })
                
                # Si on arrive ici, on procède à l'importation réelle
                print("\n=== DÉBUT IMPORTATION RÉELLE ENA ===")
                created_count = 0
                errors = []
                
                try:
                    for idx, q_data in enumerate(questions_data, 1):
                        try:
                            print(f"\n--- Traitement de la question ENA {idx}/{len(questions_data)} ---")
                            
                            # Récupérer la matière et la leçon
                            matiere_nom = q_data.get('matiere_nom', '').strip()
                            lecon_nom = q_data.get('lecon_nom', '').strip()
                            
                            print(f"  - Recherche de la matière: '{matiere_nom}' (repr: {repr(matiere_nom)})")
                            print(f"  - Recherche de la leçon: '{lecon_nom}'")
                            
                            # Trouver ou créer la matière ENA premier tour
                            matiere, matiere_created = Matiere.objects.get_or_create(
                                nom__iexact=matiere_nom.strip(),
                                choix_concours='ENA',
                                tour_ena='premier_tour',
                                defaults={
                                    'nom': matiere_nom.strip(),
                                    'choix_concours': 'ENA',
                                    'tour_ena': 'premier_tour'
                                }
                            )
                            if matiere_created:
                                print(f"  ✓ Matière '{matiere_nom}' créée automatiquement")
                                
                            # Trouver ou créer la leçon
                            lecon, lecon_created = Lecon.objects.get_or_create(
                                nom__iexact=lecon_nom,
                                matiere=matiere,
                                defaults={
                                    'nom': lecon_nom,
                                    'matiere': matiere,
                                    'ordre': Lecon.objects.filter(matiere=matiere).count() + 1,
                                    'active': True
                                }
                            )
                            if lecon_created:
                                print(f"  ✓ Leçon '{lecon_nom}' créée automatiquement")
                                
                            if not is_preview:
                                # Mapping automatique des types de questions (case insensitive)
                                type_question_mapping = {
                                    'saisie_texte': 'texte_court',
                                    'sisie_texte': 'texte_court',  # typo
                                    'texte_libre': 'texte_court',
                                    'reponse_libre': 'texte_court',
                                    'texte_long': 'texte_long',
                                    'essai': 'texte_long',
                                    'redaction': 'texte_long',
                                    'choix_multiple': 'choix_multiple',
                                    'choix_miltuple': 'choix_multiple',  # typo
                                    'choix_unique': 'choix_unique',
                                    'vrai_faux': 'vrai_faux',
                                    'vrai_false': 'vrai_faux',
                                }
                                
                                # Convertir le type de question (normaliser en minuscules)
                                type_question_raw = q_data['type_question'].lower().strip()
                                type_question = type_question_mapping.get(type_question_raw, type_question_raw)
                                if type_question != type_question_raw:
                                    print(f"  - Type de question converti: {q_data['type_question']} → {type_question}")
                                
                                # Création de la question ENA
                                question_data = {
                                    'texte': q_data['texte_question'],
                                    'type_question': type_question,
                                    'explication': q_data.get('explication', ''),
                                    'temps_limite': q_data.get('temps_limite'),
                                    'matiere': matiere,  # Définir la matière pour compatibilité avec le frontend
                                    'lecon': lecon
                                }
                                print(f"  - Matière: {matiere.nom} (ID: {matiere.id})")
                                print(f"  - Leçon: {lecon.nom} (ID: {lecon.id})")
                                
                                # Création de la question (éviter les doublons)
                                question, created = Question.objects.get_or_create(
                                    texte=question_data['texte'],
                                    matiere=question_data['matiere'],
                                    lecon=question_data['lecon'],
                                    defaults=question_data
                                )
                                if created:
                                    question.full_clean()  # Valide les champs avant sauvegarde
                                print(f"  - Question créée avec l'ID: {question.id}")
                                
                                # Création des choix si nécessaire (seulement pour les nouvelles questions)
                                if created and q_data['type_question'].lower() in ['choix_unique', 'choix_multiple'] and q_data.get('choix'):
                                    print(f"  - Création de {len(q_data['choix'])} choix...")
                                    for choix_data in q_data['choix']:
                                        Choix.objects.get_or_create(
                                            question=question,
                                            texte=choix_data['texte'],
                                            defaults={
                                                'est_correct': choix_data.get('est_correct', False),
                                                'explication': choix_data.get('explication', '')
                                            }
                                        )
                                    print(f"  - Choix créés pour la question {question.id}")
                                
                                created_count += 1
                                print(f"  ✓ Question {idx} importée avec succès")
                            
                        except Exception as e:
                            import traceback
                            error_msg = f"Erreur lors de l'import de la question {idx}: {str(e)}"
                            print(f"\n!!! ERREUR: {error_msg}")
                            traceback.print_exc()
                            errors.append({
                                'ligne': idx + 1,  # +1 pour l'en-tête, +1 pour l'index 0-based
                                'question': q_data.get('texte_question', '')[:100],
                                'erreur': str(e)
                            })
                
                except Exception as e:
                    import traceback
                    error_msg = f"Erreur critique lors de l'importation: {str(e)}"
                    print(f"\n!!! ERREUR CRITIQUE: {error_msg}")
                    traceback.print_exc()
                    return Response(
                        {'detail': error_msg, 'errors': errors},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # Créer l'enregistrement d'import
                if not is_preview:
                    import_record = ImportExcel.objects.create(
                        utilisateur=request.user,
                        fichier_nom=file.name,
                        import_type='questions',
                        nombre_elements_importes=created_count,
                        nombre_echecs=len(questions_data) - created_count,
                        status='completed',
                        details={
                            'total': len(questions_data),
                            'reussis': created_count,
                            'echecs': len(questions_data) - created_count,
                            'erreurs': errors
                        },
                        erreur=f"{len(errors)} erreur(s) sur {len(questions_data)} questions" if errors else None
                    )
                
                print(f"\n=== IMPORTATION TERMINÉE ===")
                print(f"Questions créées: {created_count}/{len(questions_data)}")
                if errors:
                    print(f"Erreurs: {len(errors)}")
                
                return Response({
                    'detail': f'Prévisualisation: {len(questions_data)} questions ENA' if is_preview else f'Import réussi: {created_count} questions créées',
                    'import_id': import_record.id if not is_preview else None,
                    'preview_data': questions_data[:10] if is_preview else None,
                    'total_rows': len(questions_data),
                    'created': created_count,
                    'errors': errors
                })
                
            elif import_type == 'questions_examen_national':
                # Traitement des questions d'examen national ENA
                questions_examen_data = []
                print("\n=== TRAITEMENT DES QUESTIONS EXAMEN NATIONAL ===")
                
                for idx, row in df.iterrows():
                    print(f"\nLigne {idx + 2} (0-based: {idx}):")
                    
                    # Fonction pour nettoyer les valeurs
                    def clean_value(value, field_name=''):
                        if pd.isna(value) or (isinstance(value, (int, float)) and pd.isna(float(value))):
                            if field_name:
                                print(f"    - Champ '{field_name}': valeur manquante (NaN), remplacée par ''")
                            return ''
                        cleaned = str(value).strip()
                        if field_name:
                            print(f"    - Champ '{field_name}': '{value}' -> '{cleaned}'")
                        return cleaned
                    
                    # Préparer les données de la question d'examen national
                    question_examen_data = {
                        'code_question': clean_value(row.get('code_question', ''), 'code_question'),
                        'texte': clean_value(row.get('texte', ''), 'texte'),
                        'type_question': clean_value(row.get('type_question', 'choix_unique'), 'type_question'),
                        'matiere_combinee': clean_value(row.get('matiere_combinee', ''), 'matiere_combinee'),
                        'choix_a': clean_value(row.get('choix_a', ''), 'choix_a'),
                        'choix_b': clean_value(row.get('choix_b', ''), 'choix_b'),
                        'choix_c': clean_value(row.get('choix_c', ''), 'choix_c'),
                        'choix_d': clean_value(row.get('choix_d', ''), 'choix_d'),
                        'choix_e': clean_value(row.get('choix_e', ''), 'choix_e'),
                        'bonne_reponse': clean_value(row.get('bonne_reponse', ''), 'bonne_reponse'),
                        'reponse_attendue': clean_value(row.get('reponse_attendue', ''), 'reponse_attendue'),
                        'correction_mode': clean_value(row.get('correction_mode', 'exacte'), 'correction_mode'),
                        'explication': clean_value(row.get('explication', ''), 'explication'),
                        'difficulte': clean_value(row.get('difficulte', 'moyen'), 'difficulte'),
                        'temps_limite_secondes': int(row.get('temps_limite_secondes', 120)) if pd.notna(row.get('temps_limite_secondes', 120)) else 120,
                        'active': bool(row.get('active', True)),
                        'validee': bool(row.get('validee', False)),
                        'creee_par': clean_value(row.get('creee_par', 'Import Excel'), 'creee_par')
                    }
                    
                    # Validation des champs obligatoires
                    if not question_examen_data['texte'] or not question_examen_data['matiere_combinee']:
                        print(f"  [ERREUR] Champs obligatoires manquants à la ligne {idx + 2}")
                        continue
                    
                    questions_examen_data.append(question_examen_data)
                
                # Si c'est une prévisualisation, retourner les données sans les enregistrer
                if is_preview:
                    print("\n=== MODE PRÉVISUALISATION EXAMEN NATIONAL ===")
                    print(f"{len(questions_examen_data)} questions d'examen national à importer")
                    
                    # Valider les matières combinées
                    validation_errors = []
                    valid_matieres = ['culture_aptitude', 'logique_combinee', 'anglais']
                    
                    for idx, q in enumerate(questions_examen_data):
                        matiere_combinee = q.get('matiere_combinee', '')
                        
                        if matiere_combinee and matiere_combinee not in valid_matieres:
                            validation_errors.append(f"Ligne {idx + 2}: Matière combinée '{matiere_combinee}' non valide. Valeurs acceptées: {', '.join(valid_matieres)}")
                    
                    return Response({
                        'detail': f'Prévisualisation: {len(questions_examen_data)} questions d\'examen national ENA',
                        'questions_examen': questions_examen_data[:10],
                        'total_rows': len(questions_examen_data),
                        'validation_errors': validation_errors,
                        'created': 0,
                        'errors': [{'ligne': i+2, 'erreur': err} for i, err in enumerate(validation_errors)]
                    })
                
                # Si on arrive ici, on procède à l'importation réelle
                print("\n=== DÉBUT IMPORTATION RÉELLE EXAMEN NATIONAL ===")
                created_count = 0
                errors = []
                
                try:
                    for idx, q_data in enumerate(questions_examen_data, 1):
                        try:
                            print(f"\n--- Traitement de la question examen national {idx}/{len(questions_examen_data)} ---")
                            
                            # Générer un code unique si pas fourni
                            if not q_data['code_question']:
                                from datetime import datetime
                                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                                q_data['code_question'] = f"ENA-{timestamp}-{idx:03d}"
                            
                            # Création de la question d'examen national
                            question_examen = QuestionExamen(
                                code_question=q_data['code_question'],
                                texte=q_data['texte'],
                                type_question=q_data['type_question'],
                                matiere_combinee=q_data['matiere_combinee'],
                                choix_a=q_data['choix_a'],
                                choix_b=q_data['choix_b'],
                                choix_c=q_data['choix_c'],
                                choix_d=q_data['choix_d'],
                                choix_e=q_data['choix_e'],
                                bonne_reponse=q_data['bonne_reponse'],
                                reponse_attendue=q_data['reponse_attendue'],
                                correction_mode=q_data['correction_mode'],
                                explication=q_data['explication'],
                                difficulte=q_data['difficulte'],
                                temps_limite_secondes=q_data['temps_limite_secondes'],
                                active=q_data['active'],
                                validee=q_data['validee'],
                                creee_par=q_data['creee_par']
                            )
                            
                            # Validation et sauvegarde
                            question_examen.full_clean()
                            question_examen.save()
                            
                            created_count += 1
                            print(f"  ✓ Question examen national {idx} importée avec succès (ID: {question_examen.id})")
                            
                        except Exception as e:
                            import traceback
                            error_msg = f"Erreur lors de l'import de la question examen national {idx}: {str(e)}"
                            print(f"\n!!! ERREUR: {error_msg}")
                            traceback.print_exc()
                            errors.append({
                                'ligne': idx + 1,
                                'question': q_data.get('texte', '')[:100],
                                'erreur': str(e)
                            })
                
                except Exception as e:
                    import traceback
                    error_msg = f"Erreur critique lors de l'importation des questions examen national: {str(e)}"
                    print(f"\n!!! ERREUR CRITIQUE: {error_msg}")
                    traceback.print_exc()
                    return Response(
                        {'detail': error_msg, 'errors': errors},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # Créer l'enregistrement d'import
                if not is_preview:
                    import_record = ImportExcel.objects.create(
                        utilisateur=request.user,
                        fichier_nom=file.name,
                        import_type='questions_examen_national',
                        nombre_elements_importes=created_count,
                        nombre_echecs=len(questions_examen_data) - created_count,
                        status='completed',
                        details={
                            'total': len(questions_examen_data),
                            'reussis': created_count,
                            'echecs': len(questions_examen_data) - created_count,
                            'erreurs': errors
                        },
                        erreur=f"{len(errors)} erreur(s) sur {len(questions_examen_data)} questions" if errors else None
                    )
                
                print(f"\n=== IMPORTATION EXAMEN NATIONAL TERMINÉE ===")
                print(f"Questions créées: {created_count}/{len(questions_examen_data)}")
                if errors:
                    print(f"Erreurs: {len(errors)}")
                
                return Response({
                    'detail': f'Import réussi: {created_count} questions d\'examen national créées',
                    'import_id': import_record.id if not is_preview else None,
                    'total_rows': len(questions_examen_data),
                    'created': created_count,
                    'errors': errors,
                    'nombre_questions_importees': created_count
                })
                
            elif import_type == 'lecons':
                # Traitement des leçons ENA
                lecons_data = []
                errors = []
                created_count = 0
                
                for idx, row in df.iterrows():
                    try:
                        # Nettoyer les valeurs
                        nom = str(row.get('nom', '')).strip()
                        matiere_nom = str(row.get('matiere_nom', '')).strip()
                        description = str(row.get('description', '')).strip()
                        
                        if not nom or not matiere_nom:
                            errors.append({
                                'ligne': idx + 2,
                                'erreur': 'Nom de leçon et matière obligatoires'
                            })
                            continue
                            
                        # Vérifier que la matière existe et est du premier tour ENA
                        try:
                            matiere = Matiere.objects.get(
                                nom__iexact=matiere_nom,
                                choix_concours='ENA',
                                tour_ena='premier_tour'
                            )
                        except Matiere.DoesNotExist:
                            errors.append({
                                'ligne': idx + 2,
                                'erreur': f'Matière "{matiere_nom}" non trouvée pour le premier tour ENA'
                            })
                            continue
                            
                        if not is_preview:
                            # Créer la leçon
                            lecon, created = Lecon.objects.get_or_create(
                                nom__iexact=nom,
                                matiere=matiere,
                                defaults={
                                    'nom': nom,
                                    'description': description
                                }
                            )
                            if created:
                                created_count += 1
                                
                        lecons_data.append({
                            'nom': nom,
                            'matiere': matiere_nom,
                            'description': description
                        })
                        
                    except Exception as e:
                        errors.append({
                            'ligne': idx + 2,
                            'erreur': str(e)
                        })
                        
                # Créer l'enregistrement d'import
                if not is_preview:
                    import_record = ImportExcel.objects.create(
                        utilisateur=request.user,
                        fichier_nom=file.name,
                        import_type='lecons',
                        nombre_elements_importes=created_count,
                        nombre_echecs=len(lecons_data) - created_count,
                        status='completed',
                        details={
                            'total': len(lecons_data),
                            'reussis': created_count,
                            'echecs': len(lecons_data) - created_count,
                            'erreurs': errors
                        }
                    )
                    
                return Response({
                    'detail': f'Prévisualisation: {len(lecons_data)} leçons' if is_preview else f'Import réussi: {created_count} leçons créées',
                    'import_id': import_record.id if not is_preview else None,
                    'preview_data': lecons_data[:10] if is_preview else None,
                    'total_rows': len(lecons_data),
                    'created': created_count,
                    'errors': errors
                })
                
            elif import_type == 'contenus_pedagogiques':
                # Traitement des contenus pédagogiques ENA
                contenus_data = []
                errors = []
                created_count = 0
                
                for idx, row in df.iterrows():
                    try:
                        # Nettoyer les valeurs
                        titre = str(row.get('titre', '')).strip()
                        matiere_nom = str(row.get('matiere_nom', '')).strip()
                        type_contenu = str(row.get('type_contenu', '')).strip()
                        description = str(row.get('description', '')).strip()
                        url_contenu = str(row.get('url_contenu', '')).strip()
                        
                        if not titre or not matiere_nom or not type_contenu:
                            errors.append({
                                'ligne': idx + 2,
                                'erreur': 'Titre, matière et type de contenu obligatoires'
                            })
                            continue
                            
                        if type_contenu not in ['PDF', 'video']:
                            errors.append({
                                'ligne': idx + 2,
                                'erreur': 'Type de contenu doit être "PDF" ou "video"'
                            })
                            continue
                            
                        # Vérifier que la matière existe et est du second tour ENA
                        try:
                            matiere = Matiere.objects.get(
                                nom__iexact=matiere_nom,
                                choix_concours='ENA',
                                tour_ena='second_tour'
                            )
                        except Matiere.DoesNotExist:
                            errors.append({
                                'ligne': idx + 2,
                                'erreur': f'Matière "{matiere_nom}" non trouvée pour le second tour ENA'
                            })
                            continue
                            
                        if not is_preview:
                            # Créer le contenu pédagogique
                            contenu = ContenuPedagogique.objects.create(
                                titre=titre,
                                matiere=matiere,
                                type_contenu=type_contenu,
                                description=description,
                                url_contenu=url_contenu
                            )
                            created_count += 1
                                
                        contenus_data.append({
                            'titre': titre,
                            'matiere': matiere_nom,
                            'type_contenu': type_contenu,
                            'description': description,
                            'url_contenu': url_contenu
                        })
                        
                    except Exception as e:
                        errors.append({
                            'ligne': idx + 2,
                            'erreur': str(e)
                        })
                        
                # Créer l'enregistrement d'import
                if not is_preview:
                    import_record = ImportExcel.objects.create(
                        utilisateur=request.user,
                        fichier_nom=file.name,
                        import_type='contenus_pedagogiques',
                        nombre_elements_importes=created_count,
                        nombre_echecs=len(contenus_data) - created_count,
                        status='completed',
                        details={
                            'total': len(contenus_data),
                            'reussis': created_count,
                            'echecs': len(contenus_data) - created_count,
                            'erreurs': errors
                        }
                    )
                    
                return Response({
                    'detail': f'Prévisualisation: {len(contenus_data)} contenus pédagogiques' if is_preview else f'Import réussi: {created_count} contenus créés',
                    'import_id': import_record.id if not is_preview else None,
                    'preview_data': contenus_data[:10] if is_preview else None,
                    'total_rows': len(contenus_data),
                    'created': created_count,
                    'errors': errors
                })
                
            elif import_type == 'sessions_zoom':
                # Traitement des sessions Zoom ENA
                sessions_data = []
                errors = []
                created_count = 0
                
                for idx, row in df.iterrows():
                    try:
                        # Nettoyer les valeurs
                        titre = str(row.get('titre', '')).strip()
                        matiere_nom = str(row.get('matiere_nom', '')).strip()
                        description = str(row.get('description', '')).strip()
                        url_zoom = str(row.get('url_zoom', '')).strip()
                        
                        # Traiter la date
                        date_session_raw = row.get('date_session')
                        if pd.isna(date_session_raw):
                            errors.append({
                                'ligne': idx + 2,
                                'erreur': 'Date de session obligatoire'
                            })
                            continue
                            
                        try:
                            if isinstance(date_session_raw, str):
                                from datetime import datetime
                                date_session = datetime.strptime(date_session_raw, '%Y-%m-%d %H:%M')
                            else:
                                date_session = date_session_raw
                        except:
                            errors.append({
                                'ligne': idx + 2,
                                'erreur': 'Format de date invalide (attendu: YYYY-MM-DD HH:MM)'
                            })
                            continue
                            
                        if not titre or not matiere_nom:
                            errors.append({
                                'ligne': idx + 2,
                                'erreur': 'Titre et matière obligatoires'
                            })
                            continue
                            
                        # Vérifier que la matière existe et est de l'oral ENA
                        try:
                            matiere = Matiere.objects.get(
                                nom__iexact=matiere_nom,
                                choix_concours='ENA',
                                tour_ena='oral'
                            )
                        except Matiere.DoesNotExist:
                            errors.append({
                                'ligne': idx + 2,
                                'erreur': f'Matière "{matiere_nom}" non trouvée pour l\'oral ENA'
                            })
                            continue
                            
                        if not is_preview:
                            # Créer la session Zoom
                            session = SessionZoomLive.objects.create(
                                titre=titre,
                                matiere=matiere,
                                description=description,
                                date_session=date_session,
                                url_zoom=url_zoom
                            )
                            created_count += 1
                                
                        sessions_data.append({
                            'titre': titre,
                            'matiere': matiere_nom,
                            'description': description,
                            'date_session': date_session.strftime('%Y-%m-%d %H:%M') if hasattr(date_session, 'strftime') else str(date_session),
                            'url_zoom': url_zoom
                        })
                        
                    except Exception as e:
                        errors.append({
                            'ligne': idx + 2,
                            'erreur': str(e)
                        })
                        
                # Créer l'enregistrement d'import
                if not is_preview:
                    import_record = ImportExcel.objects.create(
                        utilisateur=request.user,
                        fichier_nom=file.name,
                        import_type='sessions_zoom',
                        nombre_elements_importes=created_count,
                        nombre_echecs=len(sessions_data) - created_count,
                        status='completed',
                        details={
                            'total': len(sessions_data),
                            'reussis': created_count,
                            'echecs': len(sessions_data) - created_count,
                            'erreurs': errors
                        }
                    )
                    
                return Response({
                    'detail': f'Prévisualisation: {len(sessions_data)} sessions Zoom' if is_preview else f'Import réussi: {created_count} sessions créées',
                    'import_id': import_record.id if not is_preview else None,
                    'preview_data': sessions_data[:10] if is_preview else None,
                    'total_rows': len(sessions_data),
                    'created': created_count,
                    'errors': errors
                })

        except Exception as e:
            return Response(
                {'detail': f'Erreur lors du traitement du fichier: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

# JWT endpoints (login, refresh, logout) will be routed in urls.py using SimpleJWT views directly.

from rest_framework_simplejwt.views import TokenViewBase
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenViewBase):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            from rest_framework.response import Response
            from rest_framework import status
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        login = request.data.get('email')
        password = request.data.get('password')
        Utilisateur = get_user_model()
        user = None
        if login:
            try:
                user = Utilisateur.objects.get(email=login)
            except Utilisateur.DoesNotExist:
                try:
                    user = Utilisateur.objects.get(telephone=login)
                except Utilisateur.DoesNotExist:
                    pass
        # IP extraction
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        # Si l'utilisateur existe, vérifier l'IP
        if user:
            if user.last_login_ip and user.last_login_ip != ip:
                from rest_framework.response import Response
                from rest_framework import status
                return Response({
                    'detail': "Votre compte est bloqué pour des raisons de sécurité (connexion depuis un nouvel appareil ou réseau). Veuillez demander la réinitialisation de votre accès via le support ou le bouton dédié.",
                    'code': 'ip_blocked',
                    'can_request_ip_reset': True
                }, status=status.HTTP_403_FORBIDDEN)
            # Si première connexion, enregistrer l'IP
            if not user.last_login_ip:
                user.last_login_ip = ip
                user.save(update_fields=['last_login_ip'])
        return super().post(request, *args, **kwargs)

from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .serializers import RegisterSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, RequestIPResetSerializer
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model

Utilisateur = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Envoi de l'email de bienvenue
            try:
                from .utils import send_email
                subject = "Bienvenue sur Prépa Concours CI !"
                message = f"""Bonjour {user.nom_complet},

Félicitations ! Votre compte a été créé avec succès sur la plateforme Prépa Concours CI.

Vous pouvez maintenant vous connecter et commencer votre préparation aux concours administratifs :
- Parcours ENA
- Parcours Fonction Publique

Nous vous souhaitons une excellente préparation !

L'équipe Prépa Concours CI"""

                html_message = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #ff6600, #ff8800); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">🎓 Bienvenue sur Prépa Concours CI !</h1>
                    </div>
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 18px; color: #333; margin-bottom: 20px;">Bonjour <strong>{user.nom_complet}</strong>,</p>
                        
                        <p style="color: #666; line-height: 1.6;">Félicitations ! Votre compte a été créé avec succès sur notre plateforme de préparation aux concours administratifs.</p>
                        
                        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ff6600;">
                            <h3 style="color: #ff6600; margin-top: 0;">Vous pouvez maintenant accéder à :</h3>
                            <ul style="color: #666; line-height: 1.8;">
                                <li>📚 <strong>Parcours ENA</strong> - Préparation complète à l'École Nationale d'Administration</li>
                                <li>🏛️ <strong>Parcours Fonction Publique</strong> - Préparation aux concours de la fonction publique</li>
                                <li>📝 <strong>Quiz interactifs</strong> par matière et niveau</li>
                                <li>📊 <strong>Suivi de progression</strong> personnalisé</li>
                            </ul>
                        </div>
                        
                        <p style="color: #666; line-height: 1.6;">Connectez-vous dès maintenant pour commencer votre préparation !</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <p style="color: #999; font-size: 14px;">Nous vous souhaitons une excellente préparation ! 🚀</p>
                            <p style="color: #ff6600; font-weight: bold;">L'équipe Prépa Concours CI</p>
                        </div>
                    </div>
                </div>
                """
                
                send_email(subject, message, [user.email], html_message=html_message)
                print(f"[EMAIL ENVOYÉ] Email de bienvenue envoyé à {user.email}")
                
            except Exception as e:
                print(f"[ERREUR EMAIL] Impossible d'envoyer l'email de bienvenue : {e}")
                # Ne pas faire échouer l'inscription si l'email ne peut pas être envoyé
            
            return Response({'detail': 'Utilisateur créé avec succès. Un email de bienvenue a été envoyé.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = Utilisateur.objects.get(email=email)
            except Utilisateur.DoesNotExist:
                return Response({'detail': 'Aucun utilisateur avec cet email.'}, status=status.HTTP_404_NOT_FOUND)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # Ici, on simule l’envoi d’email en renvoyant le lien dans la réponse
            reset_link = f"/api/auth/reset-password-confirm/?uid={uid}&token={token}"
            return Response({'reset_link': reset_link, 'uid': uid, 'token': token}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            uid = request.query_params.get('uid')
            token = serializer.validated_data['token']
            mot_de_passe = serializer.validated_data['mot_de_passe']
            try:
                uid_int = force_str(urlsafe_base64_decode(uid))
                user = Utilisateur.objects.get(pk=uid_int)
            except (TypeError, ValueError, OverflowError, Utilisateur.DoesNotExist):
                return Response({'detail': 'Lien invalide.'}, status=status.HTTP_400_BAD_REQUEST)
            if not default_token_generator.check_token(user, token):
                return Response({'detail': 'Token invalide ou expiré.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(mot_de_passe)
            user.save()
            return Response({'detail': 'Mot de passe réinitialisé avec succès.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from .utils import notify_ip_reset

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        # Vérifier si l'utilisateur est actif
        if not user.is_active:
            return Response(
                {"detail": "Ce compte est désactivé."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # Vérifier si l'utilisateur est bloqué par adresse IP
        if hasattr(user, 'is_blocked') and user.is_blocked:
            return Response(
                {"detail": "Accès bloqué. Veuillez contacter l'administrateur."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Récupérer le cycle de l'utilisateur s'il existe
        cycle = None
        if hasattr(user, 'cycle') and user.cycle:
            cycle = {
                'id': user.cycle.id,
                'nom': user.cycle.nom
            }
            
        return Response({
            "id": user.id,
            "email": user.email,
            "telephone": user.telephone,
            "nom_complet": user.nom_complet,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "auth_provider": user.auth_provider,
            "date_inscription": user.date_inscription,
            "last_login": user.last_login,
            "cycle": cycle,
            "permissions": user.get_all_permissions(),
        })

    def put(self, request):
        user = request.user
        from .serializers import UtilisateurSerializer
        serializer = UtilisateurSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not old_password or not new_password:
            return Response({'detail': 'Les champs sont requis.'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(old_password):
            return Response({'detail': 'Ancien mot de passe incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            from django.contrib.auth.password_validation import validate_password
            validate_password(new_password, user)
        except Exception as e:
            return Response({'detail': e.messages if hasattr(e, 'messages') else str(e)}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Mot de passe modifié avec succès.'}, status=status.HTTP_200_OK)

class ResetUserIPAdminView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'detail': 'user_id requis.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = Utilisateur.objects.get(pk=user_id)
        except Utilisateur.DoesNotExist:
            return Response({'detail': 'Utilisateur introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        user.last_login_ip = None
        user.save(update_fields=['last_login_ip'])
        notify_ip_reset(user)
        return Response({'detail': "Adresse IP de l'utilisateur réinitialisée et notification envoyée."}, status=status.HTTP_200_OK)

class ConfirmIPResetView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        from .models import IPResetRequest
        uid = request.GET.get('uid')
        token = request.GET.get('token')
        if not uid or not token:
            return Response({'detail': 'Lien invalide.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            from django.contrib.auth import get_user_model
            Utilisateur = get_user_model()
            user = Utilisateur.objects.get(pk=uid)
            ip_reset = IPResetRequest.objects.get(utilisateur=user, token=token)
        except (Utilisateur.DoesNotExist, IPResetRequest.DoesNotExist):
            return Response({'detail': 'Lien invalide ou expiré.'}, status=status.HTTP_400_BAD_REQUEST)
        if not ip_reset.is_valid():
            return Response({'detail': 'Lien expiré ou déjà utilisé.'}, status=status.HTTP_400_BAD_REQUEST)
        user.last_login_ip = None
        user.save(update_fields=['last_login_ip'])
        ip_reset.used = True
        ip_reset.save(update_fields=['used'])
        # Simuler une notification à l’utilisateur (console)
        print(f"[INFO] IP réinitialisée automatiquement pour {user.nom_complet} ({user.email or user.telephone}) via lien sécurisé.")
        return Response({'detail': 'Votre accès a été réinitialisé. Vous pouvez maintenant vous reconnecter depuis votre nouvel appareil ou réseau.'}, status=status.HTTP_200_OK)

class RequestIPResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RequestIPResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            telephone = serializer.validated_data.get('telephone')
            
            try:
                if email:
                    user = Utilisateur.objects.get(email=email)
                elif telephone:
                    user = Utilisateur.objects.get(telephone=telephone)
                else:
                    return Response(
                        {'error': 'Email ou téléphone requis'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Créer une demande de réinitialisation IP
                reset_request = IPResetRequest.objects.create(
                    utilisateur=user,
                    expires_at=timezone.now() + timezone.timedelta(hours=24)
                )
                
                # Envoyer la notification
                notify_ip_reset(user, reset_request.token)
                
                return Response(
                    {'message': 'Demande de réinitialisation envoyée'}, 
                    status=status.HTTP_200_OK
                )
                
            except Utilisateur.DoesNotExist:
                return Response(
                    {'error': 'Utilisateur non trouvé'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
                html_message = f"<p>Bonjour {user.nom_complet},</p><p>Vous avez demandé la réinitialisation de votre accès.<br> Cliquez sur ce lien : <a href='{reset_link}'>{reset_link}</a><br>Ce lien est valable 1h.</p><p>L’équipe QCM.</p>"
                send_email(subject, message, [user.email], html_message=html_message)
                print(f"[EMAIL ENVOYÉ] à {user.email} | Lien : {reset_link}")
            else:
                print(f"[INFO] L’utilisateur n’a pas d’email, lien de reset : {reset_link}")
            return Response({'detail': 'Un lien de réinitialisation a été envoyé à votre email si le compte existe.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# === ViewSets pour la navigation ENA par tours ===

class LeconViewSet(viewsets.ModelViewSet):
    """ViewSet pour les leçons (catégories) du premier tour ENA"""
    queryset = Lecon.objects.all()
    serializer_class = LeconSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        matiere_id = self.request.query_params.get('matiere_id')
        if matiere_id:
            queryset = queryset.filter(matiere_id=matiere_id)
        return queryset.filter(active=True)

class ContenuPedagogiqueViewSet(viewsets.ModelViewSet):
    """ViewSet pour les contenus pédagogiques (PDF/vidéo) du second tour ENA"""
    queryset = ContenuPedagogique.objects.all()
    serializer_class = ContenuPedagogiqueSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        matiere_id = self.request.query_params.get('matiere_id')
        type_contenu = self.request.query_params.get('type_contenu')
        
        if matiere_id:
            queryset = queryset.filter(matiere_id=matiere_id)
        if type_contenu:
            queryset = queryset.filter(type_contenu=type_contenu)
            
        return queryset.filter(active=True)

class SessionZoomLiveViewSet(viewsets.ModelViewSet):
    """ViewSet pour les sessions Zoom live de l'oral ENA"""
    queryset = SessionZoomLive.objects.all()
    serializer_class = SessionZoomLiveSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        matiere_id = self.request.query_params.get('matiere_id')
        statut = self.request.query_params.get('statut')
        
        if matiere_id:
            queryset = queryset.filter(matiere_id=matiere_id)
        if statut:
            queryset = queryset.filter(statut=statut)
            
        return queryset.filter(active=True)
    
    @action(detail=False, methods=['get'])
    def prochaines_sessions(self, request):
        """Retourne les prochaines sessions programmées"""
        sessions = self.get_queryset().filter(
            statut='programmee',
            date_session__gte=timezone.now()
        ).order_by('date_session')[:10]
        
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)


# === ViewSet pour la navigation ENA unifiée ===

class ENANavigationViewSet(viewsets.ViewSet):
    """ViewSet pour la navigation ENA selon les tours"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def matieres(self, request):
        """Liste toutes les matières (ENA et Fonction Publique)"""
        # Récupérer toutes les matières ENA et Fonction Publique
        matieres = Matiere.objects.filter(
            choix_concours__in=['ENA', 'fonction_publique']
        ).order_by('nom')
        
        serializer = MatiereSerializer(matieres, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def tours(self, request):
        """Liste les tours ENA disponibles"""
        from .models import TOURS_ENA
        tours = [{'id': tour[0], 'nom': tour[1]} for tour in TOURS_ENA]
        return Response(tours)
    
    @action(detail=False, methods=['get'])
    def matieres_par_tour(self, request):
        """Liste les matières disponibles pour un tour donné"""
        tour = request.query_params.get('tour')
        if not tour:
            return Response({'error': 'Paramètre tour requis'}, status=400)
        
        matieres = Matiere.objects.filter(
            choix_concours='ENA',
            tour_ena=tour
        )
        
        serializer = MatiereSerializer(matieres, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def contenu_par_matiere(self, request):
        """Retourne le contenu disponible pour une matière selon son tour"""
        matiere_id = request.query_params.get('matiere_id')
        if not matiere_id:
            return Response({'error': 'Paramètre matiere_id requis'}, status=400)
        
        try:
            # Support both ENA and Fonction Publique
            matiere = Matiere.objects.get(
                id=matiere_id, 
                choix_concours__in=['ENA', 'fonction_publique']
            )
        except Matiere.DoesNotExist:
            return Response({'error': 'Matière non trouvée'}, status=404)
        
        # Pour les matières Fonction Publique (pas de tour_ena)
        if matiere.choix_concours == 'fonction_publique':
            # Retourner les leçons pour Fonction Publique
            lecons = Lecon.objects.filter(matiere=matiere, active=True)
            serializer = LeconSerializer(lecons, many=True)
            return Response({
                'tour': 'fonction_publique',
                'type_contenu': 'lecons',
                'data': serializer.data
            })
        
        # Pour les matières ENA avec tour_ena
        if matiere.tour_ena == 'premier_tour':
            # Retourner les leçons (catégories)
            lecons = Lecon.objects.filter(matiere=matiere, active=True)
            serializer = LeconSerializer(lecons, many=True)
            return Response({
                'tour': 'premier_tour',
                'type_contenu': 'lecons',
                'data': serializer.data
            })
        
        elif matiere.tour_ena == 'second_tour':
            # Retourner les contenus pédagogiques (PDF/vidéo)
            contenus = ContenuPedagogique.objects.filter(matiere=matiere, active=True)
            serializer = ContenuPedagogiqueSerializer(contenus, many=True)
            return Response({
                'tour': 'second_tour',
                'type_contenu': 'contenus_pedagogiques',
                'data': serializer.data
            })
        
        elif matiere.tour_ena == 'oral':
            # Retourner les sessions Zoom
            sessions = SessionZoomLive.objects.filter(matiere=matiere, active=True)
            serializer = SessionZoomLiveSerializer(sessions, many=True)
            return Response({
                'tour': 'oral',
                'type_contenu': 'sessions_zoom',
                'data': serializer.data
            })
        
        return Response({'error': 'Tour non reconnu'}, status=400)


# === ViewSets pour les questions d'examen national ===

class QuestionExamenViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des questions d'examen national ENA"""
    queryset = QuestionExamen.objects.all()
    serializer_class = QuestionExamenSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Retourne le serializer approprié selon l'action"""
        if self.action == 'list':
            return QuestionExamenDetailSerializer
        elif self.action in ['retrieve', 'create', 'update', 'partial_update']:
            return QuestionExamenSerializer
        return QuestionExamenSerializer
    
    def get_queryset(self):
        """Filtre les questions selon les paramètres"""
        queryset = super().get_queryset()
        
        # Filtres
        matiere_combinee = self.request.query_params.get('matiere_combinee')
        type_question = self.request.query_params.get('type_question')
        difficulte = self.request.query_params.get('difficulte')
        active = self.request.query_params.get('active')
        validee = self.request.query_params.get('validee')
        
        if matiere_combinee:
            queryset = queryset.filter(matiere_combinee=matiere_combinee)
        if type_question:
            queryset = queryset.filter(type_question=type_question)
        if difficulte:
            queryset = queryset.filter(difficulte=difficulte)
        if active is not None:
            queryset = queryset.filter(active=active.lower() == 'true')
        if validee is not None:
            queryset = queryset.filter(validee=validee.lower() == 'true')
        
        return queryset.order_by('matiere_combinee', 'code_question')
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Retourne les statistiques des questions d'examen"""
        try:
            total_questions = QuestionExamen.objects.count()
            questions_actives = QuestionExamen.objects.filter(active=True).count()
            questions_validees = QuestionExamen.objects.filter(validee=True).count()
            
            # Statistiques par matière combinée
            stats_par_matiere = {}
            for matiere_code, matiere_nom in QuestionExamen.MATIERE_COMBINEE_CHOICES:
                stats_par_matiere[matiere_code] = {
                    'nom': matiere_nom,
                    'total': QuestionExamen.objects.filter(matiere_combinee=matiere_code).count(),
                    'actives': QuestionExamen.objects.filter(matiere_combinee=matiere_code, active=True).count(),
                    'validees': QuestionExamen.objects.filter(matiere_combinee=matiere_code, validee=True).count(),
                }
            
            # Statistiques par type de question
            stats_par_type = {}
            for type_code, type_nom in QuestionExamen.TYPE_CHOICES:
                stats_par_type[type_code] = {
                    'nom': type_nom,
                    'count': QuestionExamen.objects.filter(type_question=type_code).count()
                }
            
            return Response({
                'total_questions': total_questions,
                'questions_actives': questions_actives,
                'questions_validees': questions_validees,
                'pourcentage_validees': round((questions_validees / total_questions * 100) if total_questions > 0 else 0, 1),
                'stats_par_matiere': stats_par_matiere,
                'stats_par_type': stats_par_type
            })
            
        except Exception as e:
            logger.error(f'Erreur lors du calcul des statistiques: {e}')
            return Response({
                'error': 'Erreur lors du calcul des statistiques'
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def valider_questions(self, request):
        """Valide en masse des questions d'examen"""
        try:
            question_ids = request.data.get('question_ids', [])
            if not question_ids:
                return Response({
                    'error': 'Aucune question spécifiée'
                }, status=400)
            
            questions_validees = QuestionExamen.objects.filter(
                id__in=question_ids
            ).update(validee=True)
            
            return Response({
                'success': True,
                'questions_validees': questions_validees,
                'message': f'{questions_validees} question(s) validée(s) avec succès'
            })
            
        except Exception as e:
            logger.error(f'Erreur lors de la validation: {e}')
            return Response({
                'error': 'Erreur lors de la validation des questions'
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def questions_pour_examen(self, request):
        """Retourne les questions disponibles pour un examen national"""
        try:
            # Nombre de questions par matière combinée
            repartition = {
                'culture_aptitude': 60,
                'logique_combinee': 40,
                'anglais': 30
            }
            
            questions_disponibles = {}
            total_disponible = 0
            
            for matiere_code, nombre_requis in repartition.items():
                questions = QuestionExamen.objects.filter(
                    matiere_combinee=matiere_code,
                    active=True,
                    validee=True
                ).count()
                
                questions_disponibles[matiere_code] = {
                    'nom': dict(QuestionExamen.MATIERE_COMBINEE_CHOICES)[matiere_code],
                    'disponibles': questions,
                    'requis': nombre_requis,
                    'suffisant': questions >= nombre_requis
                }
                total_disponible += questions
            
            # Vérifier si on peut créer un examen complet
            peut_creer_examen = all(
                info['suffisant'] for info in questions_disponibles.values()
            )
            
            return Response({
                'questions_disponibles': questions_disponibles,
                'total_disponible': total_disponible,
                'total_requis': sum(repartition.values()),
                'peut_creer_examen': peut_creer_examen,
                'message': 'Examen possible' if peut_creer_examen else 'Questions insuffisantes pour créer un examen complet'
            })
            
        except Exception as e:
            logger.error(f'Erreur lors de la vérification: {e}')
            return Response({
                'error': 'Erreur lors de la vérification des questions'
            }, status=500)


# === ViewSets pour le système d'examens ENA ===

class EvaluationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les évaluations ENA"""
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(utilisateur=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)
    
    @action(detail=False, methods=['get'])
    def can_access(self, request):
        """Vérifie si l'utilisateur peut accéder aux évaluations (>=30% score moyen ENA)"""
        user = request.user
        
        # Calculer le score moyen sur tous les quiz ENA
        tentatives_ena = Tentative.objects.filter(
            utilisateur=user,
            choix_concours='ENA',
            terminee=True
        )
        
        if not tentatives_ena.exists():
            return Response({
                'can_access': False,
                'score_moyen': 0,
                'message': 'Vous devez d\'abord passer des quiz ENA pour accéder aux évaluations.'
            })
        
        scores = tentatives_ena.values_list('score', flat=True)
        score_moyen = sum(scores) / len(scores) if scores else 0
        
        can_access = score_moyen >= 30
        
        return Response({
            'can_access': can_access,
            'score_moyen': round(score_moyen, 1),
            'message': 'Vous pouvez passer l\'évaluation !' if can_access else 'Atteignez 30% de score moyen sur vos quiz ENA.'
        })

class ExamenNationalViewSet(viewsets.ModelViewSet):
    """ViewSet pour les examens nationaux ENA"""
    queryset = ExamenNational.objects.all()
    serializer_class = ExamenNationalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(utilisateur=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)
    
    @action(detail=False, methods=['get'])
    def can_access(self, request):
        """Vérifie si l'utilisateur peut accéder à l'examen national (>=50% à l'évaluation)"""
        user = request.user
        
        # Vérifier si l'utilisateur a passé au moins une évaluation
        evaluations = Evaluation.objects.filter(utilisateur=user, terminee=True)
        
        if not evaluations.exists():
            return Response({
                'can_access': False,
                'score_evaluation': 0,
                'message': 'Vous devez d\'abord passer une évaluation ENA pour accéder à l\'examen national.'
            })
        
        # Calculer le score moyen des évaluations
        scores = evaluations.values_list('score', flat=True)
        score_moyen = sum(scores) / len(scores) if scores else 0
        
        can_access = score_moyen >= 50
        
        return Response({
            'can_access': can_access,
            'score_evaluation': round(score_moyen, 1),
            'message': 'Vous pouvez passer l\'examen national !' if can_access else 'Atteignez 50% de score moyen à l\'évaluation.'
        })
    
    @action(detail=False, methods=['get'])
    def matieres_examen(self, request):
        """Retourne les 3 matières combinées pour l'examen national ENA"""
        try:
            # Récupérer les matières ENA du premier tour
            matieres_ena = Matiere.objects.filter(
                choix_concours='ENA',
                tour_ena='premier_tour'
            )
            
            # Grouper les matières selon les spécifications
            matieres_combinees = []
            
            # 1. Culture générale + Aptitude verbale
            culture_generale = matieres_ena.filter(nom__icontains='culture').first()
            aptitude_verbale = matieres_ena.filter(nom__icontains='aptitude verbale').first()
            
            if culture_generale and aptitude_verbale:
                matieres_combinees.append({
                    'id': 'culture_aptitude',
                    'nom': 'Culture générale et Aptitude verbale',
                    'description': 'Combinaison de Culture générale et Aptitude verbale',
                    'matieres_incluses': [
                        {'id': culture_generale.id, 'nom': culture_generale.nom},
                        {'id': aptitude_verbale.id, 'nom': aptitude_verbale.nom}
                    ]
                })
            
            # 2. Logique d'organisation + Logique numérique
            logique_org = matieres_ena.filter(nom__icontains='logique').filter(nom__icontains='organisation').first()
            logique_num = matieres_ena.filter(nom__icontains='logique').filter(nom__icontains='numérique').first()
            
            if logique_org and logique_num:
                matieres_combinees.append({
                    'id': 'logique_combinee',
                    'nom': 'Logique d\'organisation et Logique numérique',
                    'description': 'Combinaison des deux types de logique',
                    'matieres_incluses': [
                        {'id': logique_org.id, 'nom': logique_org.nom},
                        {'id': logique_num.id, 'nom': logique_num.nom}
                    ]
                })
            
            # 3. Anglais (seul)
            anglais = matieres_ena.filter(nom__icontains='anglais').first()
            
            if anglais:
                matieres_combinees.append({
                    'id': 'anglais',
                    'nom': 'Anglais',
                    'description': 'Épreuve d\'anglais',
                    'matieres_incluses': [
                        {'id': anglais.id, 'nom': anglais.nom}
                    ]
                })
            
            return Response({
                'matieres_examen': matieres_combinees,
                'total_matieres': len(matieres_combinees),
                'message': f'{len(matieres_combinees)} matières disponibles pour l\'examen national'
            })
            
        except Exception as e:
            logger.error(f'Erreur lors de la récupération des matières d\'examen: {e}')
            return Response({
                'error': 'Erreur lors de la récupération des matières d\'examen'
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def creer_session_examen(self, request):
        """Crée une nouvelle session d'examen national avec les 3 matières combinées"""
        user = request.user
        
        # Vérifier l'accès
        can_access_response = self.can_access(request)
        if not can_access_response.data.get('can_access', False):
            return Response({
                'error': 'Accès refusé à l\'examen national',
                'details': can_access_response.data
            }, status=403)
        
        try:
            # Vérifier s'il existe déjà un examen en cours pour cet utilisateur ce mois-ci
            from datetime import datetime, timedelta
            debut_mois = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            fin_mois = (debut_mois + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            
            examen_existant = ExamenNational.objects.filter(
                utilisateur=user,
                date_examen__range=[debut_mois, fin_mois],
                terminee=False
            ).first()
            
            if examen_existant:
                return Response({
                    'error': 'Vous avez déjà un examen national en cours ce mois-ci',
                    'examen_id': examen_existant.id
                }, status=400)
            
            # Récupérer les questions d'examen pour les 3 matières combinées
            from .models import QuestionExamen
            questions_examen = []
            
            # 1. Culture générale + Aptitude verbale (60 questions)
            questions_culture_aptitude = list(QuestionExamen.objects.filter(
                matiere_combinee='culture_aptitude',
                active=True,
                validee=True
            ).order_by('?')[:60])
            questions_examen.extend(questions_culture_aptitude)
            
            # 2. Logique d'organisation + Logique numérique (40 questions)
            questions_logique_combinee = list(QuestionExamen.objects.filter(
                matiere_combinee='logique_combinee',
                active=True,
                validee=True
            ).order_by('?')[:40])
            questions_examen.extend(questions_logique_combinee)
            
            # 3. Anglais (30 questions)
            questions_anglais = list(QuestionExamen.objects.filter(
                matiere_combinee='anglais',
                active=True,
                validee=True
            ).order_by('?')[:30])
            questions_examen.extend(questions_anglais)
            
            # Créer l'examen national
            examen = ExamenNational.objects.create(
                utilisateur=user,
                date_examen=timezone.now(),
                terminee=False
            )
            
            # Ajouter les questions à l'examen
            examen.questions.set(questions_examen)
            
            return Response({
                'success': True,
                'examen_id': examen.id,
                'total_questions': len(questions_examen),
                'repartition_questions': {
                    'culture_generale': 30,
                    'aptitude_verbale': 30,
                    'logique_organisation': 20,
                    'logique_numerique': 20,
                    'anglais': 30
                },
                'duree_examen': {
                    'duree_totale_minutes': 180,  # 3 heures
                    'duree_par_matiere_minutes': 60,  # 1 heure par matière combinée
                    'matieres_combinees': [
                        {
                            'nom': 'Culture générale et Aptitude verbale',
                            'duree_minutes': 60,
                            'questions': 60
                        },
                        {
                            'nom': 'Logique d\'organisation et Logique numérique',
                            'duree_minutes': 60,
                            'questions': 40
                        },
                        {
                            'nom': 'Anglais',
                            'duree_minutes': 60,
                            'questions': 30
                        }
                    ]
                },
                'message': f'Examen national créé avec {len(questions_examen)} questions - Durée: 3h (60min par matière)'
            })
            
        except Exception as e:
            logger.error(f'Erreur lors de la création de l\'examen national: {e}')
            return Response({
                'error': 'Erreur lors de la création de l\'examen national'
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def classement(self, request):
        """Retourne le classement national des examens"""
        try:
            # CORRECTION: Utiliser les SessionQuiz terminées pour le classement
            from django.db.models import Q, Max
            from .models import SessionQuiz, Tentative
            
            # Récupérer uniquement les sessions d'examen national terminées
            sessions_terminees = SessionQuiz.objects.filter(
                statut='terminee',
                choix_concours='ENA'
            ).exclude(
                # Exclure les sessions d'évaluation (qui ont une leçon spécifique)
                lecon__isnull=False
            ).select_related('utilisateur').annotate(
                score_final=Max('tentatives__score')
            ).filter(
                score_final__isnull=False
            ).order_by('-score_final', 'date_fin')[:100]  # Top 100
            
            classement_data = []
            for rang, session in enumerate(sessions_terminees, start=1):
                classement_data.append({
                    'rang': rang,
                    'utilisateur': {
                        'nom': session.utilisateur.nom_complet,
                        'id': session.utilisateur.id
                    },
                    'score': float(session.score_final or 0),
                    'temps_total': 0,  # Temporaire - à calculer depuis les tentatives
                    'date_examen': session.date_fin.isoformat() if session.date_fin else session.date_debut.isoformat(),
                    'is_current_user': session.utilisateur.id == request.user.id
                })
            
            # Position de l'utilisateur actuel
            user_position = None
            for index, session in enumerate(sessions_terminees, start=1):
                if session.utilisateur.id == request.user.id:
                    user_position = index
                    break
            
            return Response({
                'classement': classement_data,
                'total_participants': sessions_terminees.count(),
                'user_position': user_position
            })
            
        except Exception as e:
            logger.error(f'Erreur lors de la récupération du classement: {e}')
            return Response({
                'error': 'Erreur lors de la récupération du classement'
            }, status=500)
    
    @action(detail=True, methods=['post'])
    def finaliser_examen(self, request, pk=None):
        """Finalise un examen national et calcule le score avec gestion du temps par matière"""
        try:
            examen = self.get_object()
            
            if examen.utilisateur != request.user:
                return Response({
                    'error': 'Accès non autorisé à cet examen'
                }, status=403)
            
            if examen.terminee:
                return Response({
                    'error': 'Cet examen est déjà terminé'
                }, status=400)
            
            # Récupérer les données de finalisation
            reponses_data = request.data.get('reponses', [])
            temps_total = request.data.get('temps_total_en_secondes', 0)
            
            # Récupérer le temps passé par matière combinée
            temps_par_matiere = request.data.get('temps_par_matiere', {})
            temps_culture_aptitude = temps_par_matiere.get('culture_aptitude', 0)
            temps_logique_combinee = temps_par_matiere.get('logique_combinee', 0)
            temps_anglais = temps_par_matiere.get('anglais', 0)
            
            if not reponses_data:
                return Response({
                    'error': 'Aucune réponse fournie'
                }, status=400)
            
            # Vérifier le respect des contraintes de temps
            violations_temps = []
            if temps_culture_aptitude > examen.DUREE_PAR_MATIERE_SECONDES:
                violations_temps.append(f'Culture générale + Aptitude verbale: {temps_culture_aptitude//60}min (max: 60min)')
            if temps_logique_combinee > examen.DUREE_PAR_MATIERE_SECONDES:
                violations_temps.append(f'Logique combinée: {temps_logique_combinee//60}min (max: 60min)')
            if temps_anglais > examen.DUREE_PAR_MATIERE_SECONDES:
                violations_temps.append(f'Anglais: {temps_anglais//60}min (max: 60min)')
            
            if temps_total > examen.DUREE_TOTALE_SECONDES:
                violations_temps.append(f'Temps total: {temps_total//60}min (max: 180min)')
            
            # Calculer le score avec QuestionExamen
            total_questions = examen.questions.count()
            bonnes_reponses = 0
            
            for reponse_data in reponses_data:
                question_id = reponse_data.get('question_id')
                reponse_utilisateur = reponse_data.get('reponse')
                
                try:
                    question = examen.questions.get(id=question_id)
                    # Utiliser la méthode de vérification de QuestionExamen
                    if question.verifier_reponse(reponse_utilisateur):
                        bonnes_reponses += 1
                    # Incrémenter le compteur d'utilisation
                    question.incrementer_utilisation()
                except QuestionExamen.DoesNotExist:
                    continue
            
            # Calculer le score en pourcentage
            score = (bonnes_reponses / total_questions * 100) if total_questions > 0 else 0
            
            # Mettre à jour l'examen avec les temps détaillés
            examen.score = score
            examen.temps_total_en_secondes = temps_total
            examen.temps_culture_aptitude = temps_culture_aptitude
            examen.temps_logique_combinee = temps_logique_combinee
            examen.temps_anglais = temps_anglais
            examen.terminee = True
            examen.save()
            
            # Le classement sera mis à jour automatiquement via le signal save()
            
            return Response({
                'success': True,
                'examen_id': examen.id,
                'score': round(score, 2),
                'bonnes_reponses': bonnes_reponses,
                'total_questions': total_questions,
                'temps_total_minutes': round(temps_total / 60, 1),
                'temps_par_matiere': {
                    'culture_aptitude_minutes': round(temps_culture_aptitude / 60, 1),
                    'logique_combinee_minutes': round(temps_logique_combinee / 60, 1),
                    'anglais_minutes': round(temps_anglais / 60, 1)
                },
                'violations_temps': violations_temps,
                'rang_national': examen.rang_national,
                'message': f'Examen terminé avec un score de {score:.1f}% - Temps total: {temps_total//60}min'
            })
            
        except Exception as e:
            logger.error(f'Erreur lors de la finalisation de l\'examen: {e}')
            return Response({
                'error': 'Erreur lors de la finalisation de l\'examen'
            }, status=500)
    
    @action(detail=True, methods=['get'])
    def temps_restant(self, request, pk=None):
        """Retourne le temps restant pour l'examen et par matière"""
        try:
            examen = self.get_object()
            
            if examen.utilisateur != request.user:
                return Response({
                    'error': 'Accès non autorisé à cet examen'
                }, status=403)
            
            if examen.terminee:
                return Response({
                    'error': 'Cet examen est déjà terminé'
                }, status=400)
            
            return Response({
                'examen_id': examen.id,
                'temps_restant_total_secondes': examen.get_temps_restant_total(),
                'temps_restant_total_minutes': round(examen.get_temps_restant_total() / 60, 1),
                'repartition_temps': examen.get_repartition_temps(),
                'temps_ecoule': {
                    'total': examen.is_temps_total_ecoule(),
                    'culture_aptitude': examen.is_temps_matiere_ecoule('culture_aptitude'),
                    'logique_combinee': examen.is_temps_matiere_ecoule('logique_combinee'),
                    'anglais': examen.is_temps_matiere_ecoule('anglais')
                }
            })
            
        except Exception as e:
            logger.error(f'Erreur lors de la récupération du temps restant: {e}')
            return Response({
                'error': 'Erreur lors de la récupération du temps restant'
            }, status=500)
    
    @action(detail=True, methods=['post'])
    def mettre_a_jour_temps(self, request, pk=None):
        """Met à jour le temps passé sur une matière spécifique"""
        try:
            examen = self.get_object()
            
            if examen.utilisateur != request.user:
                return Response({
                    'error': 'Accès non autorisé à cet examen'
                }, status=403)
            
            if examen.terminee:
                return Response({
                    'error': 'Cet examen est déjà terminé'
                }, status=400)
            
            matiere_code = request.data.get('matiere_code')
            temps_passe = request.data.get('temps_passe_secondes', 0)
            
            if not matiere_code:
                return Response({
                    'error': 'Code matière requis'
                }, status=400)
            
            # Mettre à jour le temps pour la matière spécifiée
            if matiere_code == 'culture_aptitude':
                examen.temps_culture_aptitude = temps_passe
            elif matiere_code == 'logique_combinee':
                examen.temps_logique_combinee = temps_passe
            elif matiere_code == 'anglais':
                examen.temps_anglais = temps_passe
            else:
                return Response({
                    'error': 'Code matière invalide'
                }, status=400)
            
            # Mettre à jour le temps total
            examen.temps_total_en_secondes = (
                examen.temps_culture_aptitude + 
                examen.temps_logique_combinee + 
                examen.temps_anglais
            )
            
            examen.save()
            
            return Response({
                'success': True,
                'matiere_code': matiere_code,
                'temps_passe_minutes': round(temps_passe / 60, 1),
                'temps_restant_matiere_minutes': round(examen.get_temps_restant_matiere(matiere_code) / 60, 1),
                'temps_total_minutes': round(examen.temps_total_en_secondes / 60, 1),
                'temps_restant_total_minutes': round(examen.get_temps_restant_total() / 60, 1)
            })
            
        except Exception as e:
            logger.error(f'Erreur lors de la mise à jour du temps: {e}')
            return Response({
                'error': 'Erreur lors de la mise à jour du temps'
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def statistiques_mensuelles(self, request):
        """Retourne les statistiques des examens nationaux du mois en cours"""
        try:
            from datetime import datetime, timedelta
            debut_mois = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            fin_mois = (debut_mois + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            
            # Examens du mois
            examens_mois = ExamenNational.objects.filter(
                date_examen__range=[debut_mois, fin_mois],
                terminee=True
            )
            
            # Statistiques générales
            total_participants = examens_mois.count()
            if total_participants == 0:
                return Response({
                    'total_participants': 0,
                    'score_moyen': 0,
                    'meilleur_score': 0,
                    'user_participation': False,
                    'message': 'Aucun examen terminé ce mois-ci'
                })
            
            scores = examens_mois.values_list('score', flat=True)
            score_moyen = sum(scores) / len(scores)
            meilleur_score = max(scores)
            
            # Participation de l'utilisateur actuel
            user_examen = examens_mois.filter(utilisateur=request.user).first()
            user_participation = {
                'a_participe': bool(user_examen),
                'score': float(user_examen.score) if user_examen else None,
                'rang': user_examen.rang_national if user_examen else None,
                'date_examen': user_examen.date_examen.isoformat() if user_examen else None
            }
            
            return Response({
                'total_participants': total_participants,
                'score_moyen': round(score_moyen, 2),
                'meilleur_score': round(meilleur_score, 2),
                'user_participation': user_participation,
                'periode': {
                    'debut': debut_mois.isoformat(),
                    'fin': fin_mois.isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f'Erreur lors du calcul des statistiques mensuelles: {e}')
            return Response({
                'error': 'Erreur lors du calcul des statistiques mensuelles'
            }, status=500)
    


class SessionExamenViewSet(viewsets.ModelViewSet):
    """ViewSet pour les sessions d'examen national"""
    queryset = SessionExamen.objects.all()
    serializer_class = SessionExamenSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def prochaines_sessions(self, request):
        """Retourne les prochaines sessions d'examen programmées"""
        from datetime import datetime
        
        sessions = SessionExamen.objects.filter(
            statut='programmee',
            date_debut__gte=timezone.now()
        ).order_by('date_debut')
        
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def inscrire(self, request, pk=None):
        """Inscrire l'utilisateur à une session d'examen"""
        session = self.get_object()
        user = request.user
        
        # Vérifier si l'utilisateur peut accéder aux examens nationaux
        evaluations = Evaluation.objects.filter(
            utilisateur=user,
            terminee=True
        )
        
        if not evaluations.exists():
            return Response(
                {'error': 'Vous devez d\'abord passer une évaluation.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        best_score = max(eval.score for eval in evaluations if eval.score is not None)
        if best_score < 50:
            return Response(
                {'error': 'Vous devez obtenir au moins 50% à l\'évaluation.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Créer ou récupérer la participation
        participation, created = ParticipationExamen.objects.get_or_create(
            utilisateur=user,
            session_examen=session,
            defaults={'inscrit': True}
        )
        
        if created:
            return Response({'message': 'Inscription réussie !'})
        else:
            return Response({'message': 'Vous êtes déjà inscrit à cette session.'})

# === Endpoint spécialisé pour l'import de questions ENA ===

from rest_framework.parsers import MultiPartParser, FormParser
import pandas as pd
import tempfile
import os

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def import_questions_ena_excel(request):
    """
    Import spécialisé pour les questions d'examen national ENA depuis un fichier Excel
    Utilise la classe ImportQuestionExamenExcel existante
    """
    if 'file' not in request.FILES:
        return Response({
            'success': False,
            'error': 'Aucun fichier fourni'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    uploaded_file = request.FILES['file']
    
    # Vérification du type de fichier
    if not uploaded_file.name.endswith(('.xlsx', '.xls')):
        return Response({
            'success': False,
            'error': 'Format de fichier non supporté. Utilisez un fichier Excel (.xlsx ou .xls)'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name
        
        # Importer la classe d'import existante
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            from import_questions_examen_excel import ImportQuestionExamenExcel
            
            # Créer une instance d'import
            import_instance = ImportQuestionExamenExcel(tmp_file_path)
            
            # Effectuer l'import
            rapport = import_instance.importer_questions()
            
            # Créer un enregistrement ImportExcel pour traçabilité
            import_record = ImportExcel.objects.create(
                utilisateur=request.user if hasattr(request.user, 'id') else None,
                fichier_nom=uploaded_file.name,
                import_type='questions',
                nombre_elements_importes=import_instance.questions_importees,
                nombre_echecs=import_instance.questions_echouees,
                status='completed' if import_instance.questions_echouees == 0 else 'completed',
                details={
                    'rapport': rapport,
                    'erreurs': import_instance.erreurs
                }
            )
            
            # Nettoyer le fichier temporaire
            os.unlink(tmp_file_path)
            
            return Response({
                'success': True,
                'rapport': {
                    'questions_importees': import_instance.questions_importees,
                    'questions_echouees': import_instance.questions_echouees,
                    'erreurs': import_instance.erreurs,
                    'details': rapport
                },
                'import_id': import_record.id
            }, status=status.HTTP_200_OK)
            
        except ImportError:
            # Fallback : utiliser la logique d'import directement
            return _import_questions_ena_fallback(tmp_file_path, uploaded_file.name, request.user)
            
    except Exception as e:
        # Nettoyer le fichier temporaire en cas d'erreur
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        
        logger.error(f"Erreur lors de l'import ENA: {str(e)}")
        return Response({
            'success': False,
            'error': f'Erreur lors de l\'import: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _import_questions_ena_fallback(file_path, file_name, user):
    """Logique d'import fallback intégrée"""
    try:
        # Lire le fichier Excel
        df = pd.read_excel(file_path)
        
        # Validation des colonnes requises
        colonnes_requises = ['texte', 'type_question', 'matiere_combinee']
        colonnes_manquantes = [col for col in colonnes_requises if col not in df.columns]
        
        if colonnes_manquantes:
            return Response({
                'success': False,
                'error': f'Colonnes manquantes: {", ".join(colonnes_manquantes)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        questions_importees = 0
        questions_echouees = 0
        erreurs = []
        
        for index, row in df.iterrows():
            try:
                # Générer un code unique pour la question
                code_question = f"ENA{timezone.now().year}-{row['matiere_combinee'][:3].upper()}-{str(index+1).zfill(3)}"
                
                # Créer la question d'examen
                question_data = {
                    'code_question': code_question,
                    'texte': str(row['texte']).strip(),
                    'type_question': row['type_question'],
                    'matiere_combinee': row['matiere_combinee'],
                    'difficulte': row.get('difficulte', 'moyen'),  # Valeur par défaut si non spécifiée
                    'active': True,
                    'validee': False
                }
                
                # Ajouter les choix pour les QCM
                if row['type_question'] in ['choix_unique', 'choix_multiple', 'vrai_faux']:
                    question_data.update({
                        'choix_a': str(row.get('choix_a', '')).strip() if pd.notna(row.get('choix_a')) else None,
                        'choix_b': str(row.get('choix_b', '')).strip() if pd.notna(row.get('choix_b')) else None,
                        'choix_c': str(row.get('choix_c', '')).strip() if pd.notna(row.get('choix_c')) else None,
                        'choix_d': str(row.get('choix_d', '')).strip() if pd.notna(row.get('choix_d')) else None,
                        'choix_e': str(row.get('choix_e', '')).strip() if pd.notna(row.get('choix_e')) else None,
                        'bonne_reponse': str(row.get('bonne_reponse', '')).strip() if pd.notna(row.get('bonne_reponse')) else None
                    })
                
                # Ajouter les champs optionnels
                if pd.notna(row.get('explication')):
                    question_data['explication'] = str(row['explication']).strip()
                
                if pd.notna(row.get('reponse_attendue')):
                    question_data['reponse_attendue'] = str(row['reponse_attendue']).strip()
                
                if pd.notna(row.get('temps_limite_secondes')):
                    question_data['temps_limite_secondes'] = int(row['temps_limite_secondes'])
                
                # Créer la question
                QuestionExamen.objects.create(**question_data)
                questions_importees += 1
                
            except Exception as e:
                questions_echouees += 1
                erreurs.append(f"Ligne {index+2}: {str(e)}")
        
        # Créer l'enregistrement d'import
        import_record = ImportExcel.objects.create(
            utilisateur=user if hasattr(user, 'id') else None,
            fichier_nom=file_name,
            import_type='questions',
            nombre_elements_importes=questions_importees,
            nombre_echecs=questions_echouees,
            status='completed',
            details={
                'erreurs': erreurs
            }
        )
        
        # Nettoyer le fichier temporaire
        os.unlink(file_path)
        
        return Response({
            'success': True,
            'rapport': {
                'questions_importees': questions_importees,
                'questions_echouees': questions_echouees,
                'erreurs': erreurs
            },
            'import_id': import_record.id
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur dans l'import fallback: {str(e)}")
        return Response({
            'success': False,
            'error': f'Erreur lors de l\'import: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def template_excel_ena(request):
    """
    Génère et retourne un template Excel pour l'import de questions ENA
    """
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            from generate_template_import_ena import generer_template_excel_ena
            
            # Générer le template
            file_path = generer_template_excel_ena()
            
            # Retourner le chemin du fichier généré
            return Response({
                'success': True,
                'message': 'Template Excel ENA généré avec succès',
                'file_path': file_path,
                'details': 'Template avec 10 exemples de questions et 3 feuilles (exemples, instructions, matières)'
            }, status=status.HTTP_200_OK)
            
        except ImportError:
            # Fallback : créer un template simple
            return _create_simple_template()
            
    except Exception as e:
        logger.error(f"Erreur lors de la génération du template: {str(e)}")
        return Response({
            'success': False,
            'error': f'Erreur lors de la génération du template: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _create_simple_template():
    """Crée un template Excel simple en fallback"""
    try:
        import pandas as pd
        from datetime import datetime
        
        # Données d'exemple pour le template
        exemple_data = {
            'texte': [
                'Quelle est la capitale de la France ?',
                'Le soleil se lève à l\'ouest.',
                'Expliquez brièvement le concept de démocratie.'
            ],
            'type_question': ['choix_unique', 'vrai_faux', 'texte_court'],
            'matiere_combinee': ['culture_aptitude', 'culture_aptitude', 'culture_aptitude'],
            'difficulte': ['facile', 'facile', 'moyen'],
            'choix_a': ['Paris', 'VRAI', ''],
            'choix_b': ['Londres', 'FAUX', ''],
            'choix_c': ['Berlin', '', ''],
            'choix_d': ['Madrid', '', ''],
            'choix_e': ['', '', ''],
            'bonne_reponse': ['A', 'FAUX', ''],
            'reponse_attendue': ['', '', 'gouvernement du peuple'],
            'explication': [
                'Paris est effectivement la capitale de la France.',
                'Le soleil se lève à l\'est, pas à l\'ouest.',
                'La démocratie est un système politique où le pouvoir appartient au peuple.'
            ],
            'temps_limite_secondes': [120, 60, 180]
        }
        
        df = pd.DataFrame(exemple_data)
        
        # Créer le fichier template
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        template_path = f"template_questions_examen_ena_{timestamp}.xlsx"
        
        df.to_excel(template_path, index=False)
        
        return Response({
            'success': True,
            'message': 'Template Excel simple généré avec succès',
            'file_path': template_path
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erreur lors de la création du template simple: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# === Endpoints pour les statistiques d'examens ===

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def exam_stats(request):
    """Statistiques d'examens pour l'utilisateur connecté"""
    user = request.user
    
    try:
        # Statistiques d'évaluations
        evaluations = Evaluation.objects.filter(utilisateur=user)
        evaluations_terminees = evaluations.filter(terminee=True)
        
        eval_stats = {
            'total': evaluations.count(),
            'terminees': evaluations_terminees.count(),
            'score_moyen': 0,
            'meilleur_score': 0
        }
        
        if evaluations_terminees.exists():
            scores_eval = [e.score for e in evaluations_terminees if e.score is not None]
            if scores_eval:
                eval_stats['score_moyen'] = round(sum(scores_eval) / len(scores_eval), 1)
                eval_stats['meilleur_score'] = round(max(scores_eval), 1)
        
        # Statistiques d'examens nationaux
        examens = ExamenNational.objects.filter(utilisateur=user)
        examens_termines = examens.filter(terminee=True)
        
        examen_stats = {
            'total': examens.count(),
            'termines': examens_termines.count(),
            'score_moyen': 0,
            'meilleur_score': 0,
            'meilleur_rang': None
        }
        
        if examens_termines.exists():
            scores_examen = [e.score for e in examens_termines if e.score is not None]
            if scores_examen:
                examen_stats['score_moyen'] = round(sum(scores_examen) / len(scores_examen), 1)
                examen_stats['meilleur_score'] = round(max(scores_examen), 1)
            
            # Meilleur rang
            rangs = [e.rang_national for e in examens_termines if e.rang_national is not None]
            if rangs:
                examen_stats['meilleur_rang'] = min(rangs)
        
        return Response({
            'evaluations': eval_stats,
            'examens_nationaux': examen_stats
        })
        
    except Exception as e:
        logger.error(f'Erreur calcul statistiques examens: {e}')
        return Response(
            {'error': 'Erreur lors du calcul des statistiques d\'examens'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# === ViewSets pour les compositions nationales ===

class SessionCompositionViewSet(viewsets.ModelViewSet):
    """ViewSet pour les sessions de composition nationale"""
    serializer_class = SessionCompositionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SessionComposition.objects.filter(utilisateur=self.request.user)
    
    def perform_create(self, serializer):
        # Définir les durées par matière
        durees_matieres = {
            'culture_aptitude': 90,  # 90 minutes
            'anglais': 45,           # 45 minutes
            'logique_combinee': 90   # 90 minutes
        }
        
        matiere_combinee = serializer.validated_data.get('matiere_combinee')
        duree_prevue = durees_matieres.get(matiere_combinee, 90)
        
        # Ajouter duree_prevue aux validated_data si pas fourni
        if 'duree_prevue' not in serializer.validated_data:
            serializer.validated_data['duree_prevue'] = duree_prevue
        
        serializer.save(
            utilisateur=self.request.user
        )
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Récupérer les questions pour une session de composition"""
        try:
            session = SessionComposition.objects.get(id=pk, utilisateur=request.user)
            
            # Nombre de questions par matière
            nombres_questions = {
                'culture_aptitude': 40,
                'anglais': 20,
                'logique_combinee': 40
            }
            
            # Noms des matières pour les questions de démo
            noms_matieres = {
                'culture_aptitude': 'Culture générale et Aptitude verbale',
                'anglais': 'Anglais',
                'logique_combinee': 'Logique d\'organisation et Logique numérique'
            }
            
            nombre_questions = nombres_questions.get(session.matiere_combinee, 40)
            nom_matiere = noms_matieres.get(session.matiere_combinee, session.matiere_combinee)
            
            # Récupérer les questions aléatoirement
            questions = QuestionExamen.objects.filter(
                matiere_combinee=session.matiere_combinee,
                active=True
            ).order_by('?')[:nombre_questions]
            
            # Si aucune question n'existe, générer des questions de démonstration
            if not questions.exists():
                logger.warning(f'Aucune question trouvée pour {session.matiere_combinee}, génération de questions de démonstration')
                questions_data = []
                for i in range(nombre_questions):
                    questions_data.append({
                        'id': i + 1,
                        'texte_question': f'Question {i + 1} de {nom_matiere} (démonstration)',
                        'type_question': 'choix_unique',
                        'choix': [
                            {'id': 'a', 'texte_choix': 'Option A', 'est_correcte': True},
                            {'id': 'b', 'texte_choix': 'Option B', 'est_correcte': False},
                            {'id': 'c', 'texte_choix': 'Option C', 'est_correcte': False},
                            {'id': 'd', 'texte_choix': 'Option D', 'est_correcte': False},
                        ]
                    })
                return Response(questions_data)
            
            # Sérialiser les questions avec les choix
            questions_data = []
            for question in questions:
                question_data = {
                    'id': question.id,
                    'texte_question': question.texte,
                    'type_question': question.type_question,
                    'choix': []
                }
                
                # Ajouter les choix depuis les champs du modèle QuestionExamen
                if question.type_question in ['choix_unique', 'choix_multiple']:
                    choix_map = {'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D'}
                    for lettre, label in choix_map.items():
                        choix_texte = getattr(question, f'choix_{lettre}', '')
                        if choix_texte:
                            question_data['choix'].append({
                                'id': lettre,
                                'texte_choix': choix_texte,
                                'est_correcte': question.bonne_reponse == label
                            })
                
                questions_data.append(question_data)
            
            return Response(questions_data)
            
        except SessionComposition.DoesNotExist:
            return Response(
                {'error': 'Session non trouvée'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f'Erreur récupération questions composition: {e}')
            return Response(
                {'error': 'Erreur lors de la récupération des questions'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# --- ViewSets pour Second Tour ENA ---
class ContenuPedagogiqueViewSet(viewsets.ModelViewSet):
    """ViewSet pour les contenus pédagogiques du second tour ENA"""
    queryset = ContenuPedagogique.objects.all()
    serializer_class = ContenuPedagogiqueSerializer
    permission_classes = [AllowAny]  # Permettre toutes les actions pour les tests

    def get_queryset(self):
        qs = super().get_queryset()
        matiere_id = self.request.query_params.get('matiere')
        cycle_id = self.request.query_params.get('cycle')
        search = self.request.query_params.get('search')
        
        if matiere_id:
            qs = qs.filter(matiere_id=matiere_id)
        
        if cycle_id:
            qs = qs.filter(matiere__cycle_id=cycle_id)
            
        if search:
            qs = qs.filter(
                models.Q(titre__icontains=search) | 
                models.Q(description__icontains=search)
            )
        
        return qs.order_by('ordre', 'titre')

    @action(detail=False, methods=['get'], url_path='by-matiere')
    def by_matiere(self, request):
        """Récupère les contenus pédagogiques par matière avec pagination"""
        matiere_id = request.query_params.get('matiere')
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 6))
        search = request.query_params.get('search', '')
        
        # Validation du paramètre matiere_id
        if not matiere_id or matiere_id == 'undefined' or matiere_id == 'null':
            return Response({'detail': 'Le paramètre matiere est requis et doit être un ID valide'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier que matiere_id est un entier valide
        try:
            matiere_id = int(matiere_id)
        except (ValueError, TypeError):
            return Response({'detail': 'Le paramètre matiere doit être un nombre entier'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filtrer les contenus
        contenus = ContenuPedagogique.objects.filter(
            matiere_id=matiere_id,
            active=True
        )
        
        if search:
            contenus = contenus.filter(
                models.Q(titre__icontains=search) | 
                models.Q(description__icontains=search)
            )
        
        # Pagination manuelle
        total = contenus.count()
        start = (page - 1) * per_page
        end = start + per_page
        contenus_page = contenus.order_by('ordre', 'titre')[start:end]
        
        # Sérialiser les données
        serializer = self.get_serializer(contenus_page, many=True)
        
        return Response({
            'results': serializer.data,
            'count': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
    
    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """Soumettre une réponse pour une question"""
        try:
            session = SessionComposition.objects.get(id=pk, utilisateur=request.user)
            question_id = request.data.get('question_id')
            reponse_donnee = request.data.get('reponse_donnee', '')
            temps_reponse = request.data.get('temps_reponse', 0)
            
            if not question_id:
                return Response(
                    {'error': 'question_id requis'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                question = QuestionExamen.objects.get(id=question_id)
            except QuestionExamen.DoesNotExist:
                return Response(
                    {'error': 'Question non trouvée'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Vérifier si la réponse est correcte
            est_correcte = False
            
            # Pour les QCM, vérifier si la lettre correspond à la bonne réponse
            if question.type_question in ['choix_unique', 'choix_multiple', 'vrai_faux']:
                bonne_reponse = question.bonne_reponse or ''
                reponse_upper = reponse_donnee.upper().strip()
                
                if question.type_question == 'choix_multiple':
                    # Pour les choix multiples, comparer les ensembles de lettres
                    bonnes_lettres = set(bonne_reponse.upper().replace(',', '').replace(' ', ''))
                    reponses_lettres = set(reponse_upper.replace(',', '').replace(' ', ''))
                    est_correcte = bonnes_lettres == reponses_lettres
                else:
                    # Pour choix unique et vrai/faux
                    est_correcte = reponse_upper == bonne_reponse.upper().strip()
            elif question.type_question in ['texte_court', 'texte_long']:
                # Pour les questions textuelles, comparer avec reponse_attendue
                reponse_attendue = question.reponse_attendue or ''
                est_correcte = reponse_donnee.strip().lower() == reponse_attendue.strip().lower()
            
            # Créer ou mettre à jour la réponse
            reponse, created = ReponseComposition.objects.update_or_create(
                session_composition=session,
                question_examen=question,
                defaults={
                    'reponse_donnee': reponse_donnee,
                    'est_correcte': est_correcte,
                    'temps_reponse': temps_reponse
                }
            )
            
            return Response({
                'success': True,
                'est_correct': est_correcte,
                'est_correcte': est_correcte,
                'reponse_id': reponse.id,
                'explication': question.explication or '',
                'bonne_reponse': question.bonne_reponse or ''
            })
            
        except Exception as e:
            logger.error(f'Erreur soumission réponse composition: {e}')
            return Response(
                {'error': 'Erreur lors de la soumission de la réponse'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        """Terminer une session de composition et calculer le score"""
        try:
            session = SessionComposition.objects.get(id=pk, utilisateur=request.user)
            
            if session.est_terminee:
                return Response(
                    {'error': 'Cette session est déjà terminée'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Marquer la session comme terminée
            session.date_fin = timezone.now()
            session.est_terminee = True
            
            # Calculer le score final
            score_final = session.calculer_score()
            
            return Response({
                'success': True,
                'score_final': score_final,
                'bonnes_reponses': session.nombre_bonnes_reponses,
                'total_questions': session.nombre_total_questions,
                'nombre_bonnes_reponses': session.nombre_bonnes_reponses,
                'nombre_total_questions': session.nombre_total_questions,
                'pourcentage': (session.nombre_bonnes_reponses / session.nombre_total_questions * 100) if session.nombre_total_questions > 0 else 0
            })
            
        except Exception as e:
            logger.error(f'Erreur finalisation composition: {e}')
            return Response(
                {'error': 'Erreur lors de la finalisation de la composition'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_questions_disponibles(request):
    """
    Vérifie le nombre de questions disponibles pour une matière/leçon.
    Utile pour le debug.
    """
    matiere_id = request.query_params.get('matiere_id')
    lecon_id = request.query_params.get('lecon_id')
    lecon_nom = request.query_params.get('lecon_nom')
    
    result = {
        'matiere_id': matiere_id,
        'lecon_id': lecon_id,
        'lecon_nom': lecon_nom,
        'questions_count': 0,
        'questions_avec_choix': 0,
        'lecons_disponibles': [],
        'details': []
    }
    
    try:
        # Si on cherche par nom de leçon
        if lecon_nom:
            lecons = Lecon.objects.filter(nom__icontains=lecon_nom)
            result['lecons_trouvees'] = [
                {'id': l.id, 'nom': l.nom, 'matiere_id': l.matiere_id, 'matiere_nom': l.matiere.nom}
                for l in lecons
            ]
            if lecons.exists():
                lecon_id = lecons.first().id
                result['lecon_id_utilise'] = lecon_id
        
        # Lister toutes les leçons pour la matière
        if matiere_id:
            lecons_matiere = Lecon.objects.filter(matiere_id=matiere_id)
            result['lecons_disponibles'] = [
                {'id': l.id, 'nom': l.nom, 'nb_questions': Question.objects.filter(lecon=l).count()}
                for l in lecons_matiere
            ]
        
        if lecon_id:
            questions = Question.objects.filter(lecon_id=lecon_id).prefetch_related('choix')
            result['filter'] = f'lecon_id={lecon_id}'
            # Récupérer les infos de la leçon
            try:
                lecon = Lecon.objects.get(id=lecon_id)
                result['lecon_info'] = {
                    'id': lecon.id,
                    'nom': lecon.nom,
                    'matiere_id': lecon.matiere_id,
                    'matiere_nom': lecon.matiere.nom
                }
            except Lecon.DoesNotExist:
                result['lecon_info'] = 'Leçon non trouvée!'
        elif matiere_id:
            questions = Question.objects.filter(matiere_id=matiere_id).prefetch_related('choix')
            result['filter'] = f'matiere_id={matiere_id}'
        else:
            # Afficher les statistiques globales
            result['total_questions'] = Question.objects.count()
            result['questions_avec_lecon'] = Question.objects.exclude(lecon__isnull=True).count()
            result['questions_sans_lecon'] = Question.objects.filter(lecon__isnull=True).count()
            return Response(result)
        
        result['questions_count'] = questions.count()
        result['questions_avec_choix'] = sum(1 for q in questions if q.choix.exists())
        
        # Détails des 10 premières questions
        for q in questions[:10]:
            result['details'].append({
                'id': q.id,
                'texte': q.texte[:50] + '...' if len(q.texte) > 50 else q.texte,
                'type': q.type_question,
                'nb_choix': q.choix.count(),
                'lecon_id': q.lecon_id,
                'lecon_nom': q.lecon.nom if q.lecon else None,
                'matiere_id': q.matiere_id
            })
        
        return Response(result)
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def import_questions_excel(request):
    """
    Import des questions régulières (Question model) depuis un fichier Excel.
    Colonnes requises: texte, type_question, matiere_nom, lecon_nom
    Colonnes optionnelles: choix_a, choix_b, choix_c, choix_d, bonne_reponse, explication, reponse_attendue
    """
    if 'file' not in request.FILES:
        return Response({
            'success': False,
            'error': 'Aucun fichier fourni'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    uploaded_file = request.FILES['file']
    
    if not uploaded_file.name.endswith(('.xlsx', '.xls')):
        return Response({
            'success': False,
            'error': 'Format de fichier non supporté. Utilisez un fichier Excel (.xlsx ou .xls)'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        import tempfile
        import pandas as pd
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name
        
        # Lire le fichier Excel
        df = pd.read_excel(tmp_file_path)
        
        # Validation des colonnes requises
        colonnes_requises = ['texte', 'type_question', 'matiere_nom', 'lecon_nom']
        colonnes_manquantes = [col for col in colonnes_requises if col not in df.columns]
        
        if colonnes_manquantes:
            os.unlink(tmp_file_path)
            return Response({
                'success': False,
                'error': f'Colonnes manquantes: {", ".join(colonnes_manquantes)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        questions_importees = 0
        questions_echouees = 0
        erreurs = []
        
        for index, row in df.iterrows():
            try:
                matiere_nom = str(row['matiere_nom']).strip()
                lecon_nom = str(row['lecon_nom']).strip()
                
                # Trouver ou créer la matière
                matiere = Matiere.objects.filter(nom__iexact=matiere_nom).first()
                if not matiere:
                    erreurs.append(f"Ligne {index+2}: Matière '{matiere_nom}' non trouvée")
                    questions_echouees += 1
                    continue
                
                # Trouver ou créer la leçon
                lecon = Lecon.objects.filter(nom__iexact=lecon_nom, matiere=matiere).first()
                if not lecon:
                    # Créer la leçon si elle n'existe pas
                    lecon = Lecon.objects.create(nom=lecon_nom, matiere=matiere)
                    logger.info(f"Leçon créée: {lecon_nom} pour matière {matiere_nom}")
                
                # Récupérer l'image base64 si présente
                image_base64 = None
                if pd.notna(row.get('image_base64')) and str(row.get('image_base64', '')).strip():
                    image_base64 = str(row['image_base64']).strip()
                
                # Créer la question
                question = Question.objects.create(
                    texte=str(row['texte']).strip(),
                    type_question=row['type_question'],
                    matiere=matiere,
                    lecon=lecon,
                    image_base64=image_base64,
                    explication=str(row.get('explication', '')).strip() if pd.notna(row.get('explication')) else None,
                    reponse_attendue=str(row.get('reponse_attendue', '')).strip() if pd.notna(row.get('reponse_attendue')) else None
                )
                
                # Créer les choix pour les QCM
                if row['type_question'] in ['choix_unique', 'choix_multiple']:
                    bonne_reponse = str(row.get('bonne_reponse', '')).upper().strip() if pd.notna(row.get('bonne_reponse')) else ''
                    
                    choix_mapping = [
                        ('choix_a', 'A'),
                        ('choix_b', 'B'),
                        ('choix_c', 'C'),
                        ('choix_d', 'D')
                    ]
                    
                    for col_name, lettre in choix_mapping:
                        if pd.notna(row.get(col_name)) and str(row[col_name]).strip():
                            est_correct = lettre in bonne_reponse
                            Choix.objects.create(
                                question=question,
                                texte=str(row[col_name]).strip(),
                                est_correct=est_correct
                            )
                
                elif row['type_question'] == 'vrai_faux':
                    bonne_reponse = str(row.get('bonne_reponse', '')).upper().strip() if pd.notna(row.get('bonne_reponse')) else ''
                    Choix.objects.create(question=question, texte='Vrai', est_correct=(bonne_reponse == 'VRAI'))
                    Choix.objects.create(question=question, texte='Faux', est_correct=(bonne_reponse == 'FAUX'))
                
                questions_importees += 1
                
            except Exception as e:
                erreurs.append(f"Ligne {index+2}: {str(e)}")
                questions_echouees += 1
        
        # Nettoyer le fichier temporaire
        os.unlink(tmp_file_path)
        
        return Response({
            'success': True,
            'rapport': {
                'questions_importees': questions_importees,
                'questions_echouees': questions_echouees,
                'erreurs': erreurs[:20]  # Limiter à 20 erreurs
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f'Erreur import questions Excel: {e}')
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def template_excel_questions(request):
    """
    Génère un template Excel pour l'import des questions régulières.
    """
    import pandas as pd
    from django.http import HttpResponse
    import io
    
    # Créer un DataFrame avec les colonnes requises et des exemples
    data = {
        'texte': ['Quelle est la capitale de la France ?', 'Le soleil tourne autour de la terre.', 'Quels sont les océans ?', 'Trouvez le nombre manquant dans la série'],
        'type_question': ['choix_unique', 'vrai_faux', 'choix_multiple', 'choix_unique'],
        'matiere_nom': ['Culture Générale', 'Sciences', 'Géographie', 'Logique numérique'],
        'lecon_nom': ['Géographie mondiale', 'Astronomie', 'Les océans', 'Séries numériques'],
        'choix_a': ['Paris', '', 'Atlantique', '25'],
        'choix_b': ['Londres', '', 'Pacifique', '30'],
        'choix_c': ['Berlin', '', 'Indien', '35'],
        'choix_d': ['Madrid', '', 'Arctique', '40'],
        'bonne_reponse': ['A', 'FAUX', 'A,B,C,D', 'A'],
        'explication': ['Paris est la capitale de la France depuis...', 'C\'est la Terre qui tourne autour du Soleil.', 'Il y a 5 océans principaux.', 'La suite suit le pattern +5'],
        'reponse_attendue': ['', '', '', ''],
        'image_base64': ['', '', '', 'data:image/png;base64,... (collez ici l\'image encodée en base64)']
    }
    
    df = pd.DataFrame(data)
    
    # Créer le fichier Excel en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Questions')
    
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=template_import_questions.xlsx'
    
    return response


# === ViewSets pour les abonnements ===

from .models import Plan, Abonnement, Transaction, QuotaUtilisation
from .serializers import (
    PlanSerializer, AbonnementSerializer, TransactionSerializer,
    InitierPaiementSerializer, QuotaUtilisationSerializer, StatutAbonnementSerializer
)
import uuid
import requests
import hashlib

# Configuration CinetPay
CINETPAY_API_KEY = "81368248165f9bc085b6f97.83290781"
CINETPAY_SITE_ID = "5866272"
CINETPAY_SECRET_KEY = "1905618043656f094465a831.25769262"
CINETPAY_BASE_URL = "https://api-checkout.cinetpay.com/v2"


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour lister les plans d'abonnement disponibles"""
    queryset = Plan.objects.filter(est_actif=True)
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]  # Plans visibles par tous
    
    def get_queryset(self):
        return Plan.objects.filter(est_actif=True).order_by('ordre_affichage')


class AbonnementViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les abonnements utilisateur"""
    serializer_class = AbonnementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Abonnement.objects.filter(utilisateur=self.request.user)
    
    @action(detail=False, methods=['get'])
    def actif(self, request):
        """Récupère l'abonnement actif de l'utilisateur"""
        abonnement = Abonnement.get_abonnement_actif(request.user)
        if abonnement:
            serializer = self.get_serializer(abonnement)
            return Response(serializer.data)
        return Response({'detail': 'Aucun abonnement actif'}, status=404)
    
    @action(detail=False, methods=['get'])
    def statut(self, request):
        """Récupère le statut complet d'abonnement de l'utilisateur"""
        abonnement = Abonnement.get_abonnement_actif(request.user)
        
        peut_poser, message = QuotaUtilisation.peut_poser_question(request.user)
        quota = QuotaUtilisation.get_ou_creer_quota_jour(request.user)
        
        questions_restantes = None
        if abonnement and abonnement.plan.questions_par_jour > 0:
            questions_restantes = max(0, abonnement.plan.questions_par_jour - quota.questions_utilisees)
        
        data = {
            'a_abonnement_actif': abonnement is not None,
            'abonnement': AbonnementSerializer(abonnement).data if abonnement else None,
            'peut_poser_question': peut_poser,
            'message_quota': message,
            'questions_utilisees_aujourdhui': quota.questions_utilisees,
            'questions_restantes_aujourdhui': questions_restantes
        }
        
        return Response(data)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour consulter l'historique des transactions"""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(utilisateur=self.request.user)


class PaiementViewSet(viewsets.ViewSet):
    """ViewSet pour gérer les paiements CinetPay"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def initier(self, request):
        """Initie un paiement CinetPay pour un plan d'abonnement"""
        serializer = InitierPaiementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        plan_id = serializer.validated_data['plan_id']
        telephone = serializer.validated_data.get('telephone', '')
        
        try:
            plan = Plan.objects.get(id=plan_id, est_actif=True)
        except Plan.DoesNotExist:
            return Response({'detail': 'Plan invalide'}, status=400)
        
        # 🆓 Gestion des plans gratuits (prix = 0)
        if plan.prix == 0:
            # Créer directement l'abonnement sans passer par CinetPay
            from datetime import timedelta
            from django.utils import timezone
            
            # Calculer la date de fin selon la durée du plan
            date_debut = timezone.now()
            if plan.duree == '24h':
                date_fin = date_debut + timedelta(hours=24)
            elif plan.duree == '1_mois':
                date_fin = date_debut + timedelta(days=30)
            elif plan.duree == '12_mois':
                date_fin = date_debut + timedelta(days=365)
            else:
                date_fin = date_debut + timedelta(hours=24)
            
            # Désactiver les anciens abonnements
            Abonnement.objects.filter(utilisateur=request.user, statut='actif').update(statut='annule')
            
            # Créer le nouvel abonnement
            abonnement = Abonnement.objects.create(
                utilisateur=request.user,
                plan=plan,
                date_debut=date_debut,
                date_fin=date_fin,
                statut='actif'
            )
            
            # Créer une transaction pour traçabilité
            transaction_id = f"PREPA-FREE-{uuid.uuid4().hex[:8].upper()}"
            Transaction.objects.create(
                utilisateur=request.user,
                plan=plan,
                transaction_id=transaction_id,
                montant=0,
                statut='success'
            )
            
            logger.info(f"[PLAN GRATUIT] Abonnement activé pour {request.user.email}: {plan.nom}")
            
            return Response({
                'success': True,
                'message': f'Plan {plan.nom} activé avec succès !',
                'abonnement_id': abonnement.id,
                'date_fin': date_fin.isoformat()
            })
        
        # Générer un ID de transaction unique
        transaction_id = f"PREPA-{uuid.uuid4().hex[:12].upper()}"
        
        # Créer la transaction en base
        transaction = Transaction.objects.create(
            utilisateur=request.user,
            plan=plan,
            transaction_id=transaction_id,
            montant=plan.prix,
            telephone=telephone
        )
        
        # Préparer les données pour CinetPay
        cinetpay_data = {
            "apikey": CINETPAY_API_KEY,
            "site_id": CINETPAY_SITE_ID,
            "transaction_id": transaction_id,
            "amount": plan.prix,
            "currency": "XAF",
            "description": f"Abonnement {plan.nom} - Prépa Concours",
            "customer_name": request.user.nom_complet or request.user.email,
            "customer_surname": "",
            "customer_email": request.user.email,
            "customer_phone_number": telephone or request.user.telephone or "",
            "customer_address": "",
            "customer_city": "Douala",
            "customer_country": "CM",
            "customer_state": "CM",
            "customer_zip_code": "",
            "notify_url": "https://api-concours.numerix.digital/api/paiement/webhook/",
            "return_url": "https://api-concours.numerix.digital/api/paiement/retour/",
            "channels": "ALL",
            "metadata": f"plan_id:{plan.id},user_id:{request.user.id}",
            "lang": "FR",
            "invoice_data": {
                "items": [
                    {
                        "name": plan.nom,
                        "quantity": 1,
                        "unit_price": plan.prix
                    }
                ]
            }
        }
        
        try:
            # Appel à l'API CinetPay
            response = requests.post(
                f"{CINETPAY_BASE_URL}/payment",
                json=cinetpay_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            logger.info(f"[CINETPAY] Status code: {response.status_code}")
            logger.info(f"[CINETPAY] Réponse brute: {response.text[:500] if response.text else 'VIDE'}")
            
            # Vérifier si la réponse est vide
            if not response.text:
                transaction.statut = 'failed'
                transaction.save()
                return Response({'detail': 'CinetPay a retourné une réponse vide'}, status=502)
            
            try:
                result = response.json()
            except ValueError as json_err:
                logger.error(f"[CINETPAY] Erreur JSON: {json_err}, Réponse: {response.text[:200]}")
                transaction.statut = 'failed'
                transaction.save()
                return Response({'detail': 'Réponse CinetPay invalide'}, status=502)
            
            logger.info(f"[CINETPAY] Réponse initiation: {result}")
            
            if result.get('code') == '201':
                # Succès - Mise à jour de la transaction
                payment_data = result.get('data', {})
                transaction.payment_token = payment_data.get('payment_token')
                transaction.payment_url = payment_data.get('payment_url')
                transaction.cinetpay_response = result
                transaction.save()
                
                return Response({
                    'success': True,
                    'transaction_id': transaction_id,
                    'payment_url': payment_data.get('payment_url'),
                    'payment_token': payment_data.get('payment_token'),
                    'montant': plan.prix,
                    'plan': plan.nom
                })
            else:
                # Erreur CinetPay
                transaction.statut = 'failed'
                transaction.cinetpay_response = result
                transaction.save()
                
                return Response({
                    'success': False,
                    'detail': result.get('message', 'Erreur lors de l\'initiation du paiement'),
                    'code': result.get('code')
                }, status=400)
                
        except requests.exceptions.Timeout:
            transaction.statut = 'failed'
            transaction.save()
            return Response({'detail': 'Timeout lors de la connexion à CinetPay'}, status=504)
        except Exception as e:
            logger.error(f"[CINETPAY] Erreur initiation: {str(e)}")
            transaction.statut = 'failed'
            transaction.save()
            return Response({'detail': f'Erreur: {str(e)}'}, status=500)
    
    @action(detail=False, methods=['post'])
    def verifier(self, request):
        """Vérifie le statut d'une transaction"""
        transaction_id = request.data.get('transaction_id')
        
        if not transaction_id:
            return Response({'detail': 'transaction_id requis'}, status=400)
        
        try:
            transaction = Transaction.objects.get(
                transaction_id=transaction_id,
                utilisateur=request.user
            )
        except Transaction.DoesNotExist:
            return Response({'detail': 'Transaction non trouvée'}, status=404)
        
        # Vérifier le statut auprès de CinetPay
        check_data = {
            "apikey": CINETPAY_API_KEY,
            "site_id": CINETPAY_SITE_ID,
            "transaction_id": transaction_id
        }
        
        try:
            response = requests.post(
                f"{CINETPAY_BASE_URL}/payment/check",
                json=check_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            result = response.json()
            logger.info(f"[CINETPAY] Vérification {transaction_id}: {result}")
            
            if result.get('code') == '00':
                data = result.get('data', {})
                status = data.get('status')
                
                if status == 'ACCEPTED':
                    # Paiement accepté - Activer l'abonnement
                    self._activer_abonnement(transaction, data)
                    return Response({
                        'success': True,
                        'statut': 'success',
                        'message': 'Paiement confirmé, abonnement activé'
                    })
                elif status == 'REFUSED':
                    transaction.statut = 'failed'
                    transaction.cinetpay_response = result
                    transaction.save()
                    return Response({
                        'success': False,
                        'statut': 'failed',
                        'message': 'Paiement refusé'
                    })
                else:
                    return Response({
                        'success': False,
                        'statut': 'pending',
                        'message': 'Paiement en attente'
                    })
            else:
                return Response({
                    'success': False,
                    'detail': result.get('message', 'Erreur de vérification')
                }, status=400)
                
        except Exception as e:
            logger.error(f"[CINETPAY] Erreur vérification: {str(e)}")
            return Response({'detail': f'Erreur: {str(e)}'}, status=500)
    
    def _activer_abonnement(self, transaction, cinetpay_data):
        """Active l'abonnement après paiement réussi"""
        from datetime import timedelta
        
        plan = transaction.plan
        
        # Calculer la date de fin selon la durée du plan
        if plan.duree == '24h':
            date_fin = timezone.now() + timedelta(hours=24)
        elif plan.duree == '1_mois':
            date_fin = timezone.now() + timedelta(days=30)
        elif plan.duree == '12_mois':
            date_fin = timezone.now() + timedelta(days=365)
        else:
            date_fin = timezone.now() + timedelta(days=30)
        
        # Créer l'abonnement
        abonnement = Abonnement.objects.create(
            utilisateur=transaction.utilisateur,
            plan=plan,
            date_fin=date_fin,
            statut='actif',
            transaction_id=transaction.transaction_id
        )
        
        # Mettre à jour la transaction
        transaction.abonnement = abonnement
        transaction.statut = 'success'
        transaction.date_paiement = timezone.now()
        transaction.methode_paiement = cinetpay_data.get('payment_method', '')
        transaction.cinetpay_transaction_id = cinetpay_data.get('cpm_trans_id', '')
        transaction.cinetpay_response = cinetpay_data
        transaction.save()
        
        logger.info(f"[ABONNEMENT] Activé pour {transaction.utilisateur.email} - Plan: {plan.nom}")


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def cinetpay_webhook(request):
    """Webhook appelé par CinetPay pour notifier le statut du paiement"""
    logger.info(f"[CINETPAY WEBHOOK] Données reçues: {request.data}")
    
    # Récupérer les données du webhook
    cpm_trans_id = request.data.get('cpm_trans_id')
    cpm_site_id = request.data.get('cpm_site_id')
    cpm_trans_status = request.data.get('cpm_trans_status')
    cpm_custom = request.data.get('cpm_custom')  # Notre transaction_id
    
    if not cpm_custom:
        return Response({'status': 'error', 'message': 'transaction_id manquant'}, status=400)
    
    try:
        transaction = Transaction.objects.get(transaction_id=cpm_custom)
    except Transaction.DoesNotExist:
        logger.error(f"[CINETPAY WEBHOOK] Transaction non trouvée: {cpm_custom}")
        return Response({'status': 'error', 'message': 'Transaction non trouvée'}, status=404)
    
    # Vérifier le statut auprès de CinetPay pour confirmer
    check_data = {
        "apikey": CINETPAY_API_KEY,
        "site_id": CINETPAY_SITE_ID,
        "transaction_id": cpm_custom
    }
    
    try:
        response = requests.post(
            f"{CINETPAY_BASE_URL}/payment/check",
            json=check_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        result = response.json()
        
        if result.get('code') == '00':
            data = result.get('data', {})
            status = data.get('status')
            
            if status == 'ACCEPTED' and transaction.statut != 'success':
                # Activer l'abonnement
                paiement_viewset = PaiementViewSet()
                paiement_viewset._activer_abonnement(transaction, data)
                logger.info(f"[CINETPAY WEBHOOK] Abonnement activé via webhook: {cpm_custom}")
            elif status == 'REFUSED':
                transaction.statut = 'failed'
                transaction.cinetpay_response = result
                transaction.save()
                
    except Exception as e:
        logger.error(f"[CINETPAY WEBHOOK] Erreur: {str(e)}")
    
    return Response({'status': 'ok'})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def cinetpay_retour(request):
    """Page de retour après paiement CinetPay"""
    transaction_id = request.GET.get('transaction_id')
    
    # Rediriger vers l'app mobile avec le statut
    # En production, utiliser un deep link vers l'app
    return Response({
        'message': 'Paiement traité',
        'transaction_id': transaction_id,
        'instruction': 'Vous pouvez fermer cette page et retourner à l\'application'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def import_questions_evaluation(request):
    """
    Import des questions d'évaluation ENA depuis un fichier Excel.
    Colonnes requises: texte, type_question, matiere_nom, lecon_nom
    Colonnes optionnelles: choix_a, choix_b, choix_c, choix_d, bonne_reponse, explication, difficulte
    
    IMPORTANT: Les questions doivent être liées à une leçon pour être utilisées dans les évaluations ENA.
    """
    import pandas as pd
    import tempfile
    import os
    
    if 'file' not in request.FILES:
        return Response({
            'success': False,
            'error': 'Aucun fichier fourni'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    uploaded_file = request.FILES['file']
    
    # Sauvegarder temporairement le fichier
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        for chunk in uploaded_file.chunks():
            tmp_file.write(chunk)
        tmp_file_path = tmp_file.name
    
    try:
        # Lire le fichier Excel
        df = pd.read_excel(tmp_file_path, engine='openpyxl')
        
        questions_importees = 0
        questions_echouees = 0
        erreurs = []
        
        for index, row in df.iterrows():
            try:
                # Récupérer les données
                texte = str(row.get('texte', '')).strip()
                type_question = str(row.get('type_question', 'choix_unique')).strip()
                matiere_nom = str(row.get('matiere_nom', '')).strip()
                lecon_nom = str(row.get('lecon_nom', '')).strip() if pd.notna(row.get('lecon_nom')) else ''
                difficulte = str(row.get('difficulte', 'moyen')).strip()
                explication = str(row.get('explication', '')).strip() if pd.notna(row.get('explication')) else ''
                
                if not texte or not matiere_nom:
                    erreurs.append(f"Ligne {index + 2}: texte ou matiere_nom manquant")
                    questions_echouees += 1
                    continue
                
                # Trouver la matière ENA
                try:
                    matiere = Matiere.objects.get(nom__iexact=matiere_nom, choix_concours='ENA')
                except Matiere.DoesNotExist:
                    # Essayer sans le filtre ENA pour un message d'erreur plus précis
                    matiere_existe = Matiere.objects.filter(nom__iexact=matiere_nom).exists()
                    if matiere_existe:
                        erreurs.append(f"Ligne {index + 2}: Matière '{matiere_nom}' existe mais n'est pas une matière ENA")
                    else:
                        erreurs.append(f"Ligne {index + 2}: Matière ENA '{matiere_nom}' non trouvée")
                    questions_echouees += 1
                    continue
                
                # Trouver ou créer la leçon
                lecon = None
                if lecon_nom:
                    try:
                        lecon = Lecon.objects.get(nom__iexact=lecon_nom, matiere=matiere)
                    except Lecon.DoesNotExist:
                        # Créer la leçon si elle n'existe pas
                        lecon = Lecon.objects.create(
                            nom=lecon_nom,
                            matiere=matiere,
                            ordre=Lecon.objects.filter(matiere=matiere).count() + 1
                        )
                        logger.info(f"Leçon '{lecon_nom}' créée pour la matière '{matiere_nom}'")
                else:
                    # Utiliser la première leçon de la matière ou en créer une par défaut
                    lecon = Lecon.objects.filter(matiere=matiere).first()
                    if not lecon:
                        lecon = Lecon.objects.create(
                            nom=f"Questions {matiere_nom}",
                            matiere=matiere,
                            ordre=1
                        )
                        logger.info(f"Leçon par défaut créée pour la matière '{matiere_nom}'")
                
                # Créer la question avec la leçon (IMPORTANT pour les évaluations)
                question = Question.objects.create(
                    texte=texte,
                    type_question=type_question,
                    matiere=matiere,
                    lecon=lecon,  # IMPORTANT: La leçon est requise pour les évaluations
                    explication=explication,
                    choix_concours='ENA'
                )
                
                # Créer les choix si c'est une question à choix
                if type_question in ['choix_unique', 'choix_multiple']:
                    bonne_reponse = str(row.get('bonne_reponse', '')).upper().strip() if pd.notna(row.get('bonne_reponse')) else ''
                    
                    for lettre in ['a', 'b', 'c', 'd', 'e']:
                        choix_texte = row.get(f'choix_{lettre}')
                        if pd.notna(choix_texte) and str(choix_texte).strip():
                            est_correct = (lettre.upper() == bonne_reponse)
                            Choix.objects.create(
                                question=question,
                                texte=str(choix_texte).strip(),
                                est_correct=est_correct
                            )
                
                questions_importees += 1
                
            except Exception as e:
                erreurs.append(f"Ligne {index + 2}: {str(e)}")
                questions_echouees += 1
        
        # Créer l'enregistrement d'import
        ImportExcel.objects.create(
            utilisateur=request.user,
            fichier_nom=uploaded_file.name,
            import_type='questions_evaluation_ena',
            nombre_questions_importees=questions_importees
        )
        
        return Response({
            'success': True,
            'rapport': {
                'questions_importees': questions_importees,
                'questions_echouees': questions_echouees,
                'erreurs': erreurs[:20]  # Limiter à 20 erreurs
            }
        })
        
    except Exception as e:
        logger.error(f'Erreur import questions évaluation: {e}')
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        # Nettoyer le fichier temporaire
        try:
            os.unlink(tmp_file_path)
        except:
            pass


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def template_excel_evaluation(request):
    """
    Génère et retourne un template Excel pour l'import des questions d'évaluation ENA
    Les matières ENA valides sont : Culture Générale, Aptitude verbale, Logique numérique, etc.
    """
    import pandas as pd
    from django.http import HttpResponse
    from io import BytesIO
    
    # Récupérer les matières ENA disponibles pour les afficher dans le template
    matieres_ena = list(Matiere.objects.filter(choix_concours='ENA').values_list('nom', flat=True).distinct())
    matieres_info = ', '.join(matieres_ena[:10]) if matieres_ena else 'Culture Générale, Aptitude verbale, Logique numérique'
    
    # Créer les données d'exemple avec les vraies matières ENA
    data = {
        'texte': [
            'Quelle est la capitale du Sénégal ?',
            'Quel mot est le synonyme de "perspicace" ?',
            'Dans la suite 2, 4, 8, 16, quel est le nombre suivant ?',
            'Qui est le premier président du Sénégal ?',
            'Quel est le résultat de 15 x 8 ?'
        ],
        'type_question': ['choix_unique', 'choix_unique', 'choix_unique', 'choix_unique', 'choix_unique'],
        'matiere_nom': ['Culture Générale', 'Aptitude verbale', 'Logique numérique', 'Culture Générale', 'Logique numérique'],
        'lecon_nom': ['Géographie', 'Vocabulaire', 'Suites numériques', 'Histoire politique', 'Calcul mental'],
        'choix_a': ['Dakar', 'Clairvoyant', '24', 'Léopold Sédar Senghor', '100'],
        'choix_b': ['Abidjan', 'Naïf', '32', 'Abdou Diouf', '120'],
        'choix_c': ['Bamako', 'Confus', '20', 'Abdoulaye Wade', '115'],
        'choix_d': ['Lomé', 'Lent', '48', 'Macky Sall', '125'],
        'bonne_reponse': ['A', 'A', 'B', 'A', 'B'],
        'explication': [
            'Dakar est la capitale du Sénégal depuis l\'indépendance en 1960.',
            'Perspicace signifie qui a une vue pénétrante, qui comprend vite, synonyme de clairvoyant.',
            'La suite double à chaque fois : 2, 4, 8, 16, 32.',
            'Léopold Sédar Senghor a été le premier président du Sénégal de 1960 à 1980.',
            '15 x 8 = 120'
        ],
        'difficulte': ['facile', 'moyen', 'moyen', 'facile', 'facile']
    }
    
    df = pd.DataFrame(data)
    
    # Créer le fichier Excel en mémoire avec 2 feuilles
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Questions Évaluation')
        
        # Ajouter une feuille avec les matières disponibles
        if matieres_ena:
            matieres_df = pd.DataFrame({
                'Matières ENA disponibles': matieres_ena
            })
            matieres_df.to_excel(writer, index=False, sheet_name='Matières disponibles')
    output.seek(0)
    
    # Retourner le fichier
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="template_questions_evaluation_ena.xlsx"'
    
    return response

