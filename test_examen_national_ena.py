#!/usr/bin/env python3
"""
Script de test pour les fonctionnalités d'Examen National ENA
Teste toutes les fonctionnalités implémentées selon les spécifications :
- Accès conditionné (score >= 50% à l'évaluation)
- 3 matières combinées (Culture générale + Aptitude verbale, Logique d'organisation + Logique numérique, Anglais)
- Examen une fois par mois
- Classement national comparatif
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prepaconcours.settings')
django.setup()

from prepaconcours.models import (
    Utilisateur, Matiere, Question, Evaluation, ExamenNational,
    SessionExamen, ParticipationExamen
)
from django.contrib.auth import authenticate
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

class TestExamenNationalENA:
    def __init__(self):
        self.client = APIClient()
        self.base_url = 'http://localhost:8000/api'
        self.user_token = None
        self.user = None
        
    def setup_test_data(self):
        """Crée les données de test nécessaires"""
        print("🔧 Configuration des données de test...")
        
        # Créer un utilisateur de test
        self.user, created = Utilisateur.objects.get_or_create(
            email='test_examen@ena.com',
            defaults={
                'nom': 'Test',
                'prenom': 'Examen',
                'mot_de_passe': 'testpass123',
                'choix_concours': 'ENA'
            }
        )
        
        if created:
            self.user.set_password('testpass123')
            self.user.save()
        
        # Créer les matières ENA du premier tour
        matieres_data = [
            {'nom': 'Culture générale', 'choix_concours': 'ENA', 'tour_ena': 'premier_tour'},
            {'nom': 'Aptitude verbale', 'choix_concours': 'ENA', 'tour_ena': 'premier_tour'},
            {'nom': 'Logique d\'organisation', 'choix_concours': 'ENA', 'tour_ena': 'premier_tour'},
            {'nom': 'Logique numérique', 'choix_concours': 'ENA', 'tour_ena': 'premier_tour'},
            {'nom': 'Anglais', 'choix_concours': 'ENA', 'tour_ena': 'premier_tour'},
        ]
        
        for matiere_data in matieres_data:
            matiere, created = Matiere.objects.get_or_create(
                nom=matiere_data['nom'],
                choix_concours=matiere_data['choix_concours'],
                defaults=matiere_data
            )
            
            # Créer des questions de test pour chaque matière
            if created or Question.objects.filter(matiere=matiere).count() < 50:
                for i in range(50):
                    Question.objects.get_or_create(
                        matiere=matiere,
                        texte=f'Question {i+1} de {matiere.nom}',
                        defaults={
                            'type_question': 'qcm',
                            'bonne_reponse': 'A',
                            'choix_a': 'Réponse A (correcte)',
                            'choix_b': 'Réponse B',
                            'choix_c': 'Réponse C',
                            'choix_d': 'Réponse D',
                        }
                    )
        
        # Créer une évaluation avec un score >= 50% pour permettre l'accès
        evaluation, created = Evaluation.objects.get_or_create(
            utilisateur=self.user,
            defaults={
                'score': 75.0,  # Score suffisant pour accéder à l'examen national
                'temps_total_en_secondes': 3600,
                'terminee': True
            }
        )
        
        print("✅ Données de test configurées avec succès")
        
    def authenticate(self):
        """Authentifie l'utilisateur et récupère le token"""
        print("🔐 Authentification...")
        
        response = self.client.post(f'{self.base_url}/token/', {
            'email': 'test_examen@ena.com',
            'password': 'testpass123'
        })
        
        if response.status_code == 200:
            self.user_token = response.data['access']
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
            print("✅ Authentification réussie")
            return True
        else:
            print(f"❌ Erreur d'authentification: {response.data}")
            return False
    
    def test_access_conditions(self):
        """Teste les conditions d'accès à l'examen national (score >= 50%)"""
        print("\n📋 Test des conditions d'accès à l'examen national...")
        
        response = self.client.get(f'{self.base_url}/examens-nationaux/can_access/')
        
        if response.status_code == 200:
            data = response.data
            print(f"✅ Vérification d'accès: {data}")
            
            if data.get('can_access'):
                print(f"✅ Accès autorisé avec un score de {data.get('score_evaluation')}%")
                return True
            else:
                print(f"❌ Accès refusé: {data.get('message')}")
                return False
        else:
            print(f"❌ Erreur lors de la vérification d'accès: {response.data}")
            return False
    
    def test_combined_subjects(self):
        """Teste la récupération des 3 matières combinées"""
        print("\n📚 Test des matières combinées pour l'examen national...")
        
        response = self.client.get(f'{self.base_url}/examens-nationaux/matieres_examen/')
        
        if response.status_code == 200:
            data = response.data
            print(f"✅ Matières récupérées: {data}")
            
            matieres = data.get('matieres_examen', [])
            if len(matieres) == 3:
                print("✅ 3 matières combinées trouvées:")
                for matiere in matieres:
                    print(f"  - {matiere['nom']}: {len(matiere['matieres_incluses'])} matière(s)")
                return True
            else:
                print(f"❌ Nombre incorrect de matières: {len(matieres)} au lieu de 3")
                return False
        else:
            print(f"❌ Erreur lors de la récupération des matières: {response.data}")
            return False
    
    def test_create_exam_session(self):
        """Teste la création d'une session d'examen national"""
        print("\n🎯 Test de création d'une session d'examen national...")
        
        response = self.client.post(f'{self.base_url}/examens-nationaux/creer_session_examen/')
        
        if response.status_code == 200:
            data = response.data
            print(f"✅ Session d'examen créée: {data}")
            
            if data.get('success'):
                print(f"✅ Examen créé avec {data.get('total_questions')} questions")
                print(f"✅ Répartition: {data.get('repartition')}")
                return data.get('examen_id')
            else:
                print(f"❌ Échec de création: {data}")
                return None
        else:
            print(f"❌ Erreur lors de la création: {response.data}")
            return None
    
    def test_finalize_exam(self, examen_id):
        """Teste la finalisation d'un examen avec calcul du score et gestion du temps par matière"""
        print(f"\n🏁 Test de finalisation de l'examen {examen_id}...")
        
        # Simuler des réponses (50% de bonnes réponses)
        reponses_test = []
        for i in range(130):  # Total de 130 questions
            reponses_test.append({
                'question_id': i + 1,
                'reponse': 'A' if i % 2 == 0 else 'B'  # 50% de bonnes réponses
            })
        
        # Simuler le temps passé par matière (respectant les contraintes de 60min par matière)
        temps_par_matiere = {
            'culture_aptitude': 3300,    # 55 minutes (sous la limite de 60min)
            'logique_combinee': 3000,    # 50 minutes (sous la limite de 60min)
            'anglais': 2700              # 45 minutes (sous la limite de 60min)
        }
        temps_total = sum(temps_par_matiere.values())  # 150 minutes total (sous la limite de 180min)
        
        response = self.client.post(
            f'{self.base_url}/examens-nationaux/{examen_id}/finaliser_examen/',
            {
                'reponses': reponses_test,
                'temps_total_en_secondes': temps_total,
                'temps_par_matiere': temps_par_matiere
            },
            format='json'
        )
        
        if response.status_code == 200:
            data = response.data
            print(f"✅ Examen finalisé: {data}")
            
            if data.get('success'):
                print(f"✅ Score obtenu: {data.get('score')}%")
                print(f"✅ Bonnes réponses: {data.get('bonnes_reponses')}/{data.get('total_questions')}")
                print(f"✅ Temps total: {data.get('temps_total_minutes')}min")
                print(f"✅ Temps par matière: {data.get('temps_par_matiere')}")
                print(f"✅ Violations de temps: {data.get('violations_temps', 'Aucune')}")
                print(f"✅ Rang national: {data.get('rang_national')}")
                return True
            else:
                print(f"❌ Échec de finalisation: {data}")
                return False
        else:
            print(f"❌ Erreur lors de la finalisation: {response.data}")
            return False
    
    def test_time_management(self, examen_id):
        """Teste la gestion du temps par matière"""
        print(f"\n⏱️ Test de gestion du temps pour l'examen {examen_id}...")
        
        # Test 1: Récupérer le temps restant
        response = self.client.get(f'{self.base_url}/examens-nationaux/{examen_id}/temps_restant/')
        
        if response.status_code == 200:
            data = response.data
            print(f"✅ Temps restant récupéré: {data.get('temps_restant_total_minutes')}min")
            print(f"✅ Répartition par matière: {data.get('repartition_temps')}")
        else:
            print(f"❌ Erreur lors de la récupération du temps: {response.data}")
            return False
        
        # Test 2: Mettre à jour le temps pour une matière
        response = self.client.post(
            f'{self.base_url}/examens-nationaux/{examen_id}/mettre_a_jour_temps/',
            {
                'matiere_code': 'culture_aptitude',
                'temps_passe_secondes': 1800  # 30 minutes
            },
            format='json'
        )
        
        if response.status_code == 200:
            data = response.data
            print(f"✅ Temps mis à jour pour Culture générale + Aptitude verbale: {data.get('temps_passe_minutes')}min")
            print(f"✅ Temps restant pour cette matière: {data.get('temps_restant_matiere_minutes')}min")
            return True
        else:
            print(f"❌ Erreur lors de la mise à jour du temps: {response.data}")
            return False
    
    def test_national_ranking(self):
        """Teste la récupération du classement national"""
        print("\n🏆 Test du classement national...")
        
        response = self.client.get(f'{self.base_url}/examens-nationaux/classement/')
        
        if response.status_code == 200:
            data = response.data
            print(f"✅ Classement récupéré: {len(data.get('classement', []))} participants")
            
            if data.get('user_position'):
                print(f"✅ Position de l'utilisateur: {data['user_position']}")
            
            print(f"✅ Total des participants: {data.get('total_participants')}")
            return True
        else:
            print(f"❌ Erreur lors de la récupération du classement: {response.data}")
            return False
    
    def test_monthly_statistics(self):
        """Teste les statistiques mensuelles"""
        print("\n📊 Test des statistiques mensuelles...")
        
        response = self.client.get(f'{self.base_url}/examens-nationaux/statistiques_mensuelles/')
        
        if response.status_code == 200:
            data = response.data
            print(f"✅ Statistiques mensuelles: {data}")
            
            if data.get('total_participants') > 0:
                print(f"✅ {data['total_participants']} participants ce mois-ci")
                print(f"✅ Score moyen: {data.get('score_moyen')}%")
                print(f"✅ Meilleur score: {data.get('meilleur_score')}%")
            
            return True
        else:
            print(f"❌ Erreur lors de la récupération des statistiques: {response.data}")
            return False
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🚀 Démarrage des tests d'Examen National ENA")
        print("=" * 60)
        
        # Configuration
        self.setup_test_data()
        
        if not self.authenticate():
            print("❌ Échec de l'authentification, arrêt des tests")
            return False
        
        # Tests des fonctionnalités
        tests_results = []
        
        # 1. Test des conditions d'accès
        tests_results.append(self.test_access_conditions())
        
        # 2. Test des matières combinées
        tests_results.append(self.test_combined_subjects())
        
        # 3. Test de création d'examen
        examen_id = self.test_create_exam_session()
        tests_results.append(examen_id is not None)
        
        # 4. Test de gestion du temps (si l'examen a été créé)
        if examen_id:
            tests_results.append(self.test_time_management(examen_id))
        
        # 5. Test de finalisation (si l'examen a été créé)
        if examen_id:
            tests_results.append(self.test_finalize_exam(examen_id))
        
        # 6. Test du classement national
        tests_results.append(self.test_national_ranking())
        
        # 7. Test des statistiques mensuelles
        tests_results.append(self.test_monthly_statistics())
        
        # Résultats finaux
        print("\n" + "=" * 60)
        print("📊 RÉSULTATS DES TESTS")
        print("=" * 60)
        
        passed_tests = sum(tests_results)
        total_tests = len(tests_results)
        
        print(f"✅ Tests réussis: {passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print("🎉 TOUS LES TESTS SONT PASSÉS!")
            print("✅ Les fonctionnalités d'Examen National ENA sont opérationnelles")
        else:
            print("⚠️  Certains tests ont échoué")
            print("❌ Vérifiez les logs ci-dessus pour plus de détails")
        
        return passed_tests == total_tests

if __name__ == '__main__':
    tester = TestExamenNationalENA()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Le système d'Examen National ENA est prêt pour la production!")
    else:
        print("\n🔧 Des corrections sont nécessaires avant la mise en production")
    
    sys.exit(0 if success else 1)
