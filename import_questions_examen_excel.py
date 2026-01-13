#!/usr/bin/env python3
"""
Script d'import Excel pour les questions d'examen national ENA
Supporte tous les types de questions : vrai/faux, choix unique, choix multiple, texte court, texte long
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime
import logging

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import QuestionExamen

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_questions_examen.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImportQuestionExamenExcel:
    """Classe pour importer les questions d'examen depuis un fichier Excel"""
    
    def __init__(self, fichier_excel):
        self.fichier_excel = fichier_excel
        self.questions_importees = 0
        self.questions_echouees = 0
        self.erreurs = []
    
    def valider_colonnes_requises(self, df):
        """Valide que toutes les colonnes requises sont présentes"""
        colonnes_requises = [
            'matiere_combinee', 'lecon_nom', 'texte_question', 'type_question'
        ]
        
        colonnes_manquantes = [col for col in colonnes_requises if col not in df.columns]
        
        if colonnes_manquantes:
            raise ValueError(f"Colonnes manquantes dans le fichier Excel: {colonnes_manquantes}")
        
        logger.info("Toutes les colonnes requises sont presentes")
    
    def valider_donnees_ligne(self, row, index):
        """Valide les données d'une ligne"""
        erreurs_ligne = []
        
        # Validation des champs requis
        if pd.isna(row.get('matiere_combinee')) or not str(row['matiere_combinee']).strip():
            erreurs_ligne.append("La matière combinée est obligatoire")
        
        if pd.isna(row.get('lecon_nom')) or not str(row['lecon_nom']).strip():
            erreurs_ligne.append("Le nom de la lecon est obligatoire")
        
        if pd.isna(row.get('texte_question')) or not str(row['texte_question']).strip():
            erreurs_ligne.append("Le texte de la question est obligatoire")
        
        # Validation du type de question
        types_valides = ['choix_unique', 'choix_multiple', 'vrai_faux', 'texte_court', 'texte_long']
        if row['type_question'] not in types_valides:
            erreurs_ligne.append(f"Type de question invalide: {row['type_question']}")
        
        # Validation de la matière combinée
        matieres_valides = ['culture_aptitude', 'logique_combinee', 'anglais']
        if row['matiere_combinee'] not in matieres_valides:
            erreurs_ligne.append(f"Matiere combinee invalide: {row['matiere_combinee']}. Matieres valides: {', '.join(matieres_valides)}")
        
        # Validation de la difficulté (optionnelle)
        if not pd.isna(row.get('difficulte')):
            difficultes_valides = ['facile', 'moyen', 'difficile']
            if row['difficulte'] not in difficultes_valides:
                erreurs_ligne.append(f"Difficulté invalide: {row['difficulte']}")
        
        # Validations spécifiques selon le type de question
        if row['type_question'] in ['choix_unique', 'choix_multiple']:
            if pd.isna(row.get('choix_a')) or pd.isna(row.get('choix_b')):
                erreurs_ligne.append("Les choix A et B sont obligatoires pour les QCM")
            if pd.isna(row.get('bonne_reponse')):
                erreurs_ligne.append("La bonne réponse est obligatoire pour les QCM")
        
        elif row['type_question'] == 'vrai_faux':
            if row.get('bonne_reponse') not in ['VRAI', 'FAUX', 'A', 'B']:
                erreurs_ligne.append("La bonne réponse doit être 'VRAI', 'FAUX', 'A' ou 'B' pour les questions Vrai/Faux")
        
        elif row['type_question'] in ['texte_court', 'texte_long']:
            if pd.isna(row.get('reponse_attendue')):
                erreurs_ligne.append("La réponse attendue est obligatoire pour les questions texte")
        
        if erreurs_ligne:
            self.erreurs.append(f"Ligne {index + 2}: {'; '.join(erreurs_ligne)}")
            return False
        
        return True
    
    def obtenir_ou_creer_matiere_lecon(self, matiere_combinee, lecon_nom):
        """Obtient ou crée la matière et la leçon correspondantes"""
        from prepaconcours.models import Matiere, Lecon
        
        # Mapping des matières combinées vers les noms affichés
        mapping_noms = {
            'culture_aptitude': 'Culture générale + Aptitude verbale',
            'logique_combinee': 'Logique + Raisonnement',
            'anglais': 'Anglais'
        }
        
        nom_matiere = mapping_noms.get(matiere_combinee)
        if not nom_matiere:
            raise ValueError(f"Matiere combinee non reconnue: {matiere_combinee}")
        
        # Obtenir ou créer la matière
        matiere, created = Matiere.objects.get_or_create(
            choix_concours='examen_national',
            matiere_examen_national=matiere_combinee,
            defaults={
                'nom': nom_matiere
            }
        )
        
        if created:
            logger.info(f"Matiere creee: {nom_matiere}")
        
        # Obtenir ou créer la leçon
        lecon, created = Lecon.objects.get_or_create(
            nom=lecon_nom,
            matiere=matiere,
            defaults={
                'description': f'Lecon {lecon_nom} pour {nom_matiere}',
                'ordre': 0,
                'active': True
            }
        )
        
        if created:
            logger.info(f"Lecon creee: {lecon_nom} ({nom_matiere})")
        
        return matiere, lecon
    
    def creer_question_depuis_ligne(self, row):
        """Crée une question d'examen depuis une ligne du DataFrame"""
        try:
            # Obtenir ou créer la matière et la leçon
            matiere, lecon = self.obtenir_ou_creer_matiere_lecon(
                row['matiere_combinee'], 
                row['lecon_nom']
            )
            
            # Préparation des données
            donnees_question = {
                'texte': row['texte_question'],
                'type_question': row['type_question'],
                'matiere_combinee': row['matiere_combinee'],
                'difficulte': row.get('difficulte', 'moyen'),
                'active': row.get('active', True),
                'validee': row.get('validee', False),
                'temps_limite_secondes': int(row.get('temps_limite_secondes', 120)),
            }
            
            # Ajout des champs optionnels
            champs_optionnels = [
                'code_question', 'choix_a', 'choix_b', 'choix_c', 'choix_d', 'choix_e',
                'bonne_reponse', 'reponse_attendue', 'correction_mode', 'explication'
            ]
            
            for champ in champs_optionnels:
                if champ in row and not pd.isna(row[champ]):
                    donnees_question[champ] = row[champ]
            
            # Création de la question
            question = QuestionExamen.objects.create(**donnees_question)
            
            logger.info(f"Question creee: {question.code_question} - {question.texte[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la creation de la question: {e}")
            return False
    
    def importer_questions(self):
        """Importe toutes les questions depuis le fichier Excel"""
        try:
            logger.info(f"Debut de l'import depuis: {self.fichier_excel}")
            
            # Lecture du fichier Excel
            df = pd.read_excel(self.fichier_excel)
            logger.info(f"{len(df)} lignes trouvees dans le fichier Excel")
            
            # Validation des colonnes
            self.valider_colonnes_requises(df)
            
            # Traitement ligne par ligne
            for index, row in df.iterrows():
                logger.info(f"Traitement de la ligne {index + 2}...")
                
                # Validation des données
                if not self.valider_donnees_ligne(row, index):
                    self.questions_echouees += 1
                    continue
                
                # Création de la question
                if self.creer_question_depuis_ligne(row):
                    self.questions_importees += 1
                else:
                    self.questions_echouees += 1
            
            # Rapport final
            self.generer_rapport()
            
        except Exception as e:
            logger.error(f"Erreur critique lors de l'import: {e}")
            raise
    
    def generer_rapport(self):
        """Génère un rapport d'import"""
        logger.info("\n" + "="*60)
        logger.info("RAPPORT D'IMPORT DES QUESTIONS D'EXAMEN")
        logger.info("="*60)
        logger.info(f"Questions importees avec succes: {self.questions_importees}")
        logger.info(f"Questions echouees: {self.questions_echouees}")
        if (self.questions_importees + self.questions_echouees) > 0:
            taux = (self.questions_importees / (self.questions_importees + self.questions_echouees) * 100)
            logger.info(f"Taux de succes: {taux:.1f}%")
        
        if self.erreurs:
            logger.info(f"\nERREURS DETECTEES ({len(self.erreurs)}):")
            for erreur in self.erreurs[:10]:  # Afficher les 10 premières erreurs
                logger.info(f"  - {erreur}")
            if len(self.erreurs) > 10:
                logger.info(f"  ... et {len(self.erreurs) - 10} autres erreurs")
        
        # Statistiques par matière
        logger.info(f"\nREPARTITION PAR MATIERE:")
        matieres_stats = {
            'culture_aptitude': 'Culture generale + Aptitude verbale',
            'logique_combinee': 'Logique + Raisonnement',
            'anglais': 'Anglais'
        }
        for matiere_code, matiere_nom in matieres_stats.items():
            count = QuestionExamen.objects.filter(matiere_combinee=matiere_code).count()
            logger.info(f"  - {matiere_nom}: {count} questions")
        
        logger.info("="*60)

def creer_template_excel():
    """Crée un fichier Excel template avec des exemples"""
    template_data = [
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
        {
            'code_question': 'ENA2024-LC-001',
            'texte': 'Si A > B et B > C, alors :',
            'type_question': 'choix_multiple',
            'matiere_combinee': 'logique_combinee',
            'choix_a': 'A > C',
            'choix_b': 'A = C',
            'choix_c': 'C > A',
            'choix_d': 'A < C',
            'choix_e': '',
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
        {
            'code_question': 'ENA2024-AN-002',
            'texte': 'Write a short paragraph (50 words) about the importance of education.',
            'type_question': 'texte_long',
            'matiere_combinee': 'anglais',
            'choix_a': '',
            'choix_b': '',
            'choix_c': '',
            'choix_d': '',
            'choix_e': '',
            'bonne_reponse': '',
            'reponse_attendue': 'education,important,knowledge,future,society,learning',
            'correction_mode': 'mot_cle',
            'explication': 'La réponse doit contenir des mots-clés liés à l\'importance de l\'éducation.',
            'difficulte': 'difficile',
            'temps_limite_secondes': 300,
            'active': True,
            'validee': False,
            'creee_par': 'Template'
        }
    ]
    
    df_template = pd.DataFrame(template_data)
    fichier_template = 'template_questions_examen_ena.xlsx'
    df_template.to_excel(fichier_template, index=False)
    
    logger.info(f"📄 Template Excel créé: {fichier_template}")
    logger.info("📋 Colonnes disponibles:")
    for col in df_template.columns:
        logger.info(f"  - {col}")

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import des questions d\'examen national ENA depuis Excel')
    parser.add_argument('--fichier', '-f', help='Chemin vers le fichier Excel à importer')
    parser.add_argument('--template', '-t', action='store_true', help='Créer un fichier template Excel')
    
    args = parser.parse_args()
    
    if args.template:
        creer_template_excel()
        return
    
    if not args.fichier:
        logger.error("❌ Veuillez spécifier un fichier Excel avec --fichier ou créer un template avec --template")
        return
    
    if not os.path.exists(args.fichier):
        logger.error(f"❌ Fichier non trouvé: {args.fichier}")
        return
    
    # Import des questions
    importeur = ImportQuestionExamenExcel(args.fichier)
    importeur.importer_questions()
    
    logger.info("🎉 Import terminé!")

if __name__ == '__main__':
    main()
