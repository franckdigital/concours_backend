#!/usr/bin/env python3
"""
Script pour générer un fichier Excel template pour l'import des questions d'examen national ENA
"""

import pandas as pd
from datetime import datetime

def creer_template_excel():
    """Crée un fichier Excel template avec des exemples de questions ENA"""
    
    # Données d'exemple pour chaque type de question
    template_data = [
        # Question choix unique - Culture générale
        {
            'code_question': 'ENA2024-CA-001',
            'texte': 'Qui était le premier président de la République française ?',
            'type_question': 'choix_unique',
            'matiere_combinee': 'culture_aptitude',
            'choix_a': 'Louis-Napoléon Bonaparte',
            'choix_b': 'Adolphe Thiers',
            'choix_c': 'Jules Grévy',
            'choix_d': 'Patrice de Mac-Mahon',
            'choix_e': '',
            'bonne_reponse': 'A',
            'reponse_attendue': '',
            'correction_mode': 'exacte',
            'explication': 'Louis-Napoléon Bonaparte fut élu premier président de la République française en 1848.',
            'difficulte': 'moyen',
            'temps_limite_secondes': 120,
            'active': True,
            'validee': False,
            'creee_par': 'Template'
        },
        # Question vrai/faux - Culture générale
        {
            'code_question': 'ENA2024-CA-002',
            'texte': 'La France est-elle membre fondateur de l\'Union européenne ?',
            'type_question': 'vrai_faux',
            'matiere_combinee': 'culture_aptitude',
            'choix_a': '',
            'choix_b': '',
            'choix_c': '',
            'choix_d': '',
            'choix_e': '',
            'bonne_reponse': 'VRAI',
            'reponse_attendue': '',
            'correction_mode': 'exacte',
            'explication': 'La France est l\'un des six pays fondateurs de la CEE en 1957.',
            'difficulte': 'facile',
            'temps_limite_secondes': 60,
            'active': True,
            'validee': False,
            'creee_par': 'Template'
        },
        # Question choix multiple - Aptitude verbale
        {
            'code_question': 'ENA2024-CA-003',
            'texte': 'Quels sont les synonymes du mot "perspicace" ? (Plusieurs réponses possibles)',
            'type_question': 'choix_multiple',
            'matiere_combinee': 'culture_aptitude',
            'choix_a': 'Clairvoyant',
            'choix_b': 'Naïf',
            'choix_c': 'Sagace',
            'choix_d': 'Obtus',
            'choix_e': 'Pénétrant',
            'bonne_reponse': 'ACE',
            'reponse_attendue': '',
            'correction_mode': 'exacte',
            'explication': 'Perspicace signifie clairvoyant, sagace et pénétrant.',
            'difficulte': 'difficile',
            'temps_limite_secondes': 150,
            'active': True,
            'validee': False,
            'creee_par': 'Template'
        },
        # Question logique - Raisonnement
        {
            'code_question': 'ENA2024-LC-001',
            'texte': 'Si A > B et B > C, alors :',
            'type_question': 'choix_unique',
            'matiere_combinee': 'logique_combinee',
            'choix_a': 'A > C',
            'choix_b': 'A = C',
            'choix_c': 'C > A',
            'choix_d': 'A < C',
            'choix_e': 'Impossible à déterminer',
            'bonne_reponse': 'A',
            'reponse_attendue': '',
            'correction_mode': 'exacte',
            'explication': 'Par transitivité de la relation d\'ordre, si A > B et B > C, alors A > C.',
            'difficulte': 'facile',
            'temps_limite_secondes': 90,
            'active': True,
            'validee': False,
            'creee_par': 'Template'
        },
        # Question logique - Suite numérique
        {
            'code_question': 'ENA2024-LC-002',
            'texte': 'Quelle est la suite logique : 2, 6, 18, 54, ?',
            'type_question': 'choix_unique',
            'matiere_combinee': 'logique_combinee',
            'choix_a': '108',
            'choix_b': '162',
            'choix_c': '216',
            'choix_d': '270',
            'choix_e': '324',
            'bonne_reponse': 'B',
            'reponse_attendue': '',
            'correction_mode': 'exacte',
            'explication': 'Chaque terme est multiplié par 3 : 2×3=6, 6×3=18, 18×3=54, 54×3=162.',
            'difficulte': 'moyen',
            'temps_limite_secondes': 120,
            'active': True,
            'validee': False,
            'creee_par': 'Template'
        },
        # Question anglais - Traduction courte
        {
            'code_question': 'ENA2024-AN-001',
            'texte': 'Translate to English: "Je suis étudiant"',
            'type_question': 'texte_court',
            'matiere_combinee': 'anglais',
            'choix_a': '',
            'choix_b': '',
            'choix_c': '',
            'choix_d': '',
            'choix_e': '',
            'bonne_reponse': '',
            'reponse_attendue': 'I am a student',
            'correction_mode': 'mot_cle',
            'explication': 'La traduction correcte est "I am a student".',
            'difficulte': 'facile',
            'temps_limite_secondes': 60,
            'active': True,
            'validee': False,
            'creee_par': 'Template'
        },
        # Question anglais - Grammaire
        {
            'code_question': 'ENA2024-AN-002',
            'texte': 'Choose the correct form: "She _____ to the store yesterday."',
            'type_question': 'choix_unique',
            'matiere_combinee': 'anglais',
            'choix_a': 'go',
            'choix_b': 'goes',
            'choix_c': 'went',
            'choix_d': 'going',
            'choix_e': 'gone',
            'bonne_reponse': 'C',
            'reponse_attendue': '',
            'correction_mode': 'exacte',
            'explication': 'Le passé simple "went" est correct avec l\'indicateur temporel "yesterday".',
            'difficulte': 'facile',
            'temps_limite_secondes': 90,
            'active': True,
            'validee': False,
            'creee_par': 'Template'
        },
        # Question anglais - Expression écrite
        {
            'code_question': 'ENA2024-AN-003',
            'texte': 'Write a short paragraph (50 words) about the importance of education.',
            'type_question': 'texte_long',
            'matiere_combinee': 'anglais',
            'choix_a': '',
            'choix_b': '',
            'choix_c': '',
            'choix_d': '',
            'choix_e': '',
            'bonne_reponse': '',
            'reponse_attendue': 'education,important,knowledge,future,society,learning,development,skills',
            'correction_mode': 'mot_cle',
            'explication': 'La réponse doit contenir des mots-clés liés à l\'importance de l\'éducation.',
            'difficulte': 'difficile',
            'temps_limite_secondes': 300,
            'active': True,
            'validee': False,
            'creee_par': 'Template'
        },
        # Question culture générale - Histoire
        {
            'code_question': 'ENA2024-CA-004',
            'texte': 'En quelle année a eu lieu la Révolution française ?',
            'type_question': 'choix_unique',
            'matiere_combinee': 'culture_aptitude',
            'choix_a': '1789',
            'choix_b': '1792',
            'choix_c': '1799',
            'choix_d': '1804',
            'choix_e': '1815',
            'bonne_reponse': 'A',
            'reponse_attendue': '',
            'correction_mode': 'exacte',
            'explication': 'La Révolution française a commencé en 1789.',
            'difficulte': 'facile',
            'temps_limite_secondes': 60,
            'active': True,
            'validee': True,
            'creee_par': 'Template'
        },
        # Question logique - Analogie
        {
            'code_question': 'ENA2024-LC-003',
            'texte': 'Chien est à aboyer comme chat est à :',
            'type_question': 'choix_unique',
            'matiere_combinee': 'logique_combinee',
            'choix_a': 'ronronner',
            'choix_b': 'miauler',
            'choix_c': 'griffer',
            'choix_d': 'dormir',
            'choix_e': 'chasser',
            'bonne_reponse': 'B',
            'reponse_attendue': '',
            'correction_mode': 'exacte',
            'explication': 'Le chien aboie, le chat miaule. C\'est le cri caractéristique de chaque animal.',
            'difficulte': 'facile',
            'temps_limite_secondes': 90,
            'active': True,
            'validee': True,
            'creee_par': 'Template'
        }
    ]
    
    # Création du DataFrame
    df_template = pd.DataFrame(template_data)
    
    # Nom du fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fichier_template = f'template_questions_examen_ena_{timestamp}.xlsx'
    
    # Sauvegarde du fichier Excel
    df_template.to_excel(fichier_template, index=False, sheet_name='Questions_ENA')
    
    print(f"Template Excel cree: {fichier_template}")
    print(f"{len(template_data)} questions d'exemple incluses")
    print("\nColonnes disponibles:")
    for i, col in enumerate(df_template.columns, 1):
        print(f"  {i:2d}. {col}")
    
    print("\nRepartition par matiere:")
    repartition = df_template['matiere_combinee'].value_counts()
    for matiere, count in repartition.items():
        matiere_nom = {
            'culture_aptitude': 'Culture generale + Aptitude verbale',
            'logique_combinee': 'Logique + Raisonnement',
            'anglais': 'Anglais'
        }.get(matiere, matiere)
        print(f"  - {matiere_nom}: {count} questions")
    
    print("\nTypes de questions:")
    types = df_template['type_question'].value_counts()
    for type_q, count in types.items():
        type_nom = {
            'choix_unique': 'Choix unique (QCM)',
            'choix_multiple': 'Choix multiple',
            'vrai_faux': 'Vrai/Faux',
            'texte_court': 'Texte court',
            'texte_long': 'Texte long'
        }.get(type_q, type_q)
        print(f"  - {type_nom}: {count} questions")
    
    print("\nInstructions d'utilisation:")
    print("1. Ouvrez le fichier Excel genere")
    print("2. Modifiez ou ajoutez vos questions en respectant le format")
    print("3. Sauvegardez le fichier")
    print("4. Importez avec: python import_questions_examen_excel.py --fichier votre_fichier.xlsx")
    
    print("\nRegles importantes:")
    print("- code_question: Unique, format ENA2024-XX-NNN")
    print("- type_question: choix_unique, choix_multiple, vrai_faux, texte_court, texte_long")
    print("- matiere_combinee: culture_aptitude, logique_combinee, anglais")
    print("- difficulte: facile, moyen, difficile")
    print("- Pour QCM: choix_a et choix_b obligatoires, bonne_reponse = A, B, C, D, E")
    print("- Pour Vrai/Faux: bonne_reponse = VRAI ou FAUX")
    print("- Pour texte: reponse_attendue obligatoire, correction_mode = exacte, mot_cle, regex")
    
    return fichier_template

if __name__ == '__main__':
    fichier_cree = creer_template_excel()
    print(f"\nFichier template cree avec succes: {fichier_cree}")
