from django.db import migrations


def create_default_configurations(apps, schema_editor):
    """Créer les 3 configurations de composition par défaut"""
    ConfigurationComposition = apps.get_model('prepaconcours', 'ConfigurationComposition')
    
    # Configuration 1: Culture générale + Aptitude verbale
    ConfigurationComposition.objects.get_or_create(
        matiere_combinee='culture_aptitude',
        defaults={
            'titre_principal': 'FEUILLE DE COMPOSITION N°1',
            'sous_titre_1': "CONCOURS DIRECT D'ENTRÉE EN 2024",
            'sous_titre_2': "AU CYCLE MOYEN DE L'ENA",
            'nom_affichage': 'Culture générale + Aptitude verbale',
            'duree_minutes': 90,
            'nombre_questions': 40,
            'instruction_principale': 'Choisissez la bonne réponse parmi les quatre propositions.',
            'bareme_bonne_reponse': 0.5,
            'bareme_mauvaise_reponse': -0.25,
            'bareme_absence_reponse': 0,
            'couleur_primaire': '#667eea',
            'couleur_secondaire': '#764ba2',
            'message_intro': 'Cliquez sur "Commencer" pour démarrer le timer et commencer la composition.',
            'bouton_commencer': 'Commencer la composition',
            'bouton_terminer': 'Terminer la composition',
            'pied_de_page': 'Épreuve 1/3 - Culture générale + Aptitude verbale',
            'est_actif': True,
        }
    )
    
    # Configuration 2: Anglais
    ConfigurationComposition.objects.get_or_create(
        matiere_combinee='anglais',
        defaults={
            'titre_principal': 'FEUILLE DE COMPOSITION N°2',
            'sous_titre_1': "CONCOURS DIRECT D'ENTRÉE EN 2024",
            'sous_titre_2': "AU CYCLE MOYEN DE L'ENA",
            'nom_affichage': 'Anglais',
            'duree_minutes': 45,
            'nombre_questions': 20,
            'instruction_principale': 'Choose the correct answer among the four options.',
            'bareme_bonne_reponse': 0.5,
            'bareme_mauvaise_reponse': -0.25,
            'bareme_absence_reponse': 0,
            'couleur_primaire': '#74b9ff',
            'couleur_secondaire': '#0984e3',
            'message_intro': 'Click "Start" to begin the timer and start the English test.',
            'bouton_commencer': 'Start the test',
            'bouton_terminer': 'Finish the test',
            'pied_de_page': 'Épreuve 2/3 - Anglais / English Test',
            'est_actif': True,
        }
    )
    
    # Configuration 3: Logique d'organisation + Logique numérique
    ConfigurationComposition.objects.get_or_create(
        matiere_combinee='logique_combinee',
        defaults={
            'titre_principal': 'FEUILLE DE COMPOSITION N°3',
            'sous_titre_1': "CONCOURS DIRECT D'ENTRÉE EN 2024",
            'sous_titre_2': "AU CYCLE MOYEN DE L'ENA",
            'nom_affichage': "Logique d'organisation + Logique numérique",
            'duree_minutes': 90,
            'nombre_questions': 40,
            'instruction_principale': 'Choisissez la bonne réponse parmi les quatre propositions.',
            'bareme_bonne_reponse': 0.5,
            'bareme_mauvaise_reponse': -0.25,
            'bareme_absence_reponse': 0,
            'couleur_primaire': '#fdcb6e',
            'couleur_secondaire': '#e17055',
            'message_intro': 'Cliquez sur "Commencer" pour démarrer le timer et commencer la composition.',
            'bouton_commencer': 'Commencer la composition',
            'bouton_terminer': 'Terminer la composition',
            'pied_de_page': "Épreuve 3/3 - Logique d'organisation + Logique numérique",
            'est_actif': True,
        }
    )


def reverse_migration(apps, schema_editor):
    """Supprimer les configurations par défaut (réversible)"""
    ConfigurationComposition = apps.get_model('prepaconcours', 'ConfigurationComposition')
    ConfigurationComposition.objects.filter(
        matiere_combinee__in=['culture_aptitude', 'anglais', 'logique_combinee']
    ).delete()


class Migration(migrations.Migration):
    
    dependencies = [
        ('prepaconcours', '0033_migrate_evaluation_questions'),  # Dépend de la dernière migration
    ]
    
    operations = [
        migrations.RunPython(create_default_configurations, reverse_migration),
    ]
