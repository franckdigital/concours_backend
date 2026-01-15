import pandas as pd
import os

def generate_questions():
    questions = []
    
    # Structure de base
    base_question = {
        'matiere_nom': 'Culture générale',
        # 'matiere_combinee' REMOVED as requested
        'difficulte': 'moyen',
        'temps_limite_secondes': 60,
        'correction_mode': 'exacte',
        'reponse_attendue': '',
        'choix_a': '', 'choix_b': '', 'choix_c': '', 'choix_d': '', 'choix_e': ''
    }

    # Helper pour créer une question
    def create_q(lecon, type_q, texte, correct, expl, choices=None, diff='moyen', time=60, rep_att=''):
        q = base_question.copy()
        q['lecon_nom'] = lecon
        q['type_question'] = type_q
        q['texte_question'] = texte
        q['bonne_reponse'] = correct
        q['explication'] = expl
        q['difficulte'] = diff
        q['temps_limite_secondes'] = time
        q['reponse_attendue'] = rep_att
        
        if choices:
            if 'a' in choices: q['choix_a'] = choices['a']
            if 'b' in choices: q['choix_b'] = choices['b']
            if 'c' in choices: q['choix_c'] = choices['c']
            if 'd' in choices: q['choix_d'] = choices['d']
            if 'e' in choices: q['choix_e'] = choices['e']
            
        return q

    all_questions = []

    # 1. SPORT (20 questions)
    lecon = 'Sport'
    all_questions.extend([
        create_q(lecon, 'choix_unique', 'Quel pays a remporté la Coupe du Monde de la FIFA 2018 ?', 'C', 'La France a remporté la Coupe du Monde 2018 en battant la Croatie.', {'a': 'Brésil', 'b': 'Allemagne', 'c': 'France', 'd': 'Argentine'}),
        create_q(lecon, 'choix_unique', 'Dans quel sport utilise-t-on un "volant" ?', 'B', 'Le volant est le projectile utilisé au badminton.', {'a': 'Tennis', 'b': 'Badminton', 'c': 'Squash', 'd': 'Ping-pong'}),
        create_q(lecon, 'choix_unique', 'Combien de joueurs y a-t-il dans une équipe de handball sur le terrain ?', 'C', 'Une équipe de handball se compose de 7 joueurs sur le terrain.', {'a': '5', 'b': '6', 'c': '7', 'd': '11'}),
        create_q(lecon, 'choix_unique', 'Qui détient le record du monde du 100 mètres masculin (9,58 s) ?', 'B', 'Usain Bolt détient le record du monde du 100m.', {'a': 'Tyson Gay', 'b': 'Usain Bolt', 'c': 'Yohan Blake', 'd': 'Carl Lewis'}),
        create_q(lecon, 'choix_unique', 'Quel tournoi de tennis se joue sur terre battue ?', 'C', 'Roland-Garros est le seul Grand Chelem sur terre battue.', {'a': 'Wimbledon', 'b': 'US Open', 'c': 'Roland-Garros', 'd': 'Open d\'Australie'}),
        create_q(lecon, 'choix_unique', 'En quelle année les premiers Jeux Olympiques modernes ont-ils eu lieu ?', 'A', 'À Athènes en 1896.', {'a': '1896', 'b': '1900', 'c': '1924', 'd': '1892'}),
        create_q(lecon, 'choix_unique', 'Quel pays a organisé la CAN 2023 ?', 'C', 'La Côte d\'Ivoire a organisé la CAN 2023.', {'a': 'Cameroun', 'b': 'Égypte', 'c': 'Côte d\'Ivoire', 'd': 'Sénégal'}),
        create_q(lecon, 'choix_unique', 'Sport national du Japon ?', 'B', 'Le Sumo est le sport national.', {'a': 'Judo', 'b': 'Sumo', 'c': 'Karaté', 'd': 'Baseball'}),
        create_q(lecon, 'choix_unique', 'Durée d\'un match de football standard ?', 'C', '90 minutes.', {'a': '60 min', 'b': '80 min', 'c': '90 min', 'd': '100 min'}),
        create_q(lecon, 'choix_unique', 'Surnom de LeBron James ?', 'C', 'King James.', {'a': 'Black Mamba', 'b': 'Air Jordan', 'c': 'King James', 'd': 'Chef Curry'}),
        # Types variés
        create_q(lecon, 'vrai_faux', 'Le ballon de rugby est rond.', 'B', 'Il est ovale.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Le judo est un sport olympique.', 'A', 'Le judo est aux JO depuis 1964.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Un marathon fait 42,195 km.', 'A', 'C\'est la distance officielle.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'choix_multiple', 'Quels sports font partie du triathlon ?', 'ABC', 'Natation, Cyclisme, Course à pied.', {'a': 'Natation', 'b': 'Cyclisme', 'c': 'Course à pied', 'd': 'Équitation'}),
        create_q(lecon, 'choix_multiple', 'Quels pays ont gagné la coupe du monde de foot au moins 2 fois ?', 'ABD', 'Brésil, France, Argentine l\'ont gagnée plusieurs fois.', {'a': 'Brésil', 'b': 'France', 'c': 'Pays-Bas', 'd': 'Argentine'}),
        create_q(lecon, 'choix_multiple', 'Disciplines de l\'athlétisme ?', 'ACD', 'Saut, Course, Lancer.', {'a': 'Saut en hauteur', 'b': 'Nage libre', 'c': '100m', 'd': 'Lancer de poids'}),
        create_q(lecon, 'texte_court', 'Quel est le prénom de Zidane ?', '', 'Zinédine Zidane.', rep_att='Zinédine|Zinedine'),
        create_q(lecon, 'texte_court', 'Dans quelle ville se trouve le stade Maracanã ?', '', 'Rio de Janeiro.', rep_att='Rio|Rio de Janeiro'),
        create_q(lecon, 'texte_court', 'Combien de points vaut un panier à 3 points au basket ?', '', '3 points.', rep_att='3|trois'),
        create_q(lecon, 'texte_long', 'Expliquez la règle du hors-jeu au football.', '', 'Un joueur est hors-jeu s\'il est plus près de la ligne de but adverse que le ballon et l\'avant-dernier adversaire au moment où le ballon lui est passé.', rep_att='ligne de but|avant-dernier|adversaire|ballon')
    ])

    # 2. ÉCONOMIE (20 questions)
    lecon = 'Économie'
    all_questions.extend([
        create_q(lecon, 'choix_unique', 'Monnaie de la zone Euro ?', 'B', 'L\'Euro.', {'a': 'Livre', 'b': 'Euro', 'c': 'Dollar', 'd': 'Franc'}),
        create_q(lecon, 'choix_unique', 'Que signifie PIB ?', 'A', 'Produit Intérieur Brut.', {'a': 'Produit Intérieur Brut', 'b': 'Prix Indice Bancaire', 'c': 'Plan Industriel', 'd': 'Produit International'}),
        create_q(lecon, 'choix_unique', 'Organisation du commerce mondial ?', 'C', 'OMC (Organisation Mondiale du Commerce).', {'a': 'FMI', 'b': 'BM', 'c': 'OMC', 'd': 'OCDE'}),
        create_q(lecon, 'choix_unique', 'Auteur de "La Richesse des Nations" ?', 'C', 'Adam Smith (1776).', {'a': 'Marx', 'b': 'Keynes', 'c': 'Smith', 'd': 'Ricardo'}),
        create_q(lecon, 'choix_unique', 'Hausse générale des prix ?', 'B', 'Inflation.', {'a': 'Déflation', 'b': 'Inflation', 'c': 'Stagnation', 'd': 'Récession'}),
        create_q(lecon, 'choix_unique', 'Devise du Royaume-Uni ?', 'C', 'Livre Sterling.', {'a': 'Euro', 'b': 'Dollar', 'c': 'Livre Sterling', 'd': 'Yen'}),
        create_q(lecon, 'choix_unique', 'Qu\'est-ce que le CAC 40 ?', 'B', 'Indice boursier de Paris.', {'a': 'Impôt', 'b': 'Indice boursier', 'c': 'Banque', 'd': 'Loi'}),
        create_q(lecon, 'choix_unique', '1ère puissance économique 2023 ?', 'B', 'États-Unis.', {'a': 'Chine', 'b': 'États-Unis', 'c': 'Inde', 'd': 'Japon'}),
        create_q(lecon, 'choix_unique', 'Signification FMI ?', 'A', 'Fonds Monétaire International.', {'a': 'Fonds Monétaire International', 'b': 'Fédération Mondiale', 'c': 'Force Militaire', 'd': 'Finance Mondiale'}),
        create_q(lecon, 'choix_unique', 'Offre supérieure à la demande ?', 'B', 'Surproduction ou excédent.', {'a': 'Pénurie', 'b': 'Surproduction', 'c': 'Équilibre', 'd': 'Inflation'}),
        # Variés
        create_q(lecon, 'vrai_faux', 'La TVA est un impôt direct.', 'B', 'C\'est un impôt indirect sur la consommation.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Wall Street est à New York.', 'A', 'C\'est le quartier financier de NY.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Le Bitcoin est une monnaie physique.', 'B', 'C\'est une cryptomonnaie virtuelle.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'choix_multiple', 'Quels sont des facteurs de production ?', 'AB', 'Travail et Capital.', {'a': 'Travail', 'b': 'Capital', 'c': 'Consommation', 'd': 'Épargne'}),
        create_q(lecon, 'choix_multiple', 'Pays membres du G7 ?', 'ACD', 'France, USA, Japon en font partie.', {'a': 'France', 'b': 'Chine', 'c': 'États-Unis', 'd': 'Japon'}),
        create_q(lecon, 'choix_multiple', 'Secteurs économiques ?', 'ABC', 'Primaire, Secondaire, Tertiaire.', {'a': 'Primaire', 'b': 'Secondaire', 'c': 'Tertiaire', 'd': 'Quaternaire'}),
        create_q(lecon, 'texte_court', 'Quelle est la monnaie du Japon ?', '', 'Le Yen.', rep_att='Yen'),
        create_q(lecon, 'texte_court', 'En quelle année a eu lieu le krach boursier de Wall Street ?', '', '1929.', rep_att='1929'),
        create_q(lecon, 'texte_court', 'Quelle monnaie utilise la Suisse ?', '', 'Franc suisse.', rep_att='Franc suisse|Franc'),
        create_q(lecon, 'texte_long', 'Définissez le terme "Monopole".', '', 'Situation de marché où il n\'y a qu\'un seul vendeur face à une multitude d\'acheteurs.', rep_att='seul vendeur|unique vendeur|marché')
    ])

    # 3. CUISINE (20 questions)
    lecon = 'Cuisine'
    all_questions.extend([
        create_q(lecon, 'choix_unique', 'Ingrédient principal du guacamole ?', 'B', 'Avocat.', {'a': 'Tomate', 'b': 'Avocat', 'c': 'Poivron', 'd': 'Oignon'}),
        create_q(lecon, 'choix_unique', 'Pays de la paella ?', 'C', 'Espagne.', {'a': 'Italie', 'b': 'Portugal', 'c': 'Espagne', 'd': 'Mexique'}),
        create_q(lecon, 'choix_unique', 'Qu\'est-ce qui fait lever le pain ?', 'C', 'Levure.', {'a': 'Sucre', 'b': 'Sel', 'c': 'Levure', 'd': 'Farine'}),
        create_q(lecon, 'choix_unique', 'Base de la béchamel ?', 'B', 'Beurre, farine, lait.', {'a': 'Huile/Vinaigre', 'b': 'Beurre/Farine/Lait', 'c': 'Tomate', 'd': 'Crème/Oeufs'}),
        create_q(lecon, 'choix_unique', 'Plat ivoirien de semoule de manioc ?', 'B', 'Attiéké.', {'a': 'Foutou', 'b': 'Attiéké', 'c': 'Alloco', 'd': 'Placali'}),
        create_q(lecon, 'choix_unique', 'Qu\'est-ce que le tofu ?', 'B', 'Pâte de soja.', {'a': 'Fromage', 'b': 'Soja', 'c': 'Riz', 'd': 'Algue'}),
        create_q(lecon, 'choix_unique', 'Fruit du vin ?', 'C', 'Raisin.', {'a': 'Pomme', 'b': 'Cerise', 'c': 'Raisin', 'd': 'Prune'}),
        create_q(lecon, 'choix_unique', 'Épice la plus chère ?', 'B', 'Safran.', {'a': 'Vanille', 'b': 'Safran', 'c': 'Cardamome', 'd': 'Cannelle'}),
        create_q(lecon, 'choix_unique', 'Cuisson à la vapeur ?', 'D', 'Cuisson vapeur.', {'a': 'Friture', 'b': 'Braisage', 'c': 'Étouffée', 'd': 'Vapeur'}),
        create_q(lecon, 'choix_unique', 'Ingrédient du tiep bou dien ?', 'C', 'Poisson.', {'a': 'Poulet', 'b': 'Bœuf', 'c': 'Poisson', 'd': 'Crevettes'}),
        # Variés
        create_q(lecon, 'vrai_faux', 'La tomate est un fruit.', 'A', 'Botaniquement, c\'est un fruit.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Les sushis viennent de Chine.', 'B', 'Ils viennent du Japon.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Le chocolat vient du cacao.', 'A', 'Fèves de cacao.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'choix_multiple', 'Ingrédients d\'une mayonnaise ?', 'ABD', 'Jaune d\'oeuf, Huile, Moutarde (optionnelle mais courante).', {'a': 'Jaune d\'oeuf', 'b': 'Huile', 'c': 'Lait', 'd': 'Moutarde'}),
        create_q(lecon, 'choix_multiple', 'Plats italiens ?', 'AC', 'Pizza, Lasagnes.', {'a': 'Pizza', 'b': 'Couscous', 'c': 'Lasagnes', 'd': 'Tacos'}),
        create_q(lecon, 'choix_multiple', 'Types de cuisson ?', 'ABC', 'Rôtir, Bouillir, Frire.', {'a': 'Rôtir', 'b': 'Bouillir', 'c': 'Frire', 'd': 'Congeler'}),
        create_q(lecon, 'texte_court', 'Quel ingrédient fait pleurer quand on le coupe ?', '', 'Oignon.', rep_att='Oignon'),
        create_q(lecon, 'texte_court', 'Quelle est la viande du jambon ?', '', 'Porc.', rep_att='Porc|Cochon'),
        create_q(lecon, 'texte_court', 'De quel pays vient la pizza ?', '', 'Italie.', rep_att='Italie'),
        create_q(lecon, 'texte_long', 'Qu\'est-ce qu\'un végétarien ?', '', 'Personne qui ne mange pas de chair animale (viande, poisson).', rep_att='viande|chair animale|poisson')
    ])

    # 4. MÉDECINE (20 questions)
    lecon = 'Médecine'
    all_questions.extend([
        create_q(lecon, 'choix_unique', 'Organe principal circulation ?', 'C', 'Cœur.', {'a': 'Poumon', 'b': 'Cerveau', 'c': 'Cœur', 'd': 'Foie'}),
        create_q(lecon, 'choix_unique', 'Nombre de dents adulte ?', 'C', '32.', {'a': '28', 'b': '30', 'c': '32', 'd': '34'}),
        create_q(lecon, 'choix_unique', 'Transport oxygène sang ?', 'B', 'Hémoglobine.', {'a': 'Insuline', 'b': 'Hémoglobine', 'c': 'Collagène', 'd': 'Adrénaline'}),
        create_q(lecon, 'choix_unique', 'Production insuline ?', 'B', 'Pancréas.', {'a': 'Foie', 'b': 'Pancréas', 'c': 'Rein', 'd': 'Estomac'}),
        create_q(lecon, 'choix_unique', 'Antibiotique combat ?', 'B', 'Bactéries.', {'a': 'Virus', 'b': 'Bactéries', 'c': 'Champignons', 'd': 'Parasites'}),
        create_q(lecon, 'choix_unique', 'Plus grand organe ?', 'B', 'Peau.', {'a': 'Foie', 'b': 'Peau', 'c': 'Cerveau', 'd': 'Intestin'}),
        create_q(lecon, 'choix_unique', 'Vitamine soleil ?', 'C', 'Vitamine D.', {'a': 'A', 'b': 'C', 'c': 'D', 'd': 'E'}),
        create_q(lecon, 'choix_unique', 'Médecin des enfants ?', 'B', 'Pédiatre.', {'a': 'Gériatre', 'b': 'Pédiatre', 'c': 'Cardiologue', 'd': 'Dermatologue'}),
        create_q(lecon, 'choix_unique', 'Donneur universel ?', 'C', 'O-.', {'a': 'A+', 'b': 'AB+', 'c': 'O-', 'd': 'B-'}),
        create_q(lecon, 'choix_unique', 'Inflammation appendice ?', 'B', 'Appendicite.', {'a': 'Gastrite', 'b': 'Appendicite', 'c': 'Colite', 'd': 'Hépatite'}),
        # Variés
        create_q(lecon, 'vrai_faux', 'Le fémur est l\'os le plus long.', 'A', 'Vrai.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Le cœur est un muscle.', 'A', 'C\'est un muscle creux.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'L\'aspirine guérit le SIDA.', 'B', 'Faux, il n\'y a pas de guérison définitive encore.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'choix_multiple', 'Symptômes grippe ?', 'ABC', 'Fièvre, Toux, Fatigue.', {'a': 'Fièvre', 'b': 'Toux', 'c': 'Fatigue', 'd': 'Faim'}),
        create_q(lecon, 'choix_multiple', 'Organes digestifs ?', 'ABD', 'Estomac, Intestin, Oesophage.', {'a': 'Estomac', 'b': 'Intestin', 'c': 'Poumon', 'd': 'Oesophage'}),
        create_q(lecon, 'choix_multiple', 'Types de vaisseaux sanguins ?', 'ABC', 'Artères, Veines, Capillaires.', {'a': 'Artères', 'b': 'Veines', 'c': 'Capillaires', 'd': 'Nerfs'}),
        create_q(lecon, 'texte_court', 'Quel est le nombre de chromosomes humains ?', '', '46 (23 paires).', rep_att='46|23 paires'),
        create_q(lecon, 'texte_court', 'Quel organe filtre le sang ?', '', 'Reins.', rep_att='Rein|Reins'),
        create_q(lecon, 'texte_court', 'Comment appelle-t-on le médecin des yeux ?', '', 'Ophtalmologue.', rep_att='Ophtalmologue|Ophtalmo'),
        create_q(lecon, 'texte_long', 'Qu\'est-ce que l\'hypertension ?', '', 'Une pression artérielle trop élevée.', rep_att='pression|tension|élevée|haute')
    ])

    # 5. SCIENCES (20 questions)
    lecon = 'Sciences et techniques'
    all_questions.extend([
        create_q(lecon, 'choix_unique', 'Planète proche soleil ?', 'C', 'Mercure.', {'a': 'Vénus', 'b': 'Terre', 'c': 'Mercure', 'd': 'Mars'}),
        create_q(lecon, 'choix_unique', 'Formule eau ?', 'B', 'H2O.', {'a': 'CO2', 'b': 'H2O', 'c': 'O2', 'd': 'NaCl'}),
        create_q(lecon, 'choix_unique', 'Relativité générale ?', 'B', 'Einstein.', {'a': 'Newton', 'b': 'Einstein', 'c': 'Galilée', 'd': 'Tesla'}),
        create_q(lecon, 'choix_unique', 'Gaz photosynthèse ?', 'C', 'CO2.', {'a': 'O2', 'b': 'Azote', 'c': 'CO2', 'd': 'H2'}),
        create_q(lecon, 'choix_unique', 'Symbole Fe ?', 'A', 'Fer.', {'a': 'Fer', 'b': 'Fluor', 'c': 'Francium', 'd': 'Fermium'}),
        create_q(lecon, 'choix_unique', 'Vitesse lumière ?', 'A', '300 000 km/s.', {'a': '300 000', 'b': '150 000', 'c': '1000', 'd': '340'}),
        create_q(lecon, 'choix_unique', 'Inventeur téléphone ?', 'B', 'Bell.', {'a': 'Edison', 'b': 'Bell', 'c': 'Marconi', 'd': 'Morse'}),
        create_q(lecon, 'choix_unique', 'Force sol ?', 'C', 'Gravité.', {'a': 'Magnétique', 'b': 'Centrifuge', 'c': 'Gravité', 'd': 'Nucléaire'}),
        create_q(lecon, 'choix_unique', 'Air principal ?', 'B', 'Azote.', {'a': 'Oxygène', 'b': 'Azote', 'c': 'CO2', 'd': 'Argon'}),
        create_q(lecon, 'choix_unique', 'Mesure thermomètre ?', 'C', 'Température.', {'a': 'Pression', 'b': 'Humidité', 'c': 'Température', 'd': 'Vitesse'}),
        # Variés
        create_q(lecon, 'vrai_faux', 'La Terre est plate.', 'B', 'Elle est sphérique (géoïde).', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'L\'eau bout à 100°C.', 'A', 'À pression standard.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Le soleil est une étoile.', 'A', 'Vrai.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'choix_multiple', 'États de la matière ?', 'ABC', 'Solide, Liquide, Gazeux.', {'a': 'Solide', 'b': 'Liquide', 'c': 'Gazeux', 'd': 'Mou'}),
        create_q(lecon, 'choix_multiple', 'Planètes gazeuses ?', 'AB', 'Jupiter, Saturne.', {'a': 'Jupiter', 'b': 'Saturne', 'c': 'Mars', 'd': 'Terre'}),
        create_q(lecon, 'choix_multiple', 'Sources énergie renouvelable ?', 'ABD', 'Solaire, Éolien, Hydro.', {'a': 'Solaire', 'b': 'Éolien', 'c': 'Charbon', 'd': 'Hydraulique'}),
        create_q(lecon, 'texte_court', 'Symbole chimique de l\'Or ?', '', 'Au.', rep_att='Au'),
        create_q(lecon, 'texte_court', 'Combien de planètes dans le système solaire ?', '', '8.', rep_att='8|huit'),
        create_q(lecon, 'texte_court', 'Quelle planète est la "planète rouge" ?', '', 'Mars.', rep_att='Mars'),
        create_q(lecon, 'texte_long', 'Qu\'est-ce que l\'ADN ?', '', 'Acide Désoxyribonucléique, support de l\'information génétique.', rep_att='génétique|information|acide')
    ])

    # 6. GÉOGRAPHIE (20 questions)
    lecon = 'Géographie'
    all_questions.extend([
        create_q(lecon, 'choix_unique', 'Plus grand pays ?', 'C', 'Russie.', {'a': 'Chine', 'b': 'USA', 'c': 'Russie', 'd': 'Canada'}),
        create_q(lecon, 'choix_unique', 'Capitale Australie ?', 'C', 'Canberra.', {'a': 'Sydney', 'b': 'Melbourne', 'c': 'Canberra', 'd': 'Brisbane'}),
        create_q(lecon, 'choix_unique', 'Continent Sahara ?', 'B', 'Afrique.', {'a': 'Asie', 'b': 'Afrique', 'c': 'Am. Sud', 'd': 'Australie'}),
        create_q(lecon, 'choix_unique', 'Plus long fleuve ?', 'B', 'Amazone.', {'a': 'Nil', 'b': 'Amazone', 'c': 'Yangzi', 'd': 'Mississippi'}),
        create_q(lecon, 'choix_unique', 'Nombre océans ?', 'C', '5.', {'a': '3', 'b': '4', 'c': '5', 'd': '6'}),
        create_q(lecon, 'choix_unique', 'Capitale Côte d\'Ivoire ?', 'B', 'Yamoussoukro.', {'a': 'Abidjan', 'b': 'Yamoussoukro', 'c': 'Bouaké', 'd': 'San-Pédro'}),
        create_q(lecon, 'choix_unique', 'Pays Tour Eiffel ?', 'D', 'France.', {'a': 'Italie', 'b': 'Espagne', 'c': 'Allemagne', 'd': 'France'}),
        create_q(lecon, 'choix_unique', 'Pays forme botte ?', 'B', 'Italie.', {'a': 'Grèce', 'b': 'Italie', 'c': 'Espagne', 'd': 'Portugal'}),
        create_q(lecon, 'choix_unique', 'Plus haut sommet ?', 'C', 'Everest.', {'a': 'Blanc', 'b': 'Kilimandjaro', 'c': 'Everest', 'd': 'K2'}),
        create_q(lecon, 'choix_unique', 'Mer Europe/Afrique ?', 'C', 'Méditerranée.', {'a': 'Noire', 'b': 'Rouge', 'c': 'Méditerranée', 'd': 'Caspienne'}),
        # Variés
        create_q(lecon, 'vrai_faux', 'Le Nil est en Amérique.', 'B', 'En Afrique.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'L\'Afrique est un pays.', 'B', 'C\'est un continent.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Paris est la capitale de la France.', 'A', 'Vrai.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'choix_multiple', 'Pays d\'Amérique du Nord ?', 'ABC', 'Canada, USA, Mexique.', {'a': 'Canada', 'b': 'USA', 'c': 'Mexique', 'd': 'Brésil'}),
        create_q(lecon, 'choix_multiple', 'Fleuves africains ?', 'ACD', 'Nil, Niger, Congo.', {'a': 'Nil', 'b': 'Danube', 'c': 'Niger', 'd': 'Congo'}),
        create_q(lecon, 'choix_multiple', 'Pays frontaliers de la France ?', 'ABD', 'Espagne, Belgique, Allemagne.', {'a': 'Espagne', 'b': 'Belgique', 'c': 'Portugal', 'd': 'Allemagne'}),
        create_q(lecon, 'texte_court', 'Quel est le plus grand océan ?', '', 'Pacifique.', rep_att='Pacifique'),
        create_q(lecon, 'texte_court', 'Capitale du Sénégal ?', '', 'Dakar.', rep_att='Dakar'),
        create_q(lecon, 'texte_court', 'Combien de continents (modèle à 6) ?', '', '6.', rep_att='6|six'),
        create_q(lecon, 'texte_long', 'Qu\'est-ce qu\'une péninsule ?', '', 'Une étendue de terre entourée d\'eau sur plusieurs côtés.', rep_att='terre|eau|entourée')
    ])

    # 7. HISTOIRE (20 questions)
    lecon = 'Histoire'
    all_questions.extend([
        create_q(lecon, 'choix_unique', 'Année Révolution française ?', 'B', '1789.', {'a': '1776', 'b': '1789', 'c': '1815', 'd': '1848'}),
        create_q(lecon, 'choix_unique', '1er président Ivoirien ?', 'C', 'Houphouët-Boigny.', {'a': 'Bédié', 'b': 'Gbagbo', 'c': 'Houphouët', 'd': 'Ouattara'}),
        create_q(lecon, 'choix_unique', 'Guerre 14-18 ?', 'B', '1ère Guerre Mondiale.', {'a': 'Sécession', 'b': '1ère GM', 'c': '2ème GM', 'd': 'Vietnam'}),
        create_q(lecon, 'choix_unique', 'Découverte Amérique 1492 ?', 'B', 'Colomb.', {'a': 'Gama', 'b': 'Colomb', 'c': 'Magellan', 'd': 'Cartier'}),
        create_q(lecon, 'choix_unique', 'Mort Napoléon ?', 'B', 'Sainte-Hélène.', {'a': 'Louis XIV', 'b': 'Napoléon I', 'c': 'Napoléon III', 'd': 'Charlemagne'}),
        create_q(lecon, 'choix_unique', 'Chute mur Berlin ?', 'B', '1989.', {'a': '1987', 'b': '1989', 'c': '1991', 'd': '1993'}),
        create_q(lecon, 'choix_unique', 'Pharaon masque or ?', 'C', 'Toutankhamon.', {'a': 'Ramsès', 'b': 'Khéops', 'c': 'Toutankhamon', 'd': 'Akhenaton'}),
        create_q(lecon, 'choix_unique', 'Début 2ème GM ?', 'A', 'Invasion Pologne.', {'a': 'Pologne', 'b': 'Pearl Harbor', 'c': 'Normandie', 'd': 'Stalingrad'}),
        create_q(lecon, 'choix_unique', 'I Have a Dream ?', 'C', 'Martin Luther King.', {'a': 'Malcolm X', 'b': 'Mandela', 'c': 'MLK', 'd': 'Obama'}),
        create_q(lecon, 'choix_unique', 'Homme sur Lune ?', 'B', '1969.', {'a': '1965', 'b': '1969', 'c': '1972', 'd': '1961'}),
        # Variés
        create_q(lecon, 'vrai_faux', 'La guerre de 100 ans a duré 100 ans.', 'B', '116 ans.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'César était empereur.', 'B', 'Dictateur, pas empereur (Auguste fut le 1er).', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Mandela était Sud-Africain.', 'A', 'Vrai.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'choix_multiple', 'Présidents USA ?', 'ACD', 'Washington, Lincoln, Kennedy.', {'a': 'Washington', 'b': 'Churchill', 'c': 'Lincoln', 'd': 'Kennedy'}),
        create_q(lecon, 'choix_multiple', 'Alliés 2ème GM ?', 'ABD', 'USA, URSS, UK.', {'a': 'USA', 'b': 'URSS', 'c': 'Allemagne', 'd': 'Royaume-Uni'}),
        create_q(lecon, 'choix_multiple', 'Rois de France ?', 'ABC', 'Louis XIV, François Ier, Henri IV.', {'a': 'Louis XIV', 'b': 'François Ier', 'c': 'Henri IV', 'd': 'Élisabeth II'}),
        create_q(lecon, 'texte_court', 'En quelle année a fini la 2ème guerre mondiale ?', '', '1945.', rep_att='1945'),
        create_q(lecon, 'texte_court', 'Qui a peint la Joconde ?', '', 'Léonard de Vinci.', rep_att='Vinci|Léonard'),
        create_q(lecon, 'texte_court', 'Quelle ville a été détruite par le Vésuve ?', '', 'Pompéi.', rep_att='Pompéi|Pompei'),
        create_q(lecon, 'texte_long', 'Qu\'est-ce que la Guerre Froide ?', '', 'Conflit idéologique sans affrontement direct entre USA et URSS.', rep_att='conflit|USA|URSS|idéologique')
    ])

    # 8. LITTÉRATURE (20 questions)
    lecon = 'Littérature'
    all_questions.extend([
        create_q(lecon, 'choix_unique', 'Auteur Les Misérables ?', 'B', 'Hugo.', {'a': 'Zola', 'b': 'Hugo', 'c': 'Flaubert', 'd': 'Balzac'}),
        create_q(lecon, 'choix_unique', 'Cahier retour pays natal ?', 'C', 'Césaire.', {'a': 'Kourouma', 'b': 'Dadié', 'c': 'Césaire', 'd': 'Senghor'}),
        create_q(lecon, 'choix_unique', 'L\'Étranger ?', 'B', 'Camus.', {'a': 'Sartre', 'b': 'Camus', 'c': 'Proust', 'd': 'Gide'}),
        create_q(lecon, 'choix_unique', 'Roméo et Juliette ?', 'B', 'Shakespeare.', {'a': 'Dickens', 'b': 'Shakespeare', 'c': 'Wilde', 'd': 'Austen'}),
        create_q(lecon, 'choix_unique', 'Le Petit Prince ?', 'B', 'Saint-Exupéry.', {'a': 'Verne', 'b': 'Saint-Exupéry', 'c': 'La Fontaine', 'd': 'Perrault'}),
        create_q(lecon, 'choix_unique', 'L\'Enfant noir ?', 'A', 'Camara Laye.', {'a': 'Laye', 'b': 'Achebe', 'c': 'Kane', 'd': 'Beti'}),
        create_q(lecon, 'choix_unique', 'Saga Harry Potter ?', 'B', 'Harry Potter.', {'a': 'Seigneur Anneaux', 'b': 'Harry Potter', 'c': 'Narnia', 'd': 'Percy Jackson'}),
        create_q(lecon, 'choix_unique', 'Madame Bovary ?', 'A', 'Flaubert.', {'a': 'Flaubert', 'b': 'Stendhal', 'c': 'Maupassant', 'd': 'Sand'}),
        create_q(lecon, 'choix_unique', 'Prix littéraire automne ?', 'B', 'Goncourt.', {'a': 'Pulitzer', 'b': 'Goncourt', 'c': 'Nobel', 'd': 'Booker'}),
        create_q(lecon, 'choix_unique', 'Fables ?', 'B', 'La Fontaine.', {'a': 'Molière', 'b': 'La Fontaine', 'c': 'Voltaire', 'd': 'Racine'}),
        # Variés
        create_q(lecon, 'vrai_faux', 'Molière écrivait des pièces de théâtre.', 'A', 'Vrai.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Sherlock Holmes est réel.', 'B', 'Personnage de fiction.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Victor Hugo était français.', 'A', 'Vrai.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'choix_multiple', 'Poètes français ?', 'ABD', 'Baudelaire, Rimbaud, Verlaine.', {'a': 'Baudelaire', 'b': 'Rimbaud', 'c': 'Mozart', 'd': 'Verlaine'}),
        create_q(lecon, 'choix_multiple', 'Genres littéraires ?', 'ABC', 'Roman, Poésie, Théâtre.', {'a': 'Roman', 'b': 'Poésie', 'c': 'Théâtre', 'd': 'Sculpture'}),
        create_q(lecon, 'choix_multiple', 'Œuvres de Zola ?', 'AC', 'Germinal, Nana.', {'a': 'Germinal', 'b': 'Les Misérables', 'c': 'Nana', 'd': 'L\'Étranger'}),
        create_q(lecon, 'texte_court', 'Qui a écrit "L\'Avare" ?', '', 'Molière.', rep_att='Molière|Moliere'),
        create_q(lecon, 'texte_court', 'Quel est le prénom de M. Proust ?', '', 'Marcel.', rep_att='Marcel'),
        create_q(lecon, 'texte_court', 'Héros de Cervantes ?', '', 'Don Quichotte.', rep_att='Don Quichotte|Quichotte'),
        create_q(lecon, 'texte_long', 'Qu\'est-ce qu\'une autobiographie ?', '', 'Récit de sa propre vie écrit par l\'auteur lui-même.', rep_att='propre vie|auteur|récit')
    ])

    # 9. TRADITION (20 questions)
    lecon = 'Tradition'
    all_questions.extend([
        create_q(lecon, 'choix_unique', 'Fête génération lagunaires ?', 'A', 'Abissa.', {'a': 'Abissa', 'b': 'Popo', 'c': 'Ignames', 'd': 'Dipri'}),
        create_q(lecon, 'choix_unique', 'Tissu Akan ?', 'B', 'Kita/Kente.', {'a': 'Bazin', 'b': 'Kita', 'c': 'Bogolan', 'd': 'Wax'}),
        create_q(lecon, 'choix_unique', 'Dot ?', 'C', 'Cadeaux mariage.', {'a': 'Repas', 'b': 'Danse', 'c': 'Présents', 'd': 'Vêtement'}),
        create_q(lecon, 'choix_unique', 'Masque Zaouli ?', 'B', 'Beauté.', {'a': 'Guerre', 'b': 'Beauté', 'c': 'Pluie', 'd': 'Sagesse'}),
        create_q(lecon, 'choix_unique', 'Instrument griot ?', 'B', 'Kora.', {'a': 'Piano', 'b': 'Kora', 'c': 'Violon', 'd': 'Guitare'}),
        create_q(lecon, 'choix_unique', 'Fête ignames ?', 'C', 'Nouvel an Agni.', {'a': 'Paquinou', 'b': 'Abissa', 'c': 'Fête Ignames', 'd': 'Ramadan'}),
        create_q(lecon, 'choix_unique', 'Poro Sénoufo ?', 'C', 'Initiation.', {'a': 'Danse', 'b': 'Marché', 'c': 'Initiation', 'd': 'Plat'}),
        create_q(lecon, 'choix_unique', 'Arbre palabres ?', 'B', 'Baobab.', {'a': 'Cocotier', 'b': 'Baobab', 'c': 'Hévéa', 'd': 'Manguier'}),
        create_q(lecon, 'choix_unique', 'Griot ?', 'B', 'Conteur.', {'a': 'Guerrier', 'b': 'Conteur', 'c': 'Forgeron', 'd': 'Chasseur'}),
        create_q(lecon, 'choix_unique', 'Proverbe oiseau ?', 'B', 'Patience.', {'a': 'Vitesse', 'b': 'Patience', 'c': 'Lenteur', 'd': 'Maison'}),
        # Variés
        create_q(lecon, 'vrai_faux', 'La dot est obligatoire traditionnellement.', 'A', 'Vrai.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Le masque est un objet sacré.', 'A', 'Souvent vrai.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Tous les Africains parlent la même langue.', 'B', 'Faux, milliers de langues.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'choix_multiple', 'Peuples de Côte d\'Ivoire ?', 'ABC', 'Baoulé, Bété, Sénoufo.', {'a': 'Baoulé', 'b': 'Bété', 'c': 'Sénoufo', 'd': 'Apache'}),
        create_q(lecon, 'choix_multiple', 'Instruments africains ?', 'ABD', 'Djembé, Balafon, Kora.', {'a': 'Djembé', 'b': 'Balafon', 'c': 'Violoncelle', 'd': 'Kora'}),
        create_q(lecon, 'choix_multiple', 'Cérémonies traditionnelles ?', 'AC', 'Mariage coutumier, Funérailles.', {'a': 'Mariage coutumier', 'b': 'Noël', 'c': 'Funérailles', 'd': 'Pâques'}),
        create_q(lecon, 'texte_court', 'Comment appelle-t-on le chef de village ?', '', 'Chef.', rep_att='Chef|Roi'),
        create_q(lecon, 'texte_court', 'Quel peuple célèbre le Popo Carnaval ?', '', 'Abouré.', rep_att='Abouré|Aboure'),
        create_q(lecon, 'texte_court', 'Masque aux longues échasses ?', '', 'Echassier (ou Gou), souvent chez les Dan.', rep_att='Echassier|Gou|Dan'),
        create_q(lecon, 'texte_long', 'Qu\'est-ce que le matriarcat (Akan) ?', '', 'Système où l\'héritage se transmet par la mère (neveu utérin).', rep_att='mère|héritage|neveu|femme')
    ])

    # 10. RELIGION (20 questions)
    lecon = 'Religion'
    all_questions.extend([
        create_q(lecon, 'choix_unique', 'Livre Islam ?', 'C', 'Coran.', {'a': 'Bible', 'b': 'Torah', 'c': 'Coran', 'd': 'Védas'}),
        create_q(lecon, 'choix_unique', 'Fondateur Christianisme ?', 'B', 'Jésus.', {'a': 'Moïse', 'b': 'Jésus', 'c': 'Mahomet', 'd': 'Bouddha'}),
        create_q(lecon, 'choix_unique', 'Jour Juif ?', 'C', 'Shabbat.', {'a': 'Vendredi', 'b': 'Dimanche', 'c': 'Samedi', 'd': 'Lundi'}),
        create_q(lecon, 'choix_unique', 'Siège Catholique ?', 'B', 'Vatican.', {'a': 'France', 'b': 'Vatican', 'c': 'Espagne', 'd': 'Jérusalem'}),
        create_q(lecon, 'choix_unique', 'Prophète Islam ?', 'B', 'Mahomet.', {'a': 'Abraham', 'b': 'Mahomet', 'c': 'Noé', 'd': 'David'}),
        create_q(lecon, 'choix_unique', 'Karma ?', 'C', 'Bouddhisme.', {'a': 'Christianisme', 'b': 'Islam', 'c': 'Bouddhisme', 'd': 'Judaïsme'}),
        create_q(lecon, 'choix_unique', 'Noël ?', 'B', 'Naissance Jésus.', {'a': 'Résurrection', 'b': 'Naissance', 'c': 'Esprit', 'd': 'Fin année'}),
        create_q(lecon, 'choix_unique', 'Culte Juif ?', 'C', 'Synagogue.', {'a': 'Église', 'b': 'Mosquée', 'c': 'Synagogue', 'd': 'Temple'}),
        create_q(lecon, 'choix_unique', 'Ramadan ?', 'B', 'Jeûne.', {'a': 'Fête', 'b': 'Jeûne', 'c': 'Pèlerinage', 'd': 'Prière'}),
        create_q(lecon, 'choix_unique', 'Piliers Islam ?', 'B', '5.', {'a': '3', 'b': '5', 'c': '7', 'd': '10'}),
        # Variés
        create_q(lecon, 'vrai_faux', 'Jésus est né à Jérusalem.', 'B', 'Bethléem.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'La Mecque est en Arabie Saoudite.', 'A', 'Vrai.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'vrai_faux', 'Le Dalaï-lama est chrétien.', 'B', 'Bouddhiste.', {'a': 'VRAI', 'b': 'FAUX'}),
        create_q(lecon, 'choix_multiple', 'Religions monothéistes ?', 'ABD', 'Judaïsme, Christianisme, Islam.', {'a': 'Judaïsme', 'b': 'Christianisme', 'c': 'Hindouisme', 'd': 'Islam'}),
        create_q(lecon, 'choix_multiple', 'Livres bibliques ?', 'AC', 'Genèse, Exode.', {'a': 'Genèse', 'b': 'Coran', 'c': 'Exode', 'd': 'Vedas'}),
        create_q(lecon, 'choix_multiple', 'Fêtes chrétiennes ?', 'ACD', 'Pâques, Noël, Toussaint.', {'a': 'Pâques', 'b': 'Aïd', 'c': 'Noël', 'd': 'Toussaint'}),
        create_q(lecon, 'texte_court', 'Qui a ouvert la Mer Rouge ?', '', 'Moïse.', rep_att='Moïse|Moise'),
        create_q(lecon, 'texte_court', 'Premier homme selon la Bible ?', '', 'Adam.', rep_att='Adam'),
        create_q(lecon, 'texte_court', 'Combien d\'apôtres ?', '', '12.', rep_att='12|douze'),
        create_q(lecon, 'texte_long', 'Qu\'est-ce que l\'athéisme ?', '', 'L\'absence de croyance en un dieu.', rep_att='croyance|dieu|absence')
    ])

    # Créer DataFrame
    df = pd.DataFrame(all_questions)
    
    # Colonnes attendues
    columns = [
        'matiere_nom', 'lecon_nom', 'texte_question', 'type_question',
        'choix_a', 'choix_b', 'choix_c', 'choix_d', 'choix_e',
        'bonne_reponse', 'reponse_attendue', 'explication', 'difficulte',
        'temps_limite_secondes', 'correction_mode'
    ]
    
    # S'assurer que toutes les colonnes existent
    for col in columns:
        if col not in df.columns:
            df[col] = ''
            
    df = df[columns]
    
    output_path = r'C:\Users\HP\Desktop\questionnaires.xlsx'
    
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Questions_ENA_Exemples', index=False)
            print(f"Fichier généré avec succès (200 questions) : {output_path}")
    except PermissionError:
        output_path = r'C:\Users\HP\Desktop\questionnaires_v3.xlsx'
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Questions_ENA_Exemples', index=False)
            print(f"Fichier généré avec succès (redirection v3) : {output_path}")

if __name__ == "__main__":
    generate_questions()
