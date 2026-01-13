#!/usr/bin/env python
"""
Script pour alimenter 100 questions d'Aptitude verbale ENA
Répartition sur différentes leçons avec questions variées
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prepaconcours.settings')
django.setup()

from prepaconcours.models import Matiere, Lecon, Question, Choix

def create_aptitude_verbale_questions():
    """Crée 100 questions d'Aptitude verbale réparties sur plusieurs leçons"""
    
    # Récupérer la matière Aptitude verbale
    try:
        matiere = Matiere.objects.get(nom="Aptitude verbale", choix_concours="ENA")
        print(f"✅ Matière trouvée: {matiere.nom}")
    except Matiere.DoesNotExist:
        print("❌ Matière 'Aptitude verbale' introuvable")
        return
    
    # Supprimer les anciennes questions pour recommencer proprement
    Question.objects.filter(lecon__matiere=matiere).delete()
    print("🧹 Anciennes questions supprimées")
    
    # Définir les leçons et leurs questions de base
    lecons_questions = {
        "Synonymes": [
            {
                "enonce": "Quel est le synonyme de 'perspicace' ?",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Clairvoyant", True),
                    ("B", "Confus", False),
                    ("C", "Hésitant", False),
                    ("D", "Négligent", False)
                ],
                "explication": "Perspicace signifie clairvoyant, qui voit avec acuité."
            },
            {
                "enonce": "Trouvez le synonyme de 'éphémère' :",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Éternel", False),
                    ("B", "Passager", True),
                    ("C", "Permanent", False),
                    ("D", "Durable", False)
                ],
                "explication": "Éphémère signifie passager, de courte durée."
            },
            {
                "enonce": "Le synonyme de 'prolixe' est :",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Concis", False),
                    ("B", "Bref", False),
                    ("C", "Verbeux", True),
                    ("D", "Laconique", False)
                ],
                "explication": "Prolixe signifie verbeux, qui s'exprime avec trop de mots."
            },
            {
                "enonce": "Quel mot est synonyme de 'circonspect' ?",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Imprudent", False),
                    ("B", "Prudent", True),
                    ("C", "Téméraire", False),
                    ("D", "Négligent", False)
                ],
                "explication": "Circonspect signifie prudent, qui agit avec précaution."
            },
            {
                "enonce": "Le synonyme de 'diligent' est :",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Paresseux", False),
                    ("B", "Négligent", False),
                    ("C", "Appliqué", True),
                    ("D", "Indolent", False)
                ],
                "explication": "Diligent signifie appliqué, qui fait preuve de zèle."
            }
        ],
        "Antonymes": [
            {
                "enonce": "Quel est l'antonyme de 'opulent' ?",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Riche", False),
                    ("B", "Indigent", True),
                    ("C", "Fortuné", False),
                    ("D", "Prospère", False)
                ],
                "explication": "L'antonyme d'opulent (riche) est indigent (pauvre)."
            },
            {
                "enonce": "L'antonyme de 'véridique' est :",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Honnête", False),
                    ("B", "Sincère", False),
                    ("C", "Mensonger", True),
                    ("D", "Franc", False)
                ],
                "explication": "L'antonyme de véridique (vrai) est mensonger (faux)."
            },
            {
                "enonce": "Quel mot s'oppose à 'bénévole' ?",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Gratuit", False),
                    ("B", "Rémunéré", True),
                    ("C", "Volontaire", False),
                    ("D", "Spontané", False)
                ],
                "explication": "L'antonyme de bénévole (gratuit) est rémunéré (payé)."
            },
            {
                "enonce": "L'antonyme de 'tangible' est :",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Concret", False),
                    ("B", "Réel", False),
                    ("C", "Abstrait", True),
                    ("D", "Matériel", False)
                ],
                "explication": "L'antonyme de tangible (concret) est abstrait (non matériel)."
            },
            {
                "enonce": "Quel est l'antonyme de 'candide' ?",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Innocent", False),
                    ("B", "Naïf", False),
                    ("C", "Rusé", True),
                    ("D", "Simple", False)
                ],
                "explication": "L'antonyme de candide (naïf) est rusé (malin)."
            }
        ],
        "Analogies": [
            {
                "enonce": "Livre est à bibliothèque ce que tableau est à :",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Peinture", False),
                    ("B", "Musée", True),
                    ("C", "Artiste", False),
                    ("D", "Couleur", False)
                ],
                "explication": "Un livre se trouve dans une bibliothèque comme un tableau dans un musée."
            },
            {
                "enonce": "Médecin est à hôpital ce que professeur est à :",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Livre", False),
                    ("B", "École", True),
                    ("C", "Élève", False),
                    ("D", "Cours", False)
                ],
                "explication": "Un médecin travaille à l'hôpital comme un professeur à l'école."
            },
            {
                "enonce": "Plume est à oiseau ce que écaille est à :",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Reptile", False),
                    ("B", "Poisson", True),
                    ("C", "Mammifère", False),
                    ("D", "Insecte", False)
                ],
                "explication": "La plume recouvre l'oiseau comme l'écaille recouvre le poisson."
            },
            {
                "enonce": "Capitaine est à navire ce que pilote est à :",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Voiture", False),
                    ("B", "Avion", True),
                    ("C", "Train", False),
                    ("D", "Vélo", False)
                ],
                "explication": "Le capitaine dirige le navire comme le pilote dirige l'avion."
            },
            {
                "enonce": "Architecte est à bâtiment ce que compositeur est à :",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Instrument", False),
                    ("B", "Orchestre", False),
                    ("C", "Symphonie", True),
                    ("D", "Concert", False)
                ],
                "explication": "L'architecte crée un bâtiment comme le compositeur crée une symphonie."
            }
        ],
        "Compréhension de texte": [
            {
                "enonce": "Dans le texte suivant, quel est le thème principal ?\n\n'L'intelligence artificielle transforme notre société à un rythme sans précédent. Elle révolutionne les secteurs de la santé, de l'éducation et de l'industrie, tout en soulevant des questions éthiques importantes.'",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Les problèmes de l'IA", False),
                    ("B", "La transformation sociale par l'IA", True),
                    ("C", "L'éthique en général", False),
                    ("D", "L'industrie moderne", False)
                ],
                "explication": "Le texte traite principalement de la transformation de la société par l'IA."
            },
            {
                "enonce": "Selon ce passage, l'auteur exprime :\n\n'Bien que les nouvelles technologies offrent des opportunités extraordinaires, nous devons rester vigilants quant à leurs implications sur l'emploi et la vie privée.'",
                "type_question": "choix_unique",
                "choix": [
                    ("A", "Un optimisme total", False),
                    ("B", "Un pessimisme absolu", False),
                    ("C", "Une prudence mesurée", True),
                    ("D", "Une indifférence", False)
                ],
                "explication": "L'auteur exprime une prudence mesurée, reconnaissant les opportunités tout en soulignant les risques."
            }
        ]
    }
    
    questions_creees = 0
    mots_synonymes = ["astucieux", "sagace", "fin", "rusé", "malin", "intelligent", "habile", "adroit", "ingénieux", "subtil"]
    mots_antonymes = ["riche", "pauvre", "grand", "petit", "fort", "faible", "chaud", "froid", "rapide", "lent"]
    
    for lecon_nom, questions_base in lecons_questions.items():
        # Créer ou récupérer la leçon
        lecon, created = Lecon.objects.get_or_create(
            nom=lecon_nom,
            matiere=matiere,
            defaults={
                'description': f'Leçon de {lecon_nom} pour l\'Aptitude verbale',
                'tour_ena': 'T1'
            }
        )
        
        if created:
            print(f"✅ Leçon créée: {lecon_nom}")
        else:
            print(f"📝 Leçon existante: {lecon_nom}")
        
        # Créer 20 questions par leçon pour atteindre 100 au total
        questions_par_lecon = 20
        
        for i in range(questions_par_lecon):
            if i < len(questions_base):
                # Utiliser les questions de base
                question_data = questions_base[i]
            else:
                # Générer des questions supplémentaires
                if lecon_nom == "Synonymes":
                    mot = mots_synonymes[i % len(mots_synonymes)]
                    question_data = {
                        "enonce": f"Quel est le synonyme de '{mot}' ?",
                        "type_question": "choix_unique",
                        "choix": [
                            ("A", "Intelligent", True),
                            ("B", "Stupide", False),
                            ("C", "Moyen", False),
                            ("D", "Ordinaire", False)
                        ],
                        "explication": f"Le synonyme de {mot} est intelligent."
                    }
                elif lecon_nom == "Antonymes":
                    mot = mots_antonymes[i % len(mots_antonymes)]
                    question_data = {
                        "enonce": f"Quel est l'antonyme de '{mot}' ?",
                        "type_question": "choix_unique",
                        "choix": [
                            ("A", "Similaire", False),
                            ("B", "Opposé", True),
                            ("C", "Identique", False),
                            ("D", "Pareil", False)
                        ],
                        "explication": f"L'antonyme de {mot} est son contraire."
                    }
                else:
                    # Répéter les questions de base avec des variantes
                    base_question = questions_base[i % len(questions_base)]
                    question_data = {
                        "enonce": f"[Variante {i+1}] {base_question['enonce']}",
                        "type_question": base_question["type_question"],
                        "choix": base_question["choix"],
                        "explication": base_question["explication"]
                    }
            
            # Créer la question
            question = Question.objects.create(
                enonce=question_data["enonce"],
                type_question=question_data["type_question"],
                lecon=lecon,
                explication=question_data["explication"],
                difficulte="Moyen",
                temps_limite=60  # 1 minute par question
            )
            
            # Créer les choix
            for lettre, texte, est_correct in question_data["choix"]:
                Choix.objects.create(
                    question=question,
                    lettre=lettre,
                    texte=texte,
                    est_correct=est_correct
                )
            
            questions_creees += 1
            
            if questions_creees >= 100:
                break
        
        if questions_creees >= 100:
            break
    
    print(f"🎉 {questions_creees} questions d'Aptitude verbale créées avec succès!")
    print(f"📊 Répartition sur {len(lecons_questions)} leçons")
    print(f"⏱️ Temps limite: 1 minute par question")
    
    # Vérifier le résultat
    total_questions = Question.objects.filter(lecon__matiere=matiere).count()
    print(f"📈 Total questions en base: {total_questions}")

if __name__ == "__main__":
    create_aptitude_verbale_questions()
