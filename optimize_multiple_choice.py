#!/usr/bin/env python
"""
Script d'optimisation pour la validation des questions à choix multiple
Remplace la logique coûteuse O(n²) par une approche O(n) optimisée
"""

def optimize_multiple_choice_validation():
    """
    Optimise la logique de validation des questions à choix multiple
    dans le fichier views.py
    """
    import os
    
    views_file = os.path.join(os.path.dirname(__file__), 'prepaconcours', 'views.py')
    
    # Lire le contenu actuel
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Code lent à remplacer
    old_code = """                if question.type_question == 'choix_multiple':
                    # Pour les choix multiples, toutes les bonnes réponses doivent être sélectionnées
                    choix_corrects = [c for c in choix_list if c.est_correct]
                    choix_corrects_lettres = [chr(ord('A') + choix_list.index(c)) for c in choix_corrects]
                    est_correct = set(reponses_lettres) == set(choix_corrects_lettres)"""
    
    # Code optimisé
    new_code = """                if question.type_question == 'choix_multiple':
                    # 🚀 OPTIMISATION: Éviter choix_list.index() coûteux (O(n²) → O(n))
                    # Créer directement les indices des bonnes réponses
                    choix_corrects_indices = {i for i, c in enumerate(choix_list) if c.est_correct}
                    reponses_indices = {ord(lettre) - ord('A') for lettre in reponses_lettres}
                    est_correct = choix_corrects_indices == reponses_indices"""
    
    # Remplacer le code
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        # Sauvegarder le fichier optimisé
        with open(views_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Optimisation appliquée avec succès !")
        print("🚀 Performance des questions à choix multiple améliorée")
        print("📊 Complexité réduite de O(n²) à O(n)")
        
        return True
    else:
        print("❌ Code à optimiser non trouvé")
        return False

if __name__ == "__main__":
    optimize_multiple_choice_validation()
