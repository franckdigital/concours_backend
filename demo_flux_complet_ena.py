#!/usr/bin/env python3
"""
Démonstration complète du flux administrateur pour les questions d'examen national ENA
Ce script simule le workflow complet d'un administrateur
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import QuestionExamen, ExamenNational, SessionExamen, ParticipationExamen
from django.contrib.auth.models import User

class DemoFluxCompletENA:
    """Démonstration complète du flux administrateur ENA"""
    
    def __init__(self):
        self.demo_user = None
        self.questions_creees = []
        self.examen_cree = None
        
    def etape_1_preparation_donnees(self):
        """Étape 1: Préparer les données de démonstration"""
        print("=== ETAPE 1: PREPARATION DES DONNEES ===")
        
        # Créer un utilisateur de test
        self.demo_user, created = User.objects.get_or_create(
            username='admin_demo_ena',
            defaults={
                'email': 'admin@ena-demo.com',
                'first_name': 'Admin',
                'last_name': 'Demo ENA',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            self.demo_user.set_password('demo123')
            self.demo_user.save()
            print(f"Utilisateur admin créé: {self.demo_user.username}")
        else:
            print(f"Utilisateur admin existant: {self.demo_user.username}")
        
        print("Données de base préparées")
    
    def etape_2_creation_questions_manuelles(self):
        """Étape 2: Créer des questions manuellement pour compléter le stock"""
        print("\n=== ETAPE 2: CREATION QUESTIONS SUPPLEMENTAIRES ===")
        
        # Questions Culture générale + Aptitude verbale (pour atteindre 65 questions)
        questions_culture = [
            {
                'texte': 'Quel écrivain a écrit "Les Misérables" ?',
                'type_question': 'choix_unique',
                'matiere_combinee': 'culture_aptitude',
                'choix_a': 'Victor Hugo',
                'choix_b': 'Émile Zola',
                'choix_c': 'Gustave Flaubert',
                'choix_d': 'Honoré de Balzac',
                'bonne_reponse': 'A',
                'explication': 'Victor Hugo a écrit "Les Misérables" en 1862.',
                'difficulte': 'facile'
            },
            {
                'texte': 'La capitale de l\'Australie est-elle Sydney ?',
                'type_question': 'vrai_faux',
                'matiere_combinee': 'culture_aptitude',
                'bonne_reponse': 'FAUX',
                'explication': 'La capitale de l\'Australie est Canberra, pas Sydney.',
                'difficulte': 'moyen'
            },
            {
                'texte': 'Quel est le synonyme de "perspicace" ?',
                'type_question': 'choix_unique',
                'matiere_combinee': 'culture_aptitude',
                'choix_a': 'Clairvoyant',
                'choix_b': 'Naïf',
                'choix_c': 'Confus',
                'choix_d': 'Hésitant',
                'bonne_reponse': 'A',
                'explication': 'Perspicace signifie clairvoyant, qui voit avec pénétration.',
                'difficulte': 'moyen'
            }
        ]
        
        # Questions Logique + Raisonnement (pour atteindre 45 questions)
        questions_logique = [
            {
                'texte': 'Dans la suite 2, 4, 8, 16, quel est le nombre suivant ?',
                'type_question': 'choix_unique',
                'matiere_combinee': 'logique_combinee',
                'choix_a': '24',
                'choix_b': '32',
                'choix_c': '20',
                'choix_d': '18',
                'bonne_reponse': 'B',
                'explication': 'Chaque terme est multiplié par 2: 16 × 2 = 32.',
                'difficulte': 'facile'
            },
            {
                'texte': 'Si tous les chats sont des mammifères et tous les mammifères sont des animaux, alors tous les chats sont des animaux.',
                'type_question': 'vrai_faux',
                'matiere_combinee': 'logique_combinee',
                'bonne_reponse': 'VRAI',
                'explication': 'C\'est un syllogisme logique valide.',
                'difficulte': 'facile'
            },
            {
                'texte': 'Livre est à bibliothèque comme voiture est à :',
                'type_question': 'choix_unique',
                'matiere_combinee': 'logique_combinee',
                'choix_a': 'Route',
                'choix_b': 'Garage',
                'choix_c': 'Essence',
                'choix_d': 'Conducteur',
                'bonne_reponse': 'B',
                'explication': 'Analogie de lieu: les livres sont dans une bibliothèque, les voitures dans un garage.',
                'difficulte': 'moyen'
            }
        ]
        
        # Questions Anglais (pour atteindre 35 questions)
        questions_anglais = [
            {
                'texte': 'Choose the correct form: "She _____ to school every day."',
                'type_question': 'choix_unique',
                'matiere_combinee': 'anglais',
                'choix_a': 'go',
                'choix_b': 'goes',
                'choix_c': 'going',
                'choix_d': 'gone',
                'bonne_reponse': 'B',
                'explication': 'Présent simple 3ème personne: "She goes".',
                'difficulte': 'facile'
            },
            {
                'texte': 'What is the past tense of "buy"?',
                'type_question': 'texte_court',
                'matiere_combinee': 'anglais',
                'reponse_attendue': 'bought',
                'correction_mode': 'exacte',
                'explication': 'Le passé de "buy" est "bought".',
                'difficulte': 'facile'
            },
            {
                'texte': 'The weather is nice today.',
                'type_question': 'vrai_faux',
                'matiere_combinee': 'anglais',
                'bonne_reponse': 'VRAI',
                'explication': 'Cette phrase est grammaticalement correcte.',
                'difficulte': 'facile'
            }
        ]
        
        # Créer toutes les questions
        toutes_questions = questions_culture + questions_logique + questions_anglais
        
        for question_data in toutes_questions:
            question = QuestionExamen.objects.create(
                **question_data,
                active=True,
                validee=True,
                creee_par='Demo Admin',
                temps_limite_secondes=120
            )
            self.questions_creees.append(question)
            print(f"Question créée: {question.code_question}")
        
        print(f"Total questions créées: {len(self.questions_creees)}")
    
    def etape_3_verification_stock(self):
        """Étape 3: Vérifier le stock de questions"""
        print("\n=== ETAPE 3: VERIFICATION DU STOCK ===")
        
        quotas_requis = {
            'culture_aptitude': 60,
            'logique_combinee': 40,
            'anglais': 30
        }
        
        stock_global_ok = True
        
        for matiere, quota in quotas_requis.items():
            disponibles = QuestionExamen.objects.filter(
                matiere_combinee=matiere,
                active=True,
                validee=True
            ).count()
            
            suffisant = disponibles >= quota
            if not suffisant:
                stock_global_ok = False
            
            matiere_nom = dict(QuestionExamen.MATIERE_COMBINEE_CHOICES)[matiere]
            status = "OK" if suffisant else "INSUFFISANT"
            print(f"  - {matiere_nom}: {disponibles}/{quota} ({status})")
        
        print(f"\nStock global: {'SUFFISANT' if stock_global_ok else 'INSUFFISANT'}")
        
        if not stock_global_ok:
            print("ATTENTION: Il faut créer plus de questions pour avoir un stock suffisant!")
            return False
        
        return True
    
    def etape_4_creation_examen_national(self):
        """Étape 4: Créer un examen national"""
        print("\n=== ETAPE 4: CREATION EXAMEN NATIONAL ===")
        
        # Sélectionner les questions pour l'examen
        questions_culture = list(QuestionExamen.objects.filter(
            matiere_combinee='culture_aptitude',
            active=True,
            validee=True
        ).order_by('?')[:60])
        
        questions_logique = list(QuestionExamen.objects.filter(
            matiere_combinee='logique_combinee',
            active=True,
            validee=True
        ).order_by('?')[:40])
        
        questions_anglais = list(QuestionExamen.objects.filter(
            matiere_combinee='anglais',
            active=True,
            validee=True
        ).order_by('?')[:30])
        
        # Créer l'examen national
        maintenant = datetime.now()
        debut_examen = maintenant.replace(hour=9, minute=0, second=0, microsecond=0)
        fin_examen = debut_examen + timedelta(days=30)
        
        self.examen_cree = ExamenNational.objects.create(
            date_examen=debut_examen,
            date_creation=maintenant,
            temps_total_en_secondes=10800,  # 3 heures
            
            # Durées par matière (60 minutes chacune)
            temps_culture_aptitude=60,
            temps_logique_combinee=60,
            temps_anglais=60,
            
            # Débuts des sections
            debut_culture_aptitude=0,
            debut_logique_combinee=60,
            debut_anglais=120,
            
            terminee=False,
            utilisateur=self.demo_user
        )
        
        # Associer les questions
        toutes_questions = questions_culture + questions_logique + questions_anglais
        self.examen_cree.questions.set(toutes_questions)
        
        print(f"Examen national créé:")
        print(f"  - ID: {self.examen_cree.id}")
        print(f"  - Date: {self.examen_cree.date_examen}")
        print(f"  - Questions: {len(toutes_questions)}")
        print(f"    * Culture/Aptitude: {len(questions_culture)}")
        print(f"    * Logique: {len(questions_logique)}")
        print(f"    * Anglais: {len(questions_anglais)}")
        
        return self.examen_cree
    
    def etape_5_simulation_participation(self):
        """Étape 5: Simuler une participation d'examen"""
        print("\n=== ETAPE 5: SIMULATION PARTICIPATION ===")
        
        if not self.examen_cree:
            print("Erreur: Aucun examen créé")
            return None
        
        # Créer un participant de test
        participant, created = User.objects.get_or_create(
            username='candidat_demo',
            defaults={
                'email': 'candidat@demo.com',
                'first_name': 'Candidat',
                'last_name': 'Demo'
            }
        )
        
        # Créer une participation
        participation = ParticipationExamen.objects.create(
            examen=self.examen_cree,
            utilisateur=participant,
            score=0,
            temps_total=7200,  # 2 heures
            terminee=True,
            corrigee=False
        )
        
        # Simuler des réponses aléatoirement correctes (70% de bonnes réponses)
        questions_examen = list(self.examen_cree.questions.all())
        reponses_simulees = {}
        
        for question in questions_examen:
            # 70% de chance de donner la bonne réponse
            if random.random() < 0.7:
                if question.type_question in ['choix_unique', 'choix_multiple', 'vrai_faux']:
                    reponse = question.bonne_reponse
                else:
                    reponse = question.reponse_attendue
            else:
                # Mauvaise réponse
                if question.type_question == 'choix_unique':
                    mauvaises = ['A', 'B', 'C', 'D']
                    if question.bonne_reponse in mauvaises:
                        mauvaises.remove(question.bonne_reponse)
                    reponse = random.choice(mauvaises)
                elif question.type_question == 'vrai_faux':
                    reponse = 'FAUX' if question.bonne_reponse == 'VRAI' else 'VRAI'
                else:
                    reponse = 'mauvaise réponse'
            
            reponses_simulees[str(question.id)] = reponse
        
        participation.reponses_detaillees = reponses_simulees
        participation.save()
        
        print(f"Participation simulée:")
        print(f"  - Participant: {participant.username}")
        print(f"  - Questions répondues: {len(reponses_simulees)}")
        print(f"  - Temps total: {participation.temps_total} secondes")
        
        return participation
    
    def etape_6_correction_automatique(self, participation):
        """Étape 6: Correction automatique de la participation"""
        print("\n=== ETAPE 6: CORRECTION AUTOMATIQUE ===")
        
        if not participation:
            print("Erreur: Aucune participation à corriger")
            return
        
        score_total = 0
        questions_correctes = 0
        details_correction = {}
        
        reponses = participation.reponses_detaillees or {}
        
        for question_id, reponse_utilisateur in reponses.items():
            try:
                question = QuestionExamen.objects.get(id=question_id)
                
                # Utiliser la méthode de vérification de QuestionExamen
                est_correcte = question.verifier_reponse(reponse_utilisateur)
                
                if est_correcte:
                    questions_correctes += 1
                    score_total += 1
                
                details_correction[question_id] = {
                    'question': question.texte[:50] + "...",
                    'reponse_utilisateur': reponse_utilisateur,
                    'bonne_reponse': question.bonne_reponse or question.reponse_attendue,
                    'correcte': est_correcte,
                    'matiere': question.matiere_combinee
                }
                
                # Incrémenter le compteur d'utilisation
                question.nombre_utilisations += 1
                question.save()
                
            except QuestionExamen.DoesNotExist:
                continue
        
        # Calculer le score final
        total_questions = len(reponses)
        score_pourcentage = (score_total / total_questions * 100) if total_questions > 0 else 0
        
        # Mettre à jour la participation
        participation.score = score_pourcentage
        participation.questions_correctes = questions_correctes
        participation.total_questions = total_questions
        participation.details_correction = details_correction
        participation.corrigee = True
        participation.save()
        
        print(f"Correction terminée:")
        print(f"  - Score final: {score_pourcentage:.1f}%")
        print(f"  - Questions correctes: {questions_correctes}/{total_questions}")
        
        # Répartition par matière
        print(f"\nRépartition par matière:")
        stats_matieres = {}
        for detail in details_correction.values():
            matiere = detail['matiere']
            if matiere not in stats_matieres:
                stats_matieres[matiere] = {'correctes': 0, 'total': 0}
            stats_matieres[matiere]['total'] += 1
            if detail['correcte']:
                stats_matieres[matiere]['correctes'] += 1
        
        for matiere, stats in stats_matieres.items():
            pourcentage = (stats['correctes'] / stats['total'] * 100) if stats['total'] > 0 else 0
            matiere_nom = dict(QuestionExamen.MATIERE_COMBINEE_CHOICES)[matiere]
            print(f"  - {matiere_nom}: {stats['correctes']}/{stats['total']} ({pourcentage:.1f}%)")
        
        return participation
    
    def etape_7_statistiques_finales(self):
        """Étape 7: Générer les statistiques finales"""
        print("\n=== ETAPE 7: STATISTIQUES FINALES ===")
        
        # Statistiques des questions
        total_questions = QuestionExamen.objects.count()
        questions_actives = QuestionExamen.objects.filter(active=True).count()
        questions_validees = QuestionExamen.objects.filter(validee=True).count()
        questions_utilisees = QuestionExamen.objects.filter(nombre_utilisations__gt=0).count()
        
        print(f"Questions dans la base:")
        print(f"  - Total: {total_questions}")
        print(f"  - Actives: {questions_actives}")
        print(f"  - Validées: {questions_validees}")
        print(f"  - Utilisées: {questions_utilisees}")
        
        # Statistiques par matière
        print(f"\nRépartition par matière:")
        for matiere_code, matiere_nom in QuestionExamen.MATIERE_COMBINEE_CHOICES:
            count = QuestionExamen.objects.filter(matiere_combinee=matiere_code).count()
            utilisees = QuestionExamen.objects.filter(
                matiere_combinee=matiere_code,
                nombre_utilisations__gt=0
            ).count()
            print(f"  - {matiere_nom}: {count} questions ({utilisees} utilisées)")
        
        # Statistiques des examens
        total_examens = ExamenNational.objects.count()
        examens_actifs = ExamenNational.objects.filter(terminee=False).count()
        
        print(f"\nExamens nationaux:")
        print(f"  - Total: {total_examens}")
        print(f"  - En cours: {examens_actifs}")
        
        # Statistiques des participations
        total_participations = ParticipationExamen.objects.count()
        participations_corrigees = ParticipationExamen.objects.filter(corrigee=True).count()
        
        if participations_corrigees > 0:
            score_moyen = ParticipationExamen.objects.filter(
                corrigee=True
            ).aggregate(
                moyenne=django.db.models.Avg('score')
            )['moyenne']
            
            print(f"\nParticipations:")
            print(f"  - Total: {total_participations}")
            print(f"  - Corrigées: {participations_corrigees}")
            print(f"  - Score moyen: {score_moyen:.1f}%")
        
    def nettoyer_donnees_demo(self):
        """Nettoyer les données de démonstration"""
        print("\n=== NETTOYAGE DES DONNEES DEMO ===")
        
        # Supprimer les participations de demo
        ParticipationExamen.objects.filter(
            utilisateur__username__in=['candidat_demo']
        ).delete()
        
        # Supprimer les examens de demo
        if self.examen_cree:
            self.examen_cree.delete()
        
        # Supprimer les questions créées pour la demo
        QuestionExamen.objects.filter(creee_par='Demo Admin').delete()
        
        # Supprimer les utilisateurs de demo
        User.objects.filter(
            username__in=['admin_demo_ena', 'candidat_demo']
        ).delete()
        
        print("Données de démonstration nettoyées")
    
    def executer_demo_complete(self):
        """Exécuter la démonstration complète"""
        print("=" * 80)
        print("DEMONSTRATION COMPLETE DU FLUX ADMINISTRATEUR ENA")
        print("=" * 80)
        
        try:
            # Exécuter toutes les étapes
            self.etape_1_preparation_donnees()
            self.etape_2_creation_questions_manuelles()
            
            if not self.etape_3_verification_stock():
                print("\nDEMO INTERROMPUE: Stock insuffisant")
                return False
            
            examen = self.etape_4_creation_examen_national()
            participation = self.etape_5_simulation_participation()
            self.etape_6_correction_automatique(participation)
            self.etape_7_statistiques_finales()
            
            print("\n" + "=" * 80)
            print("DEMONSTRATION TERMINEE AVEC SUCCES!")
            print("=" * 80)
            print("\nRESUME:")
            print("✅ Questions créées et validées")
            print("✅ Stock vérifié et suffisant")
            print("✅ Examen national généré")
            print("✅ Participation simulée")
            print("✅ Correction automatique fonctionnelle")
            print("✅ Statistiques générées")
            print("\n🎉 LE SYSTEME QUESTIONEXAMEN ENA EST ENTIEREMENT OPERATIONNEL!")
            
            return True
            
        except Exception as e:
            print(f"\nERREUR lors de la démonstration: {e}")
            return False
        
        finally:
            # Nettoyer les données de demo
            self.nettoyer_donnees_demo()

def main():
    """Fonction principale"""
    demo = DemoFluxCompletENA()
    
    try:
        succes = demo.executer_demo_complete()
        return 0 if succes else 1
        
    except Exception as e:
        print(f"ERREUR CRITIQUE: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
