#!/usr/bin/env python3
"""
Script pour générer un fichier Excel template pour l'importation des questions ENA
conforme à la nouvelle structure (questions liées aux leçons, explications par choix)
"""

import pandas as pd
import os
from datetime import datetime

def create_questions_template():
    """Crée un template Excel pour l'importation des questions ENA"""
    
    # Structure des colonnes pour les questions ENA
    questions_data = [
        {
            'texte_question': 'Quel est le sport le plus populaire au monde ?',
            'matiere_nom': 'Culture Générale',
            'lecon_nom': 'Sport',
            'type_question': 'choix_unique',
            'explication_question': 'Cette question teste les connaissances générales sur le sport mondial.',
            'temps_limite_secondes': 60,
            'choix_a_texte': 'Football',
            'choix_a_correct': 'OUI',
            'choix_a_explication': 'Correct ! Le football est effectivement le sport le plus populaire au monde avec plus de 4 milliards de fans.',
            'choix_b_texte': 'Basketball',
            'choix_b_correct': 'NON',
            'choix_b_explication': 'Le basketball est très populaire mais arrive en deuxième position après le football.',
            'choix_c_texte': 'Tennis',
            'choix_c_correct': 'NON',
            'choix_c_explication': 'Le tennis est populaire mais ne rivalise pas avec le football en termes de nombre de fans.',
            'choix_d_texte': 'Cricket',
            'choix_d_correct': 'NON',
            'choix_d_explication': 'Le cricket est très populaire dans certains pays mais reste derrière le football globalement.'
        },
        {
            'texte_question': 'Quelle est la capitale de la France ?',
            'matiere_nom': 'Culture Générale',
            'lecon_nom': 'Histoire',
            'type_question': 'choix_unique',
            'explication_question': 'Question de base sur la géographie française.',
            'temps_limite_secondes': 45,
            'choix_a_texte': 'Lyon',
            'choix_a_correct': 'NON',
            'choix_a_explication': 'Lyon est une grande ville française mais pas la capitale.',
            'choix_b_texte': 'Marseille',
            'choix_b_correct': 'NON',
            'choix_b_explication': 'Marseille est la deuxième plus grande ville de France mais pas la capitale.',
            'choix_c_texte': 'Paris',
            'choix_c_correct': 'OUI',
            'choix_c_explication': 'Correct ! Paris est bien la capitale de la France depuis des siècles.',
            'choix_d_texte': 'Toulouse',
            'choix_d_correct': 'NON',
            'choix_d_explication': 'Toulouse est une ville importante du sud-ouest mais pas la capitale.'
        },
        {
            'texte_question': 'Combien font 2 + 2 ?',
            'matiere_nom': 'Mathématiques',
            'lecon_nom': 'Algèbre',
            'type_question': 'choix_unique',
            'explication_question': 'Question d\'arithmétique de base.',
            'temps_limite_secondes': 30,
            'choix_a_texte': '3',
            'choix_a_correct': 'NON',
            'choix_a_explication': 'Incorrect. 2 + 2 ne fait pas 3.',
            'choix_b_texte': '4',
            'choix_b_correct': 'OUI',
            'choix_b_explication': 'Correct ! 2 + 2 = 4 est la bonne réponse.',
            'choix_c_texte': '5',
            'choix_c_correct': 'NON',
            'choix_c_explication': 'Incorrect. 2 + 2 ne fait pas 5.',
            'choix_d_texte': '22',
            'choix_d_correct': 'NON',
            'choix_d_explication': 'Incorrect. Il s\'agit d\'une addition, pas d\'une concaténation.'
        },
        {
            'texte_question': 'La Terre est-elle ronde ?',
            'matiere_nom': 'Culture Générale',
            'lecon_nom': 'Science',
            'type_question': 'vrai_faux',
            'explication_question': 'Question sur la forme de la Terre.',
            'temps_limite_secondes': 30,
            'choix_a_texte': 'Vrai',
            'choix_a_correct': 'OUI',
            'choix_a_explication': 'Correct ! La Terre est effectivement de forme sphérique (légèrement aplatie aux pôles).',
            'choix_b_texte': 'Faux',
            'choix_b_correct': 'NON',
            'choix_b_explication': 'Incorrect. La Terre est bien ronde, c\'est un fait scientifique établi.',
            'choix_c_texte': '',
            'choix_c_correct': '',
            'choix_c_explication': '',
            'choix_d_texte': '',
            'choix_d_correct': '',
            'choix_d_explication': ''
        },
        {
            'texte_question': 'Quels sont les pays membres permanents du Conseil de sécurité de l\'ONU ? (Plusieurs réponses possibles)',
            'matiere_nom': 'Culture Générale',
            'lecon_nom': 'Société',
            'type_question': 'choix_multiple',
            'explication_question': 'Question sur les institutions internationales.',
            'temps_limite_secondes': 90,
            'choix_a_texte': 'États-Unis',
            'choix_a_correct': 'OUI',
            'choix_a_explication': 'Correct ! Les États-Unis sont un membre permanent du Conseil de sécurité.',
            'choix_b_texte': 'Chine',
            'choix_b_correct': 'OUI',
            'choix_b_explication': 'Correct ! La Chine est un membre permanent du Conseil de sécurité.',
            'choix_c_texte': 'Allemagne',
            'choix_c_correct': 'NON',
            'choix_c_explication': 'Incorrect. L\'Allemagne n\'est pas un membre permanent, seulement temporaire.',
            'choix_d_texte': 'France',
            'choix_d_correct': 'OUI',
            'choix_d_explication': 'Correct ! La France est un membre permanent du Conseil de sécurité.'
        }
    ]
    
    # Créer le DataFrame
    df_questions = pd.DataFrame(questions_data)
    
    return df_questions

def create_lecons_template():
    """Crée un template Excel pour l'importation des leçons ENA"""
    
    lecons_data = [
        {
            'nom': 'Sport',
            'matiere_nom': 'Culture Générale',
            'description': 'Leçons sur le sport mondial, les compétitions, les records',
            'ordre': 1,
            'active': 'OUI'
        },
        {
            'nom': 'Science',
            'matiere_nom': 'Culture Générale',
            'description': 'Connaissances scientifiques générales, découvertes, inventions',
            'ordre': 2,
            'active': 'OUI'
        },
        {
            'nom': 'Art',
            'matiere_nom': 'Culture Générale',
            'description': 'Histoire de l\'art, artistes célèbres, mouvements artistiques',
            'ordre': 3,
            'active': 'OUI'
        },
        {
            'nom': 'Histoire',
            'matiere_nom': 'Culture Générale',
            'description': 'Événements historiques, personnages, chronologie',
            'ordre': 4,
            'active': 'OUI'
        },
        {
            'nom': 'Société',
            'matiere_nom': 'Culture Générale',
            'description': 'Institutions, politique, société contemporaine',
            'ordre': 5,
            'active': 'OUI'
        },
        {
            'nom': 'Algèbre',
            'matiere_nom': 'Mathématiques',
            'description': 'Équations, fonctions, calcul algébrique',
            'ordre': 1,
            'active': 'OUI'
        },
        {
            'nom': 'Géométrie',
            'matiere_nom': 'Mathématiques',
            'description': 'Formes, surfaces, volumes, théorèmes géométriques',
            'ordre': 2,
            'active': 'OUI'
        }
    ]
    
    df_lecons = pd.DataFrame(lecons_data)
    return df_lecons

def create_contenus_pedagogiques_template():
    """Crée un template Excel pour l'importation des contenus pédagogiques ENA (Second Tour)"""
    
    contenus_data = [
        {
            'titre': 'Constitution de la Ve République',
            'matiere_nom': 'Droit Constitutionnel',
            'type_contenu': 'pdf',
            'description': 'Texte intégral de la Constitution française avec commentaires',
            'fichier_pdf': 'constitution_ve_republique.pdf',
            'url_video': '',
            'duree_minutes': '',
            'ordre': 1,
            'active': 'OUI'
        },
        {
            'titre': 'Les Institutions Françaises',
            'matiere_nom': 'Droit Constitutionnel',
            'type_contenu': 'video',
            'description': 'Présentation vidéo du fonctionnement des institutions',
            'fichier_pdf': '',
            'url_video': 'https://example.com/video/institutions-francaises',
            'duree_minutes': 45,
            'ordre': 2,
            'active': 'OUI'
        },
        {
            'titre': 'Le Conseil Constitutionnel',
            'matiere_nom': 'Droit Constitutionnel',
            'type_contenu': 'pdf',
            'description': 'Rôle et fonctionnement du Conseil Constitutionnel',
            'fichier_pdf': 'conseil_constitutionnel.pdf',
            'url_video': '',
            'duree_minutes': '',
            'ordre': 3,
            'active': 'OUI'
        }
    ]
    
    df_contenus = pd.DataFrame(contenus_data)
    return df_contenus

def create_sessions_zoom_template():
    """Crée un template Excel pour l'importation des sessions Zoom ENA (Oral)"""
    
    sessions_data = [
        {
            'titre': 'Préparation Entretien - Session 1',
            'matiere_nom': 'Entretien de Motivation',
            'description': 'Session de préparation aux techniques d\'entretien',
            'date_session': '2025-08-03 16:00:00',
            'duree_minutes': 90,
            'nombre_participants_max': 20,
            'url_zoom': 'https://zoom.us/j/123456789',
            'meeting_id': '123-456-789',
            'statut': 'programmee'
        },
        {
            'titre': 'Simulation Entretien - Session 2',
            'matiere_nom': 'Entretien de Motivation',
            'description': 'Simulation d\'entretien avec feedback personnalisé',
            'date_session': '2025-08-05 14:00:00',
            'duree_minutes': 120,
            'nombre_participants_max': 15,
            'url_zoom': 'https://zoom.us/j/987654321',
            'meeting_id': '987-654-321',
            'statut': 'programmee'
        },
        {
            'titre': 'Analyse de Cas - Session 1',
            'matiere_nom': 'Analyse de Cas Pratique',
            'description': 'Méthodologie d\'analyse de cas pratiques',
            'date_session': '2025-08-07 10:00:00',
            'duree_minutes': 180,
            'nombre_participants_max': 25,
            'url_zoom': 'https://zoom.us/j/456789123',
            'meeting_id': '456-789-123',
            'statut': 'programmee'
        }
    ]
    
    df_sessions = pd.DataFrame(sessions_data)
    return df_sessions

def main():
    """Fonction principale pour générer tous les templates Excel"""
    
    print("Generation des templates Excel pour l'importation ENA...")
    
    # Créer le répertoire de sortie
    output_dir = "templates_excel_ena"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Template Questions/Réponses/Explications
    print("Generation du template Questions/Reponses/Explications...")
    df_questions = create_questions_template()
    questions_file = os.path.join(output_dir, "template_questions_ena.xlsx")
    
    with pd.ExcelWriter(questions_file, engine='openpyxl') as writer:
        df_questions.to_excel(writer, sheet_name='Questions', index=False)
        
        # Ajouter une feuille d'instructions
        instructions = pd.DataFrame([
            ['INSTRUCTIONS POUR L\'IMPORTATION DES QUESTIONS ENA'],
            [''],
            ['Structure du fichier:'],
            ['- texte_question: Le texte de la question'],
            ['- matiere_nom: Nom de la matière (doit exister dans la base)'],
            ['- lecon_nom: Nom de la leçon (doit exister pour cette matière)'],
            ['- type_question: choix_unique, choix_multiple, vrai_faux, texte_court, texte_long'],
            ['- explication_question: Explication générale de la question (optionnel)'],
            ['- temps_limite_secondes: Temps limite en secondes (optionnel)'],
            ['- choix_a_texte à choix_d_texte: Texte des choix de réponse'],
            ['- choix_a_correct à choix_d_correct: OUI/NON pour indiquer si le choix est correct'],
            ['- choix_a_explication à choix_d_explication: Explication pour chaque choix'],
            [''],
            ['Notes importantes:'],
            ['- Pour les questions vrai_faux, utilisez seulement choix_a et choix_b'],
            ['- Pour les questions texte, les choix ne sont pas nécessaires'],
            ['- Chaque choix peut avoir sa propre explication'],
            ['- Les matières et leçons doivent exister avant l\'import'],
            ['- Utilisez OUI/NON (pas True/False) pour les champs booléens']
        ])
        instructions.to_excel(writer, sheet_name='Instructions', index=False, header=False)
    
    # 2. Template Leçons
    print("Generation du template Lecons...")
    df_lecons = create_lecons_template()
    lecons_file = os.path.join(output_dir, "template_lecons_ena.xlsx")
    df_lecons.to_excel(lecons_file, index=False)
    
    # 3. Template Contenus Pédagogiques
    print("Generation du template Contenus Pedagogiques...")
    df_contenus = create_contenus_pedagogiques_template()
    contenus_file = os.path.join(output_dir, "template_contenus_pedagogiques_ena.xlsx")
    df_contenus.to_excel(contenus_file, index=False)
    
    # 4. Template Sessions Zoom
    print("Generation du template Sessions Zoom...")
    df_sessions = create_sessions_zoom_template()
    sessions_file = os.path.join(output_dir, "template_sessions_zoom_ena.xlsx")
    df_sessions.to_excel(sessions_file, index=False)
    
    print(f"\nTemplates Excel generes avec succes dans le dossier '{output_dir}':")
    print(f"   Questions: {questions_file}")
    print(f"   Lecons: {lecons_file}")
    print(f"   Contenus: {contenus_file}")
    print(f"   Sessions: {sessions_file}")
    print(f"\nCes fichiers sont prets a etre utilises pour l'importation dans l'interface admin ENA!")

if __name__ == "__main__":
    main()
