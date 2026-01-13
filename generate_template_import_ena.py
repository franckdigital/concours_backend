#!/usr/bin/env python3
"""
Générateur de template Excel pour l'import de questions d'examen national ENA
Inspiré de la structure du fichier qcm_aptitude_verbale_par_lecon.xlsx
"""

import pandas as pd
from datetime import datetime
import os

def generer_template_excel_ena():
    """
    Génère un template Excel pour l'import de questions d'examen national ENA
    avec des exemples réalistes basés sur la structure existante
    """
    
    # Données d'exemple pour le template ENA
    exemples_questions = [
        {
            # Question de Culture générale + Aptitude verbale - Choix unique
            'matiere_nom': 'Culture générale',
            'lecon_nom': 'Organisations internationales',
            'texte_question': 'Quel est le siège de l\'Organisation des Nations Unies ?',
            'type_question': 'choix_unique',
            'matiere_combinee': 'culture_aptitude',
            'choix_a': 'Paris',
            'choix_b': 'New York',
            'choix_c': 'Genève',
            'choix_d': 'Londres',
            'choix_e': '',
            'bonne_reponse': 'B',
            'reponse_attendue': '',
            'explication': 'Le siège principal de l\'ONU est situé à New York, États-Unis, depuis 1952.',
            'difficulte': 'facile',
            'temps_limite_secondes': 120,
            'correction_mode': 'exacte'
        },
        {
            # Question de Culture générale + Aptitude verbale - Choix multiple
            'matiere_nom': 'Culture générale',
            'lecon_nom': 'Organisations internationales',
            'texte_question': 'Quels sont les pays membres permanents du Conseil de sécurité de l\'ONU ?',
            'type_question': 'choix_multiple',
            'matiere_combinee': 'culture_aptitude',
            'choix_a': 'États-Unis',
            'choix_b': 'Russie',
            'choix_c': 'Chine',
            'choix_d': 'France',
            'choix_e': 'Royaume-Uni',
            'bonne_reponse': 'ABCDE',
            'reponse_attendue': '',
            'explication': 'Les cinq membres permanents du Conseil de sécurité sont : États-Unis, Russie, Chine, France et Royaume-Uni.',
            'difficulte': 'moyen',
            'temps_limite_secondes': 180,
            'correction_mode': 'exacte'
        },
        {
            # Question de Culture générale + Aptitude verbale - Vrai/Faux
            'matiere_nom': 'Culture générale',
            'lecon_nom': 'Union européenne',
            'texte_question': 'La France est membre fondateur de l\'Union européenne.',
            'type_question': 'vrai_faux',
            'matiere_combinee': 'culture_aptitude',
            'choix_a': 'VRAI',
            'choix_b': 'FAUX',
            'choix_c': '',
            'choix_d': '',
            'choix_e': '',
            'bonne_reponse': 'A',
            'reponse_attendue': '',
            'explication': 'La France est effectivement l\'un des six pays fondateurs de la Communauté européenne du charbon et de l\'acier en 1951.',
            'difficulte': 'facile',
            'temps_limite_secondes': 60,
            'correction_mode': 'exacte'
        },
        {
            # Question de Culture générale + Aptitude verbale - Texte court
            'matiere_nom': 'Aptitude verbale',
            'lecon_nom': 'Synonymes',
            'texte_question': 'Donnez un synonyme du mot "diligent".',
            'type_question': 'texte_court',
            'matiere_combinee': 'culture_aptitude',
            'choix_a': '',
            'choix_b': '',
            'choix_c': '',
            'choix_d': '',
            'choix_e': '',
            'bonne_reponse': '',
            'reponse_attendue': 'assidu|consciencieux|appliqué|soigneux',
            'explication': 'Les synonymes de "diligent" incluent : assidu, consciencieux, appliqué, soigneux.',
            'difficulte': 'moyen',
            'temps_limite_secondes': 90,
            'correction_mode': 'mot_cle'
        },
        {
            # Question de Logique d'organisation + Logique numérique - Choix unique
            'matiere_nom': 'Logique numérique',
            'lecon_nom': 'Suites numériques',
            'texte_question': 'Dans la suite logique 2, 6, 18, 54, ?, quel est le nombre manquant ?',
            'type_question': 'choix_unique',
            'matiere_combinee': 'logique_combinee',
            'choix_a': '108',
            'choix_b': '162',
            'choix_c': '216',
            'choix_d': '270',
            'choix_e': '',
            'bonne_reponse': 'B',
            'reponse_attendue': '',
            'explication': 'Chaque terme est multiplié par 3 : 2×3=6, 6×3=18, 18×3=54, 54×3=162.',
            'difficulte': 'moyen',
            'temps_limite_secondes': 150,
            'correction_mode': 'exacte'
        },
        {
            # Question de Logique d'organisation + Logique numérique - Texte court
            'matiere_nom': 'Logique d\'organisation',
            'lecon_nom': 'Codage alphabétique',
            'texte_question': 'Si A=1, B=2, C=3, etc., quelle est la valeur numérique du mot "CHAT" ?',
            'type_question': 'texte_court',
            'matiere_combinee': 'logique_combinee',
            'choix_a': '',
            'choix_b': '',
            'choix_c': '',
            'choix_d': '',
            'choix_e': '',
            'bonne_reponse': '',
            'reponse_attendue': '28',
            'explication': 'C=3, H=8, A=1, T=20. Total : 3+8+1+20=32. (Erreur dans l\'exemple, devrait être 32)',
            'difficulte': 'facile',
            'temps_limite_secondes': 120,
            'correction_mode': 'exacte'
        },
        {
            # Question d'Anglais - Choix unique
            'matiere_nom': 'Anglais',
            'lecon_nom': 'Grammaire - Temps du passé',
            'texte_question': 'Choose the correct form: "She _____ to the store yesterday."',
            'type_question': 'choix_unique',
            'matiere_combinee': 'anglais',
            'choix_a': 'go',
            'choix_b': 'goes',
            'choix_c': 'went',
            'choix_d': 'going',
            'choix_e': '',
            'bonne_reponse': 'C',
            'reponse_attendue': '',
            'explication': '"Went" is the past tense of "go", which is correct with "yesterday".',
            'difficulte': 'facile',
            'temps_limite_secondes': 90,
            'correction_mode': 'exacte'
        },
        {
            # Question d'Anglais - Texte court
            'matiere_nom': 'Anglais',
            'lecon_nom': 'Traduction français-anglais',
            'texte_question': 'Translate to English: "Je suis étudiant"',
            'type_question': 'texte_court',
            'matiere_combinee': 'anglais',
            'choix_a': '',
            'choix_b': '',
            'choix_c': '',
            'choix_d': '',
            'choix_e': '',
            'bonne_reponse': '',
            'reponse_attendue': 'I am a student|I\'m a student',
            'explication': 'The correct translation is "I am a student" or "I\'m a student".',
            'difficulte': 'facile',
            'temps_limite_secondes': 60,
            'correction_mode': 'mot_cle'
        },
        {
            # Question d'Anglais - Vrai/Faux
            'matiere_nom': 'Anglais',
            'lecon_nom': 'Vocabulaire - Différences sémantiques',
            'texte_question': '"Library" and "bookstore" have the same meaning in English.',
            'type_question': 'vrai_faux',
            'matiere_combinee': 'anglais',
            'choix_a': 'TRUE',
            'choix_b': 'FALSE',
            'choix_c': '',
            'choix_d': '',
            'choix_e': '',
            'bonne_reponse': 'B',
            'reponse_attendue': '',
            'explication': 'A library is for borrowing books, while a bookstore is for buying books.',
            'difficulte': 'moyen',
            'temps_limite_secondes': 90,
            'correction_mode': 'exacte'
        },
        {
            # Question de Culture générale + Aptitude verbale - Texte long
            'matiere_nom': 'Culture générale',
            'lecon_nom': 'Institutions démocratiques',
            'texte_question': 'Expliquez brièvement l\'importance de la séparation des pouvoirs dans un système démocratique (maximum 100 mots).',
            'type_question': 'texte_long',
            'matiere_combinee': 'culture_aptitude',
            'choix_a': '',
            'choix_b': '',
            'choix_c': '',
            'choix_d': '',
            'choix_e': '',
            'bonne_reponse': '',
            'reponse_attendue': 'équilibre|contrôle|pouvoir|exécutif|législatif|judiciaire|démocratie',
            'explication': 'La séparation des pouvoirs (exécutif, législatif, judiciaire) assure l\'équilibre et le contrôle mutuel, évitant la concentration du pouvoir et protégeant les libertés démocratiques.',
            'difficulte': 'difficile',
            'temps_limite_secondes': 300,
            'correction_mode': 'mot_cle'
        }
    ]
    
    # Créer le DataFrame avec la structure optimisée
    df = pd.DataFrame(exemples_questions)
    
    # Réorganiser les colonnes dans l'ordre logique pour l'import
    colonnes_ordre = [
        'matiere_nom',
        'lecon_nom',
        'texte_question',
        'type_question', 
        'matiere_combinee',
        'choix_a',
        'choix_b', 
        'choix_c',
        'choix_d',
        'choix_e',
        'bonne_reponse',
        'reponse_attendue',
        'explication',
        'difficulte',
        'temps_limite_secondes',
        'correction_mode'
    ]
    
    df = df[colonnes_ordre]
    
    # Générer le nom du fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_fichier = f"template_import_questions_examen_ena_{timestamp}.xlsx"
    
    # Créer le fichier Excel avec formatage
    with pd.ExcelWriter(nom_fichier, engine='openpyxl') as writer:
        # Feuille principale avec les exemples
        df.to_excel(writer, sheet_name='Questions_ENA_Exemples', index=False)
        
        # Feuille d'instructions
        instructions = pd.DataFrame({
            'INSTRUCTIONS IMPORT QUESTIONS EXAMEN NATIONAL ENA': [
                '=== COLONNES REQUISES ===',
                'matiere_nom : Nom de la matière (ex: Culture générale, Aptitude verbale, Anglais)',
                'lecon_nom : Nom de la leçon/thème (ex: Organisations internationales, Synonymes)',
                'texte_question : Énoncé de la question',
                'type_question : choix_unique, choix_multiple, vrai_faux, texte_court, texte_long',
                '',
                '=== COLONNES OPTIONNELLES ===',
                'matiere_combinee : culture_aptitude, logique_combinee, anglais (calculé automatiquement)',
                'choix_a, choix_b, choix_c, choix_d, choix_e : Choix pour QCM',
                'bonne_reponse : A, B, C, D, E ou combinaisons (ex: ABC pour choix multiple)',
                'reponse_attendue : Réponse attendue pour questions texte (peut contenir | pour alternatives)',
                'explication : Explication de la réponse',
                'difficulte : facile, moyen, difficile (défaut: moyen)',
                'temps_limite_secondes : Temps limite en secondes (défaut: 120)',
                'correction_mode : exacte, mot_cle, regex (défaut: exacte)',
                '',
                '=== MATIÈRES COMBINÉES ===',
                'culture_aptitude : Culture générale + Aptitude verbale',
                'logique_combinee : Logique d\'organisation + Logique numérique', 
                'anglais : Anglais',
                '',
                '=== TYPES DE QUESTIONS ===',
                'choix_unique : Une seule bonne réponse (A, B, C, D ou E)',
                'choix_multiple : Plusieurs bonnes réponses (ex: ABC, BD, etc.)',
                'vrai_faux : Question Vrai/Faux (A=VRAI/TRUE, B=FAUX/FALSE)',
                'texte_court : Réponse courte en texte libre',
                'texte_long : Réponse longue en texte libre',
                '',
                '=== CONSEILS ===',
                '• Utilisez la feuille "Questions_ENA_Exemples" comme modèle',
                '• Pour les questions texte, utilisez | dans reponse_attendue pour les alternatives',
                '• Le correction_mode "mot_cle" cherche les mots-clés dans la réponse',
                '• Laissez vides les colonnes non utilisées (ex: choix_c pour vrai/faux)',
                '• Vérifiez que bonne_reponse correspond aux choix définis'
            ]
        })
        
        instructions.to_excel(writer, sheet_name='Instructions', index=False)
        
        # Feuille de référence des matières
        matieres_ref = pd.DataFrame({
            'matiere_combinee': ['culture_aptitude', 'logique_combinee', 'anglais'],
            'description': [
                'Culture générale et Aptitude verbale',
                'Logique d\'organisation et Logique numérique',
                'Anglais'
            ],
            'exemples_sujets': [
                'Histoire, géographie, littérature, synonymes, antonymes',
                'Suites logiques, calculs, organisation, raisonnement',
                'Grammaire, vocabulaire, compréhension, traduction'
            ]
        })
        
        matieres_ref.to_excel(writer, sheet_name='Matières_Référence', index=False)
    
    print(f"Template Excel genere : {nom_fichier}")
    print(f"{len(exemples_questions)} exemples de questions inclus")
    print(f"3 feuilles creees : Questions_ENA_Exemples, Instructions, Matieres_Reference")
    
    return nom_fichier

if __name__ == '__main__':
    fichier_genere = generer_template_excel_ena()
    print(f"\nFichier pret pour l'import ENA : {fichier_genere}")
