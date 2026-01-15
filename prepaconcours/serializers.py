from rest_framework import serializers
from .models import (
    Cycle, Matiere, Utilisateur, Question, Choix,
    Tentative, ReponseTentative, Certificat, ImportExcel, SessionQuiz,
    Lecon, ContenuPedagogique, SessionZoomLive,
    Evaluation, ExamenNational, SessionExamen, ParticipationExamen,
    QuestionExamen, SessionComposition, ReponseComposition
)

class CycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cycle
        fields = '__all__'

class MatiereSerializer(serializers.ModelSerializer):
    nb_lecons = serializers.SerializerMethodField()
    
    class Meta:
        model = Matiere
        fields = ['id', 'nom', 'cycle', 'choix_concours', 'tour_ena', 'matiere_examen_national', 'nb_lecons']
    
    def get_nb_lecons(self, obj):
        """Compte le nombre de leçons/contenus actifs pour cette matière selon le tour ENA"""
        from .models import ContenuPedagogique, Lecon, SessionZoomLive
        
        if obj.choix_concours == 'ENA':
            if obj.tour_ena == 'premier_tour':
                # Pour le premier tour : compter les leçons (catégories)
                return Lecon.objects.filter(matiere=obj, active=True).count()
            elif obj.tour_ena == 'second_tour':
                # Pour le second tour : compter les contenus pédagogiques
                return ContenuPedagogique.objects.filter(matiere=obj, active=True).count()
            elif obj.tour_ena == 'oral':
                # Pour l'oral : compter les sessions Zoom
                return SessionZoomLive.objects.filter(matiere=obj, active=True).count()
        
        # Pour les autres concours, compter les contenus pédagogiques par défaut
        return ContenuPedagogique.objects.filter(matiere=obj, active=True).count()

class LeconSerializer(serializers.ModelSerializer):
    matiere_nom = serializers.CharField(source='matiere.nom', read_only=True)
    nb_questions_disponibles = serializers.SerializerMethodField()
    
    class Meta:
        model = Lecon
        fields = '__all__'
    
    def get_nb_questions_disponibles(self, obj):
        """Calcule le nombre de questions disponibles pour cette leçon"""
        return Question.objects.filter(lecon=obj).count()

class ContenuPedagogiqueSerializer(serializers.ModelSerializer):
    matiere_nom = serializers.CharField(source='matiere.nom', read_only=True)
    cycle_nom = serializers.CharField(source='matiere.cycle.nom', read_only=True)
    cycle = serializers.SerializerMethodField()
    
    class Meta:
        model = ContenuPedagogique
        fields = '__all__'
    
    def get_cycle(self, obj):
        if obj.matiere and obj.matiere.cycle:
            return {
                'id': obj.matiere.cycle.id,
                'nom': obj.matiere.cycle.nom
            }
        return None

class SessionZoomLiveSerializer(serializers.ModelSerializer):
    matiere_nom = serializers.CharField(source='matiere.nom', read_only=True)
    
    class Meta:
        model = SessionZoomLive
        fields = '__all__'

# === Serializers pour les questions d'examen national ===

class QuestionExamenSerializer(serializers.ModelSerializer):
    choix_list = serializers.SerializerMethodField()
    matiere_combinee_display = serializers.CharField(source='get_matiere_combinee_display', read_only=True)
    type_question_display = serializers.CharField(source='get_type_question_display', read_only=True)
    
    class Meta:
        model = QuestionExamen
        fields = '__all__'
        read_only_fields = ('code_question', 'nombre_utilisations', 'date_creation', 'date_modification')
    
    def get_choix_list(self, obj):
        """Retourne la liste des choix formatés"""
        return obj.get_choix_list()
    
    def validate(self, data):
        """Validation personnalisée selon le type de question"""
        type_question = data.get('type_question')
        
        if type_question in ['choix_unique', 'choix_multiple']:
            if not (data.get('choix_a') and data.get('choix_b')):
                raise serializers.ValidationError("Les choix A et B sont obligatoires pour les QCM")
            if not data.get('bonne_reponse'):
                raise serializers.ValidationError("La bonne réponse est obligatoire pour les QCM")
        
        elif type_question == 'vrai_faux':
            if data.get('bonne_reponse') not in ['VRAI', 'FAUX']:
                raise serializers.ValidationError("La bonne réponse doit être 'VRAI' ou 'FAUX'")
        
        elif type_question in ['texte_court', 'texte_long']:
            if not data.get('reponse_attendue'):
                raise serializers.ValidationError("La réponse attendue est obligatoire pour les questions texte")
        
        return data

class QuestionExamenDetailSerializer(QuestionExamenSerializer):
    """Serializer détaillé incluant les statistiques d'utilisation"""
    
    class Meta(QuestionExamenSerializer.Meta):
        fields = '__all__'

class QuestionExamenPublicSerializer(serializers.ModelSerializer):
    """Serializer public pour les questions d'examen (sans les bonnes réponses)"""
    choix = serializers.SerializerMethodField()
    matiere_combinee_display = serializers.CharField(source='get_matiere_combinee_display', read_only=True)
    type_question_display = serializers.CharField(source='get_type_question_display', read_only=True)
    
    class Meta:
        model = QuestionExamen
        fields = [
            'id', 'code_question', 'texte', 'type_question', 'type_question_display',
            'matiere_combinee', 'matiere_combinee_display', 'choix_a', 'choix_b', 
            'choix_c', 'choix_d', 'choix_e', 'choix', 'temps_limite_secondes',
            'difficulte'
        ]
    
    def get_choix(self, obj):
        """Retourne la liste des choix sans indiquer la bonne réponse"""
        return obj.get_choix_list()

# === Serializers pour le système d'examens ENA ===

class EvaluationSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.CharField(source='utilisateur.nom_complet', read_only=True)
    
    class Meta:
        model = Evaluation
        fields = '__all__'
        read_only_fields = ('utilisateur', 'date_creation')

class ExamenNationalSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.CharField(source='utilisateur.nom_complet', read_only=True)
    total_questions = serializers.SerializerMethodField()
    questions_details = serializers.SerializerMethodField()
    repartition_temps = serializers.SerializerMethodField()
    temps_restant_total = serializers.SerializerMethodField()
    temps_ecoule_total = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamenNational
        fields = '__all__'
        read_only_fields = ('utilisateur', 'date_creation', 'rang_national')
    
    def get_total_questions(self, obj):
        """Retourne le nombre total de questions dans l'examen"""
        return obj.questions.count()
    
    def get_questions_details(self, obj):
        """Retourne les détails des questions pour l'examen"""
        if self.context.get('include_questions', False):
            from .serializers import QuestionSerializer
            return QuestionSerializer(obj.questions.all(), many=True).data
        return None
    
    def get_repartition_temps(self, obj):
        """Retourne la répartition du temps par matière"""
        return obj.get_repartition_temps()
    
    def get_temps_restant_total(self, obj):
        """Retourne le temps restant total en minutes"""
        return round(obj.get_temps_restant_total() / 60, 1)
    
    def get_temps_ecoule_total(self, obj):
        """Retourne si le temps total est écoulé"""
        return obj.is_temps_total_ecoule()

class SessionExamenSerializer(serializers.ModelSerializer):
    participants_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SessionExamen
        fields = '__all__'
    
    def get_participants_count(self, obj):
        """Retourne le nombre de participants à la session"""
        return obj.participants.count()

class ParticipationExamenSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.CharField(source='utilisateur.nom_complet', read_only=True)
    session_titre = serializers.CharField(source='session.titre', read_only=True)
    
    class Meta:
        model = ParticipationExamen
        fields = '__all__'

class ClassementExamenSerializer(serializers.ModelSerializer):
    """Serializer pour le classement des examens nationaux"""
    utilisateur_nom = serializers.CharField(source='utilisateur.nom_complet', read_only=True)
    position = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamenNational
        fields = ['id', 'utilisateur_nom', 'score', 'temps_total_en_secondes', 
                 'date_examen', 'rang_national', 'position']
    
    def get_position(self, obj):
        """Retourne la position dans le classement"""
        return obj.rang_national

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        exclude = ['password']

class QuestionChoixSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choix
        fields = ['id', 'texte', 'est_correct', 'explication']
        read_only_fields = ['id']

class QuestionDetailSerializer(serializers.ModelSerializer):
    choix = QuestionChoixSerializer(many=True, read_only=True)
    matiere_nom = serializers.CharField(source='matiere.nom', read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'matiere', 'matiere_nom', 'texte', 'type_question', 
            'reponse_attendue', 'explication', 'correction_mode',
            'temps_limite', 'date_ajout', 'choix'
        ]
        read_only_fields = ['date_ajout']

class MatiereNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matiere
        fields = ['id', 'nom', 'cycle', 'choix_concours']

class QuestionSerializer(serializers.ModelSerializer):
    """Serializer pour la lecture des questions avec détails des relations"""
    matiere = MatiereSerializer(read_only=True)
    lecon = LeconSerializer(read_only=True)
    
    class Meta:
        model = Question
        fields = '__all__'
        extra_kwargs = {
            'choix_concours': {'required': False}
        }

class QuestionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la création/modification des questions avec IDs"""
    matiere = serializers.PrimaryKeyRelatedField(queryset=Matiere.objects.all())
    lecon = serializers.PrimaryKeyRelatedField(queryset=Lecon.objects.all(), required=False, allow_null=True)
    choix = serializers.ListField(child=serializers.DictField(), required=False, write_only=True)
    
    class Meta:
        model = Question
        fields = '__all__'
        extra_kwargs = {
            'choix_concours': {'required': False}
        }
        
    def validate(self, data):
        """Validation personnalisée pour les questions ENA"""
        matiere = data.get('matiere')
        lecon = data.get('lecon')
        
        # Si une leçon est spécifiée, vérifier qu'elle appartient à la matière
        if lecon and matiere and lecon.matiere != matiere:
            raise serializers.ValidationError({
                'lecon': f'La leçon "{lecon.nom}" n\'appartient pas à la matière "{matiere.nom}"'
            })
            
        return data
    
    def create(self, validated_data):
        """Créer une question avec ses choix"""
        choix_data = validated_data.pop('choix', [])
        question = Question.objects.create(**validated_data)
        
        # Créer les choix associés
        for choix_item in choix_data:
            Choix.objects.create(
                question=question,
                texte=choix_item.get('texte', ''),
                est_correct=choix_item.get('est_correct', False),
                explication=choix_item.get('explication', '')
            )
        
        return question
    
    def update(self, instance, validated_data):
        """Mettre à jour une question et ses choix"""
        choix_data = validated_data.pop('choix', None)
        
        # Mettre à jour les champs de la question
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Si des choix sont fournis, les mettre à jour
        if choix_data is not None:
            # Supprimer les anciens choix
            instance.choix.all().delete()
            
            # Créer les nouveaux choix
            for choix_item in choix_data:
                Choix.objects.create(
                    question=instance,
                    texte=choix_item.get('texte', ''),
                    est_correct=choix_item.get('est_correct', False),
                    explication=choix_item.get('explication', '')
                )
        
        return instance

class ChoixSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choix
        fields = '__all__'

class TentativeSerializer(serializers.ModelSerializer):
    session = serializers.PrimaryKeyRelatedField(queryset=SessionQuiz.objects.all(), required=False, allow_null=True)
    utilisateur = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Tentative
        fields = '__all__'
        extra_kwargs = {
            'cycle': {'required': False, 'allow_null': True},
            'choix_concours': {'required': False}
        }

class SessionQuizSerializer(serializers.ModelSerializer):
    utilisateur = serializers.PrimaryKeyRelatedField(read_only=True)
    cycle = serializers.PrimaryKeyRelatedField(queryset=Cycle.objects.all(), required=False, allow_null=True)
    matiere = serializers.PrimaryKeyRelatedField(queryset=Matiere.objects.all(), required=True)
    # Remplacement du champ niveau par lecon
    lecon = serializers.PrimaryKeyRelatedField(queryset=Lecon.objects.all(), required=False, allow_null=True)
    nb_questions = serializers.IntegerField(required=True, min_value=1)
    choix_concours = serializers.ChoiceField(choices=SessionQuiz.CHOIX_CONCOURS, required=False)
    # Champs calculés pour les résultats
    bonnes_reponses = serializers.SerializerMethodField()
    total_questions = serializers.SerializerMethodField()
    temps_total = serializers.SerializerMethodField()

    class Meta:
        model = SessionQuiz
        fields = '__all__'
    
    def get_bonnes_reponses(self, obj):
        """Calcule le nombre de bonnes réponses depuis ReponseTentative"""
        from .models import Tentative, ReponseTentative
        tentative = Tentative.objects.filter(session=obj).first()
        if tentative:
            return ReponseTentative.objects.filter(tentative=tentative, est_correct=True).count()
        return 0
    
    def get_total_questions(self, obj):
        """Retourne le nombre total de questions de la session"""
        return obj.nb_questions or obj.questions.count()
    
    def get_temps_total(self, obj):
        """Calcule le temps total depuis ReponseTentative"""
        from .models import Tentative, ReponseTentative
        tentative = Tentative.objects.filter(session=obj).first()
        if tentative:
            return sum(r.temps_question_en_secondes or 0 for r in ReponseTentative.objects.filter(tentative=tentative))
        return 0

    def validate(self, data):
        # Vérifie que les champs essentiels sont bien présents
        choix_concours = data.get('choix_concours', 'ENA')
        
        # Pour ENA, vérifier qu'au moins une matière est spécifiée
        if choix_concours == 'ENA':
            if not data.get('matiere'):
                raise serializers.ValidationError({'matiere': 'Ce champ est obligatoire pour ENA.'})
        
        # Vérifier le nombre de questions
        if not data.get('nb_questions') or data['nb_questions'] < 1:
            raise serializers.ValidationError({'nb_questions': 'Veuillez indiquer un nombre de questions valide.'})
        
        return data

class ReponseTentativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReponseTentative
        fields = '__all__'

class CertificatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificat
        fields = '__all__'

class ImportExcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportExcel
        fields = '__all__'

# --- Serializers pour inscription et reset password ---
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

Utilisateur = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    class Meta:
        model = Utilisateur
        fields = ('nom_complet', 'email', 'telephone', 'password', 'auth_provider')
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Utilisateur.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

class RequestIPResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    telephone = serializers.CharField(required=False)
    def validate(self, attrs):
        if not attrs.get('email') and not attrs.get('telephone'):
            raise serializers.ValidationError('Veuillez fournir un email ou un téléphone.')
        return attrs

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def to_internal_value(self, data):
        # Permet d'accepter 'username' dans la requête, mais le mappe sur 'email' pour SimpleJWT
        if 'username' in data and 'email' not in data:
            data = data.copy()
            data['email'] = data['username']
        return super().to_internal_value(data)

    def validate(self, attrs):
        # Récupère l'identifiant (email ou téléphone) depuis 'email' (après mapping) ou 'username'
        identifier = attrs.get('email') or attrs.get('username')
        password = attrs.get('password')

        if not identifier or not password:
            raise serializers.ValidationError('Veuillez fournir un identifiant et un mot de passe.')

        Utilisateur = get_user_model()
        user = None

        # Essayer de trouver l'utilisateur par email
        try:
            user = Utilisateur.objects.get(email=identifier)
        except Utilisateur.DoesNotExist:
            # Sinon chercher par téléphone
            try:
                user = Utilisateur.objects.get(telephone=identifier)
            except Utilisateur.DoesNotExist:
                raise serializers.ValidationError('Aucun utilisateur trouvé avec cet identifiant.')

        # Debug: log password verification
        print(f'DEBUG: Attempting login for user: {user.email}')
        print(f'DEBUG: Password check result: {user.check_password(password)}')
        print(f'DEBUG: User is_active: {user.is_active}')
        
        # Vérifier le mot de passe
        if not user.check_password(password):
            print(f'DEBUG: Password verification failed for user {user.email}')
            raise serializers.ValidationError('Mot de passe incorrect.')

        if not user.is_active:
            raise serializers.ValidationError('Ce compte est désactivé. Veuillez contacter un administrateur.')

        # Appeler le parent avec email et password (SimpleJWT attend 'email' comme username_field)
        data = super().validate({'email': user.email, 'password': password})
        return data

    @classmethod
    def get_token(cls, user):
        return super().get_token(user)

# --- Serializers pour le système d'examens ENA ---

class EvaluationSerializer(serializers.ModelSerializer):
    """Serializer pour les évaluations ENA"""
    utilisateur = serializers.PrimaryKeyRelatedField(read_only=True)
    utilisateur_nom = serializers.CharField(source='utilisateur.nom_complet', read_only=True)
    
    class Meta:
        model = Evaluation
        fields = '__all__'
        read_only_fields = ('utilisateur', 'date_creation')

class ExamenNationalSerializer(serializers.ModelSerializer):
    """Serializer pour les examens nationaux ENA"""
    utilisateur = serializers.PrimaryKeyRelatedField(read_only=True)
    utilisateur_nom = serializers.CharField(source='utilisateur.nom_complet', read_only=True)
    
    class Meta:
        model = ExamenNational
        fields = '__all__'
        read_only_fields = ('utilisateur', 'rang_national', 'date_creation')

class ClassementExamenSerializer(serializers.ModelSerializer):
    """Serializer pour le classement des examens nationaux"""
    utilisateur_nom = serializers.CharField(source='utilisateur.nom_complet', read_only=True)
    utilisateur_email = serializers.CharField(source='utilisateur.email', read_only=True)
    
    class Meta:
        model = ExamenNational
        fields = ('id', 'utilisateur_nom', 'utilisateur_email', 'score', 'temps_total_en_secondes', 
                 'rang_national', 'date_examen')
        read_only_fields = '__all__'

class SessionExamenSerializer(serializers.ModelSerializer):
    """Serializer pour les sessions d'examen national"""
    nombre_participants = serializers.SerializerMethodField()
    
    class Meta:
        model = SessionExamen
        fields = '__all__'
        read_only_fields = ('date_creation',)
    
    def get_nombre_participants(self, obj):
        return obj.participants.count()

class ParticipationExamenSerializer(serializers.ModelSerializer):
    """Serializer pour les participations aux examens"""
    utilisateur_nom = serializers.CharField(source='utilisateur.nom_complet', read_only=True)
    session_titre = serializers.CharField(source='session_examen.titre', read_only=True)
    
    class Meta:
        model = ParticipationExamen
        fields = '__all__'
        read_only_fields = ('date_inscription',)

# === Serializers pour les compositions nationales ===

class SessionCompositionSerializer(serializers.ModelSerializer):
    """Serializer pour les sessions de composition"""
    utilisateur = serializers.PrimaryKeyRelatedField(read_only=True)
    utilisateur_nom = serializers.CharField(source='utilisateur.nom_complet', read_only=True)
    matiere_combinee_display = serializers.CharField(source='get_matiere_combinee_display', read_only=True)
    
    class Meta:
        model = SessionComposition
        fields = ['id', 'matiere_combinee', 'type_session', 'date_creation', 'date_debut', 'date_fin', 'duree_prevue', 'score_final', 'nombre_bonnes_reponses', 'nombre_total_questions', 'utilisateur', 'utilisateur_nom', 'matiere_combinee_display']
        read_only_fields = ('utilisateur', 'date_creation', 'score_final', 'nombre_bonnes_reponses', 'nombre_total_questions', 'duree_prevue')

class ReponseCompositionSerializer(serializers.ModelSerializer):
    """Serializer pour les réponses de composition"""
    question_texte = serializers.CharField(source='question_examen.texte_question', read_only=True)
    
    class Meta:
        model = ReponseComposition
        fields = '__all__'
        read_only_fields = ('date_reponse', 'est_correcte')

