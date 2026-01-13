import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Matiere, Lecon, Question, Choix

def diagnose_ena_session():
    print("Diagnostic creation session ENA")
    print("=" * 50)
    
    # Verifier matieres ENA
    print("\nMATIERES ENA:")
    matieres_ena = Matiere.objects.filter(choix_concours='ENA')
    for matiere in matieres_ena:
        print(f"  ID: {matiere.id} | Nom: {matiere.nom}")
    
    # Verifier lecons
    print("\nLECONS PAR MATIERE:")
    for matiere in matieres_ena:
        lecons = Lecon.objects.filter(matiere=matiere)
        print(f"\n  Matiere: {matiere.nom} (ID: {matiere.id})")
        if lecons.exists():
            for lecon in lecons:
                questions_count = Question.objects.filter(lecon=lecon).count()
                print(f"    Lecon ID: {lecon.id} | Nom: {lecon.nom} | Questions: {questions_count}")
        else:
            print(f"    Aucune lecon trouvee")
    
    # Verifier IDs specifiques de l'erreur
    print("\nVERIFICATION IDs SPECIFIQUES:")
    print("Donnees erreur: matiere=3, lecon=13")
    
    try:
        matiere_3 = Matiere.objects.get(id=3)
        print(f"  Matiere ID 3: {matiere_3.nom} (concours: {matiere_3.choix_concours})")
    except Matiere.DoesNotExist:
        print(f"  ERREUR: Matiere ID 3 non trouvee")
    
    try:
        lecon_13 = Lecon.objects.get(id=13)
        print(f"  Lecon ID 13: {lecon_13.nom} (matiere: {lecon_13.matiere.nom})")
        
        # Verifier coherence matiere-lecon
        if lecon_13.matiere.id == 3:
            print(f"    OK: Lecon 13 appartient a matiere 3")
        else:
            print(f"    PROBLEME: Lecon 13 appartient a matiere {lecon_13.matiere.id}, pas 3")
        
        # Verifier questions
        questions_lecon_13 = Question.objects.filter(lecon=lecon_13)
        print(f"    Questions dans lecon 13: {questions_lecon_13.count()}")
        
    except Lecon.DoesNotExist:
        print(f"  ERREUR: Lecon ID 13 non trouvee")
    
    # Test validation
    print("\nTEST VALIDATION:")
    test_data = {
        "matiere": 3,
        "lecon": 13,
        "nb_questions": 1,
        "choix_concours": "ena"
    }
    
    print(f"Donnees test: {test_data}")
    
    try:
        matiere = Matiere.objects.get(id=test_data["matiere"])
        print(f"  Matiere trouvee: {matiere.nom}")
        
        lecon = Lecon.objects.get(id=test_data["lecon"])
        print(f"  Lecon trouvee: {lecon.nom}")
        
        # Verifier coherence
        if lecon.matiere.id != matiere.id:
            print(f"  ERREUR: Lecon {lecon.id} n'appartient pas a matiere {matiere.id}")
            print(f"    Lecon appartient a: {lecon.matiere.nom} (ID: {lecon.matiere.id})")
        else:
            print(f"  OK: Coherence matiere-lecon validee")
        
        # Verifier questions
        questions = Question.objects.filter(lecon=lecon)
        print(f"  Questions disponibles: {questions.count()}")
        
        if questions.count() >= test_data["nb_questions"]:
            print(f"  OK: Assez de questions ({questions.count()} >= {test_data['nb_questions']})")
        else:
            print(f"  ERREUR: Pas assez de questions ({questions.count()} < {test_data['nb_questions']})")
            
    except Exception as e:
        print(f"  ERREUR validation: {e}")
    
    print("\n" + "=" * 50)
    print("Diagnostic termine")

if __name__ == '__main__':
    diagnose_ena_session()
