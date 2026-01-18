from django.core.management.base import BaseCommand
from prepaconcours.models import Plan


class Command(BaseCommand):
    help = 'Initialise les 4 plans d\'abonnement par défaut'

    def handle(self, *args, **options):
        plans_data = [
            {
                'code': 'test',
                'nom': 'Plan Test',
                'description': 'Essayez gratuitement pendant 7 jours avec accès complet',
                'prix': 0,
                'duree': '7_jours',
                'questions_par_jour': 0,  # Illimité pour test
                'examens_blancs_par_mois': 5,
                'acces_ena': True,
                'acces_fonction_publique': True,  # Accès FP activé pour test
                'acces_tous_concours': True,
                'mode_classique': True,
                'mode_chronometre': True,
                'statistiques_basiques': True,
                'statistiques_avancees': True,
                'corrections_detaillees': True,
                'support_email': False,
                'support_prioritaire': False,
                'support_vip': False,
                'export_pdf': False,
                'est_actif': True,
                'est_populaire': False,
                'ordre_affichage': 1,
            },
            {
                'code': 'basique',
                'nom': 'Plan Basique',
                'description': 'Accès aux quiz ENA et Fonction Publique avec statistiques de base',
                'prix': 2500,
                'duree': '1_mois',
                'questions_par_jour': 200,
                'examens_blancs_par_mois': 2,
                'acces_ena': True,
                'acces_fonction_publique': True,
                'acces_tous_concours': False,
                'mode_classique': True,
                'mode_chronometre': True,
                'statistiques_basiques': True,
                'statistiques_avancees': False,
                'corrections_detaillees': False,
                'support_email': True,
                'support_prioritaire': False,
                'support_vip': False,
                'export_pdf': False,
                'est_actif': True,
                'est_populaire': False,
                'ordre_affichage': 2,
            },
            {
                'code': 'premium',
                'nom': 'Plan Premium',
                'description': 'Accès illimité à tous les concours avec statistiques avancées et support prioritaire',
                'prix': 5000,
                'duree': '1_mois',
                'questions_par_jour': 0,  # Illimité
                'examens_blancs_par_mois': 0,  # Illimité
                'acces_ena': True,
                'acces_fonction_publique': True,
                'acces_tous_concours': True,
                'mode_classique': True,
                'mode_chronometre': True,
                'statistiques_basiques': True,
                'statistiques_avancees': True,
                'corrections_detaillees': True,
                'support_email': True,
                'support_prioritaire': True,
                'support_vip': False,
                'export_pdf': False,
                'est_actif': True,
                'est_populaire': True,  # Badge "Populaire"
                'ordre_affichage': 3,
            },
            {
                'code': 'annuel',
                'nom': 'Plan Annuel',
                'description': 'Meilleure valeur ! Accès illimité pendant 1 an avec toutes les fonctionnalités VIP',
                'prix': 100000,
                'duree': '12_mois',
                'questions_par_jour': 0,  # Illimité
                'examens_blancs_par_mois': 0,  # Illimité
                'acces_ena': True,
                'acces_fonction_publique': True,
                'acces_tous_concours': True,
                'mode_classique': True,
                'mode_chronometre': True,
                'statistiques_basiques': True,
                'statistiques_avancees': True,
                'corrections_detaillees': True,
                'support_email': True,
                'support_prioritaire': True,
                'support_vip': True,
                'export_pdf': True,
                'est_actif': True,
                'est_populaire': False,
                'ordre_affichage': 4,
            },
        ]

        created_count = 0
        updated_count = 0

        for plan_data in plans_data:
            plan, created = Plan.objects.update_or_create(
                code=plan_data['code'],
                defaults=plan_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Plan créé: {plan.nom}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'🔄 Plan mis à jour: {plan.nom}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Terminé ! {created_count} plans créés, {updated_count} plans mis à jour.'))
        self.stdout.write('')
        self.stdout.write('📋 Récapitulatif des plans:')
        for plan in Plan.objects.all().order_by('ordre_affichage'):
            questions = 'Illimité' if plan.questions_par_jour == 0 else f'{plan.questions_par_jour}/jour'
            self.stdout.write(f'   - {plan.nom}: {plan.prix} FCFA ({plan.get_duree_display()}) - {questions}')
