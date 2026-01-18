# Generated manually - Data migration to mark existing evaluation questions

from django.db import migrations


def mark_evaluation_questions(apps, schema_editor):
    """
    Marque les questions importées via l'import d'évaluation comme type_source='evaluation'.
    Identifie les questions d'évaluation par:
    1. Leur association avec une leçon de type 'evaluation'
    2. Ou leur import via 'questions_evaluation_ena'
    """
    Question = apps.get_model('prepaconcours', 'Question')
    Lecon = apps.get_model('prepaconcours', 'Lecon')
    ImportExcel = apps.get_model('prepaconcours', 'ImportExcel')
    
    # Méthode 1: Marquer les questions dont la leçon est de type 'evaluation'
    evaluation_lecons = Lecon.objects.filter(type_lecon='evaluation').values_list('id', flat=True)
    updated_by_lecon = Question.objects.filter(lecon_id__in=evaluation_lecons).update(type_source='evaluation')
    
    print(f"Questions marquées 'evaluation' par leçon: {updated_by_lecon}")
    
    # Méthode 2: Pour les questions sans leçon, vérifier l'historique d'import
    # (Cette partie est optionnelle car l'import crée toujours une leçon)


def reverse_migration(apps, schema_editor):
    """Annule la migration en remettant toutes les questions en 'quiz'"""
    Question = apps.get_model('prepaconcours', 'Question')
    Question.objects.filter(type_source='evaluation').update(type_source='quiz')


class Migration(migrations.Migration):

    dependencies = [
        ('prepaconcours', '0032_add_type_source_to_question'),
    ]

    operations = [
        migrations.RunPython(mark_evaluation_questions, reverse_migration),
    ]
