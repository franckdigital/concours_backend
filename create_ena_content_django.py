#!/usr/bin/env python3
"""
Script Django pour créer des leçons et des questions pour les matières ENA
À exécuter avec: python manage.py shell < create_ena_content_django.py
"""

from admin.models import Matiere, Lecon, Question, Choix

def create_ena_lessons_and_questions():
    """Crée des leçons et des questions pour chaque matière ENA"""
    
    print("🚀 Création des leçons et questions pour les matières ENA...")
    
    # Récupérer les matières ENA existantes
    matieres_ena = Matiere.objects.filter(concours='ena')
    print(f"📚 Matières ENA trouvées: {matieres_ena.count()}")
    
    for matiere in matieres_ena:
        print(f"\n🎯 Traitement de la matière: {matiere.nom} (ID: {matiere.id})")
        
        # Créer des leçons pour cette matière
        create_lessons_for_matiere(matiere)
        
        # Créer des questions pour chaque leçon
        lecons = Lecon.objects.filter(matiere=matiere)
        for lecon in lecons:
            create_questions_for_lecon(matiere, lecon)
    
    print("\n✅ Création terminée avec succès!")

def create_lessons_for_matiere(matiere):
    """Crée des leçons pour une matière donnée"""
    
    lessons_data = {
        'Anglais': [
            'Grammaire de base',
            'Vocabulaire essentiel',
            'Compréhension écrite',
            'Expression écrite'
        ],
        'Aptitude verbale': [
            'Synonymes et antonymes',
            'Analogies verbales',
            'Compréhension de texte',
            'Logique verbale'
        ],
        'Culture générale': [
            'Histoire de France',
            'Géographie mondiale',
            'Institutions françaises',
            'Actualités politiques'
        ],
        'Logique d\'organisation': [
            'Planification et gestion',
            'Analyse de processus',
            'Résolution de problèmes',
            'Organisation du travail'
        ],
        'Logique numérique': [
            'Suites numériques',
            'Calculs et pourcentages',
            'Graphiques et tableaux',
            'Raisonnement mathématique'
        ]
    }
    
    lecons_names = lessons_data.get(matiere.nom, ['Leçon générale 1', 'Leçon générale 2'])
    
    for i, lecon_name in enumerate(lecons_names, 1):
        lecon, created = Lecon.objects.get_or_create(
            nom=lecon_name,
            matiere=matiere,
            defaults={
                'description': f'Leçon {i} de {matiere.nom}',
                'ordre': i
            }
        )
        
        if created:
            print(f"  ✅ Leçon créée: {lecon_name}")
        else:
            print(f"  ℹ️ Leçon existe déjà: {lecon_name}")

def create_questions_for_lecon(matiere, lecon):
    """Crée des questions variées pour une leçon"""
    
    print(f"    📝 Création de questions pour: {lecon.nom}")
    
    # Questions spécifiques par matière et leçon
    questions_data = get_questions_for_matiere_lecon(matiere.nom, lecon.nom)
    
    for question_data in questions_data:
        create_single_question(matiere, lecon, question_data)

def get_questions_for_matiere_lecon(matiere_nom, lecon_nom):
    """Retourne les données de questions pour une matière et leçon spécifique"""
    
    # Questions pour Anglais
    if matiere_nom == 'Anglais':
        if 'Grammaire' in lecon_nom:
            return [
                {
                    'texte': 'What is the correct form: "She ___ very happy"?',
                    'type': 'choix_unique',
                    'choix': [
                        {'texte': 'am', 'correct': False},
                        {'texte': 'is', 'correct': True},
                        {'texte': 'are', 'correct': False},
                        {'texte': 'be', 'correct': False}
                    ],
                    'explication': 'Avec "she" (3ème personne du singulier), on utilise "is".'
                },
                {
                    'texte': 'Select all correct forms of past tense:',
                    'type': 'choix_multiple',
                    'choix': [
                        {'texte': 'went', 'correct': True},
                        {'texte': 'saw', 'correct': True},
                        {'texte': 'goed', 'correct': False},
                        {'texte': 'catched', 'correct': False}
                    ],
                    'explication': '"Went" et "saw" sont des formes correctes du passé.'
                },
                {
                    'texte': 'The word "beautiful" is an adjective.',
                    'type': 'vrai_faux',
                    'choix': [
                        {'texte': 'Vrai', 'correct': True},
                        {'texte': 'Faux', 'correct': False}
                    ],
                    'explication': '"Beautiful" est effectivement un adjectif.'
                },
                {
                    'texte': 'What is the past tense of "go"?',
                    'type': 'texte_court',
                    'reponse_attendue': 'went',
                    'explication': 'Le passé de "go" est "went" (verbe irrégulier).'
                },
                {
                    'texte': 'Write a short paragraph about your hobbies in English.',
                    'type': 'texte_long',
                    'reponse_attendue': 'I enjoy reading books and playing sports. My favorite hobby is photography because it allows me to capture beautiful moments. I also like cooking and trying new recipes.',
                    'explication': 'Un paragraphe sur les loisirs doit inclure des activités personnelles avec des explications.'
                }
            ]
        else:
            return [
                {
                    'texte': f'Question générale pour {lecon_nom}',
                    'type': 'choix_unique',
                    'choix': [
                        {'texte': 'Option A', 'correct': True},
                        {'texte': 'Option B', 'correct': False},
                        {'texte': 'Option C', 'correct': False},
                        {'texte': 'Option D', 'correct': False}
                    ],
                    'explication': f'Explication pour {lecon_nom}.'
                }
            ]
    
    # Questions pour Aptitude verbale
    elif matiere_nom == 'Aptitude verbale':
        if 'Synonymes' in lecon_nom:
            return [
                {
                    'texte': 'Quel est le synonyme de "difficile" ?',
                    'type': 'choix_unique',
                    'choix': [
                        {'texte': 'facile', 'correct': False},
                        {'texte': 'ardu', 'correct': True},
                        {'texte': 'simple', 'correct': False},
                        {'texte': 'évident', 'correct': False}
                    ],
                    'explication': '"Ardu" est un synonyme de "difficile".'
                },
                {
                    'texte': 'Quels sont les antonymes de "joyeux" ?',
                    'type': 'choix_multiple',
                    'choix': [
                        {'texte': 'triste', 'correct': True},
                        {'texte': 'malheureux', 'correct': True},
                        {'texte': 'heureux', 'correct': False},
                        {'texte': 'content', 'correct': False}
                    ],
                    'explication': '"Triste" et "malheureux" sont des antonymes de "joyeux".'
                },
                {
                    'texte': 'Le mot "rapide" a-t-il le même sens que "véloce" ?',
                    'type': 'vrai_faux',
                    'choix': [
                        {'texte': 'Vrai', 'correct': True},
                        {'texte': 'Faux', 'correct': False}
                    ],
                    'explication': '"Rapide" et "véloce" sont synonymes.'
                },
                {
                    'texte': 'Donnez un synonyme de "intelligent".',
                    'type': 'texte_court',
                    'reponse_attendue': 'brillant, astucieux, malin, sage, érudit',
                    'explication': 'Plusieurs synonymes sont possibles : brillant, astucieux, malin, sage, érudit.'
                },
                {
                    'texte': 'Rédigez un court texte utilisant au moins 3 synonymes du mot "beau".',
                    'type': 'texte_long',
                    'reponse_attendue': 'Le paysage était magnifique. Les fleurs splendides ornaient le jardin. Cette vue superbe m\'a émerveillé.',
                    'explication': 'Le texte doit utiliser des synonymes comme magnifique, splendide, superbe, etc.'
                }
            ]
        else:
            return [
                {
                    'texte': f'Question générale pour {lecon_nom}',
                    'type': 'choix_unique',
                    'choix': [
                        {'texte': 'Réponse A', 'correct': True},
                        {'texte': 'Réponse B', 'correct': False}
                    ],
                    'explication': f'Explication pour {lecon_nom}.'
                }
            ]
    
    # Questions pour Culture générale
    elif matiere_nom == 'Culture générale':
        if 'Histoire' in lecon_nom:
            return [
                {
                    'texte': 'En quelle année a eu lieu la Révolution française ?',
                    'type': 'choix_unique',
                    'choix': [
                        {'texte': '1789', 'correct': True},
                        {'texte': '1792', 'correct': False},
                        {'texte': '1804', 'correct': False},
                        {'texte': '1815', 'correct': False}
                    ],
                    'explication': 'La Révolution française a commencé en 1789.'
                },
                {
                    'texte': 'Quels événements marquent la Révolution française ?',
                    'type': 'choix_multiple',
                    'choix': [
                        {'texte': 'Prise de la Bastille', 'correct': True},
                        {'texte': 'Déclaration des droits', 'correct': True},
                        {'texte': 'Bataille de Waterloo', 'correct': False},
                        {'texte': 'Sacre de Napoléon', 'correct': False}
                    ],
                    'explication': 'La prise de la Bastille et la Déclaration des droits sont des événements révolutionnaires.'
                }
            ]
        else:
            return [
                {
                    'texte': f'Question générale pour {lecon_nom}',
                    'type': 'choix_unique',
                    'choix': [
                        {'texte': 'Réponse A', 'correct': True},
                        {'texte': 'Réponse B', 'correct': False}
                    ],
                    'explication': f'Explication pour {lecon_nom}.'
                }
            ]
    
    # Questions pour Logique numérique
    elif matiere_nom == 'Logique numérique':
        if 'Suites' in lecon_nom:
            return [
                {
                    'texte': 'Quelle est la suite logique : 2, 4, 8, 16, ... ?',
                    'type': 'choix_unique',
                    'choix': [
                        {'texte': '24', 'correct': False},
                        {'texte': '32', 'correct': True},
                        {'texte': '20', 'correct': False},
                        {'texte': '18', 'correct': False}
                    ],
                    'explication': 'Chaque terme est multiplié par 2 : 16 × 2 = 32.'
                },
                {
                    'texte': 'Quelles suites sont arithmétiques ?',
                    'type': 'choix_multiple',
                    'choix': [
                        {'texte': '1, 3, 5, 7', 'correct': True},
                        {'texte': '2, 4, 6, 8', 'correct': True},
                        {'texte': '1, 2, 4, 8', 'correct': False},
                        {'texte': '1, 4, 9, 16', 'correct': False}
                    ],
                    'explication': 'Les suites arithmétiques ont une différence constante entre les termes.'
                }
            ]
        else:
            return [
                {
                    'texte': f'Question générale pour {lecon_nom}',
                    'type': 'choix_unique',
                    'choix': [
                        {'texte': 'Réponse A', 'correct': True},
                        {'texte': 'Réponse B', 'correct': False}
                    ],
                    'explication': f'Explication pour {lecon_nom}.'
                }
            ]
    
    # Questions génériques pour autres matières
    else:
        return [
            {
                'texte': f'Question de base pour {lecon_nom} - {matiere_nom}',
                'type': 'choix_unique',
                'choix': [
                    {'texte': 'Réponse correcte', 'correct': True},
                    {'texte': 'Réponse incorrecte 1', 'correct': False},
                    {'texte': 'Réponse incorrecte 2', 'correct': False},
                    {'texte': 'Réponse incorrecte 3', 'correct': False}
                ],
                'explication': f'Explication pour la question de {lecon_nom} en {matiere_nom}.'
            },
            {
                'texte': f'Question vrai/faux pour {lecon_nom}',
                'type': 'vrai_faux',
                'choix': [
                    {'texte': 'Vrai', 'correct': True},
                    {'texte': 'Faux', 'correct': False}
                ],
                'explication': f'Cette affirmation sur {lecon_nom} est vraie.'
            },
            {
                'texte': f'Question à réponse courte pour {lecon_nom}',
                'type': 'texte_court',
                'reponse_attendue': 'réponse courte',
                'explication': f'La réponse attendue pour cette question de {lecon_nom}.'
            }
        ]

def create_single_question(matiere, lecon, question_data):
    """Crée une question individuelle avec ses choix"""
    
    # Créer la question
    question, created = Question.objects.get_or_create(
        texte=question_data['texte'],
        matiere=matiere,
        lecon=lecon,
        defaults={
            'type_question': question_data['type'],
            'explication': question_data['explication'],
            'reponse_attendue': question_data.get('reponse_attendue', ''),
            'difficulte': 'moyen',
            'temps_limite': 60
        }
    )
    
    if created:
        print(f"      ✅ Question créée: {question_data['texte'][:50]}...")
        
        # Créer les choix si c'est une question à choix
        if 'choix' in question_data:
            for i, choix_data in enumerate(question_data['choix']):
                Choix.objects.create(
                    question=question,
                    texte=choix_data['texte'],
                    est_correct=choix_data['correct'],
                    ordre=i + 1
                )
    else:
        print(f"      ℹ️ Question existe déjà: {question_data['texte'][:50]}...")

# Exécuter le script
if __name__ == '__main__':
    create_ena_lessons_and_questions()
    print("\n🎉 Script terminé avec succès!")
else:
    # Si exécuté via manage.py shell
    create_ena_lessons_and_questions()
    print("\n🎉 Script terminé avec succès!")
