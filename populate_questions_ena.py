#!/usr/bin/env python
"""
Script pour peupler la base de données avec des questions ENA pour les compositions nationales
"""

import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import QuestionExamen, ChoixExamen

def create_culture_aptitude_questions():
    """Créer 40 questions de Culture générale + Aptitude verbale"""
    questions_data = [
        {
            'texte': 'Quel écrivain français a écrit "Les Misérables" ?',
            'choix': [
                ('Victor Hugo', True),
                ('Émile Zola', False),
                ('Gustave Flaubert', False),
                ('Honoré de Balzac', False)
            ]
        },
        {
            'texte': 'Quelle est la capitale du Sénégal ?',
            'choix': [
                ('Dakar', True),
                ('Bamako', False),
                ('Abidjan', False),
                ('Conakry', False)
            ]
        },
        {
            'texte': 'En quelle année le Sénégal a-t-il accédé à l\'indépendance ?',
            'choix': [
                ('1960', True),
                ('1958', False),
                ('1962', False),
                ('1956', False)
            ]
        },
        {
            'texte': 'Quel mot est correctement orthographié ?',
            'choix': [
                ('Développement', True),
                ('Dévelopement', False),
                ('Développemant', False),
                ('Dévelopemant', False)
            ]
        },
        {
            'texte': 'Quel est le synonyme de "perspicace" ?',
            'choix': [
                ('Clairvoyant', True),
                ('Négligent', False),
                ('Confus', False),
                ('Indécis', False)
            ]
        },
        {
            'texte': 'Qui était le premier président du Sénégal ?',
            'choix': [
                ('Léopold Sédar Senghor', True),
                ('Abdou Diouf', False),
                ('Abdoulaye Wade', False),
                ('Macky Sall', False)
            ]
        },
        {
            'texte': 'Quelle est la monnaie officielle du Sénégal ?',
            'choix': [
                ('Franc CFA', True),
                ('Euro', False),
                ('Dollar', False),
                ('Livre sterling', False)
            ]
        },
        {
            'texte': 'Quel fleuve traverse Dakar ?',
            'choix': [
                ('Aucun fleuve ne traverse Dakar', True),
                ('Fleuve Sénégal', False),
                ('Gambie', False),
                ('Casamance', False)
            ]
        },
        {
            'texte': 'Dans quel continent se trouve le Sénégal ?',
            'choix': [
                ('Afrique', True),
                ('Asie', False),
                ('Europe', False),
                ('Amérique', False)
            ]
        },
        {
            'texte': 'Quel est l\'antonyme de "optimiste" ?',
            'choix': [
                ('Pessimiste', True),
                ('Joyeux', False),
                ('Confiant', False),
                ('Espérant', False)
            ]
        }
    ]
    
    # Dupliquer les questions pour atteindre 40
    all_questions = questions_data * 4
    
    for i, q_data in enumerate(all_questions[:40], 1):
        # Préparer les choix
        choix_list = q_data['choix']
        bonne_reponse = ''
        
        question = QuestionExamen.objects.create(
            code_question=f'ENA2024-CG-{i:03d}',
            texte=q_data['texte'],
            type_question='choix_unique',
            matiere_combinee='culture_aptitude',
            choix_a=choix_list[0][0],
            choix_b=choix_list[1][0],
            choix_c=choix_list[2][0] if len(choix_list) > 2 else '',
            choix_d=choix_list[3][0] if len(choix_list) > 3 else '',
            bonne_reponse=chr(65 + next(i for i, (_, correct) in enumerate(choix_list) if correct))  # A, B, C, D
        )
        
        for j, (texte_choix, est_correcte) in enumerate(q_data['choix']):
            ChoixExamen.objects.create(
                question_examen=question,
                texte_choix=texte_choix,
                est_correcte=est_correcte,
                ordre=j + 1
            )
    
    print(f"Cree 40 questions de Culture generale + Aptitude verbale")

def create_anglais_questions():
    """Créer 20 questions d'Anglais"""
    questions_data = [
        {
            'texte': 'Choose the correct answer: "I ___ to school every day."',
            'choix': [
                ('go', True),
                ('goes', False),
                ('went', False),
                ('going', False)
            ]
        },
        {
            'texte': 'What is the past tense of "run"?',
            'choix': [
                ('ran', True),
                ('runned', False),
                ('running', False),
                ('runs', False)
            ]
        },
        {
            'texte': 'Which word means "beautiful"?',
            'choix': [
                ('Pretty', True),
                ('Ugly', False),
                ('Tall', False),
                ('Fast', False)
            ]
        },
        {
            'texte': 'Complete: "She ___ a book yesterday."',
            'choix': [
                ('read', True),
                ('reads', False),
                ('reading', False),
                ('will read', False)
            ]
        },
        {
            'texte': 'What is the plural of "child"?',
            'choix': [
                ('children', True),
                ('childs', False),
                ('childes', False),
                ('child', False)
            ]
        },
        {
            'texte': 'Choose the correct preposition: "I live ___ Paris."',
            'choix': [
                ('in', True),
                ('on', False),
                ('at', False),
                ('by', False)
            ]
        },
        {
            'texte': 'What does "library" mean?',
            'choix': [
                ('A place where books are kept', True),
                ('A place to buy food', False),
                ('A place to sleep', False),
                ('A place to work', False)
            ]
        },
        {
            'texte': 'Complete: "They ___ playing football now."',
            'choix': [
                ('are', True),
                ('is', False),
                ('was', False),
                ('were', False)
            ]
        },
        {
            'texte': 'What is the opposite of "hot"?',
            'choix': [
                ('cold', True),
                ('warm', False),
                ('cool', False),
                ('wet', False)
            ]
        },
        {
            'texte': 'Choose the correct article: "___ apple is red."',
            'choix': [
                ('The', True),
                ('A', False),
                ('An', False),
                ('Some', False)
            ]
        }
    ]
    
    # Dupliquer pour atteindre 20
    all_questions = questions_data * 2
    
    for i, q_data in enumerate(all_questions[:20], 1):
        # Préparer les choix
        choix_list = q_data['choix']
        
        question = QuestionExamen.objects.create(
            code_question=f'ENA2024-EN-{i:03d}',
            texte=q_data['texte'],
            type_question='choix_unique',
            matiere_combinee='anglais',
            choix_a=choix_list[0][0],
            choix_b=choix_list[1][0],
            choix_c=choix_list[2][0] if len(choix_list) > 2 else '',
            choix_d=choix_list[3][0] if len(choix_list) > 3 else '',
            bonne_reponse=chr(65 + next(i for i, (_, correct) in enumerate(choix_list) if correct))  # A, B, C, D
        )
        
        for j, (texte_choix, est_correcte) in enumerate(q_data['choix']):
            ChoixExamen.objects.create(
                question_examen=question,
                texte_choix=texte_choix,
                est_correcte=est_correcte,
                ordre=j + 1
            )
    
    print(f"Cree 20 questions d'Anglais")

def create_logique_questions():
    """Créer 40 questions de Logique d'organisation + Logique numérique"""
    questions_data = [
        {
            'texte': 'Quelle est la suite logique : 2, 6, 18, ?',
            'choix': [
                ('54', True),
                ('36', False),
                ('72', False),
                ('24', False)
            ]
        },
        {
            'texte': 'Si A = 1, B = 2, C = 3, que vaut "CAB" ?',
            'choix': [
                ('312', True),
                ('123', False),
                ('321', False),
                ('213', False)
            ]
        },
        {
            'texte': 'Complétez la série : 1, 4, 9, 16, ?',
            'choix': [
                ('25', True),
                ('20', False),
                ('24', False),
                ('30', False)
            ]
        },
        {
            'texte': 'Quel nombre manque : 3, 6, 12, ?, 48',
            'choix': [
                ('24', True),
                ('18', False),
                ('30', False),
                ('36', False)
            ]
        },
        {
            'texte': 'Si tous les chats sont des animaux et tous les animaux respirent, alors :',
            'choix': [
                ('Tous les chats respirent', True),
                ('Tous les animaux sont des chats', False),
                ('Seuls les chats respirent', False),
                ('Aucune conclusion possible', False)
            ]
        },
        {
            'texte': 'Quelle est la prochaine lettre : A, C, E, G, ?',
            'choix': [
                ('I', True),
                ('H', False),
                ('J', False),
                ('F', False)
            ]
        },
        {
            'texte': 'Dans une classe de 30 élèves, 18 aiment le football et 20 aiment le basketball. Combien aiment les deux sports au minimum ?',
            'choix': [
                ('8', True),
                ('10', False),
                ('12', False),
                ('15', False)
            ]
        },
        {
            'texte': 'Complétez : 5, 10, 20, 40, ?',
            'choix': [
                ('80', True),
                ('60', False),
                ('70', False),
                ('50', False)
            ]
        },
        {
            'texte': 'Si Pierre est plus grand que Paul et Paul est plus grand que Jacques, alors :',
            'choix': [
                ('Pierre est plus grand que Jacques', True),
                ('Jacques est plus grand que Pierre', False),
                ('Pierre et Jacques ont la même taille', False),
                ('On ne peut pas conclure', False)
            ]
        },
        {
            'texte': 'Quel est le nombre suivant : 1, 1, 2, 3, 5, ?',
            'choix': [
                ('8', True),
                ('7', False),
                ('6', False),
                ('9', False)
            ]
        }
    ]
    
    # Dupliquer pour atteindre 40
    all_questions = questions_data * 4
    
    for i, q_data in enumerate(all_questions[:40], 1):
        # Préparer les choix
        choix_list = q_data['choix']
        
        question = QuestionExamen.objects.create(
            code_question=f'ENA2024-LG-{i:03d}',
            texte=q_data['texte'],
            type_question='choix_unique',
            matiere_combinee='logique_combinee',
            choix_a=choix_list[0][0],
            choix_b=choix_list[1][0],
            choix_c=choix_list[2][0] if len(choix_list) > 2 else '',
            choix_d=choix_list[3][0] if len(choix_list) > 3 else '',
            bonne_reponse=chr(65 + next(i for i, (_, correct) in enumerate(choix_list) if correct))  # A, B, C, D
        )
        
        for j, (texte_choix, est_correcte) in enumerate(q_data['choix']):
            ChoixExamen.objects.create(
                question_examen=question,
                texte_choix=texte_choix,
                est_correcte=est_correcte,
                ordre=j + 1
            )
    
    print(f"Cree 40 questions de Logique d'organisation + Logique numerique")

def main():
    """Fonction principale"""
    print("Debut du peuplement des questions ENA...")
    
    # Supprimer les questions existantes
    QuestionExamen.objects.filter(matiere_combinee__in=['culture_aptitude', 'anglais', 'logique_combinee']).delete()
    print("Questions existantes supprimees")
    
    # Créer les nouvelles questions
    create_culture_aptitude_questions()
    create_anglais_questions()
    create_logique_questions()
    
    # Vérification
    total_questions = QuestionExamen.objects.filter(matiere_combinee__in=['culture_aptitude', 'anglais', 'logique_combinee']).count()
    print(f"\nTotal des questions creees : {total_questions}")
    print(f"   - Culture generale + Aptitude verbale : {QuestionExamen.objects.filter(matiere_combinee='culture_aptitude').count()}")
    print(f"   - Anglais : {QuestionExamen.objects.filter(matiere_combinee='anglais').count()}")
    print(f"   - Logique : {QuestionExamen.objects.filter(matiere_combinee='logique_combinee').count()}")
    
    print("\nPeuplement termine avec succes !")

if __name__ == '__main__':
    main()
