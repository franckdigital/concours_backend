from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

# --- Cycle ---
class Cycle(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom

# --- Matiere ---
CHOIX_CONCOURS = [
    ('ENA', 'ENA'),
    ('fonction_publique', 'Fonction Publique'),
    ('examen_national', 'Examen National'),
]

# Tours pour ENA
TOURS_ENA = [
    ('premier_tour', 'Premier Tour'),
    ('second_tour', 'Second Tour'),
    ('oral', 'Oral'),
]

# Matières combinées pour l'examen national
MATIERES_EXAMEN_NATIONAL = [
    ('culture_aptitude', 'Culture générale + Aptitude verbale'),
    ('logique_combinee', 'Logique + Raisonnement'),
    ('anglais', 'Anglais'),
]

class Matiere(models.Model):
    nom = models.CharField(max_length=100)
    # Le cycle n'est utilisé que pour le second tour et la fonction publique
    cycle = models.ForeignKey(Cycle, null=True, blank=True, on_delete=models.CASCADE, related_name='matieres', 
                             help_text="Cycle (uniquement pour second_tour et fonction_publique)")
    choix_concours = models.CharField(max_length=20, choices=CHOIX_CONCOURS, default='ENA')
    # Nouveau champ pour les tours ENA
    tour_ena = models.CharField(max_length=20, choices=TOURS_ENA, null=True, blank=True, help_text="Tour ENA (uniquement pour choix_concours='ENA')")
    # Nouveau champ pour les matières d'examen national
    matiere_examen_national = models.CharField(max_length=20, choices=MATIERES_EXAMEN_NATIONAL, null=True, blank=True, help_text="Matière combinée pour l'examen national")

    class Meta:
        # Pour le premier tour, pas besoin de cycle dans l'unicité
        unique_together = ('nom', 'cycle', 'choix_concours', 'tour_ena')
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Validation : le cycle est obligatoire seulement pour second_tour ENA
        # Pour Fonction Publique, le cycle n'est pas requis
        if self.choix_concours == 'ENA' and self.tour_ena == 'second_tour' and not self.cycle:
            raise ValidationError("Le cycle est obligatoire pour le second tour ENA")
        # Pour le premier tour ENA, le cycle doit être null
        if self.choix_concours == 'ENA' and self.tour_ena == 'premier_tour' and self.cycle:
            raise ValidationError("Le cycle ne doit pas être défini pour le premier tour ENA")
        # Pour l'oral ENA, pas de cycle non plus
        if self.choix_concours == 'ENA' and self.tour_ena == 'oral' and self.cycle:
            raise ValidationError("Le cycle ne doit pas être défini pour l'oral ENA")
        # Pour l'examen national, la matière combinée est obligatoire
        if self.choix_concours == 'examen_national' and not self.matiere_examen_national:
            raise ValidationError("La matière combinée est obligatoire pour l'examen national")
        # Pour l'examen national, pas de cycle ni de tour ENA
        if self.choix_concours == 'examen_national' and (self.cycle or self.tour_ena):
            raise ValidationError("Le cycle et le tour ENA ne doivent pas être définis pour l'examen national")

    def __str__(self):
        if self.choix_concours == 'ENA' and self.tour_ena:
            if self.tour_ena == 'premier_tour':
                return f"{self.nom} - {self.get_tour_ena_display()}"
            elif self.cycle:
                return f"{self.nom} - {self.get_tour_ena_display()} ({self.cycle.nom})"
            else:
                return f"{self.nom} - {self.get_tour_ena_display()}"
        return f"{self.nom} ({self.cycle.nom if self.cycle else 'Sans cycle'})"

# --- Leçon (catégories de leçons pour premier tour uniquement) ---
class Lecon(models.Model):
    """Représente une catégorie de leçon pour le premier tour ENA uniquement (ex: sport, éducation, science pour culture générale)"""
    
    nom = models.CharField(max_length=200, help_text="Nom de la catégorie (ex: Sport, Éducation, Science)")
    # Relation uniquement avec les matières du premier tour ENA
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='lecons', 
                               help_text="Matière du premier tour ENA")
    description = models.TextField(null=True, blank=True, help_text="Description de cette catégorie de leçon")
    
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage dans la matière")
    active = models.BooleanField(default=True, help_text="Automatiquement activé à la création")
    date_creation = models.DateTimeField(default=timezone.now)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Validation : les leçons ne peuvent être créées que pour les matières du premier tour ENA
        if self.matiere.choix_concours != 'ENA' or self.matiere.tour_ena != 'premier_tour':
            raise ValidationError("Les leçons ne peuvent être créées que pour les matières du premier tour ENA")
    
    class Meta:
        ordering = ['ordre', 'nom']
        unique_together = ('nom', 'matiere')
        verbose_name = "Leçon (Catégorie - Premier Tour)"
        verbose_name_plural = "Leçons (Catégories - Premier Tour)"
    
    def __str__(self):
        return f"{self.nom} ({self.matiere.nom})"

# --- Contenu Pédagogique (pour second tour ENA uniquement) ---
class ContenuPedagogique(models.Model):
    """Contenus PDF et vidéo pour le second tour ENA uniquement"""
    
    TYPE_CONTENU = [
        ('pdf', 'PDF'),
        ('video', 'Vidéo'),
    ]
    
    titre = models.CharField(max_length=200, help_text="Titre du contenu pédagogique")
    # Relation uniquement avec les matières du second tour ENA (qui ont un cycle)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='contenus_pedagogiques',
                               help_text="Matière du second tour ENA (avec cycle)")
    type_contenu = models.CharField(max_length=10, choices=TYPE_CONTENU)
    description = models.TextField(null=True, blank=True)
    
    # Champs spécifiques selon le type
    fichier_pdf = models.FileField(upload_to='contenus/pdf/', null=True, blank=True, help_text="Fichier PDF")
    url_video = models.URLField(null=True, blank=True, help_text="URL de la vidéo")
    youtube_video_id = models.CharField(max_length=50, null=True, blank=True, help_text="ID de la vidéo YouTube (ex: dQw4w9WgXcQ)")
    duree_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Durée en minutes (pour vidéos)")
    
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    active = models.BooleanField(default=True, help_text="Automatiquement activé à la création")
    date_creation = models.DateTimeField(default=timezone.now)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Validation : les contenus pédagogiques ne peuvent être créés que pour les matières du second tour ENA
        if self.matiere.choix_concours != 'ENA' or self.matiere.tour_ena != 'second_tour':
            raise ValidationError("Les contenus pédagogiques ne peuvent être créés que pour les matières du second tour ENA")
        if not self.matiere.cycle:
            raise ValidationError("La matière doit avoir un cycle pour le second tour ENA")
    
    class Meta:
        ordering = ['ordre', 'titre']
        verbose_name = "Contenu Pédagogique (Second Tour)"
        verbose_name_plural = "Contenus Pédagogiques (Second Tour)"
    
    def __str__(self):
        return f"{self.titre} ({self.get_type_contenu_display()}) - {self.matiere.nom}"

# --- Session Zoom Live (pour oral ENA uniquement) ---
class SessionZoomLive(models.Model):
    """Sessions Zoom live pour l'oral ENA uniquement"""
    
    STATUT_CHOICES = [
        ('programmee', 'Programmée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]
    
    titre = models.CharField(max_length=200, help_text="Titre de la session")
    # Relation uniquement avec les matières de l'oral ENA (sans cycle)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='sessions_zoom',
                               help_text="Matière de l'oral ENA (sans cycle)")
    description = models.TextField(null=True, blank=True)
    
    # Informations Zoom
    url_zoom = models.URLField(help_text="Lien Zoom pour rejoindre la session")
    meeting_id = models.CharField(max_length=50, null=True, blank=True, help_text="ID de la réunion Zoom")
    mot_de_passe = models.CharField(max_length=50, null=True, blank=True, help_text="Mot de passe Zoom")
    
    # Planning
    date_session = models.DateTimeField(help_text="Date et heure de la session")
    duree_minutes = models.PositiveIntegerField(default=60, help_text="Durée prévue en minutes")
    
    # Gestion
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='programmee')
    nombre_participants_max = models.PositiveIntegerField(default=50, help_text="Nombre maximum de participants")
    active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(default=timezone.now)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Validation : les sessions Zoom ne peuvent être créées que pour les matières de l'oral ENA
        if self.matiere.choix_concours != 'ENA' or self.matiere.tour_ena != 'oral':
            raise ValidationError("Les sessions Zoom ne peuvent être créées que pour les matières de l'oral ENA")
        if self.matiere.cycle:
            raise ValidationError("La matière ne doit pas avoir de cycle pour l'oral ENA")
    
    class Meta:
        ordering = ['date_session']
        verbose_name = "Session Zoom Live (Oral)"
        verbose_name_plural = "Sessions Zoom Live (Oral)"
    
    def __str__(self):
        return f"{self.titre} - {self.date_session.strftime('%d/%m/%Y %H:%M')} ({self.matiere.nom})"


# --- Custom User Manager ---
class UtilisateurManager(BaseUserManager):
    def create_user(self, email=None, telephone=None, password=None, **extra_fields):
        if not email and not telephone:
            raise ValueError('Un email ou un téléphone est requis')
        email = self.normalize_email(email) if email else None
        user = self.model(email=email, telephone=telephone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        # Remove is_staff if present - it's a property derived from is_admin
        extra_fields.pop('is_staff', None)
        return self.create_user(email, password=password, **extra_fields)


# --- Utilisateur ---
class Utilisateur(AbstractBaseUser, PermissionsMixin):
    # Champs correspondant à la structure existante dans la DB
    nom_complet = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True, default='')
    telephone = models.CharField(max_length=20, null=True, blank=True)
    auth_provider = models.CharField(max_length=20, default='local')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_inscription = models.DateTimeField(default=timezone.now)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_ua = models.TextField(null=True, blank=True)
    last_login_device = models.TextField(null=True, blank=True)
    cycle = models.ForeignKey(Cycle, null=True, blank=True, on_delete=models.SET_NULL)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom_complet']

    objects = UtilisateurManager()
    
    class Meta:
        db_table = 'prepaconcours_utilisateur'
    
    @property
    def is_staff(self):
        """Propriété pour compatibilité Django admin"""
        return self.is_admin

    def __str__(self):
        return self.nom_complet

# --- Question ---

class Question(models.Model):
    # Suppression de NIVEAU_CHOICES - remplacé par les leçons
    TYPE_CHOICES = [
        ('choix_unique', 'Choix unique'),
        ('choix_multiple', 'Choix multiple'),
        ('vrai_faux', 'Vrai/Faux'),
        ('texte_court', 'Texte court'),
        ('texte_long', 'Texte long'),
    ]
    CORRECTION_MODE_CHOICES = [
        ('exacte', 'Exacte'),
        ('mot_cle', 'Mot-clé'),
        ('regex', 'Regex'),
    ]
    texte = models.TextField()
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='questions')
    # Remplacement du champ niveau par une relation avec Lecon
    lecon = models.ForeignKey(Lecon, on_delete=models.CASCADE, related_name='questions', null=True, blank=True, help_text="Leçon à laquelle appartient cette question")
    type_question = models.CharField(max_length=20, choices=TYPE_CHOICES, default='choix_unique')
    explication = models.TextField(null=True, blank=True)
    reponse_attendue = models.TextField(null=True, blank=True, help_text="Pour les questions texte : réponse attendue, mot-clé ou regex")
    correction_mode = models.CharField(max_length=10, choices=CORRECTION_MODE_CHOICES, default='exacte', null=True, blank=True, help_text="Mode de correction automatique pour les questions texte")
    date_ajout = models.DateTimeField(default=timezone.now)
    temps_limite = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Durée limite en secondes pour répondre à cette question (laisser vide pour la valeur par défaut)"
    )
    choix_concours = models.CharField(max_length=32, choices=CHOIX_CONCOURS, default='ENA')
    
    def save(self, *args, **kwargs):
        # Définir une valeur par défaut pour temps_limite en fonction du type de question
        if self.temps_limite is None:
            if self.type_question in ['choix_unique', 'vrai_faux']:
                self.temps_limite = 60  # 1 minute pour QCM et Vrai/Faux
            elif self.type_question == 'choix_multiple':
                self.temps_limite = 90  # 1 minute 30 pour QCM multiple
            elif self.type_question == 'texte_court':
                self.temps_limite = 120  # 2 minutes pour réponse courte
            else:  # texte_long
                self.temps_limite = 300  # 5 minutes pour réponse longue
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.texte[:50]}... ({self.matiere.nom})"

# --- Question Examen National ENA ---
class QuestionExamen(models.Model):
    """
    Questions spécifiques à l'examen national ENA
    Liées aux matières et leçons existantes du système ENA
    """
    TYPE_CHOICES = [
        ('choix_unique', 'Choix unique'),
        ('choix_multiple', 'Choix multiple'),
        ('vrai_faux', 'Vrai/Faux'),
        ('texte_court', 'Texte court'),
        ('texte_long', 'Texte long'),
    ]
    
    CORRECTION_MODE_CHOICES = [
        ('exacte', 'Exacte'),
        ('mot_cle', 'Mot-clé'),
        ('regex', 'Regex'),
    ]
    
    # Identification et contenu
    code_question = models.CharField(max_length=20, unique=True, help_text="Code unique de la question (ex: ENA2024-CG-001)")
    texte = models.TextField(help_text="Énoncé de la question")
    type_question = models.CharField(max_length=20, choices=TYPE_CHOICES, default='choix_unique')
    
    # Relations avec le système ENA existant
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='questions_examen', null=True, blank=True,
                               help_text="Matière de l'examen national (choix_concours='examen_national')")
    lecon = models.ForeignKey(Lecon, on_delete=models.CASCADE, related_name='questions_examen', null=True, blank=True,
                             help_text="Leçon spécifique (optionnelle, pour organiser les questions par thème)")
    
    # Champ de compatibilité pour l'import Excel (sera déduit automatiquement)
    matiere_combinee = models.CharField(max_length=20, null=True, blank=True, 
                                       help_text="Matière combinée (calculée automatiquement depuis matiere.matiere_examen_national)")
    
    # Réponses et choix
    choix_a = models.TextField(null=True, blank=True, help_text="Choix A (pour QCM)")
    choix_b = models.TextField(null=True, blank=True, help_text="Choix B (pour QCM)")
    choix_c = models.TextField(null=True, blank=True, help_text="Choix C (pour QCM)")
    choix_d = models.TextField(null=True, blank=True, help_text="Choix D (pour QCM)")
    choix_e = models.TextField(null=True, blank=True, help_text="Choix E (optionnel)")
    
    # Bonnes réponses
    bonne_reponse = models.CharField(max_length=10, null=True, blank=True, help_text="Bonne(s) réponse(s) pour QCM (ex: A, AB, VRAI)")
    reponse_attendue = models.TextField(null=True, blank=True, help_text="Réponse attendue pour questions texte")
    correction_mode = models.CharField(max_length=10, choices=CORRECTION_MODE_CHOICES, default='exacte', help_text="Mode de correction pour questions texte")
    
    # Explications et métadonnées
    explication = models.TextField(null=True, blank=True, help_text="Explication de la réponse")
    difficulte = models.CharField(max_length=10, choices=[('facile', 'Facile'), ('moyen', 'Moyen'), ('difficile', 'Difficile')], default='moyen')
    temps_limite_secondes = models.PositiveIntegerField(default=120, help_text="Temps limite en secondes pour cette question")
    
    # Statut et gestion
    active = models.BooleanField(default=True, help_text="Question active pour les examens")
    validee = models.BooleanField(default=False, help_text="Question validée par un administrateur")
    nombre_utilisations = models.PositiveIntegerField(default=0, help_text="Nombre de fois utilisée dans des examens")
    
    # Métadonnées
    date_creation = models.DateTimeField(default=timezone.now)
    date_modification = models.DateTimeField(auto_now=True)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validation : la matière doit être de type examen_national
        if self.matiere and self.matiere.choix_concours != 'examen_national':
            raise ValidationError("La matière doit être de type 'examen_national'")
        
        # Validation : la leçon doit appartenir à la matière sélectionnée
        if self.lecon and self.matiere and self.lecon.matiere != self.matiere:
            raise ValidationError("La leçon doit appartenir à la matière sélectionnée")
        
        # Synchroniser matiere_combinee avec matiere.matiere_examen_national
        if self.matiere:
            self.matiere_combinee = self.matiere.matiere_examen_national
        
        # Validation selon le type de question
        if self.type_question in ['choix_unique', 'choix_multiple']:
            if not (self.choix_a and self.choix_b):
                raise ValidationError("Les choix A et B sont obligatoires pour les QCM")
            if not self.bonne_reponse:
                raise ValidationError("La bonne réponse est obligatoire pour les QCM")
        
        elif self.type_question == 'vrai_faux':
            if self.bonne_reponse not in ['VRAI', 'FAUX', 'A', 'B']:
                raise ValidationError("La bonne réponse doit être 'VRAI', 'FAUX', 'A' ou 'B' pour les questions Vrai/Faux")
        
        elif self.type_question in ['texte_court', 'texte_long']:
            if not self.reponse_attendue:
                raise ValidationError("La réponse attendue est obligatoire pour les questions texte")
    
    def save(self, *args, **kwargs):
        # Générer automatiquement le code_question si pas défini
        if not self.code_question:
            from datetime import datetime
            year = datetime.now().year
            if self.matiere and self.matiere.matiere_examen_national:
                prefix_map = {
                    'culture_aptitude': 'CA',
                    'logique_combinee': 'LC', 
                    'anglais': 'AN'
                }
                prefix = prefix_map.get(self.matiere.matiere_examen_national, 'EX')
                # Compter les questions existantes pour cette matière
                count = QuestionExamen.objects.filter(
                    matiere__matiere_examen_national=self.matiere.matiere_examen_national
                ).count() + 1
                self.code_question = f"ENA{year}-{prefix}-{count:03d}"
            else:
                # Fallback si pas de matière définie
                count = QuestionExamen.objects.count() + 1
                self.code_question = f"ENA{year}-XX-{count:03d}"
        
        # Synchroniser matiere_combinee
        if self.matiere:
            self.matiere_combinee = self.matiere.matiere_examen_national
            
        self.clean()
        super().save(*args, **kwargs)
    
    def get_choix_list(self):
        """Retourne la liste des choix disponibles au format attendu par le frontend"""
        choix = []
        if self.choix_a:
            choix.append({'id': 0, 'lettre': 'A', 'texte': self.choix_a})
        if self.choix_b:
            choix.append({'id': 1, 'lettre': 'B', 'texte': self.choix_b})
        if self.choix_c:
            choix.append({'id': 2, 'lettre': 'C', 'texte': self.choix_c})
        if self.choix_d:
            choix.append({'id': 3, 'lettre': 'D', 'texte': self.choix_d})
        if self.choix_e:
            choix.append({'id': 4, 'lettre': 'E', 'texte': self.choix_e})
        return choix
    
    def verifier_reponse(self, reponse_utilisateur):
        """Vérifie si la réponse de l'utilisateur est correcte"""
        if self.type_question in ['choix_unique', 'choix_multiple', 'vrai_faux']:
            return self.bonne_reponse == reponse_utilisateur
        
        elif self.type_question in ['texte_court', 'texte_long']:
            if self.correction_mode == 'exacte':
                return self.reponse_attendue.strip().lower() == reponse_utilisateur.strip().lower()
            elif self.correction_mode == 'mot_cle':
                mots_cles = [mot.strip().lower() for mot in self.reponse_attendue.split(',')]
                reponse_lower = reponse_utilisateur.lower()
                return any(mot in reponse_lower for mot in mots_cles)
            elif self.correction_mode == 'regex':
                import re
                return bool(re.search(self.reponse_attendue, reponse_utilisateur, re.IGNORECASE))
        
        return False
    
    def incrementer_utilisation(self):
        """Incrémente le compteur d'utilisation"""
        self.nombre_utilisations += 1
        self.save(update_fields=['nombre_utilisations'])
    
    @property
    def matiere_nom(self):
        """Nom de la matière pour compatibilité avec l'import Excel"""
        return self.matiere.nom if self.matiere else None
    
    @property 
    def lecon_nom(self):
        """Nom de la leçon pour compatibilité avec l'import Excel"""
        return self.lecon.nom if self.lecon else None
    
    def get_statistiques(self):
        """Retourne les statistiques d'utilisation de cette question"""
        # Statistiques d'évaluations
        return {
            'nombre_utilisations': self.nombre_utilisations,
            'taux_reussite': 0.0,  # À calculer selon les réponses des utilisateurs
            'difficulte_percue': self.difficulte,
            'temps_moyen_reponse': self.temps_limite_secondes
        }
    
    class Meta:
        ordering = ['matiere__nom', 'lecon__nom', 'code_question']
        verbose_name = "Question Examen National"
        verbose_name_plural = "Questions Examen National"
        indexes = [
            models.Index(fields=['matiere', 'active']),
            models.Index(fields=['type_question', 'difficulte']),
            models.Index(fields=['validee', 'active']),
        ]
    
    def __str__(self):
        if self.lecon:
            return f"{self.code_question} - {self.matiere.nom} ({self.lecon.nom})"
        return f"{self.code_question} - {self.matiere.nom if self.matiere else 'Sans matière'}"

# --- Choix Examen ---
class ChoixExamen(models.Model):
    """Choix de réponse pour les questions d'examen national"""
    question_examen = models.ForeignKey(QuestionExamen, on_delete=models.CASCADE, related_name='choix_examen')
    texte_choix = models.TextField(help_text="Texte du choix de réponse")
    est_correcte = models.BooleanField(default=False, help_text="Ce choix est-il correct ?")
    ordre = models.PositiveIntegerField(default=1, help_text="Ordre d'affichage du choix")
    
    class Meta:
        ordering = ['ordre']
        verbose_name = "Choix d'examen"
        verbose_name_plural = "Choix d'examens"
    
    def __str__(self):
        return f"{self.question_examen.code_question} - Choix {self.ordre}: {self.texte_choix[:50]}"

# --- Choix ---
class Choix(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choix')
    texte = models.CharField(max_length=255)
    est_correct = models.BooleanField(default=False)
    explication = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('question', 'texte')

    def __str__(self):
        return f"{self.texte} ({'Correct' if self.est_correct else 'Faux'})"

# --- Tentative ---
class Tentative(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='tentatives')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='tentatives')
    cycle = models.ForeignKey(Cycle, on_delete=models.SET_NULL, null=True, blank=True, related_name='tentatives')
    choix_concours = models.CharField(max_length=32, choices=CHOIX_CONCOURS, default='ENA')
    date_test = models.DateTimeField(default=timezone.now)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temps_total_en_secondes = models.PositiveIntegerField(default=0)
    temps_limite = models.PositiveIntegerField(null=True, blank=True, help_text="Durée limite en minutes pour cette tentative")
    terminee = models.BooleanField(default=False)
    session = models.ForeignKey('SessionQuiz', on_delete=models.CASCADE, null=True, blank=True, related_name='tentatives')

    def __str__(self):
        return f"{self.utilisateur.nom_complet} - {self.matiere.nom} ({self.date_test})"

# --- ReponseTentative ---
class ReponseTentative(models.Model):
    tentative = models.ForeignKey(Tentative, on_delete=models.CASCADE, related_name='reponses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choix = models.ForeignKey(Choix, on_delete=models.CASCADE, null=True, blank=True)
    texte_reponse = models.TextField(null=True, blank=True, help_text="Réponse libre pour les questions texte")
    est_correct = models.BooleanField(null=True)
    temps_question_en_secondes = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Tentative {self.tentative.id} - Q{self.question.id} - C{self.choix.id if self.choix else ''}"

# --- Certificat ---
class Certificat(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='certificats')
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='certificats')
    date_obtention = models.DateTimeField(default=timezone.now)
    score_final = models.DecimalField(max_digits=5, decimal_places=2)
    fichier_pdf_url = models.TextField()

    def __str__(self):
        return f"Certificat {self.utilisateur.nom_complet} - {self.cycle.nom}"

# --- SessionQuiz ---
class SessionQuiz(models.Model):
    # Suppression de NIVEAU_CHOICES - remplacé par les leçons
    CHOIX_CONCOURS = [
        ('ENA', 'ENA'),
        ('fonction_publique', 'Fonction Publique'),
    ]
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='sessions_quiz')
    cycle = models.ForeignKey(Cycle, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions_quiz')
    choix_concours = models.CharField(max_length=32, choices=CHOIX_CONCOURS, default='ENA')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='sessions_quiz', null=True, blank=True)
    # Remplacement du champ niveau par une relation avec Lecon
    lecon = models.ForeignKey(Lecon, on_delete=models.CASCADE, related_name='sessions_quiz', null=True, blank=True, help_text="Leçon pour cette session de quiz")
    date_debut = models.DateTimeField(default=timezone.now)
    date_fin = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=[('en_cours','En cours'),('terminee','Terminée'),('reinitialisee','Réinitialisée')], default='en_cours')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    nb_questions = models.PositiveIntegerField(default=0)
    questions = models.ManyToManyField('Question', related_name='sessions', blank=True)

    def __str__(self):
        cycle_nom = self.cycle.nom if self.cycle else "Aucun cycle"
        lecon_nom = self.lecon.nom if self.lecon else "Aucune leçon"
        return f"{self.utilisateur} - {cycle_nom} - {lecon_nom} ({self.statut})"

# --- ImportExcel ---
class ImportExcel(models.Model):
    IMPORT_TYPES = [
        ('questions', 'Questions'),
        ('matieres', 'Matières'),
        ('utilisateurs', 'Utilisateurs'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
    ]
    
    utilisateur = models.ForeignKey(Utilisateur, null=True, blank=True, on_delete=models.SET_NULL, related_name='imports_excel')
    fichier_nom = models.CharField(max_length=255, verbose_name="Nom du fichier")
    import_type = models.CharField(max_length=20, choices=IMPORT_TYPES, default='questions', verbose_name="Type d'import")
    nombre_elements_importes = models.PositiveIntegerField(default=0, verbose_name="Éléments importés")
    nombre_echecs = models.PositiveIntegerField(default=0, verbose_name="Échecs")
    date_import = models.DateTimeField(default=timezone.now, verbose_name="Date d'import")
    date_fin = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    details = models.JSONField(null=True, blank=True, help_text="Détails supplémentaires sur l'import")
    erreur = models.TextField(null=True, blank=True, verbose_name="Message d'erreur")

    class Meta:
        verbose_name = "Import Excel"
        verbose_name_plural = "Imports Excel"
        ordering = ['-date_import']

    def __str__(self):
        return f"Import {self.import_type} - {self.fichier_nom} ({self.get_status_display()})"
        
    def save(self, *args, **kwargs):
        # Mettre à jour la date de fin si le statut est terminé ou échoué
        if self.status in ['completed', 'failed'] and not self.date_fin:
            self.date_fin = timezone.now()
        super().save(*args, **kwargs)

# --- Evaluation ENA ---
class Evaluation(models.Model):
    """
    Évaluation ENA : test de validation avant l'examen national
    Accessible uniquement si l'utilisateur a >=30% de score moyen sur tous ses quiz ENA
    """
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='evaluations')
    date_evaluation = models.DateTimeField(default=timezone.now)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temps_total_en_secondes = models.PositiveIntegerField(default=0)
    terminee = models.BooleanField(default=False)
    questions = models.ManyToManyField('Question', related_name='evaluations', blank=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-date_evaluation']
    
    def __str__(self):
        return f"Évaluation de {self.utilisateur.nom_complet} - {self.date_evaluation.strftime('%d/%m/%Y')}"

# --- Examen National ENA ---
class ExamenNational(models.Model):
    """
    Examen National ENA : examen officiel avec classement
    Accessible uniquement si l'utilisateur a >=50% de score à l'évaluation
    Durée totale : 3h (180 minutes) - 60 minutes par matière combinée
    """
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='examens_nationaux')
    date_examen = models.DateTimeField(default=timezone.now)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temps_total_en_secondes = models.PositiveIntegerField(default=0)
    terminee = models.BooleanField(default=False)
    questions = models.ManyToManyField('QuestionExamen', related_name='examens_nationaux', blank=True)
    
    # Gestion du temps par matière combinée (3h = 180 minutes total)
    DUREE_TOTALE_MINUTES = 180  # 3 heures
    DUREE_PAR_MATIERE_MINUTES = 60  # 1 heure par matière combinée
    DUREE_TOTALE_SECONDES = DUREE_TOTALE_MINUTES * 60  # 10800 secondes
    DUREE_PAR_MATIERE_SECONDES = DUREE_PAR_MATIERE_MINUTES * 60  # 3600 secondes
    
    # Temps passé par matière combinée (en secondes)
    temps_culture_aptitude = models.PositiveIntegerField(default=0, help_text="Temps passé sur Culture générale + Aptitude verbale")
    temps_logique_combinee = models.PositiveIntegerField(default=0, help_text="Temps passé sur Logique d'organisation + Logique numérique")
    temps_anglais = models.PositiveIntegerField(default=0, help_text="Temps passé sur Anglais")
    
    # Heure de début pour chaque matière (pour contrôle du temps)
    debut_culture_aptitude = models.DateTimeField(null=True, blank=True)
    debut_logique_combinee = models.DateTimeField(null=True, blank=True)
    debut_anglais = models.DateTimeField(null=True, blank=True)
    
    # Classement
    rang_national = models.PositiveIntegerField(null=True, blank=True, help_text="Rang dans le classement national")
    
    # Métadonnées
    date_creation = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-score', 'temps_total_en_secondes']  # Classement par score décroissant, puis temps croissant
    
    def __str__(self):
        return f"Examen National de {self.utilisateur.nom_complet} - {self.date_examen.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculer les rangs après chaque sauvegarde
        if self.terminee and self.score is not None:
            self.update_rankings()
    
    def get_temps_restant_total(self):
        """Retourne le temps restant total en secondes"""
        if self.terminee:
            return 0
        return max(0, self.DUREE_TOTALE_SECONDES - self.temps_total_en_secondes)
    
    def get_temps_restant_matiere(self, matiere_code):
        """Retourne le temps restant pour une matière spécifique"""
        if self.terminee:
            return 0
        
        temps_utilise = 0
        if matiere_code == 'culture_aptitude':
            temps_utilise = self.temps_culture_aptitude
        elif matiere_code == 'logique_combinee':
            temps_utilise = self.temps_logique_combinee
        elif matiere_code == 'anglais':
            temps_utilise = self.temps_anglais
        
        return max(0, self.DUREE_PAR_MATIERE_SECONDES - temps_utilise)
    
    def is_temps_matiere_ecoule(self, matiere_code):
        """Vérifie si le temps alloué à une matière est écoulé"""
        return self.get_temps_restant_matiere(matiere_code) <= 0
    
    def is_temps_total_ecoule(self):
        """Vérifie si le temps total de l'examen est écoulé"""
        return self.get_temps_restant_total() <= 0
    
    def get_repartition_temps(self):
        """Retourne la répartition du temps par matière"""
        return {
            'duree_totale_minutes': self.DUREE_TOTALE_MINUTES,
            'duree_par_matiere_minutes': self.DUREE_PAR_MATIERE_MINUTES,
            'matieres': {
                'culture_aptitude': {
                    'nom': 'Culture générale et Aptitude verbale',
                    'duree_allouee_minutes': self.DUREE_PAR_MATIERE_MINUTES,
                    'temps_utilise_minutes': round(self.temps_culture_aptitude / 60, 1),
                    'temps_restant_minutes': round(self.get_temps_restant_matiere('culture_aptitude') / 60, 1)
                },
                'logique_combinee': {
                    'nom': 'Logique d\'organisation et Logique numérique',
                    'duree_allouee_minutes': self.DUREE_PAR_MATIERE_MINUTES,
                    'temps_utilise_minutes': round(self.temps_logique_combinee / 60, 1),
                    'temps_restant_minutes': round(self.get_temps_restant_matiere('logique_combinee') / 60, 1)
                },
                'anglais': {
                    'nom': 'Anglais',
                    'duree_allouee_minutes': self.DUREE_PAR_MATIERE_MINUTES,
                    'temps_utilise_minutes': round(self.temps_anglais / 60, 1),
                    'temps_restant_minutes': round(self.get_temps_restant_matiere('anglais') / 60, 1)
                }
            }
        }
    
    @classmethod
    def update_rankings(cls):
        """Met à jour le classement national de tous les examens terminés"""
        examens = cls.objects.filter(terminee=True, score__isnull=False).order_by('-score', 'temps_total_en_secondes')
        
        for index, examen in enumerate(examens, start=1):
            if examen.rang_national != index:
                examen.rang_national = index
                examen.save(update_fields=['rang_national'])

# --- Session d'Examen (pour planifier les examens nationaux) ---
class SessionExamen(models.Model):
    """
    Session d'examen national planifiée (une fois par semaine)
    """
    STATUT_CHOICES = [
        ('programmee', 'Programmée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]
    
    titre = models.CharField(max_length=200, help_text="Titre de la session d'examen")
    date_debut = models.DateTimeField(help_text="Date et heure de début de l'examen")
    date_fin = models.DateTimeField(help_text="Date et heure de fin de l'examen")
    duree_minutes = models.PositiveIntegerField(default=180, help_text="Durée de l'examen en minutes (3h par défaut)")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='programmee')
    
    # Configuration
    nombre_questions = models.PositiveIntegerField(default=100, help_text="Nombre de questions dans l'examen")
    questions = models.ManyToManyField('Question', related_name='sessions_examen', blank=True)
    
    # Participants
    participants = models.ManyToManyField(Utilisateur, through='ParticipationExamen', related_name='sessions_examen')
    
    # Métadonnées
    date_creation = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"{self.titre} - {self.date_debut.strftime('%d/%m/%Y %H:%M')}"

# --- Participation à un Examen ---
class ParticipationExamen(models.Model):
    """
    Participation d'un utilisateur à une session d'examen national
    """
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    session_examen = models.ForeignKey(SessionExamen, on_delete=models.CASCADE)
    examen_national = models.OneToOneField(ExamenNational, on_delete=models.CASCADE, null=True, blank=True)
    
    # Statut de participation
    inscrit = models.BooleanField(default=True)
    present = models.BooleanField(default=False)
    
    # Métadonnées
    date_inscription = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('utilisateur', 'session_examen')
    
    def __str__(self):
        return f"{self.utilisateur.nom_complet} - {self.session_examen.titre}"

# --- IP Reset Request ---
from django.utils import timezone
import uuid

class IPResetRequest(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='ip_reset_requests')
    token = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Reset IP {self.utilisateur.nom_complet} ({self.token})"

# --- Session Composition ---
class SessionComposition(models.Model):
    TYPE_SESSION_CHOICES = [
        ('composition', 'Composition Nationale'),
        ('entrainement', 'Entraînement'),
    ]
    
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='sessions_composition')
    matiere_combinee = models.CharField(max_length=20, choices=MATIERES_EXAMEN_NATIONAL)
    type_session = models.CharField(max_length=20, choices=TYPE_SESSION_CHOICES, default='composition')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    duree_prevue = models.IntegerField(help_text="Durée prévue en minutes")
    est_terminee = models.BooleanField(default=False)
    score_final = models.FloatField(null=True, blank=True)
    nombre_bonnes_reponses = models.IntegerField(default=0)
    nombre_total_questions = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.utilisateur.nom_complet} - {self.get_matiere_combinee_display()} ({self.date_creation.strftime('%d/%m/%Y')})"
    
    def calculer_score(self):
        """Calcule le score selon le barème ENA : +0.5 bonne, -0.25 mauvaise, 0 pas de réponse"""
        reponses = self.reponses_composition.all()
        score = 0
        bonnes_reponses = 0
        
        for reponse in reponses:
            if reponse.est_correcte:
                score += 0.5
                bonnes_reponses += 1
            elif reponse.reponse_donnee:  # Mauvaise réponse (pas vide)
                score -= 0.25
        
        self.score_final = max(0, score)  # Score minimum de 0
        self.nombre_bonnes_reponses = bonnes_reponses
        self.nombre_total_questions = reponses.count()
        self.save()
        
        return self.score_final

# --- Réponse Composition ---
class ReponseComposition(models.Model):
    session_composition = models.ForeignKey(SessionComposition, on_delete=models.CASCADE, related_name='reponses_composition')
    question_examen = models.ForeignKey('QuestionExamen', on_delete=models.CASCADE)
    reponse_donnee = models.TextField(blank=True)  # Pour QCM: lettre (a,b,c,d), pour texte: réponse complète
    est_correcte = models.BooleanField(default=False)
    temps_reponse = models.IntegerField(default=0, help_text="Temps de réponse en secondes")
    date_reponse = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('session_composition', 'question_examen')
    
    def __str__(self):
        return f"{self.session_composition.utilisateur.nom_complet} - Q{self.question_examen.id}"

