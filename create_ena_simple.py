import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Matiere, Lecon, Question, Choix

def create_ena_content():
    print("Creating ENA lessons and questions...")
    
    # Get ENA subjects
    matieres_ena = Matiere.objects.filter(choix_concours='ENA')
    print(f"Found {matieres_ena.count()} ENA subjects")
    
    for matiere in matieres_ena:
        print(f"Processing: {matiere.nom}")
        
        # Create lessons for each subject
        lessons = get_lessons_for_subject(matiere.nom)
        
        for i, lesson_name in enumerate(lessons, 1):
            lecon, created = Lecon.objects.get_or_create(
                nom=lesson_name,
                matiere=matiere,
                defaults={
                    'description': f'Lesson {i} for {matiere.nom}',
                    'ordre': i
                }
            )
            
            if created:
                print(f"  Created lesson: {lesson_name}")
                
                # Create questions for this lesson
                questions = get_questions_for_lesson(matiere.nom, lesson_name)
                
                for question_data in questions:
                    create_question(matiere, lecon, question_data)
            else:
                print(f"  Lesson exists: {lesson_name}")
    
    print("ENA content creation completed!")

def get_lessons_for_subject(subject_name):
    lessons_map = {
        'Anglais': ['Grammar Basics', 'Essential Vocabulary', 'Reading Comprehension'],
        'Aptitude verbale': ['Synonyms and Antonyms', 'Verbal Analogies', 'Text Comprehension'],
        'Culture generale': ['French History', 'World Geography', 'French Institutions'],
        'Logique d\'organisation': ['Planning Management', 'Process Analysis', 'Problem Solving'],
        'Logique numerique': ['Number Sequences', 'Calculations', 'Mathematical Reasoning']
    }
    return lessons_map.get(subject_name, ['General Lesson 1', 'General Lesson 2'])

def get_questions_for_lesson(subject_name, lesson_name):
    if subject_name == 'Anglais' and 'Grammar' in lesson_name:
        return [
            {
                'text': 'What is the correct form: She ___ happy?',
                'type': 'choix_unique',
                'choices': [
                    {'text': 'am', 'correct': False},
                    {'text': 'is', 'correct': True},
                    {'text': 'are', 'correct': False}
                ],
                'explanation': 'With "she" we use "is".'
            },
            {
                'text': 'Select correct past tense forms:',
                'type': 'choix_multiple',
                'choices': [
                    {'text': 'went', 'correct': True},
                    {'text': 'saw', 'correct': True},
                    {'text': 'goed', 'correct': False}
                ],
                'explanation': 'Went and saw are correct past forms.'
            },
            {
                'text': 'Beautiful is an adjective.',
                'type': 'vrai_faux',
                'choices': [
                    {'text': 'True', 'correct': True},
                    {'text': 'False', 'correct': False}
                ],
                'explanation': 'Beautiful is indeed an adjective.'
            },
            {
                'text': 'What is the past tense of go?',
                'type': 'texte_court',
                'expected_answer': 'went',
                'explanation': 'The past tense of go is went.'
            },
            {
                'text': 'Write about your hobbies in English.',
                'type': 'texte_long',
                'expected_answer': 'I enjoy reading and sports. Photography is my favorite hobby.',
                'explanation': 'A paragraph about hobbies should include personal activities.'
            }
        ]
    elif subject_name == 'Aptitude verbale' and 'Synonyms' in lesson_name:
        return [
            {
                'text': 'Quel est le synonyme de difficile?',
                'type': 'choix_unique',
                'choices': [
                    {'text': 'facile', 'correct': False},
                    {'text': 'ardu', 'correct': True},
                    {'text': 'simple', 'correct': False}
                ],
                'explanation': 'Ardu est un synonyme de difficile.'
            },
            {
                'text': 'Quels sont les antonymes de joyeux?',
                'type': 'choix_multiple',
                'choices': [
                    {'text': 'triste', 'correct': True},
                    {'text': 'malheureux', 'correct': True},
                    {'text': 'heureux', 'correct': False}
                ],
                'explanation': 'Triste et malheureux sont des antonymes de joyeux.'
            }
        ]
    else:
        # Generic questions for other subjects/lessons
        return [
            {
                'text': f'Question for {lesson_name}',
                'type': 'choix_unique',
                'choices': [
                    {'text': 'Correct answer', 'correct': True},
                    {'text': 'Wrong answer 1', 'correct': False},
                    {'text': 'Wrong answer 2', 'correct': False}
                ],
                'explanation': f'Explanation for {lesson_name}.'
            },
            {
                'text': f'True/False question for {lesson_name}',
                'type': 'vrai_faux',
                'choices': [
                    {'text': 'True', 'correct': True},
                    {'text': 'False', 'correct': False}
                ],
                'explanation': f'This statement about {lesson_name} is true.'
            }
        ]

def create_question(matiere, lecon, question_data):
    question, created = Question.objects.get_or_create(
        texte=question_data['text'],
        matiere=matiere,
        lecon=lecon,
        defaults={
            'type_question': question_data['type'],
            'explication': question_data['explanation'],
            'reponse_attendue': question_data.get('expected_answer', ''),
            'temps_limite': 60
        }
    )
    
    if created:
        print(f"    Created question: {question_data['text'][:40]}...")
        
        # Create choices if applicable
        if 'choices' in question_data:
            for i, choice_data in enumerate(question_data['choices']):
                Choix.objects.create(
                    question=question,
                    texte=choice_data['text'],
                    est_correct=choice_data['correct']
                )

if __name__ == '__main__':
    create_ena_content()
