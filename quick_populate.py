import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prepaconcours.settings')
django.setup()

from prepaconcours.models import Matiere, Lecon, Question, Choix

# Récupérer la matière Aptitude verbale
matiere = Matiere.objects.get(nom="Aptitude verbale", choix_concours="ENA")
print(f"Matière trouvée: {matiere.nom}")

# Supprimer les anciennes questions
Question.objects.filter(lecon__matiere=matiere).delete()
print("Anciennes questions supprimées")

# Créer les leçons
lecons_data = [
    ("Synonymes", "Étude des mots de même sens"),
    ("Antonymes", "Étude des mots de sens contraire"),
    ("Analogies", "Relations logiques entre les mots"),
    ("Compréhension", "Analyse et compréhension de textes"),
    ("Vocabulaire", "Enrichissement du vocabulaire")
]

lecons = []
for nom, desc in lecons_data:
    lecon, created = Lecon.objects.get_or_create(
        nom=nom,
        matiere=matiere,
        defaults={'description': desc, 'tour_ena': 'T1'}
    )
    lecons.append(lecon)
    print(f"Leçon: {nom}")

# Créer 100 questions (20 par leçon)
questions_base = [
    ("Quel est le synonyme de 'perspicace' ?", [("A", "Clairvoyant", True), ("B", "Confus", False), ("C", "Hésitant", False), ("D", "Négligent", False)]),
    ("Trouvez le synonyme de 'éphémère' :", [("A", "Éternel", False), ("B", "Passager", True), ("C", "Permanent", False), ("D", "Durable", False)]),
    ("Le synonyme de 'prolixe' est :", [("A", "Concis", False), ("B", "Bref", False), ("C", "Verbeux", True), ("D", "Laconique", False)]),
    ("Quel mot est synonyme de 'circonspect' ?", [("A", "Imprudent", False), ("B", "Prudent", True), ("C", "Téméraire", False), ("D", "Négligent", False)]),
    ("Le synonyme de 'diligent' est :", [("A", "Paresseux", False), ("B", "Négligent", False), ("C", "Appliqué", True), ("D", "Indolent", False)])
]

mots_test = ["intelligent", "rapide", "fort", "grand", "beau", "bon", "nouveau", "important", "difficile", "facile"]

total_questions = 0
for i, lecon in enumerate(lecons):
    for j in range(20):  # 20 questions par leçon
        if j < len(questions_base):
            enonce, choix_data = questions_base[j]
        else:
            mot = mots_test[j % len(mots_test)]
            enonce = f"Question {j+1} - Quel est le synonyme de '{mot}' ?"
            choix_data = [
                ("A", "Correct", True),
                ("B", "Incorrect1", False),
                ("C", "Incorrect2", False),
                ("D", "Incorrect3", False)
            ]
        
        question = Question.objects.create(
            enonce=f"[{lecon.nom}] {enonce}",
            type_question="choix_unique",
            lecon=lecon,
            explication=f"Explication pour la question {j+1} de {lecon.nom}",
            difficulte="Moyen",
            temps_limite=60
        )
        
        for lettre, texte, est_correct in choix_data:
            Choix.objects.create(
                question=question,
                lettre=lettre,
                texte=texte,
                est_correct=est_correct
            )
        
        total_questions += 1

print(f"✅ {total_questions} questions créées avec succès!")
print(f"📊 Répartition: {total_questions//len(lecons)} questions par leçon")
print(f"⏱️ Temps limite: 1 minute par question")

# Vérification
total_final = Question.objects.filter(lecon__matiere=matiere).count()
print(f"📈 Total en base: {total_final} questions")
