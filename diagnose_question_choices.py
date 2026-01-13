import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Matiere, Lecon, Question, Choix

def diagnose_question_choices():
    print("Diagnostic des choix de questions ENA")
    print("=" * 50)
    
    # Verifier les questions dans la lecon 13 (Essential Vocabulary)
    print("\nVERIFICATION LECON 13 (Essential Vocabulary):")
    try:
        lecon_13 = Lecon.objects.get(id=13)
        print(f"Lecon: {lecon_13.nom}")
        
        questions = Question.objects.filter(lecon=lecon_13)
        print(f"Nombre de questions: {questions.count()}")
        
        for question in questions:
            print(f"\n  Question ID: {question.id}")
            print(f"  Texte: {question.texte}")
            print(f"  Type: {question.type_question}")
            
            # Verifier les choix pour cette question
            choix = Choix.objects.filter(question=question)
            print(f"  Nombre de choix: {choix.count()}")
            
            if choix.exists():
                for i, choix_item in enumerate(choix):
                    print(f"    Choix {i+1}: {choix_item.texte} (Correct: {choix_item.est_correct})")
            else:
                print(f"    PROBLEME: Aucun choix trouve pour cette question!")
                
    except Lecon.DoesNotExist:
        print("ERREUR: Lecon 13 non trouvee")
    
    # Verifier toutes les questions ENA et leurs choix
    print("\n\nVERIFICATION GLOBALE QUESTIONS ENA:")
    matieres_ena = Matiere.objects.filter(choix_concours='ENA')
    
    total_questions = 0
    questions_sans_choix = 0
    
    for matiere in matieres_ena:
        questions = Question.objects.filter(matiere=matiere)
        total_questions += questions.count()
        
        print(f"\nMatiere: {matiere.nom}")
        print(f"  Questions: {questions.count()}")
        
        for question in questions:
            choix = Choix.objects.filter(question=question)
            if question.type_question in ['choix_unique', 'choix_multiple', 'vrai_faux'] and choix.count() == 0:
                questions_sans_choix += 1
                print(f"    PROBLEME: Question {question.id} ({question.type_question}) sans choix!")
    
    print(f"\nRESUME:")
    print(f"  Total questions ENA: {total_questions}")
    print(f"  Questions sans choix: {questions_sans_choix}")
    
    # Test de serialisation comme l'API
    print("\n\nTEST SERIALISATION API:")
    try:
        from prepaconcours.serializers import QuestionDetailSerializer
        
        # Prendre la premiere question de la lecon 13
        question = Question.objects.filter(lecon_id=13).first()
        if question:
            print(f"Question test: {question.texte}")
            
            # Serialiser comme l'API
            serializer = QuestionDetailSerializer(question)
            data = serializer.data
            
            print(f"Donnees serialisees:")
            print(f"  ID: {data.get('id')}")
            print(f"  Type: {data.get('type_question')}")
            print(f"  Choix: {data.get('choix', [])}")
            
            if 'choix' in data and len(data['choix']) > 0:
                print(f"  Nombre de choix serialises: {len(data['choix'])}")
                for i, choix in enumerate(data['choix']):
                    print(f"    Choix {i+1}: {choix}")
            else:
                print(f"  PROBLEME: Aucun choix dans les donnees serialisees!")
        else:
            print("Aucune question trouvee dans la lecon 13")
            
    except Exception as e:
        print(f"Erreur lors de la serialisation: {e}")
    
    print("\n" + "=" * 50)
    print("Diagnostic termine")

if __name__ == '__main__':
    diagnose_question_choices()
