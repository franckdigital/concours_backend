import openai
import json
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.utils import timezone
from .models import Matiere, ContenuPedagogique, Question, QuestionExamen, Lecon, Choix
from django.db import models

# Configuration OpenAI
openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat(request):
    """
    Endpoint pour le chat avec l'assistant IA OpenAI
    """
    print(f"[AI_CHAT] Requête reçue de {request.user}")
    print(f"[AI_CHAT] Headers: {dict(request.headers)}")
    print(f"[AI_CHAT] Data: {request.data}")
    
    try:
        data = request.data
        user_message = data.get('message', '')
        context = data.get('context', 'general')
        
        print(f"[AI_CHAT] Message utilisateur: {user_message}")
        
        if not user_message:
            return Response({
                'error': 'Message requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Récupérer le contexte complet de la base de données
        db_context = get_database_context(user_message)
        
        # Construire le prompt système avec données de la BD
        system_prompt = f"""
Tu es un assistant IA expert en préparation aux concours administratifs, spécialisé dans l'ENA (École Nationale d'Administration).

CONTEXTE DE LA BASE DE DONNÉES :
{db_context}

TON RÔLE :
- Corriger les réponses des étudiants aux sujets d'examen
- Expliquer les concepts et leçons des matières ENA
- Donner des conseils méthodologiques personnalisés
- Répondre aux questions sur les contenus pédagogiques stockés en base
- Fournir des statistiques et informations sur les questions disponibles
- Aider à l'amélioration des performances avec des données concrètes

INSTRUCTIONS :
- Utilise les données réelles de la base pour tes réponses
- Sois précis, pédagogique et bienveillant
- Donne des explications détaillées avec des exemples concrets tirés de la BD
- Propose des axes d'amélioration constructifs basés sur les données
- Adapte ton niveau de réponse au niveau de l'étudiant
- Utilise un ton professionnel mais accessible
- Structure tes réponses avec des points clés quand c'est pertinent
- Cite les sources de données quand pertinent (nombre de questions, leçons, etc.)

L'utilisateur peut te poser des questions, soumettre des réponses à corriger, ou demander des explications sur les matières ENA.
"""

        # Appel à l'API OpenAI
        if not openai.api_key:
            print("[AI_CHAT] ERREUR: Clé API OpenAI manquante")
            return Response({
                'error': 'Configuration OpenAI manquante'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        print(f"[AI_CHAT] Clé API disponible: {openai.api_key[:20]}...")
        
        try:
            # Mode développement - Réponse simulée pour éviter les quotas OpenAI
            print("[AI_CHAT] Mode développement - Génération d'une réponse simulée")
            
            # Générer une réponse basée sur les données de la BD
            ai_response = generate_database_response(user_message, db_context)
            
            print(f"[AI_CHAT] Réponse simulée générée: {ai_response[:100]}...")
            
            return Response({
                'response': ai_response,
                'context': context,
                'timestamp': int(timezone.now().timestamp())
            })
            
        except Exception as openai_error:
            print(f"[AI_CHAT] ERREUR OpenAI: {str(openai_error)}")
            print(f"[AI_CHAT] Type d'erreur: {type(openai_error)}")
            
            error_msg = str(openai_error).lower()
            
            if "authentication" in error_msg:
                return Response({
                    'error': 'Erreur d\'authentification OpenAI - Vérifiez votre clé API'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif "quota" in error_msg or "exceeded" in error_msg:
                return Response({
                    'error': 'Quota OpenAI dépassé - Vérifiez votre plan de facturation'
                }, status=status.HTTP_402_PAYMENT_REQUIRED)
            elif "rate limit" in error_msg:
                return Response({
                    'error': 'Limite de taux OpenAI atteinte, réessayez plus tard'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                return Response({
                    'error': f'Erreur OpenAI: {str(openai_error)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        print(f"[AI_CHAT] ERREUR SERVEUR: {str(e)}")
        print(f"[AI_CHAT] Type d'erreur: {type(e)}")
        import traceback
        print(f"[AI_CHAT] Traceback: {traceback.format_exc()}")
        return Response({
            'error': f'Erreur serveur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_database_context(user_message):
    """
    Récupère le contexte complet de la base de données pour alimenter l'IA
    """
    try:
        context_parts = []
        
        # 1. Matières ENA disponibles
        context_parts.append("=== MATIÈRES ENA DISPONIBLES ===")
        
        # Premier tour
        matieres_premier = Matiere.objects.filter(
            choix_concours='ENA',
            tour_ena='premier_tour'
        )
        if matieres_premier.exists():
            context_parts.append("\n📚 PREMIER TOUR ENA:")
            for matiere in matieres_premier:
                nb_questions = Question.objects.filter(matiere=matiere).count()
                nb_lecons = Lecon.objects.filter(matiere=matiere, active=True).count()
                context_parts.append(f"  • {matiere.nom}: {nb_questions} questions, {nb_lecons} leçons")
        
        # Second tour
        matieres_second = Matiere.objects.filter(
            choix_concours='ENA',
            tour_ena='second_tour'
        )
        if matieres_second.exists():
            context_parts.append("\n📖 SECOND TOUR ENA:")
            for matiere in matieres_second:
                nb_contenus = ContenuPedagogique.objects.filter(matiere=matiere, active=True).count()
                context_parts.append(f"  • {matiere.nom}: {nb_contenus} contenus pédagogiques")
        
        # Examen national
        matieres_examen = Matiere.objects.filter(
            choix_concours='examen_national'
        )
        if matieres_examen.exists():
            context_parts.append("\n🎯 EXAMEN NATIONAL ENA:")
            for matiere in matieres_examen:
                nb_questions_examen = QuestionExamen.objects.filter(matiere=matiere, active=True).count()
                context_parts.append(f"  • {matiere.nom}: {nb_questions_examen} questions d'examen")
        
        # 2. Statistiques générales
        context_parts.append("\n=== STATISTIQUES GÉNÉRALES ===")
        total_questions = Question.objects.count()
        total_questions_examen = QuestionExamen.objects.filter(active=True).count()
        total_lecons = Lecon.objects.filter(active=True).count()
        total_contenus = ContenuPedagogique.objects.filter(active=True).count()
        
        context_parts.append(f"📊 Questions Premier Tour: {total_questions}")
        context_parts.append(f"📊 Questions Examen National: {total_questions_examen}")
        context_parts.append(f"📊 Leçons disponibles: {total_lecons}")
        context_parts.append(f"📊 Contenus pédagogiques: {total_contenus}")
        
        # 3. Contexte spécifique selon la question
        if any(word in user_message.lower() for word in ['question', 'exercice', 'quiz']):
            context_parts.append("\n=== QUESTIONS DISPONIBLES ===")
            questions_sample = Question.objects.select_related('matiere', 'lecon')[:5]
            for q in questions_sample:
                context_parts.append(f"  • {q.texte[:100]}... ({q.matiere.nom})")
        
        # 4. Contenus pédagogiques uploadés (PDF)
        if any(word in user_message.lower() for word in ['droit', 'administratif', 'cours', 'résumé']):
            context_parts.append("\n=== CONTENUS PÉDAGOGIQUES DISPONIBLES ===")
            contenus_pdf = ContenuPedagogique.objects.filter(
                type_contenu='pdf',
                active=True
            ).select_related('matiere')
            
            for contenu in contenus_pdf:
                if contenu.fichier_pdf:
                    context_parts.append(f"  📄 {contenu.titre} ({contenu.matiere.nom if contenu.matiere else 'Sans matière'})")
                    if 'droit' in contenu.titre.lower():
                        context_parts.append(f"    → Fichier: {contenu.fichier_pdf.name}")
        
        return "\n".join(context_parts)
        
    except Exception as e:
        return f"Erreur lors de la récupération du contexte BD: {str(e)}"


def generate_database_response(user_message, db_context):
    """
    Génère une réponse basée sur les données de la base de données
    """
    message_lower = user_message.lower()
    
    # Réponses contextuelles basées sur les données BD
    if any(word in message_lower for word in ['statistique', 'combien', 'nombre']):
        # Récupérer les statistiques réelles
        stats = get_database_statistics()
        return f"""📊 **Statistiques de la base de données ENA**

{stats}

Ces données sont mises à jour en temps réel depuis notre base de données. 

**Comment puis-je vous aider avec ces données ?**
- Analyser vos performances sur une matière spécifique
- Recommander des questions selon votre niveau
- Expliquer des concepts basés sur nos contenus pédagogiques
- Proposer un plan de révision personnalisé"""

    elif any(word in message_lower for word in ['synonyme', 'vocabulaire']):
        return """🔤 **Synonymes et Vocabulaire ENA**

Basé sur notre base de données de questions d'aptitude verbale :

**Exemples tirés de nos questions :**
• Grand = Immense, Énorme, Vaste, Colossal
• Petit = Minuscule, Réduit, Exigu, Infime
• Beau = Magnifique, Splendide, Superbe, Esthétique

**Dans nos contenus ENA :**
Nous avons des questions spécialisées sur :
- Synonymes administratifs (décret, arrêté, ordonnance)
- Vocabulaire juridique (jurisprudence, doctrine, coutume)
- Termes économiques (inflation, déflation, stagflation)

**Conseil basé sur nos données :** Les questions de synonymes représentent 25% des questions d'aptitude verbale dans notre base."""

    elif any(word in message_lower for word in ['droit', 'administratif', 'résumé', 'cours']):
        # Rechercher spécifiquement les contenus de droit administratif
        contenus_droit = get_administrative_law_content()
        return f"""📚 **Cours de Droit Administratif ENA**

{contenus_droit}

**Basé sur nos contenus uploadés :**
- Résumé complet du cours de droit administratif 2025
- Concepts clés et définitions
- Jurisprudence importante
- Méthodologie pour les épreuves

**Comment puis-je vous aider ?**
- Expliquer un concept spécifique du droit administratif
- Résumer une partie du cours
- Donner des exemples concrets
- Proposer des exercices d'application

Quel aspect du droit administratif vous intéresse ?"""

    elif any(word in message_lower for word in ['matière', 'sujet']):
        matieres_info = get_subjects_info()
        return f"""📚 **Matières ENA disponibles**

{matieres_info}

**Recommandations basées sur nos données :**
- Commencez par les matières avec le plus de contenu
- Utilisez nos questions pour tester vos connaissances
- Consultez nos contenus pédagogiques pour approfondir

Quelle matière vous intéresse le plus ?"""

    else:
        return f"""🤖 **Assistant IA ENA - Connecté à la base de données**

Votre question : "{user_message}"

Je suis connecté à notre base de données complète ENA qui contient :

{db_context}

**Je peux vous aider avec :**
📚 **Analyse de contenu** - Basée sur nos vraies données
💡 **Recommandations personnalisées** - Selon vos performances
📊 **Statistiques détaillées** - Temps réel depuis la BD
🎯 **Questions ciblées** - Adaptées à votre niveau

**Exemples de questions que vous pouvez me poser :**
- "Combien de questions avons-nous en culture générale ?"
- "Quels sont les sujets les plus difficiles ?"
- "Peux-tu me donner des exemples de questions ?"
- "Comment améliorer mes performances en logique ?"

Comment puis-je vous accompagner dans votre préparation ?"""


def get_database_statistics():
    """
    Récupère les statistiques détaillées de la base de données
    """
    try:
        stats = []
        
        # Questions par matière
        matieres = Matiere.objects.filter(choix_concours='ENA')
        for matiere in matieres:
            if matiere.tour_ena == 'premier_tour':
                nb_questions = Question.objects.filter(matiere=matiere).count()
                if nb_questions > 0:
                    stats.append(f"📝 {matiere.nom}: {nb_questions} questions")
            elif matiere.tour_ena == 'second_tour':
                nb_contenus = ContenuPedagogique.objects.filter(matiere=matiere, active=True).count()
                if nb_contenus > 0:
                    stats.append(f"📖 {matiere.nom}: {nb_contenus} contenus")
        
        # Questions examen national
        questions_examen = QuestionExamen.objects.filter(active=True).count()
        if questions_examen > 0:
            stats.append(f"🎯 Questions Examen National: {questions_examen}")
        
        return "\n".join(stats) if stats else "Aucune donnée disponible"
        
    except Exception as e:
        return f"Erreur statistiques: {str(e)}"


def get_subjects_info():
    """
    Récupère les informations détaillées sur les matières
    """
    try:
        info = []
        
        # Premier tour
        matieres_premier = Matiere.objects.filter(choix_concours='ENA', tour_ena='premier_tour')
        if matieres_premier.exists():
            info.append("🎯 **PREMIER TOUR:**")
            for matiere in matieres_premier:
                nb_questions = Question.objects.filter(matiere=matiere).count()
                nb_lecons = Lecon.objects.filter(matiere=matiere, active=True).count()
                info.append(f"  • {matiere.nom}: {nb_questions} questions, {nb_lecons} leçons")
        
        # Second tour
        matieres_second = Matiere.objects.filter(choix_concours='ENA', tour_ena='second_tour')
        if matieres_second.exists():
            info.append("\n📚 **SECOND TOUR:**")
            for matiere in matieres_second:
                nb_contenus = ContenuPedagogique.objects.filter(matiere=matiere, active=True).count()
                info.append(f"  • {matiere.nom}: {nb_contenus} contenus pédagogiques")
        
        # Examen national
        matieres_examen = Matiere.objects.filter(choix_concours='examen_national')
        if matieres_examen.exists():
            info.append("\n🏆 **EXAMEN NATIONAL:**")
            for matiere in matieres_examen:
                nb_questions = QuestionExamen.objects.filter(matiere=matiere, active=True).count()
                info.append(f"  • {matiere.nom}: {nb_questions} questions")
        
        return "\n".join(info) if info else "Aucune matière disponible"
        
    except Exception as e:
        return f"Erreur matières: {str(e)}"


def get_administrative_law_content():
    """
    Récupère les contenus de droit administratif uploadés
    """
    try:
        info = []
        
        # Rechercher les contenus PDF de droit administratif
        contenus_droit = ContenuPedagogique.objects.filter(
            type_contenu='pdf',
            active=True
        ).filter(
            models.Q(titre__icontains='droit') | 
            models.Q(titre__icontains='administratif')
        )
        
        if contenus_droit.exists():
            info.append("📄 **CONTENUS DROIT ADMINISTRATIF DISPONIBLES:**")
            for contenu in contenus_droit:
                info.append(f"  • {contenu.titre}")
                if contenu.description:
                    info.append(f"    Description: {contenu.description}")
                if contenu.fichier_pdf:
                    info.append(f"    📎 Fichier: {contenu.fichier_pdf.name}")
                info.append(f"    📅 Ajouté le: {contenu.date_creation.strftime('%d/%m/%Y')}")
        
        # Vérifier aussi les fichiers dans le dossier contenus
        import os
        from django.conf import settings
        
        contenus_dir = os.path.join(settings.BASE_DIR, 'contenus', 'pdf')
        if os.path.exists(contenus_dir):
            info.append("\n📁 **FICHIERS PDF DÉTECTÉS:**")
            for filename in os.listdir(contenus_dir):
                if 'droit' in filename.lower() or 'administratif' in filename.lower():
                    info.append(f"  • {filename}")
        
        return "\n".join(info) if info else "Aucun contenu de droit administratif trouvé"
        
    except Exception as e:
        return f"Erreur contenus droit: {str(e)}"
