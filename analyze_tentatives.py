
#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from prepaconcours.models import Utilisateur, Tentative

def analyze_user_tentatives():
    print("=== ANALYSE DES TENTATIVES DANS LA BASE DE DONNÉES ===\n")
    
    # Trouver l'utilisateur KONAN ALAIN FRANCK KOUADIO
    try:
        konan = Utilisateur.objects.get(nom_complet="KONAN ALAIN FRANCK KOUADIO")
        print(f"Utilisateur trouvé: {konan.nom_complet} (ID: {konan.id})")
        print(f"Email: {konan.email}")
    except Utilisateur.DoesNotExist:
        print("Utilisateur KONAN ALAIN FRANCK KOUADIO non trouvé")
        return
    
    # Analyser ses tentatives
    tentatives = Tentative.objects.filter(utilisateur=konan).order_by('date_test')
    print(f"\nNombre total de tentatives: {tentatives.count()}")
    
    # Statistiques par statut
    terminées = tentatives.filter(terminee=True)
    non_terminées = tentatives.filter(terminee=False)
    
    print(f"Tentatives terminées: {terminées.count()}")
    print(f"Tentatives non terminées: {non_terminées.count()}")
    
    # Analyse des scores des tentatives terminées
    if terminées.exists():
        print(f"\n=== ANALYSE DES SCORES (tentatives terminées seulement) ===")
        scores = [t.score for t in terminées]
        print(f"Scores: {scores}")
        print(f"Score total: {sum(scores)}")
        print(f"Score moyen: {sum(scores) / len(scores):.2f}")
        print(f"Score minimum: {min(scores)}")
        print(f"Score maximum: {max(scores)}")
        
        # Distribution des scores
        score_zero = len([s for s in scores if s == 0])
        score_positif = len([s for s in scores if s > 0])
        
        print(f"\nDistribution:")
        print(f"- Tentatives avec score = 0: {score_zero}")
        print(f"- Tentatives avec score > 0: {score_positif}")
        
        # Détail des 10 premières tentatives
        print(f"\n=== DÉTAIL DES 10 PREMIÈRES TENTATIVES TERMINÉES ===")
        for i, tentative in enumerate(terminées[:10]):
            print(f"Tentative {i+1}: Score={tentative.score}, Date={tentative.date_test}, Session={tentative.session}")
    
    # Même analyse pour franck alain
    print(f"\n" + "="*60)
    try:
        franck = Utilisateur.objects.get(nom_complet="franck alain")
        print(f"Utilisateur trouvé: {franck.nom_complet} (ID: {franck.id})")
        
        tentatives_franck = Tentative.objects.filter(utilisateur=franck, terminee=True)
        print(f"Tentatives terminées: {tentatives_franck.count()}")
        
        if tentatives_franck.exists():
            scores_franck = [t.score for t in tentatives_franck]
            print(f"Scores: {scores_franck}")
            print(f"Score total: {sum(scores_franck)}")
            print(f"Score moyen: {sum(scores_franck) / len(scores_franck):.2f}")
            
    except Utilisateur.DoesNotExist:
        print("Utilisateur franck alain non trouvé")

if __name__ == "__main__":
    analyze_user_tentatives()
