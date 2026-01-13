import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Matiere, Lecon, Question, Choix

def diagnose_ena_session_creation():
    print("Diagnostic de la creation de session ENA...")
    print("=" * 60)
    
    # Verifier les matieres ENA
    print("\nMATIERES ENA:")
    matieres_ena = Matiere.objects.filter(choix_concours='ENA')
    for matiere in matieres_ena:
        print(f"  ID: {matiere.id} | Nom: {matiere.nom} | Tour: {matiere.tour_ena}")
    
    # Vérifier les leçons pour chaque matière
    print("\n📖 LEÇONS PAR MATIÈRE:")
    for matiere in matieres_ena:
        lecons = Lecon.objects.filter(matiere=matiere)
        print(f"\n  Matière: {matiere.nom} (ID: {matiere.id})")
        if lecons.exists():
            for lecon in lecons:
                questions_count = Question.objects.filter(lecon=lecon).count()
                print(f"    ✅ Leçon ID: {lecon.id} | Nom: {lecon.nom} | Questions: {questions_count}")
        else:
            print(f"    ❌ Aucune leçon trouvée")
    
    # Vérifier spécifiquement les IDs mentionnés dans l'erreur
    print("\n🎯 VÉRIFICATION DES IDs SPÉCIFIQUES:")
    print("Données de l'erreur: matiere=3, lecon=13")
    
    try:
        matiere_3 = Matiere.objects.get(id=3)
        print(f"  ✅ Matière ID 3 trouvée: {matiere_3.nom} (concours: {matiere_3.choix_concours})")
    except Matiere.DoesNotExist:
        print(f"  ❌ Matière ID 3 non trouvée")
    
    try:
        lecon_13 = Lecon.objects.get(id=13)
        print(f"  ✅ Leçon ID 13 trouvée: {lecon_13.nom} (matière: {lecon_13.matiere.nom})")
        
        # Vérifier si cette leçon appartient à la matière 3
        if lecon_13.matiere.id == 3:
            print(f"    ✅ La leçon 13 appartient bien à la matière 3")
        else:
            print(f"    ❌ PROBLÈME: La leçon 13 appartient à la matière {lecon_13.matiere.id} ({lecon_13.matiere.nom}), pas à la matière 3")
        
        # Vérifier les questions dans cette leçon
        questions_lecon_13 = Question.objects.filter(lecon=lecon_13)
        print(f"    📝 Questions dans la leçon 13: {questions_lecon_13.count()}")
        
    except Lecon.DoesNotExist:
        print(f"  ❌ Leçon ID 13 non trouvée")
    
    # Vérifier les questions par matière (sans leçon spécifique)
    print("\n📝 QUESTIONS PAR MATIÈRE:")
    for matiere in matieres_ena:
        questions_matiere = Question.objects.filter(matiere=matiere)
        questions_avec_lecon = Question.objects.filter(matiere=matiere, lecon__isnull=False)
        questions_sans_lecon = Question.objects.filter(matiere=matiere, lecon__isnull=True)
        
        print(f"\n  Matière: {matiere.nom} (ID: {matiere.id})")
        print(f"    Total questions: {questions_matiere.count()}")
        print(f"    Avec leçon: {questions_avec_lecon.count()}")
        print(f"    Sans leçon: {questions_sans_lecon.count()}")
    
    # Test de validation comme le fait le serializer
    print("\n🧪 TEST DE VALIDATION:")
    test_data = {
        "matiere": 3,
        "lecon": 13,
        "nb_questions": 1,
        "choix_concours": "ena"
    }
    
    print(f"Données de test: {test_data}")
    
    # Simuler la validation du serializer
    try:
        matiere = Matiere.objects.get(id=test_data["matiere"])
        print(f"  ✅ Matière trouvée: {matiere.nom}")
        
        lecon = Lecon.objects.get(id=test_data["lecon"])
        print(f"  ✅ Leçon trouvée: {lecon.nom}")
        
        # Vérifier la cohérence matière-leçon
        if lecon.matiere.id != matiere.id:
            print(f"  ❌ ERREUR: La leçon {lecon.id} n'appartient pas à la matière {matiere.id}")
            print(f"      Leçon appartient à: {lecon.matiere.nom} (ID: {lecon.matiere.id})")
        else:
            print(f"  ✅ Cohérence matière-leçon validée")
        
        # Vérifier les questions disponibles
        questions = Question.objects.filter(lecon=lecon)
        print(f"  📝 Questions disponibles dans la leçon: {questions.count()}")
        
        if questions.count() >= test_data["nb_questions"]:
            print(f"  ✅ Assez de questions disponibles ({questions.count()} >= {test_data['nb_questions']})")
        else:
            print(f"  ❌ Pas assez de questions ({questions.count()} < {test_data['nb_questions']})")
            
    except Exception as e:
        print(f"  ❌ Erreur lors de la validation: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Diagnostic terminé")

if __name__ == '__main__':
    diagnose_ena_session_creation()
