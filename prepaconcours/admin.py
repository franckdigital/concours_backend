from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Cycle, Matiere, Utilisateur, Question, Choix,
    Tentative, ReponseTentative, Certificat, ImportExcel, Lecon,
    ContenuPedagogique, SessionZoomLive, ConfigurationComposition, QuestionExamen
)

from .utils import notify_ip_reset

@admin.register(Utilisateur)
class UtilisateurAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'telephone', 'password', 'nom_complet', 'is_active', 'is_admin')}),
        ('Permissions', {'fields': ('is_superuser', 'groups', 'user_permissions')}),
        ('Infos connexion', {'fields': ('last_login_ip', 'last_login_ua', 'last_login_device')}),
        ('Dates', {'fields': ('date_inscription', 'last_login')}),
        ('Cycle', {'fields': ('cycle',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'telephone', 'nom_complet', 'password1', 'password2', 'is_active', 'is_admin'),
        }),
    )
    list_display = ('nom_complet', 'email', 'telephone', 'is_admin', 'is_active')
    search_fields = ('nom_complet', 'email', 'telephone')
    list_filter = ('is_admin', 'is_active', 'auth_provider')
    ordering = ('nom_complet',)
    filter_horizontal = ('groups', 'user_permissions',)

    actions = ['reset_ip']

    @admin.action(description="Réinitialiser l'adresse IP de connexion")
    def reset_ip(self, request, queryset):
        for user in queryset:
            user.last_login_ip = None
            user.save(update_fields=['last_login_ip'])
            notify_ip_reset(user)
        self.message_user(request, f"{queryset.count()} utilisateur(s) ont eu leur IP réinitialisée et ont été notifiés.")

@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom')
    search_fields = ('nom',)

from import_export import resources
from import_export.admin import ImportExportModelAdmin

class MatiereResource(resources.ModelResource):
    class Meta:
        model = Matiere
        fields = ('id', 'nom', 'cycle',)
        import_id_fields = ('id',)

@admin.register(Matiere)
class MatiereAdmin(ImportExportModelAdmin):
    resource_class = MatiereResource
    list_display = ('id', 'nom', 'cycle')
    search_fields = ('nom',)
    list_filter = ('cycle',)

@admin.register(Lecon)
class LeconAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'matiere', 'ordre', 'active')
    list_filter = ('matiere', 'active')
    search_fields = ('nom', 'description')
    ordering = ('matiere', 'ordre', 'nom')
    
    def get_form(self, request, obj=None, **kwargs):
        """Personnalise le formulaire pour pré-cocher 'active' lors de la création"""
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Nouvelle leçon (création)
            form.base_fields['active'].initial = True
        return form
    
    def save_model(self, request, obj, form, change):
        """Force l'activation lors de la sauvegarde"""
        if not change:  # Nouvelle création
            obj.active = True
            print(f"[ADMIN DEBUG] Forcing active=True for new lesson: {obj.titre if hasattr(obj, 'titre') else obj.nom}")
        super().save_model(request, obj, form, change)

@admin.register(ContenuPedagogique)
class ContenuPedagogiqueAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'matiere', 'type_contenu', 'ordre', 'active')
    list_filter = ('matiere', 'type_contenu', 'active')
    search_fields = ('titre', 'description')
    ordering = ('matiere', 'ordre', 'titre')
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'matiere', 'type_contenu', 'description', 'ordre', 'active')
        }),
        ('Contenu PDF', {
            'fields': ('fichier_pdf',),
            'classes': ('collapse',)
        }),
        ('Contenu Vidéo', {
            'fields': ('url_video', 'duree_minutes'),
            'classes': ('collapse',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """Personnalise le formulaire pour pré-cocher 'active' lors de la création"""
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Nouveau contenu (création)
            form.base_fields['active'].initial = True
        return form
    
    def save_model(self, request, obj, form, change):
        """Force l'activation lors de la sauvegarde"""
        if not change:  # Nouvelle création
            obj.active = True
            print(f"[ADMIN DEBUG] Forcing active=True for new lesson: {obj.titre if hasattr(obj, 'titre') else obj.nom}")
        super().save_model(request, obj, form, change)

@admin.register(SessionZoomLive)
class SessionZoomLiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'matiere', 'date_session', 'statut', 'nombre_participants_max', 'active')
    list_filter = ('matiere', 'statut', 'active', 'date_session')
    search_fields = ('titre', 'description')
    ordering = ('date_session',)
    date_hierarchy = 'date_session'
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'matiere', 'description', 'active')
        }),
        ('Planning', {
            'fields': ('date_session', 'duree_minutes', 'statut')
        }),
        ('Paramètres Zoom', {
            'fields': ('url_zoom', 'meeting_id', 'mot_de_passe', 'nombre_participants_max')
        }),
    )

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'texte', 'matiere', 'lecon', 'type_question', 'date_ajout')
    list_filter = ('matiere', 'lecon', 'type_question')
    search_fields = ('texte', 'explication')

@admin.register(Choix)
class ChoixAdmin(admin.ModelAdmin):
    list_display = ('id', 'texte', 'question', 'est_correct')
    search_fields = ('texte',)
    list_filter = ('question', 'est_correct')

@admin.register(Tentative)
class TentativeAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'matiere', 'date_test', 'score', 'temps_total_en_secondes')
    search_fields = ('utilisateur__nom_complet',)
    list_filter = ('matiere', 'utilisateur')

@admin.register(ReponseTentative)
class ReponseTentativeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'get_utilisateur', 
        'get_matiere', 
        'get_question_texte', 
        'get_choix_texte', 
        'get_texte_reponse',
        'est_correct', 
        'get_temps_affichage',
        'get_date_tentative'
    )
    list_filter = (
        'tentative__matiere',
        'est_correct',
        'question__type_question',
        'tentative__utilisateur'
    )
    search_fields = (
        'tentative__utilisateur__nom_complet',
        'question__texte',
        'choix__texte',
        'texte_reponse'
    )
    list_select_related = ('tentative', 'tentative__utilisateur', 'tentative__matiere', 'question', 'choix')
    readonly_fields = ('get_question_texte', 'get_choix_texte', 'get_utilisateur', 'get_matiere', 'get_date_tentative')
    date_hierarchy = 'tentative__date_test'
    list_per_page = 20
    
    fieldsets = (
        ('Informations de la tentative', {
            'fields': ('get_utilisateur', 'get_matiere', 'get_date_tentative')
        }),
        ('Détails de la question', {
            'fields': ('get_question_texte', 'get_choix_texte', 'texte_reponse', 'est_correct')
        }),
        ('Métriques', {
            'fields': ('temps_question_en_secondes', 'get_temps_affichage')
        }),
    )
    
    def get_utilisateur(self, obj):
        return obj.tentative.utilisateur.nom_complet
    get_utilisateur.short_description = 'Utilisateur'
    get_utilisateur.admin_order_field = 'tentative__utilisateur__nom_complet'
    
    def get_matiere(self, obj):
        return obj.tentative.matiere.nom
    get_matiere.short_description = 'Matière'
    get_matiere.admin_order_field = 'tentative__matiere__nom'
    
    def get_question_texte(self, obj):
        return obj.question.texte[:100] + '...' if len(obj.question.texte) > 100 else obj.question.texte
    get_question_texte.short_description = 'Question'
    
    def get_choix_texte(self, obj):
        return obj.choix.texte if obj.choix else 'Réponse libre'
    get_choix_texte.short_description = 'Réponse choisie'
    
    def get_texte_reponse(self, obj):
        return obj.texte_reponse[:50] + '...' if obj.texte_reponse and len(obj.texte_reponse) > 50 else obj.texte_reponse
    get_texte_reponse.short_description = 'Réponse texte'
    
    def get_temps_affichage(self, obj):
        if not obj.temps_question_en_secondes:
            return 'N/A'
        minutes = obj.temps_question_en_secondes // 60
        secondes = obj.temps_question_en_secondes % 60
        return f"{minutes:02d}:{secondes:02d}"
    get_temps_affichage.short_description = 'Temps passé'
    get_temps_affichage.admin_order_field = 'temps_question_en_secondes'
    
    def get_date_tentative(self, obj):
        return obj.tentative.date_test
    get_date_tentative.short_description = 'Date tentative'
    get_date_tentative.admin_order_field = 'tentative__date_test'

@admin.register(Certificat)
class CertificatAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'cycle', 'date_obtention', 'score_final')
    search_fields = ('utilisateur__nom_complet',)
    list_filter = ('cycle',)

@admin.register(ImportExcel)
class ImportExcelAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'fichier_nom', 'import_type', 'nombre_elements_importes', 'nombre_echecs', 'status', 'date_import', 'date_fin')
    list_filter = ('import_type', 'status', 'utilisateur', 'date_import')
    search_fields = ('fichier_nom', 'details', 'erreur')
    readonly_fields = ('date_import', 'date_fin', 'details', 'erreur')
    list_select_related = ('utilisateur',)
    date_hierarchy = 'date_import'


# === Configuration des Compositions Nationales ===
@admin.register(ConfigurationComposition)
class ConfigurationCompositionAdmin(admin.ModelAdmin):
    """Admin pour la configuration dynamique des pages de composition"""
    list_display = ('matiere_combinee', 'nom_affichage', 'duree_minutes', 'nombre_questions', 'est_actif', 'date_modification')
    list_filter = ('est_actif', 'matiere_combinee')
    search_fields = ('nom_affichage', 'titre_principal')
    readonly_fields = ('date_creation', 'date_modification')
    
    fieldsets = (
        ('Matière', {
            'fields': ('matiere_combinee', 'nom_affichage', 'est_actif'),
            'description': 'Configuration de base de la matière'
        }),
        ('En-tête de la feuille', {
            'fields': ('titre_principal', 'sous_titre_1', 'sous_titre_2'),
            'description': 'Textes affichés dans l\'en-tête de la feuille de composition'
        }),
        ('Paramètres de l\'épreuve', {
            'fields': ('duree_minutes', 'nombre_questions'),
            'description': 'Durée et nombre de questions'
        }),
        ('Instructions et barème', {
            'fields': ('instruction_principale', 'bareme_bonne_reponse', 'bareme_mauvaise_reponse', 'bareme_absence_reponse'),
            'description': 'Instructions et système de notation'
        }),
        ('Apparence', {
            'fields': ('couleur_primaire', 'couleur_secondaire'),
            'description': 'Couleurs du dégradé de la page'
        }),
        ('Messages et boutons', {
            'fields': ('message_intro', 'bouton_commencer', 'bouton_terminer'),
            'description': 'Textes des messages et boutons'
        }),
        ('Pied de page', {
            'fields': ('pied_de_page',),
            'classes': ('collapse',),
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',),
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Empêche la modification de matiere_combinee après création"""
        if obj:
            return self.readonly_fields + ('matiere_combinee',)
        return self.readonly_fields


# === Questions d'Examen National ===
@admin.register(QuestionExamen)
class QuestionExamenAdmin(admin.ModelAdmin):
    """Admin pour les questions de l'examen national (composition)"""
    list_display = ('id', 'get_texte_court', 'matiere_combinee', 'type_question', 'bonne_reponse', 'active', 'date_creation')
    list_filter = ('matiere_combinee', 'type_question', 'active')
    search_fields = ('texte', 'choix_a', 'choix_b', 'choix_c', 'choix_d', 'explication')
    list_editable = ('active',)
    ordering = ('-date_creation', 'matiere_combinee')
    date_hierarchy = 'date_creation'
    list_per_page = 50
    
    fieldsets = (
        ('Question', {
            'fields': ('texte', 'matiere_combinee', 'type_question', 'active'),
        }),
        ('Choix de réponses', {
            'fields': ('choix_a', 'choix_b', 'choix_c', 'choix_d'),
            'description': 'Les 4 choix possibles (A, B, C, D)'
        }),
        ('Réponse correcte', {
            'fields': ('bonne_reponse', 'explication'),
            'description': 'Indiquez la lettre de la bonne réponse (A, B, C ou D)'
        }),
    )
    
    def get_texte_court(self, obj):
        """Affiche un extrait du texte de la question"""
        return obj.texte[:80] + '...' if len(obj.texte) > 80 else obj.texte
    get_texte_court.short_description = 'Question'
    
    actions = ['activer_questions', 'desactiver_questions']
    
    @admin.action(description="Activer les questions sélectionnées")
    def activer_questions(self, request, queryset):
        count = queryset.update(active=True)
        self.message_user(request, f"{count} question(s) activée(s).")
    
    @admin.action(description="Désactiver les questions sélectionnées")
    def desactiver_questions(self, request, queryset):
        count = queryset.update(active=False)
        self.message_user(request, f"{count} question(s) désactivée(s).")

