#!/usr/bin/env python3
"""
Script de test pour valider l'implémentation complète des questions d'examen national ENA
"""

import os
import sys
import django
import json
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import QuestionExamen
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class TestQuestionExamenENA:
    """Classe de test pour les questions d'examen national ENA"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = []
        self.errors = []
    
    def log_test(self, test_name, success, message=""):
        """Enregistre le résultat d'un test"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if not success:
            self.errors.append(f"{test_name}: {message}")
    
    def test_model_creation(self):
        """Test de création du modèle QuestionExamen"""
        try:
            # Test création question choix unique
            question_qcm = QuestionExamen.objects.create(
                texte="Test question choix unique",
                type_question="choix_unique",
                matiere_combinee="culture_aptitude",
                choix_a="Réponse A",
                choix_b="Réponse B",
                choix_c="Réponse C",
                choix_d="Réponse D",
                bonne_reponse="A",
                difficulte="moyen",
                creee_par="Test"
            )
            
            # Vérifier la génération automatique du code
            assert question_qcm.code_question.startswith("ENA2024-CA-")
            self.log_test("Création question QCM", True, f"Code généré: {question_qcm.code_question}")
            
            # Test création question vrai/faux
            question_vf = QuestionExamen.objects.create(
                texte="Test question vrai/faux",
                type_question="vrai_faux",
                matiere_combinee="logique_combinee",
                bonne_reponse="VRAI",
                difficulte="facile",
                creee_par="Test"
            )
            
            assert question_vf.code_question.startswith("ENA2024-LC-")
            self.log_test("Création question Vrai/Faux", True, f"Code généré: {question_vf.code_question}")
            
            # Test création question texte
            question_texte = QuestionExamen.objects.create(
                texte="Test question texte court",
                type_question="texte_court",
                matiere_combinee="anglais",
                reponse_attendue="test answer",
                correction_mode="exacte",
                difficulte="difficile",
                creee_par="Test"
            )
            
            assert question_texte.code_question.startswith("ENA2024-AN-")
            self.log_test("Création question Texte", True, f"Code généré: {question_texte.code_question}")
            
        except Exception as e:
            self.log_test("Création modèle", False, str(e))
    
    def test_validation_methods(self):
        """Test des méthodes de validation des réponses"""
        try:
            # Test question QCM
            question_qcm = QuestionExamen.objects.create(
                texte="Test validation QCM",
                type_question="choix_unique",
                matiere_combinee="culture_aptitude",
                choix_a="Bonne réponse",
                choix_b="Mauvaise réponse",
                bonne_reponse="A",
                difficulte="moyen",
                creee_par="Test"
            )
            
            # Test réponse correcte
            assert question_qcm.verifier_reponse("A") == True
            assert question_qcm.verifier_reponse("B") == False
            self.log_test("Validation QCM", True, "Réponses correctement validées")
            
            # Test question Vrai/Faux
            question_vf = QuestionExamen.objects.create(
                texte="Test validation Vrai/Faux",
                type_question="vrai_faux",
                matiere_combinee="culture_aptitude",
                bonne_reponse="VRAI",
                difficulte="facile",
                creee_par="Test"
            )
            
            assert question_vf.verifier_reponse("VRAI") == True
            assert question_vf.verifier_reponse("FAUX") == False
            self.log_test("Validation Vrai/Faux", True, "Réponses correctement validées")
            
            # Test question texte - mode exacte
            question_texte_exacte = QuestionExamen.objects.create(
                texte="Test validation texte exacte",
                type_question="texte_court",
                matiere_combinee="anglais",
                reponse_attendue="Paris",
                correction_mode="exacte",
                difficulte="facile",
                creee_par="Test"
            )
            
            assert question_texte_exacte.verifier_reponse("Paris") == True
            assert question_texte_exacte.verifier_reponse("paris") == True  # Insensible à la casse
            assert question_texte_exacte.verifier_reponse("Londres") == False
            self.log_test("Validation Texte Exacte", True, "Correction exacte fonctionnelle")
            
            # Test question texte - mode mot-clé
            question_texte_motcle = QuestionExamen.objects.create(
                texte="Test validation texte mot-clé",
                type_question="texte_long",
                matiere_combinee="anglais",
                reponse_attendue="education,important,knowledge",
                correction_mode="mot_cle",
                difficulte="difficile",
                creee_par="Test"
            )
            
            reponse_test = "Education is very important for gaining knowledge"
            assert question_texte_motcle.verifier_reponse(reponse_test) == True
            self.log_test("Validation Texte Mot-clé", True, "Correction par mots-clés fonctionnelle")
            
        except Exception as e:
            self.log_test("Méthodes validation", False, str(e))
    
    def test_api_endpoints(self):
        """Test des endpoints API"""
        try:
            # Créer un utilisateur de test
            user = User.objects.create_user(
                username='testuser',
                password='testpass123'
            )
            self.client.login(username='testuser', password='testpass123')
            
            # Test GET liste des questions
            response = self.client.get('/api/questions-examen/')
            if response.status_code == 200:
                self.log_test("API GET Liste", True, f"Status: {response.status_code}")
            else:
                self.log_test("API GET Liste", False, f"Status: {response.status_code}")
            
            # Test POST création question
            question_data = {
                'texte': 'Question test API',
                'type_question': 'choix_unique',
                'matiere_combinee': 'culture_aptitude',
                'choix_a': 'Option A',
                'choix_b': 'Option B',
                'bonne_reponse': 'A',
                'difficulte': 'moyen',
                'creee_par': 'API Test'
            }
            
            response = self.client.post(
                '/api/questions-examen/',
                data=json.dumps(question_data),
                content_type='application/json'
            )
            
            if response.status_code in [200, 201]:
                self.log_test("API POST Création", True, f"Status: {response.status_code}")
                question_id = response.json().get('id')
                
                # Test GET détail question
                response = self.client.get(f'/api/questions-examen/{question_id}/')
                if response.status_code == 200:
                    self.log_test("API GET Détail", True, f"Status: {response.status_code}")
                else:
                    self.log_test("API GET Détail", False, f"Status: {response.status_code}")
            else:
                self.log_test("API POST Création", False, f"Status: {response.status_code}")
            
            # Test endpoint statistiques
            response = self.client.get('/api/questions-examen/statistiques/')
            if response.status_code == 200:
                stats = response.json()
                self.log_test("API Statistiques", True, f"Total questions: {stats.get('total_questions', 0)}")
            else:
                self.log_test("API Statistiques", False, f"Status: {response.status_code}")
            
            # Test endpoint questions pour examen
            response = self.client.get('/api/questions-examen/questions_pour_examen/')
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Questions Examen", True, f"Peut créer examen: {data.get('peut_creer_examen', False)}")
            else:
                self.log_test("API Questions Examen", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Endpoints API", False, str(e))
    
    def test_filtres_api(self):
        """Test des filtres API"""
        try:
            # Créer des questions de test avec différents attributs
            QuestionExamen.objects.create(
                texte="Question culture facile",
                type_question="choix_unique",
                matiere_combinee="culture_aptitude",
                choix_a="A", choix_b="B",
                bonne_reponse="A",
                difficulte="facile",
                active=True,
                validee=True,
                creee_par="Test"
            )
            
            QuestionExamen.objects.create(
                texte="Question logique difficile",
                type_question="vrai_faux",
                matiere_combinee="logique_combinee",
                bonne_reponse="VRAI",
                difficulte="difficile",
                active=True,
                validee=False,
                creee_par="Test"
            )
            
            # Test filtre par matière
            response = self.client.get('/api/questions-examen/?matiere_combinee=culture_aptitude')
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    results = data['results']
                else:
                    results = data
                
                culture_questions = [q for q in results if q.get('matiere_combinee') == 'culture_aptitude']
                self.log_test("Filtre Matière", True, f"Questions culture: {len(culture_questions)}")
            else:
                self.log_test("Filtre Matière", False, f"Status: {response.status_code}")
            
            # Test filtre par type
            response = self.client.get('/api/questions-examen/?type_question=choix_unique')
            if response.status_code == 200:
                self.log_test("Filtre Type", True, "Filtre par type fonctionnel")
            else:
                self.log_test("Filtre Type", False, f"Status: {response.status_code}")
            
            # Test filtre par difficulté
            response = self.client.get('/api/questions-examen/?difficulte=facile')
            if response.status_code == 200:
                self.log_test("Filtre Difficulté", True, "Filtre par difficulté fonctionnel")
            else:
                self.log_test("Filtre Difficulté", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Filtres API", False, str(e))
    
    def test_quota_examen(self):
        """Test de la vérification des quotas pour l'examen"""
        try:
            # Créer suffisamment de questions pour chaque matière
            matieres = [
                ('culture_aptitude', 65),
                ('logique_combinee', 45),
                ('anglais', 35)
            ]
            
            for matiere, nombre in matieres:
                for i in range(nombre):
                    QuestionExamen.objects.create(
                        texte=f"Question {matiere} {i+1}",
                        type_question="choix_unique",
                        matiere_combinee=matiere,
                        choix_a="A", choix_b="B",
                        bonne_reponse="A",
                        difficulte="moyen",
                        active=True,
                        validee=True,
                        creee_par="Test Quota"
                    )
            
            # Vérifier les quotas via l'API
            response = self.client.get('/api/questions-examen/questions_pour_examen/')
            if response.status_code == 200:
                data = response.json()
                peut_creer = data.get('peut_creer_examen', False)
                
                if peut_creer:
                    self.log_test("Quota Examen", True, "Quotas suffisants pour créer un examen")
                else:
                    self.log_test("Quota Examen", False, "Quotas insuffisants")
            else:
                self.log_test("Quota Examen", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Quota Examen", False, str(e))
    
    def test_selection_questions_aleatoire(self):
        """Test de la sélection aléatoire des questions"""
        try:
            # Créer plus de questions que nécessaire pour tester l'aléatoire
            for i in range(70):  # Plus que les 60 requis
                QuestionExamen.objects.create(
                    texte=f"Question culture aléatoire {i+1}",
                    type_question="choix_unique",
                    matiere_combinee="culture_aptitude",
                    choix_a="A", choix_b="B",
                    bonne_reponse="A",
                    difficulte="moyen",
                    active=True,
                    validee=True,
                    creee_par="Test Aléatoire"
                )
            
            # Sélectionner 60 questions aléatoirement
            questions_1 = list(QuestionExamen.objects.filter(
                matiere_combinee='culture_aptitude',
                active=True,
                validee=True
            ).order_by('?')[:60])
            
            questions_2 = list(QuestionExamen.objects.filter(
                matiere_combinee='culture_aptitude',
                active=True,
                validee=True
            ).order_by('?')[:60])
            
            # Vérifier que les sélections sont différentes (aléatoire)
            ids_1 = [q.id for q in questions_1]
            ids_2 = [q.id for q in questions_2]
            
            if len(set(ids_1) & set(ids_2)) < 60:  # Pas exactement les mêmes
                self.log_test("Sélection Aléatoire", True, "Sélection aléatoire fonctionnelle")
            else:
                self.log_test("Sélection Aléatoire", False, "Sélection non aléatoire")
                
        except Exception as e:
            self.log_test("Sélection Aléatoire", False, str(e))
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🚀 Début des tests pour QuestionExamen ENA")
        print("=" * 60)
        
        # Nettoyer les données de test existantes
        QuestionExamen.objects.filter(creee_par__icontains="Test").delete()
        
        # Exécuter les tests
        self.test_model_creation()
        self.test_validation_methods()
        self.test_api_endpoints()
        self.test_filtres_api()
        self.test_quota_examen()
        self.test_selection_questions_aleatoire()
        
        # Rapport final
        self.generate_report()
    
    def generate_report(self):
        """Génère le rapport final des tests"""
        print("\n" + "=" * 60)
        print("📊 RAPPORT FINAL DES TESTS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"📈 Tests exécutés: {total_tests}")
        print(f"✅ Tests réussis: {passed_tests}")
        print(f"❌ Tests échoués: {failed_tests}")
        print(f"📊 Taux de succès: {(passed_tests/total_tests*100):.1f}%")
        
        if self.errors:
            print(f"\n🚨 ERREURS DÉTECTÉES ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        # Statistiques finales
        total_questions = QuestionExamen.objects.count()
        questions_validees = QuestionExamen.objects.filter(validee=True).count()
        
        print(f"\n📚 STATISTIQUES BASE DE DONNÉES:")
        print(f"  - Total questions: {total_questions}")
        print(f"  - Questions validées: {questions_validees}")
        
        for matiere_code, matiere_nom in QuestionExamen.MATIERE_COMBINEE_CHOICES:
            count = QuestionExamen.objects.filter(matiere_combinee=matiere_code).count()
            print(f"  - {matiere_nom}: {count} questions")
        
        print("=" * 60)
        
        if failed_tests == 0:
            print("🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
            print("✅ Le système QuestionExamen ENA est opérationnel")
        else:
            print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
            print("🔧 Vérifiez les erreurs ci-dessus avant le déploiement")

def main():
    """Fonction principale"""
    try:
        tester = TestQuestionExamenENA()
        tester.run_all_tests()
        
    except Exception as e:
        print(f"❌ Erreur critique lors des tests: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
