# Questions d'Examen National ENA - Documentation Complète

## 📋 Vue d'Ensemble

Ce module implémente un système complet de gestion des questions spécifiques à l'examen national ENA, séparé des questions de quiz classiques pour garantir l'unicité et la qualité des épreuves nationales.

## 🏗️ Architecture

### Modèle QuestionExamen

Le modèle `QuestionExamen` est conçu pour gérer tous les types de questions de l'examen national :

```python
class QuestionExamen(models.Model):
    # Identification unique
    code_question = models.CharField(max_length=20, unique=True)
    
    # Contenu de la question
    texte = models.TextField()
    type_question = models.CharField(max_length=20, choices=TYPE_CHOICES)
    matiere_combinee = models.CharField(max_length=20, choices=MATIERE_COMBINEE_CHOICES)
    
    # Options pour QCM (choix unique/multiple)
    choix_a = models.TextField(blank=True)
    choix_b = models.TextField(blank=True)
    choix_c = models.TextField(blank=True)
    choix_d = models.TextField(blank=True)
    choix_e = models.TextField(blank=True)
    
    # Réponses et correction
    bonne_reponse = models.CharField(max_length=10, blank=True)
    reponse_attendue = models.TextField(blank=True)
    correction_mode = models.CharField(max_length=10, choices=CORRECTION_MODE_CHOICES)
    
    # Métadonnées pédagogiques
    explication = models.TextField(blank=True)
    difficulte = models.CharField(max_length=10, choices=DIFFICULTE_CHOICES)
    temps_limite_secondes = models.PositiveIntegerField(default=120)
    
    # Gestion et validation
    active = models.BooleanField(default=True)
    validee = models.BooleanField(default=False)
    nombre_utilisations = models.PositiveIntegerField(default=0)
    
    # Audit
    creee_par = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
```

### Types de Questions Supportés

#### 1. Choix Unique (QCM Classique)
- **Champs requis** : `choix_a`, `choix_b`, `bonne_reponse`
- **Format réponse** : A, B, C, D, ou E
- **Exemple** : Question d'histoire avec 4 options

#### 2. Choix Multiple
- **Champs requis** : `choix_a`, `choix_b`, `bonne_reponse`
- **Format réponse** : Combinaison de lettres (ex: ACE)
- **Exemple** : Synonymes d'un mot (plusieurs bonnes réponses)

#### 3. Vrai/Faux
- **Champs requis** : `bonne_reponse`
- **Format réponse** : VRAI ou FAUX
- **Exemple** : Affirmation historique à valider

#### 4. Texte Court
- **Champs requis** : `reponse_attendue`, `correction_mode`
- **Modes correction** : exacte, mot_cle, regex
- **Exemple** : Traduction courte, définition

#### 5. Texte Long
- **Champs requis** : `reponse_attendue`, `correction_mode`
- **Modes correction** : mot_cle (recommandé), regex
- **Exemple** : Rédaction, analyse, argumentation

### Matières Combinées

#### 1. Culture Générale + Aptitude Verbale (`culture_aptitude`)
- **Quota examen** : 60 questions
- **Domaines** : Histoire, géographie, littérature, vocabulaire, compréhension
- **Temps moyen** : 120 secondes par question

#### 2. Logique + Raisonnement (`logique_combinee`)
- **Quota examen** : 40 questions
- **Domaines** : Suites logiques, analogies, déduction, mathématiques
- **Temps moyen** : 90 secondes par question

#### 3. Anglais (`anglais`)
- **Quota examen** : 30 questions
- **Domaines** : Grammaire, vocabulaire, compréhension, expression
- **Temps moyen** : 90 secondes par question

## 🔧 API REST

### Endpoints Principaux

#### Gestion CRUD
```http
GET    /api/questions-examen/           # Liste des questions
POST   /api/questions-examen/           # Créer une question
GET    /api/questions-examen/{id}/      # Détail d'une question
PUT    /api/questions-examen/{id}/      # Modifier une question
DELETE /api/questions-examen/{id}/      # Supprimer une question
```

#### Endpoints Spécialisés
```http
GET  /api/questions-examen/statistiques/         # Statistiques globales
POST /api/questions-examen/valider_questions/    # Validation en masse
GET  /api/questions-examen/questions_pour_examen/ # Vérification quota examen
```

### Filtres Disponibles

```http
GET /api/questions-examen/?matiere_combinee=culture_aptitude
GET /api/questions-examen/?type_question=choix_unique
GET /api/questions-examen/?difficulte=moyen
GET /api/questions-examen/?active=true
GET /api/questions-examen/?validee=true
```

### Exemples de Réponses

#### Statistiques
```json
{
  "total_questions": 150,
  "questions_actives": 140,
  "questions_validees": 120,
  "pourcentage_validees": 80.0,
  "stats_par_matiere": {
    "culture_aptitude": {
      "nom": "Culture générale + Aptitude verbale",
      "total": 60,
      "actives": 55,
      "validees": 50
    },
    "logique_combinee": {
      "nom": "Logique + Raisonnement",
      "total": 50,
      "actives": 45,
      "validees": 40
    },
    "anglais": {
      "nom": "Anglais",
      "total": 40,
      "actives": 40,
      "validees": 30
    }
  },
  "stats_par_type": {
    "choix_unique": {"nom": "Choix unique", "count": 90},
    "choix_multiple": {"nom": "Choix multiple", "count": 20},
    "vrai_faux": {"nom": "Vrai/Faux", "count": 20},
    "texte_court": {"nom": "Texte court", "count": 15},
    "texte_long": {"nom": "Texte long", "count": 5}
  }
}
```

#### Vérification Quota Examen
```json
{
  "questions_disponibles": {
    "culture_aptitude": {
      "nom": "Culture générale + Aptitude verbale",
      "disponibles": 65,
      "requis": 60,
      "suffisant": true
    },
    "logique_combinee": {
      "nom": "Logique + Raisonnement",
      "disponibles": 45,
      "requis": 40,
      "suffisant": true
    },
    "anglais": {
      "nom": "Anglais",
      "disponibles": 35,
      "requis": 30,
      "suffisant": true
    }
  },
  "total_disponible": 145,
  "total_requis": 130,
  "peut_creer_examen": true,
  "message": "Examen possible"
}
```

## 📊 Import Excel

### Script d'Import

Le script `import_questions_examen_excel.py` permet l'import en masse depuis Excel :

```bash
# Créer un template
python import_questions_examen_excel.py --template

# Importer des questions
python import_questions_examen_excel.py --fichier questions_ena.xlsx
```

### Format Excel Requis

#### Colonnes Obligatoires
- `texte` : Énoncé de la question
- `type_question` : Type (choix_unique, choix_multiple, vrai_faux, texte_court, texte_long)
- `matiere_combinee` : Matière (culture_aptitude, logique_combinee, anglais)
- `difficulte` : Niveau (facile, moyen, difficile)

#### Colonnes Conditionnelles

**Pour QCM (choix_unique, choix_multiple) :**
- `choix_a`, `choix_b` : Obligatoires
- `choix_c`, `choix_d`, `choix_e` : Optionnels
- `bonne_reponse` : Obligatoire (A, B, C, D, E ou combinaison)

**Pour Vrai/Faux :**
- `bonne_reponse` : Obligatoire (VRAI ou FAUX)

**Pour Texte (court/long) :**
- `reponse_attendue` : Obligatoire
- `correction_mode` : Obligatoire (exacte, mot_cle, regex)

#### Colonnes Optionnelles
- `code_question` : Auto-généré si vide
- `explication` : Explication de la réponse
- `temps_limite_secondes` : Défaut 120s
- `active` : Défaut True
- `validee` : Défaut False
- `creee_par` : Défaut "Import Excel"

### Validation Automatique

Le script valide automatiquement :
- ✅ Format des types de questions
- ✅ Cohérence des matières
- ✅ Présence des champs requis selon le type
- ✅ Format des réponses (A-E pour QCM, VRAI/FAUX, etc.)
- ✅ Unicité des codes questions

### Rapport d'Import

```
==============================================================
📊 RAPPORT D'IMPORT DES QUESTIONS D'EXAMEN
==============================================================
✅ Questions importées avec succès: 95
❌ Questions échouées: 5
📈 Taux de succès: 95.0%

🚨 ERREURS DÉTECTÉES (5):
  - Ligne 12: Type de question invalide: choix_simple
  - Ligne 25: Matière combinée invalide: mathematiques
  - Ligne 38: Les choix A et B sont obligatoires pour les QCM
  - Ligne 47: La bonne réponse doit être 'VRAI' ou 'FAUX'
  - Ligne 63: La réponse attendue est obligatoire pour les questions texte

📚 RÉPARTITION PAR MATIÈRE:
  - Culture générale + Aptitude verbale: 65 questions
  - Logique + Raisonnement: 45 questions
  - Anglais: 35 questions
==============================================================
```

## 🎯 Intégration avec l'Examen National

### Sélection des Questions

```python
def selectionner_questions_examen():
    """Sélectionne les questions pour un examen national"""
    
    # Culture générale + Aptitude verbale (60 questions)
    questions_culture = QuestionExamen.objects.filter(
        matiere_combinee='culture_aptitude',
        active=True,
        validee=True
    ).order_by('?')[:60]
    
    # Logique + Raisonnement (40 questions)
    questions_logique = QuestionExamen.objects.filter(
        matiere_combinee='logique_combinee',
        active=True,
        validee=True
    ).order_by('?')[:40]
    
    # Anglais (30 questions)
    questions_anglais = QuestionExamen.objects.filter(
        matiere_combinee='anglais',
        active=True,
        validee=True
    ).order_by('?')[:30]
    
    return {
        'culture_aptitude': list(questions_culture),
        'logique_combinee': list(questions_logique),
        'anglais': list(questions_anglais)
    }
```

### Correction Intelligente

```python
def corriger_reponse(question, reponse_utilisateur):
    """Corrige une réponse selon le type de question"""
    
    if question.type_question in ['choix_unique', 'choix_multiple', 'vrai_faux']:
        # Correction exacte pour QCM et Vrai/Faux
        return question.bonne_reponse.upper() == reponse_utilisateur.upper()
    
    elif question.type_question in ['texte_court', 'texte_long']:
        if question.correction_mode == 'exacte':
            # Comparaison exacte (insensible à la casse)
            return question.reponse_attendue.lower().strip() == reponse_utilisateur.lower().strip()
        
        elif question.correction_mode == 'mot_cle':
            # Recherche de mots-clés
            mots_cles = question.reponse_attendue.lower().split(',')
            reponse_lower = reponse_utilisateur.lower()
            return any(mot.strip() in reponse_lower for mot in mots_cles)
        
        elif question.correction_mode == 'regex':
            # Expression régulière
            import re
            return bool(re.search(question.reponse_attendue, reponse_utilisateur, re.IGNORECASE))
    
    return False
```

## 🔒 Sécurité et Permissions

### Niveaux d'Accès

#### Administrateurs
- ✅ CRUD complet sur toutes les questions
- ✅ Validation en masse
- ✅ Import/Export Excel
- ✅ Accès aux statistiques détaillées

#### Enseignants
- ✅ Lecture de toutes les questions validées
- ✅ Création de nouvelles questions (non validées)
- ✅ Modification de leurs propres questions
- ❌ Validation des questions

#### Étudiants
- ✅ Accès aux questions pendant l'examen uniquement
- ❌ Accès aux bonnes réponses
- ❌ Accès aux explications (sauf après correction)

### Serializers Sécurisés

```python
# Pour les examens en cours (sans réponses)
class QuestionExamenPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionExamen
        exclude = ['bonne_reponse', 'reponse_attendue', 'explication']

# Pour l'administration complète
class QuestionExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionExamen
        fields = '__all__'
```

## 📈 Monitoring et Analytics

### Métriques Suivies

- **Utilisation** : Nombre d'utilisations par question
- **Performance** : Taux de réussite par question
- **Qualité** : Questions à réviser (taux d'échec élevé)
- **Couverture** : Répartition par matière et difficulté

### Alertes Automatiques

- ⚠️ Stock insuffisant pour créer un examen
- ⚠️ Questions non validées en attente
- ⚠️ Déséquilibre dans la répartition par matière
- ⚠️ Questions avec taux d'échec anormal

## 🚀 Déploiement et Maintenance

### Migration Django

```bash
# Créer les migrations
python manage.py makemigrations prepaconcours

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur pour l'admin
python manage.py createsuperuser
```

### Initialisation des Données

```bash
# Générer le template Excel
python import_questions_examen_excel.py --template

# Importer les premières questions
python import_questions_examen_excel.py --fichier template_questions_examen_ena.xlsx
```

### Maintenance Régulière

#### Hebdomadaire
- Vérifier le stock de questions par matière
- Valider les nouvelles questions soumises
- Analyser les statistiques de performance

#### Mensuelle
- Réviser les questions avec taux d'échec élevé
- Ajouter de nouvelles questions selon les besoins
- Mettre à jour les explications et corrections

#### Annuelle
- Renouveler 30% du stock de questions
- Analyser les tendances de performance
- Ajuster les quotas par matière si nécessaire

## 🔧 Dépannage

### Problèmes Courants

#### Import Excel Échoue
```bash
# Vérifier le format du fichier
python -c "import pandas as pd; print(pd.read_excel('fichier.xlsx').columns.tolist())"

# Valider les données
python import_questions_examen_excel.py --fichier fichier.xlsx --dry-run
```

#### Questions Non Sélectionnées
```python
# Vérifier le statut des questions
QuestionExamen.objects.filter(active=False).count()
QuestionExamen.objects.filter(validee=False).count()

# Activer/valider en masse
QuestionExamen.objects.filter(matiere_combinee='culture_aptitude').update(active=True, validee=True)
```

#### Performance Lente
```python
# Ajouter des index sur les champs de filtre
class Meta:
    indexes = [
        models.Index(fields=['matiere_combinee', 'active', 'validee']),
        models.Index(fields=['type_question']),
        models.Index(fields=['difficulte']),
    ]
```

## 📚 Ressources Supplémentaires

- **Documentation Django** : https://docs.djangoproject.com/
- **Django REST Framework** : https://www.django-rest-framework.org/
- **Pandas Excel** : https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
- **Expressions Régulières** : https://docs.python.org/3/library/re.html

---

**Version** : 1.0  
**Dernière mise à jour** : 14 août 2025  
**Auteur** : Système ENA - Questions d'Examen National
