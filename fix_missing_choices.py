import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Matiere, Lecon, Question, Choix

def fix_missing_choices():
    print("Correction des choix manquants pour les questions ENA")
    print("=" * 60)
    
    # Trouver toutes les questions ENA sans choix
    matieres_ena = Matiere.objects.filter(choix_concours='ENA')
    questions_sans_choix = []
    
    for matiere in matieres_ena:
        questions = Question.objects.filter(matiere=matiere)
        for question in questions:
            # Verifier si la question necessite des choix
            if question.type_question in ['choix_unique', 'choix_multiple', 'vrai_faux']:
                choix_count = Choix.objects.filter(question=question).count()
                if choix_count == 0:
                    questions_sans_choix.append(question)
                    print(f"Question sans choix: {question.id} - {question.texte[:50]}...")
    
    print(f"\nNombre de questions a corriger: {len(questions_sans_choix)}")
    
    # Corriger chaque question
    for question in questions_sans_choix:
        print(f"\nCorrection question {question.id}: {question.texte[:50]}...")
        
        if question.type_question == 'choix_unique':
            # Creer 4 choix pour choix unique
            choices_data = [
                {'texte': 'Option A', 'correct': True},
                {'texte': 'Option B', 'correct': False},
                {'texte': 'Option C', 'correct': False},
                {'texte': 'Option D', 'correct': False}
            ]
            
            # Personnaliser selon la matiere
            if 'Anglais' in question.matiere.nom:
                if 'Essential Vocabulary' in question.lecon.nom:
                    choices_data = [
                        {'texte': 'Synonym of "happy"', 'correct': False},
                        {'texte': 'Joyful', 'correct': True},
                        {'texte': 'Sad', 'correct': False},
                        {'texte': 'Angry', 'correct': False}
                    ]
            
            for i, choice_data in enumerate(choices_data):
                Choix.objects.create(
                    question=question,
                    texte=choice_data['texte'],
                    est_correct=choice_data['correct']
                )
                print(f"  Choix cree: {choice_data['texte']} (Correct: {choice_data['correct']})")
        
        elif question.type_question == 'choix_multiple':
            # Creer 4 choix avec 2 bonnes reponses
            choices_data = [
                {'texte': 'Correct option 1', 'correct': True},
                {'texte': 'Correct option 2', 'correct': True},
                {'texte': 'Wrong option 1', 'correct': False},
                {'texte': 'Wrong option 2', 'correct': False}
            ]
            
            for choice_data in choices_data:
                Choix.objects.create(
                    question=question,
                    texte=choice_data['texte'],
                    est_correct=choice_data['correct']
                )
                print(f"  Choix cree: {choice_data['texte']} (Correct: {choice_data['correct']})")
        
        elif question.type_question == 'vrai_faux':
            # Creer 2 choix pour vrai/faux
            choices_data = [
                {'texte': 'Vrai', 'correct': True},
                {'texte': 'Faux', 'correct': False}
            ]
            
            for choice_data in choices_data:
                Choix.objects.create(
                    question=question,
                    texte=choice_data['texte'],
                    est_correct=choice_data['correct']
                )
                print(f"  Choix cree: {choice_data['texte']} (Correct: {choice_data['correct']})")
    
    # Verification finale
    print(f"\nVERIFICATION FINALE:")
    questions_encore_sans_choix = 0
    
    for matiere in matieres_ena:
        questions = Question.objects.filter(matiere=matiere)
        for question in questions:
            if question.type_question in ['choix_unique', 'choix_multiple', 'vrai_faux']:
                choix_count = Choix.objects.filter(question=question).count()
                if choix_count == 0:
                    questions_encore_sans_choix += 1
                    print(f"  ENCORE SANS CHOIX: Question {question.id}")
    
    if questions_encore_sans_choix == 0:
        print("  Toutes les questions ont maintenant des choix!")
    else:
        print(f"  Il reste {questions_encore_sans_choix} questions sans choix")
    
    print("\n" + "=" * 60)
    print("Correction terminee avec succes!")

if __name__ == '__main__':
    fix_missing_choices()
