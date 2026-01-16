from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CycleViewSet, MatiereViewSet, UtilisateurViewSet, QuestionViewSet, ChoixViewSet,
    TentativeViewSet, ReponseTentativeViewSet, CertificatViewSet, ImportExcelViewSet,
    RegisterView, PasswordResetView, PasswordResetConfirmView,
    CustomTokenObtainPairView, TokenBlacklistView,
    ResetUserIPAdminView, RequestIPResetView, ConfirmIPResetView,
    ProfileView, ChangePasswordView, SessionQuizViewSet,
    user_profile, user_stats, DifficulteViewSet,
    # Nouveaux ViewSets pour la navigation ENA
    LeconViewSet, ContenuPedagogiqueViewSet, SessionZoomLiveViewSet, ENANavigationViewSet,
    # ViewSets pour le système d'examens ENA
    EvaluationViewSet, ExamenNationalViewSet, SessionExamenViewSet, exam_stats,
    # ViewSets pour les questions d'examen national
    QuestionExamenViewSet,
    # ViewSets pour les compositions nationales
    SessionCompositionViewSet,
    # Endpoints spécialisés pour l'import ENA
    import_questions_ena_excel, template_excel_ena,
    # Endpoints pour l'import des questions régulières
    import_questions_excel, template_excel_questions,
    # Debug endpoint
    check_questions_disponibles,
    # ViewSets pour les abonnements et paiements
    PlanViewSet, AbonnementViewSet, TransactionViewSet, PaiementViewSet,
    cinetpay_webhook, cinetpay_retour
)
from .views_auth import login_view, profile_view
# Import des vues IA
from .views_ai import ai_chat
# Import des vues d'évaluation par matière
from quiz.views_evaluation import (
    evaluation_stats, matiere_evaluation_stats, create_matiere_evaluation,
    available_questions_count, matieres_with_evaluation_stats, reset_weekly_evaluations
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenBlacklistView
)

router = DefaultRouter()
router.register(r'cycles', CycleViewSet)
router.register(r'matieres', MatiereViewSet)
router.register(r'difficultes', DifficulteViewSet, basename='difficulte')
router.register(r'utilisateurs', UtilisateurViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'choix', ChoixViewSet)
router.register(r'tentatives', TentativeViewSet)
router.register(r'reponses', ReponseTentativeViewSet)
router.register(r'certificats', CertificatViewSet)
router.register(r'imports', ImportExcelViewSet)
router.register(r'sessions_quiz', SessionQuizViewSet, basename='sessions_quiz')

# Routes pour la navigation ENA par tours
router.register(r'lecons', LeconViewSet, basename='lecons')
router.register(r'contenus-pedagogiques', ContenuPedagogiqueViewSet, basename='contenus_pedagogiques')
router.register(r'sessions-zoom', SessionZoomLiveViewSet, basename='sessions_zoom')
router.register(r'ena-navigation', ENANavigationViewSet, basename='ena_navigation')

# Routes pour le système d'examens ENA
router.register(r'evaluations', EvaluationViewSet, basename='evaluations')
router.register(r'examens-nationaux', ExamenNationalViewSet, basename='examens_nationaux')
router.register(r'sessions-examen', SessionExamenViewSet, basename='sessions_examen')

# Routes pour les questions d'examen national
router.register(r'questions-examen', QuestionExamenViewSet, basename='questions_examen')

# Routes pour les compositions nationales
router.register(r'sessions_composition', SessionCompositionViewSet, basename='sessions_composition')

# Routes pour les abonnements et paiements
router.register(r'plans', PlanViewSet, basename='plans')
router.register(r'abonnements', AbonnementViewSet, basename='abonnements')
router.register(r'transactions', TransactionViewSet, basename='transactions')
router.register(r'paiement', PaiementViewSet, basename='paiement')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', user_profile, name='user-profile'),
    path('user/profile/', user_profile, name='user-profile-alt'),  # Endpoint pour le frontend
    path('user/stats/', user_stats, name='user-stats'),
    path('exam/stats/', exam_stats, name='exam-stats'),
    path('admin/reset-ip/', ResetUserIPAdminView.as_view(), name='admin_reset_ip'),
    path('auth/request-ip-reset/', RequestIPResetView.as_view(), name='request_ip_reset'),
    path('auth/confirm-ip-reset/', ConfirmIPResetView.as_view(), name='confirm_ip_reset'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('auth/reset-password-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Endpoints pour les évaluations par matière
    path('evaluation/stats/', evaluation_stats, name='evaluation_stats'),
    path('evaluation/matiere/<int:matiere_id>/stats/', matiere_evaluation_stats, name='matiere_evaluation_stats'),
    path('evaluation/matiere/create/', create_matiere_evaluation, name='create_matiere_evaluation'),
    path('evaluation/matiere/<int:matiere_id>/questions/count/', available_questions_count, name='available_questions_count'),
    path('evaluation/matieres/with-stats/', matieres_with_evaluation_stats, name='matieres_with_evaluation_stats'),
    path('evaluation/reset/', reset_weekly_evaluations, name='reset_weekly_evaluations'),
    
    # Endpoints spécialisés pour l'import de questions ENA (QuestionExamen)
    path('admin/import-questions-ena/', import_questions_ena_excel, name='import_questions_ena'),
    path('admin/template-excel-ena/', template_excel_ena, name='template_excel_ena'),
    
    # Endpoints pour l'import des questions régulières (Question)
    path('admin/import-questions/', import_questions_excel, name='import_questions'),
    path('admin/template-excel-questions/', template_excel_questions, name='template_excel_questions'),
    
    # Debug endpoint pour vérifier les questions disponibles
    path('debug/questions-disponibles/', check_questions_disponibles, name='check_questions_disponibles'),
    
    # Endpoint pour l'assistant IA
    path('ai-chat/', ai_chat, name='ai_chat'),
    
    # Endpoints d'authentification Ma Caisse (priorité haute)
    path('auth/login/', login_view, name='auth-login'),
    path('auth/profile/', profile_view, name='auth-profile'),
    
    # Endpoints CinetPay (webhook et retour)
    path('paiement/webhook/', cinetpay_webhook, name='cinetpay_webhook'),
    path('paiement/retour/', cinetpay_retour, name='cinetpay_retour'),
    
]
