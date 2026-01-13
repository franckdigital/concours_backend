#!/usr/bin/env python
"""
Script pour améliorer la validation des réponses texte
Ajoute le support des réponses multiples acceptées séparées par des virgules
"""

def enhance_text_validation():
    """
    Améliore la logique de validation des réponses texte dans views.py
    pour supporter plusieurs réponses acceptées
    """
    import os
    
    views_file = os.path.join(os.path.dirname(__file__), 'prepaconcours', 'views.py')
    
    # Lire le contenu actuel
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Code actuel à remplacer
    old_validation = """                # Évaluer la réponse textuelle
                est_correct = False
                if question.reponse_attendue:
                    if question.correction_mode == 'exacte':
                        est_correct = reponse_texte.strip().lower() == question.reponse_attendue.strip().lower()
                    elif question.correction_mode == 'mot_cle':
                        est_correct = question.reponse_attendue.lower() in reponse_texte.lower()
                    elif question.correction_mode == 'regex':
                        import re
                        est_correct = bool(re.search(question.reponse_attendue, reponse_texte, re.IGNORECASE))"""
    
    # Nouvelle logique avec support des réponses multiples
    new_validation = """                # Évaluer la réponse textuelle avec support des réponses multiples
                est_correct = False
                if question.reponse_attendue:
                    # Support des réponses multiples séparées par des virgules
                    reponses_acceptees = [r.strip().lower() for r in question.reponse_attendue.split(',')]
                    reponse_utilisateur = reponse_texte.strip().lower()
                    
                    if question.correction_mode == 'exacte':
                        # Vérifier si la réponse utilisateur correspond à l'une des réponses acceptées
                        est_correct = reponse_utilisateur in reponses_acceptees
                    elif question.correction_mode == 'mot_cle':
                        # Vérifier si l'un des mots-clés est présent dans la réponse
                        est_correct = any(mot_cle in reponse_utilisateur for mot_cle in reponses_acceptees)
                    elif question.correction_mode == 'regex':
                        import re
                        # Tester chaque pattern regex
                        est_correct = any(bool(re.search(pattern, reponse_texte, re.IGNORECASE)) for pattern in reponses_acceptees)"""
    
    # Remplacer le code
    if old_validation in content:
        content = content.replace(old_validation, new_validation)
        
        # Sauvegarder le fichier amélioré
        with open(views_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("AMELIORATION APPLIQUEE AVEC SUCCES!")
        print("Support des reponses multiples acceptees ajoute")
        print("Format: 'heureux,content,gai,enjoue' dans reponse_attendue")
        
        return True
    else:
        print("Code a ameliorer non trouve")
        return False

def create_test_question():
    """
    Crée une question de test avec plusieurs réponses acceptées
    """
    print("\n=== EXEMPLE D'UTILISATION ===")
    print("Pour la question: 'Donnez un synonyme du mot joyeux'")
    print("Dans la base de donnees, definir:")
    print("  reponse_attendue = 'heureux,content,gai,enjoue,radieux'")
    print("  correction_mode = 'exacte'")
    print("")
    print("Reponses acceptees:")
    print("  - 'heureux' -> CORRECT")
    print("  - 'content' -> CORRECT") 
    print("  - 'gai' -> CORRECT")
    print("  - 'enjoue' -> CORRECT")
    print("  - 'radieux' -> CORRECT")
    print("  - 'triste' -> INCORRECT")

if __name__ == "__main__":
    enhance_text_validation()
    create_test_question()
