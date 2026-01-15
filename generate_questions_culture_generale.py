import pandas as pd
import os

def generate_questions():
    questions = []
    
    # Structure de base pour toutes les questions
    base_question = {
        'matiere_nom': 'Culture générale',
        'type_question': 'choix_unique',
        'matiere_combinee': 'culture_aptitude',
        'difficulte': 'moyen',
        'temps_limite_secondes': 60,
        'correction_mode': 'exacte',
        'reponse_attendue': ''
    }

    # 1. SPORT
    sport_questions = [
        {
            'lecon_nom': 'Sport',
            'texte_question': 'Quel pays a remporté la Coupe du Monde de la FIFA 2018 ?',
            'choix_a': 'Brésil', 'choix_b': 'Allemagne', 'choix_c': 'France', 'choix_d': 'Argentine',
            'bonne_reponse': 'C',
            'explication': 'La France a remporté la Coupe du Monde 2018 en battant la Croatie 4-2 en finale.'
        },
        {
            'lecon_nom': 'Sport',
            'texte_question': 'Dans quel sport utilise-t-on un "volant" ?',
            'choix_a': 'Tennis', 'choix_b': 'Badminton', 'choix_c': 'Squash', 'choix_d': 'Ping-pong',
            'bonne_reponse': 'B',
            'explication': 'Le volant est le projectile utilisé au badminton.'
        },
        {
            'lecon_nom': 'Sport',
            'texte_question': 'Combien de joueurs y a-t-il dans une équipe de handball sur le terrain ?',
            'choix_a': '5', 'choix_b': '6', 'choix_c': '7', 'choix_d': '11',
            'bonne_reponse': 'C',
            'explication': 'Une équipe de handball se compose de 7 joueurs sur le terrain (6 joueurs de champ et 1 gardien).'
        },
        {
            'lecon_nom': 'Sport',
            'texte_question': 'Qui détient le record du monde du 100 mètres masculin (9,58 s) ?',
            'choix_a': 'Tyson Gay', 'choix_b': 'Usain Bolt', 'choix_c': 'Yohan Blake', 'choix_d': 'Carl Lewis',
            'bonne_reponse': 'B',
            'explication': 'Usain Bolt détient le record du monde du 100m en 9,58 secondes, établi en 2009.'
        },
        {
            'lecon_nom': 'Sport',
            'texte_question': 'Quel tournoi de tennis se joue sur terre battue ?',
            'choix_a': 'Wimbledon', 'choix_b': 'US Open', 'choix_c': 'Roland-Garros', 'choix_d': 'Open d\'Australie',
            'bonne_reponse': 'C',
            'explication': 'Roland-Garros est le seul tournoi du Grand Chelem qui se joue sur terre battue.'
        },
        {
            'lecon_nom': 'Sport',
            'texte_question': 'En quelle année les premiers Jeux Olympiques modernes ont-ils eu lieu ?',
            'choix_a': '1896', 'choix_b': '1900', 'choix_c': '1924', 'choix_d': '1892',
            'bonne_reponse': 'A',
            'explication': 'Les premiers Jeux Olympiques modernes ont eu lieu à Athènes en 1896.'
        },
        {
            'lecon_nom': 'Sport',
            'texte_question': 'Quel pays a organisé la Coupe d\'Afrique des Nations (CAN) 2023 ?',
            'choix_a': 'Cameroun', 'choix_b': 'Égypte', 'choix_c': 'Côte d\'Ivoire', 'choix_d': 'Sénégal',
            'bonne_reponse': 'C',
            'explication': 'La Côte d\'Ivoire a organisé la CAN 2023 (jouée en 2024).'
        },
        {
            'lecon_nom': 'Sport',
            'texte_question': 'Quel est le sport national du Japon ?',
            'choix_a': 'Judo', 'choix_b': 'Sumo', 'choix_c': 'Karaté', 'choix_d': 'Baseball',
            'bonne_reponse': 'B',
            'explication': 'Le Sumo est considéré comme le sport national du Japon.'
        },
        {
            'lecon_nom': 'Sport',
            'texte_question': 'Combien de temps dure un match de football standard (sans arrêts de jeu) ?',
            'choix_a': '60 minutes', 'choix_b': '80 minutes', 'choix_c': '90 minutes', 'choix_d': '100 minutes',
            'bonne_reponse': 'C',
            'explication': 'Un match de football standard dure 90 minutes, divisées en deux mi-temps de 45 minutes.'
        },
        {
            'lecon_nom': 'Sport',
            'texte_question': 'Quel basketteur est surnommé "King James" ?',
            'choix_a': 'Kobe Bryant', 'choix_b': 'Michael Jordan', 'choix_c': 'LeBron James', 'choix_d': 'Stephen Curry',
            'bonne_reponse': 'C',
            'explication': 'LeBron James est surnommé "King James".'
        }
    ]

    # 2. ÉCONOMIE
    economie_questions = [
        {
            'lecon_nom': 'Économie',
            'texte_question': 'Quelle est la monnaie commune de la zone Euro ?',
            'choix_a': 'Livre Sterling', 'choix_b': 'Euro', 'choix_c': 'Dollar', 'choix_d': 'Franc Suisse',
            'bonne_reponse': 'B',
            'explication': 'L\'Euro est la monnaie unique partagée par les pays de la zone euro.'
        },
        {
            'lecon_nom': 'Économie',
            'texte_question': 'Que signifie le sigle PIB ?',
            'choix_a': 'Produit Intérieur Brut', 'choix_b': 'Prix Indice Bancaire', 'choix_c': 'Plan Industriel de Base', 'choix_d': 'Produit International Brut',
            'bonne_reponse': 'A',
            'explication': 'PIB signifie Produit Intérieur Brut, un indicateur économique de la richesse produite par un pays.'
        },
        {
            'lecon_nom': 'Économie',
            'texte_question': 'Quelle organisation internationale gère les règles du commerce mondial ?',
            'choix_a': 'FMI', 'choix_b': 'Banque Mondiale', 'choix_c': 'OMC', 'choix_d': 'OCDE',
            'bonne_reponse': 'C',
            'explication': 'L\'Organisation Mondiale du Commerce (OMC) s\'occupe des règles régissant le commerce entre les pays.'
        },
        {
            'lecon_nom': 'Économie',
            'texte_question': 'Qui est l\'auteur de "La Richesse des Nations" (1776) ?',
            'choix_a': 'Karl Marx', 'choix_b': 'John Maynard Keynes', 'choix_c': 'Adam Smith', 'choix_d': 'David Ricardo',
            'bonne_reponse': 'C',
            'explication': 'Adam Smith est l\'auteur de cet ouvrage fondateur de l\'économie moderne.'
        },
        {
            'lecon_nom': 'Économie',
            'texte_question': 'Quel terme désigne une augmentation générale et durable des prix ?',
            'choix_a': 'Déflation', 'choix_b': 'Inflation', 'choix_c': 'Stagnation', 'choix_d': 'Récession',
            'bonne_reponse': 'B',
            'explication': 'L\'inflation est la perte du pouvoir d\'achat de la monnaie qui se traduit par une augmentation générale et durable des prix.'
        },
        {
            'lecon_nom': 'Économie',
            'texte_question': 'Quelle est la devise du Royaume-Uni ?',
            'choix_a': 'Euro', 'choix_b': 'Dollar', 'choix_c': 'Livre Sterling', 'choix_d': 'Yen',
            'bonne_reponse': 'C',
            'explication': 'La Livre Sterling (Pound Sterling) est la monnaie du Royaume-Uni.'
        },
        {
            'lecon_nom': 'Économie',
            'texte_question': 'Qu\'est-ce que le CAC 40 ?',
            'choix_a': 'Un impôt', 'choix_b': 'Un indice boursier français', 'choix_c': 'Une banque', 'choix_d': 'Une loi économique',
            'bonne_reponse': 'B',
            'explication': 'Le CAC 40 est le principal indice boursier de la place de Paris.'
        },
        {
            'lecon_nom': 'Économie',
            'texte_question': 'Quel pays est la première puissance économique mondiale (PIB) en 2023 ?',
            'choix_a': 'Chine', 'choix_b': 'États-Unis', 'choix_c': 'Inde', 'choix_d': 'Japon',
            'bonne_reponse': 'B',
            'explication': 'Les États-Unis demeurent la première économie mondiale en termes de PIB nominal.'
        },
        {
            'lecon_nom': 'Économie',
            'texte_question': 'Que signifie FMI ?',
            'choix_a': 'Fonds Monétaire International', 'choix_b': 'Fédération Mondiale de l\'Industrie', 'choix_c': 'Force Militaire Internationale', 'choix_d': 'Finance Mondiale Investissement',
            'bonne_reponse': 'A',
            'explication': 'FMI signifie Fonds Monétaire International.'
        },
        {
            'lecon_nom': 'Économie',
            'texte_question': 'Comment appelle-t-on une situation où l\'offre est supérieure à la demande ?',
            'choix_a': 'Pénurie', 'choix_b': 'Surproduction', 'choix_c': 'Équilibre', 'choix_d': 'Inflation',
            'bonne_reponse': 'B',
            'explication': 'Une situation où l\'offre dépasse la demande est une situation de surproduction ou d\'excédent.'
        }
    ]

    # 3. CUISINE
    cuisine_questions = [
        {
            'lecon_nom': 'Cuisine',
            'texte_question': 'Quel est l\'ingrédient principal du guacamole ?',
            'choix_a': 'Tomate', 'choix_b': 'Avocat', 'choix_c': 'Poivron', 'choix_d': 'Oignon',
            'bonne_reponse': 'B',
            'explication': 'L\'avocat est l\'ingrédient de base du guacamole mexicain.'
        },
        {
            'lecon_nom': 'Cuisine',
            'texte_question': 'De quel pays est originaire la paella ?',
            'choix_a': 'Italie', 'choix_b': 'Portugal', 'choix_c': 'Espagne', 'choix_d': 'Mexique',
            'bonne_reponse': 'C',
            'explication': 'La paella est un plat traditionnel originaire d\'Espagne, plus précisément de Valence.'
        },
        {
            'lecon_nom': 'Cuisine',
            'texte_question': 'Quel ingrédient fait lever la pâte à pain ?',
            'choix_a': 'Sucre', 'choix_b': 'Sel', 'choix_c': 'Levure', 'choix_d': 'Farine',
            'bonne_reponse': 'C',
            'explication': 'La levure (boulangère) est l\'agent levant utilisé pour faire gonfler le pain.'
        },
        {
            'lecon_nom': 'Cuisine',
            'texte_question': 'Quelle est la base de la sauce béchamel ?',
            'choix_a': 'Huile et vinaigre', 'choix_b': 'Beurre, farine et lait', 'choix_c': 'Tomate et oignon', 'choix_d': 'Crème fraîche et œufs',
            'bonne_reponse': 'B',
            'explication': 'La béchamel est réalisée à partir d\'un roux (beurre + farine) cuit avec du lait.'
        },
        {
            'lecon_nom': 'Cuisine',
            'texte_question': 'Quel est le plat national de la Côte d\'Ivoire composé de semoule de manioc ?',
            'choix_a': 'Foutou', 'choix_b': 'Attiéké', 'choix_c': 'Alloco', 'choix_d': 'Placali',
            'bonne_reponse': 'B',
            'explication': 'L\'Attiéké est un mets traditionnel ivoirien fait à base de semoule de manioc fermentée.'
        },
        {
            'lecon_nom': 'Cuisine',
            'texte_question': 'Qu\'est-ce que le tofu ?',
            'choix_a': 'Du fromage de chèvre', 'choix_b': 'De la pâte de soja', 'choix_c': 'Du pain de riz', 'choix_d': 'Une algue',
            'bonne_reponse': 'B',
            'explication': 'Le tofu est un aliment d\'origine chinoise, issu du caillage du lait de soja.'
        },
        {
            'lecon_nom': 'Cuisine',
            'texte_question': 'Quel fruit est utilisé pour produire le vin ?',
            'choix_a': 'Pomme', 'choix_b': 'Cerise', 'choix_c': 'Raisin', 'choix_d': 'Prune',
            'bonne_reponse': 'C',
            'explication': 'Le vin est une boisson alcoolisée obtenue par la fermentation du raisin.'
        },
        {
            'lecon_nom': 'Cuisine',
            'texte_question': 'Quel est l\'épice la plus chère au monde ?',
            'choix_a': 'Vanille', 'choix_b': 'Safran', 'choix_c': 'Cardamome', 'choix_d': 'Cannelle',
            'bonne_reponse': 'B',
            'explication': 'Le safran est l\'épice la plus chère au monde, extraite d\'une variété de crocus.'
        },
        {
            'lecon_nom': 'Cuisine',
            'texte_question': 'Comment appelle-t-on la cuisson des aliments à la vapeur ?',
            'choix_a': 'Friture', 'choix_b': 'Braisage', 'choix_c': 'Cuisson à l\'étouffée', 'choix_d': 'Cuisson vapeur',
            'bonne_reponse': 'D',
            'explication': 'La cuisson vapeur consiste à cuire les aliments grâce à la vapeur d\'eau bouillante.'
        },
        {
            'lecon_nom': 'Cuisine',
            'texte_question': 'Quel poisson est l\'ingrédient principal du "tiep bou dien" sénégalais ?',
            'choix_a': 'Poulet', 'choix_b': 'Bœuf', 'choix_c': 'Poisson (Mérou)', 'choix_d': 'Crevettes',
            'bonne_reponse': 'C',
            'explication': 'Le tiep bou dien (riz au poisson) est préparé traditionnellement avec du poisson, souvent du mérou (thiof).'
        }
    ]

    # 4. MÉDECINE
    medecine_questions = [
        {
            'lecon_nom': 'Médecine',
            'texte_question': 'Quel est l\'organe principal du système circulatoire ?',
            'choix_a': 'Poumon', 'choix_b': 'Cerveau', 'choix_c': 'Cœur', 'choix_d': 'Foie',
            'bonne_reponse': 'C',
            'explication': 'Le cœur est le moteur du système circulatoire, pompant le sang dans tout le corps.'
        },
        {
            'lecon_nom': 'Médecine',
            'texte_question': 'Combien de dents un adulte humain possède-t-il en général (dents de sagesse comprises) ?',
            'choix_a': '28', 'choix_b': '30', 'choix_c': '32', 'choix_d': '34',
            'bonne_reponse': 'C',
            'explication': 'Une dentition adulte complète comporte 32 dents.'
        },
        {
            'lecon_nom': 'Médecine',
            'texte_question': 'Quelle molécule transporte l\'oxygène dans le sang ?',
            'choix_a': 'Insuline', 'choix_b': 'Hémoglobine', 'choix_c': 'Collagène', 'choix_d': 'Adrénaline',
            'bonne_reponse': 'B',
            'explication': 'L\'hémoglobine, présente dans les globules rouges, transporte l\'oxygène des poumons vers les tissus.'
        },
        {
            'lecon_nom': 'Médecine',
            'texte_question': 'Quel organe produit l\'insuline ?',
            'choix_a': 'Foie', 'choix_b': 'Pancréas', 'choix_c': 'Rein', 'choix_d': 'Estomac',
            'bonne_reponse': 'B',
            'explication': 'Le pancréas produit l\'insuline, hormone régulant le taux de sucre dans le sang.'
        },
        {
            'lecon_nom': 'Médecine',
            'texte_question': 'Qu\'est-ce qu\'un antibiotique combat ?',
            'choix_a': 'Les virus', 'choix_b': 'Les bactéries', 'choix_c': 'Les champignons', 'choix_d': 'Les parasites',
            'bonne_reponse': 'B',
            'explication': 'Les antibiotiques sont des médicaments utilisés pour traiter les infections bactériennes.'
        },
        {
            'lecon_nom': 'Médecine',
            'texte_question': 'Quel est le plus grand organe du corps humain ?',
            'choix_a': 'Le foie', 'choix_b': 'La peau', 'choix_c': 'Le cerveau', 'choix_d': 'L\'intestin',
            'bonne_reponse': 'B',
            'explication': 'La peau est l\'organe le plus étendu et le plus lourd du corps humain.'
        },
        {
            'lecon_nom': 'Médecine',
            'texte_question': 'Quelle vitamine est principalement synthétisée grâce au soleil ?',
            'choix_a': 'Vitamine A', 'choix_b': 'Vitamine C', 'choix_c': 'Vitamine D', 'choix_d': 'Vitamine E',
            'bonne_reponse': 'C',
            'explication': 'La vitamine D est synthétisée par la peau sous l\'action des rayons ultraviolets du soleil.'
        },
        {
            'lecon_nom': 'Médecine',
            'texte_question': 'Quel médecin est spécialiste des enfants ?',
            'choix_a': 'Gériatre', 'choix_b': 'Pédiatre', 'choix_c': 'Cardiologue', 'choix_d': 'Dermatologue',
            'bonne_reponse': 'B',
            'explication': 'Le pédiatre est le médecin spécialiste de la santé des enfants.'
        },
        {
            'lecon_nom': 'Médecine',
            'texte_question': 'Quel est le groupe sanguin "donneur universel" ?',
            'choix_a': 'A+', 'choix_b': 'AB+', 'choix_c': 'O-', 'choix_d': 'B-',
            'bonne_reponse': 'C',
            'explication': 'Le groupe O négatif (O-) est considéré comme donneur universel pour les globules rouges.'
        },
        {
            'lecon_nom': 'Médecine',
            'texte_question': 'Comment appelle-t-on l\'inflammation de l\'appendice ?',
            'choix_a': 'Gastrite', 'choix_b': 'Appendicite', 'choix_c': 'Colite', 'choix_d': 'Hépatite',
            'bonne_reponse': 'B',
            'explication': 'L\'appendicite est l\'inflammation aiguë de l\'appendice vermiforme.'
        }
    ]

    # 5. SCIENCES ET TECHNIQUES
    sciences_questions = [
        {
            'lecon_nom': 'Sciences et techniques',
            'texte_question': 'Quelle est la planète la plus proche du Soleil ?',
            'choix_a': 'Vénus', 'choix_b': 'Terre', 'choix_c': 'Mercure', 'choix_d': 'Mars',
            'bonne_reponse': 'C',
            'explication': 'Mercure est la planète la plus proche du Soleil dans notre système solaire.'
        },
        {
            'lecon_nom': 'Sciences et techniques',
            'texte_question': 'Quelle est la formule chimique de l\'eau ?',
            'choix_a': 'CO2', 'choix_b': 'H2O', 'choix_c': 'O2', 'choix_d': 'NaCl',
            'bonne_reponse': 'B',
            'explication': 'H2O signifie que la molécule d\'eau est composée de deux atomes d\'hydrogène et d\'un atome d\'oxygène.'
        },
        {
            'lecon_nom': 'Sciences et techniques',
            'texte_question': 'Qui a formulé la théorie de la relativité générale ?',
            'choix_a': 'Isaac Newton', 'choix_b': 'Albert Einstein', 'choix_c': 'Galilée', 'choix_d': 'Nikola Tesla',
            'bonne_reponse': 'B',
            'explication': 'Albert Einstein a publié la théorie de la relativité générale en 1915.'
        },
        {
            'lecon_nom': 'Sciences et techniques',
            'texte_question': 'Quel gaz les plantes absorbent-elles principalement pour la photosynthèse ?',
            'choix_a': 'Oxygène', 'choix_b': 'Azote', 'choix_c': 'Dioxyde de carbone (CO2)', 'choix_d': 'Hydrogène',
            'bonne_reponse': 'C',
            'explication': 'Les plantes absorbent le dioxyde de carbone (CO2) pour produire de l\'énergie via la photosynthèse.'
        },
        {
            'lecon_nom': 'Sciences et techniques',
            'texte_question': 'Quel est l\'élément chimique de symbole "Fe" ?',
            'choix_a': 'Fer', 'choix_b': 'Fluor', 'choix_c': 'Francium', 'choix_d': 'Fermium',
            'bonne_reponse': 'A',
            'explication': 'Fe est le symbole chimique du Fer (du latin Ferrum).'
        },
        {
            'lecon_nom': 'Sciences et techniques',
            'texte_question': 'Quelle est la vitesse de la lumière dans le vide ?',
            'choix_a': '300 000 km/s', 'choix_b': '150 000 km/s', 'choix_c': '1 000 km/s', 'choix_d': '340 m/s',
            'bonne_reponse': 'A',
            'explication': 'La vitesse de la lumière dans le vide est d\'environ 300 000 km/s (exactement 299 792 458 m/s).'
        },
        {
            'lecon_nom': 'Sciences et techniques',
            'texte_question': 'Qui a inventé le téléphone ?',
            'choix_a': 'Thomas Edison', 'choix_b': 'Alexander Graham Bell', 'choix_c': 'Guglielmo Marconi', 'choix_d': 'Samuel Morse',
            'bonne_reponse': 'B',
            'explication': 'Alexander Graham Bell est crédité de l\'invention du téléphone en 1876.'
        },
        {
            'lecon_nom': 'Sciences et techniques',
            'texte_question': 'Quelle force nous maintient au sol sur Terre ?',
            'choix_a': 'La force magnétique', 'choix_b': 'La force centrifuge', 'choix_c': 'La gravité', 'choix_d': 'La force nucléaire',
            'bonne_reponse': 'C',
            'explication': 'La gravité (ou gravitation) est la force qui attire les corps massifs entre eux, nous maintenant sur Terre.'
        },
        {
            'lecon_nom': 'Sciences et techniques',
            'texte_question': 'Quel est le composant principal de l\'air que nous respirons ?',
            'choix_a': 'Oxygène', 'choix_b': 'Azote', 'choix_c': 'Dioxyde de carbone', 'choix_d': 'Argon',
            'bonne_reponse': 'B',
            'explication': 'L\'atmosphère terrestre est composée à environ 78% d\'azote.'
        },
        {
            'lecon_nom': 'Sciences et techniques',
            'texte_question': 'Que mesure un thermomètre ?',
            'choix_a': 'La pression', 'choix_b': 'L\'humidité', 'choix_c': 'La température', 'choix_d': 'La vitesse du vent',
            'bonne_reponse': 'C',
            'explication': 'Le thermomètre est l\'instrument destiné à la mesure de la température.'
        }
    ]

    # 6. GÉOGRAPHIE
    geographie_questions = [
        {
            'lecon_nom': 'Géographie',
            'texte_question': 'Quel est le plus grand pays du monde par sa superficie ?',
            'choix_a': 'Chine', 'choix_b': 'États-Unis', 'choix_c': 'Russie', 'choix_d': 'Canada',
            'bonne_reponse': 'C',
            'explication': 'La Russie est le plus grand pays du monde avec une superficie de plus de 17 millions de km².'
        },
        {
            'lecon_nom': 'Géographie',
            'texte_question': 'Quelle est la capitale de l\'Australie ?',
            'choix_a': 'Sydney', 'choix_b': 'Melbourne', 'choix_c': 'Canberra', 'choix_d': 'Brisbane',
            'bonne_reponse': 'C',
            'explication': 'Canberra est la capitale fédérale de l\'Australie, choisie comme compromis entre Sydney et Melbourne.'
        },
        {
            'lecon_nom': 'Géographie',
            'texte_question': 'Sur quel continent se trouve le désert du Sahara ?',
            'choix_a': 'Asie', 'choix_b': 'Afrique', 'choix_c': 'Amérique du Sud', 'choix_d': 'Australie',
            'bonne_reponse': 'B',
            'explication': 'Le Sahara est le plus grand désert chaud du monde, situé en Afrique du Nord.'
        },
        {
            'lecon_nom': 'Géographie',
            'texte_question': 'Quel est le plus long fleuve du monde ?',
            'choix_a': 'Le Nil', 'choix_b': 'L\'Amazone', 'choix_c': 'Le Yangzi Jiang', 'choix_d': 'Le Mississippi',
            'bonne_reponse': 'B',
            'explication': 'L\'Amazone est généralement considéré comme le plus long fleuve du monde (selon les mesures les plus récentes).'
        },
        {
            'lecon_nom': 'Géographie',
            'texte_question': 'Combien y a-t-il d\'océans sur Terre ?',
            'choix_a': '3', 'choix_b': '4', 'choix_c': '5', 'choix_d': '6',
            'bonne_reponse': 'C',
            'explication': 'Il y a 5 océans : Pacifique, Atlantique, Indien, Arctique et Austral (Antarctique).'
        },
        {
            'lecon_nom': 'Géographie',
            'texte_question': 'Quelle est la capitale de la Côte d\'Ivoire ?',
            'choix_a': 'Abidjan', 'choix_b': 'Yamoussoukro', 'choix_c': 'Bouaké', 'choix_d': 'San-Pédro',
            'bonne_reponse': 'B',
            'explication': 'Yamoussoukro est la capitale politique et administrative de la Côte d\'Ivoire depuis 1983.'
        },
        {
            'lecon_nom': 'Géographie',
            'texte_question': 'Dans quel pays se trouve la Tour Eiffel ?',
            'choix_a': 'Italie', 'choix_b': 'Espagne', 'choix_c': 'Allemagne', 'choix_d': 'France',
            'bonne_reponse': 'D',
            'explication': 'La Tour Eiffel est située à Paris, en France.'
        },
        {
            'lecon_nom': 'Géographie',
            'texte_question': 'Quel pays a la forme d\'une botte ?',
            'choix_a': 'Grèce', 'choix_b': 'Italie', 'choix_c': 'Espagne', 'choix_d': 'Portugal',
            'bonne_reponse': 'B',
            'explication': 'L\'Italie est souvent décrite comme ayant la forme d\'une botte sur la carte.'
        },
        {
            'lecon_nom': 'Géographie',
            'texte_question': 'Quel est le plus haut sommet du monde ?',
            'choix_a': 'Mont Blanc', 'choix_b': 'Kilimandjaro', 'choix_c': 'Mont Everest', 'choix_d': 'K2',
            'bonne_reponse': 'C',
            'explication': 'Le Mont Everest, dans l\'Himalaya, est le plus haut sommet du monde (8 848 m).'
        },
        {
            'lecon_nom': 'Géographie',
            'texte_question': 'Quelle mer sépare l\'Europe de l\'Afrique ?',
            'choix_a': 'La mer Noire', 'choix_b': 'La mer Rouge', 'choix_c': 'La mer Méditerranée', 'choix_d': 'La mer Caspienne',
            'bonne_reponse': 'C',
            'explication': 'La mer Méditerranée sépare l\'Europe au nord de l\'Afrique au sud.'
        }
    ]

    # 7. HISTOIRE
    histoire_questions = [
        {
            'lecon_nom': 'Histoire',
            'texte_question': 'En quelle année a eu lieu la Révolution française ?',
            'choix_a': '1776', 'choix_b': '1789', 'choix_c': '1815', 'choix_d': '1848',
            'bonne_reponse': 'B',
            'explication': 'La Révolution française a débuté en 1789 avec la prise de la Bastille.'
        },
        {
            'lecon_nom': 'Histoire',
            'texte_question': 'Qui fut le premier président de la République de Côte d\'Ivoire ?',
            'choix_a': 'Henri Konan Bédié', 'choix_b': 'Laurent Gbagbo', 'choix_c': 'Félix Houphouët-Boigny', 'choix_d': 'Alassane Ouattara',
            'bonne_reponse': 'C',
            'explication': 'Félix Houphouët-Boigny a été le père de l\'indépendance et le premier président de la Côte d\'Ivoire.'
        },
        {
            'lecon_nom': 'Histoire',
            'texte_question': 'Quelle guerre s\'est déroulée de 1914 à 1918 ?',
            'choix_a': 'La guerre de Sécession', 'choix_b': 'La Première Guerre mondiale', 'choix_c': 'La Seconde Guerre mondiale', 'choix_d': 'La guerre du Vietnam',
            'bonne_reponse': 'B',
            'explication': 'La Première Guerre mondiale a eu lieu de 1914 à 1918.'
        },
        {
            'lecon_nom': 'Histoire',
            'texte_question': 'Qui a découvert l\'Amérique en 1492 ?',
            'choix_a': 'Vasco de Gama', 'choix_b': 'Christophe Colomb', 'choix_c': 'Fernand de Magellan', 'choix_d': 'Jacques Cartier',
            'bonne_reponse': 'B',
            'explication': 'Christophe Colomb est arrivé en Amérique en 1492.'
        },
        {
            'lecon_nom': 'Histoire',
            'texte_question': 'Quel empereur français est mort à Sainte-Hélène ?',
            'choix_a': 'Louis XIV', 'choix_b': 'Napoléon Ier', 'choix_c': 'Napoléon III', 'choix_d': 'Charlemagne',
            'bonne_reponse': 'B',
            'explication': 'Napoléon Bonaparte (Napoléon Ier) est mort en exil sur l\'île de Sainte-Hélène en 1821.'
        },
        {
            'lecon_nom': 'Histoire',
            'texte_question': 'En quelle année le mur de Berlin est-il tombé ?',
            'choix_a': '1987', 'choix_b': '1989', 'choix_c': '1991', 'choix_d': '1993',
            'bonne_reponse': 'B',
            'explication': 'La chute du mur de Berlin a eu lieu le 9 novembre 1989.'
        },
        {
            'lecon_nom': 'Histoire',
            'texte_question': 'Qui était le pharaon de l\'Égypte ancienne célèbre pour son masque en or ?',
            'choix_a': 'Ramsès II', 'choix_b': 'Khéops', 'choix_c': 'Toutankhamon', 'choix_d': 'Akhenaton',
            'bonne_reponse': 'C',
            'explication': 'Toutankhamon est célèbre pour la découverte de son tombeau intact et de son masque funéraire en or.'
        },
        {
            'lecon_nom': 'Histoire',
            'texte_question': 'Quel événement marque le début de la Seconde Guerre mondiale ?',
            'choix_a': 'L\'invasion de la Pologne', 'choix_b': 'L\'attaque de Pearl Harbor', 'choix_c': 'Le débarquement de Normandie', 'choix_d': 'La bataille de Stalingrad',
            'bonne_reponse': 'A',
            'explication': 'L\'invasion de la Pologne par l\'Allemagne le 1er septembre 1939 marque le début de la guerre.'
        },
        {
            'lecon_nom': 'Histoire',
            'texte_question': 'Qui a prononcé le discours "I Have a Dream" ?',
            'choix_a': 'Malcolm X', 'choix_b': 'Nelson Mandela', 'choix_c': 'Martin Luther King', 'choix_d': 'Barack Obama',
            'bonne_reponse': 'C',
            'explication': 'Martin Luther King a prononcé ce discours célèbre en 1963 à Washington.'
        },
        {
            'lecon_nom': 'Histoire',
            'texte_question': 'En quelle année l\'homme a-t-il marché sur la Lune pour la première fois ?',
            'choix_a': '1965', 'choix_b': '1969', 'choix_c': '1972', 'choix_d': '1961',
            'bonne_reponse': 'B',
            'explication': 'Neil Armstrong a marché sur la Lune le 21 juillet 1969 lors de la mission Apollo 11.'
        }
    ]

    # 8. LITTÉRATURE
    litterature_questions = [
        {
            'lecon_nom': 'Littérature',
            'texte_question': 'Qui a écrit "Les Misérables" ?',
            'choix_a': 'Émile Zola', 'choix_b': 'Victor Hugo', 'choix_c': 'Gustave Flaubert', 'choix_d': 'Honoré de Balzac',
            'bonne_reponse': 'B',
            'explication': 'Victor Hugo est l\'auteur du roman "Les Misérables", publié en 1862.'
        },
        {
            'lecon_nom': 'Littérature',
            'texte_question': 'Quel auteur ivoirien a écrit "Cahier d\'un retour au pays natal" ?',
            'choix_a': 'Ahmadou Kourouma', 'choix_b': 'Bernard Dadié', 'choix_c': 'Aimé Césaire', 'choix_d': 'Léopold Sédar Senghor',
            'bonne_reponse': 'C',
            'explication': 'Attention au piège : Aimé Césaire est Martiniquais, mais l\'œuvre est majeure dans la littérature francophone noire. Bernard Dadié est un célèbre auteur ivoirien ("Climbié").'
        },
        {
            'lecon_nom': 'Littérature',
            'texte_question': 'Qui a écrit "L\'Étranger" ?',
            'choix_a': 'Jean-Paul Sartre', 'choix_b': 'Albert Camus', 'choix_c': 'Marcel Proust', 'choix_d': 'André Gide',
            'bonne_reponse': 'B',
            'explication': 'Albert Camus a publié "L\'Étranger" en 1942.'
        },
        {
            'lecon_nom': 'Littérature',
            'texte_question': 'Quel est le dramaturge anglais auteur de "Roméo et Juliette" ?',
            'choix_a': 'Charles Dickens', 'choix_b': 'William Shakespeare', 'choix_c': 'Oscar Wilde', 'choix_d': 'Jane Austen',
            'bonne_reponse': 'B',
            'explication': 'William Shakespeare est l\'auteur de la tragédie "Roméo et Juliette".'
        },
        {
            'lecon_nom': 'Littérature',
            'texte_question': 'Qui a écrit "Le Petit Prince" ?',
            'choix_a': 'Jules Verne', 'choix_b': 'Antoine de Saint-Exupéry', 'choix_c': 'Jean de la Fontaine', 'choix_d': 'Charles Perrault',
            'bonne_reponse': 'B',
            'explication': 'Antoine de Saint-Exupéry a écrit et illustré "Le Petit Prince" (1943).'
        },
        {
            'lecon_nom': 'Littérature',
            'texte_question': 'Qui est l\'auteur de "L\'Enfant noir" ?',
            'choix_a': 'Camara Laye', 'choix_b': 'Chinua Achebe', 'choix_c': 'Cheikh Hamidou Kane', 'choix_d': 'Mongo Beti',
            'bonne_reponse': 'A',
            'explication': 'Camara Laye, auteur guinéen, a publié "L\'Enfant noir" en 1953.'
        },
        {
            'lecon_nom': 'Littérature',
            'texte_question': 'Dans quelle série de romans trouve-t-on le personnage de Harry Potter ?',
            'choix_a': 'Le Seigneur des Anneaux', 'choix_b': 'Harry Potter', 'choix_c': 'Narnia', 'choix_d': 'Percy Jackson',
            'bonne_reponse': 'B',
            'explication': 'Harry Potter est le héros de la saga écrite par J.K. Rowling.'
        },
        {
            'lecon_nom': 'Littérature',
            'texte_question': 'Qui a écrit "Madame Bovary" ?',
            'choix_a': 'Gustave Flaubert', 'choix_b': 'Stendhal', 'choix_c': 'Maupassant', 'choix_d': 'George Sand',
            'bonne_reponse': 'A',
            'explication': 'Gustave Flaubert est l\'auteur de "Madame Bovary" (1857).'
        },
        {
            'lecon_nom': 'Littérature',
            'texte_question': 'Quel prix littéraire prestigieux est décerné chaque année en France en automne ?',
            'choix_a': 'Le prix Pulitzer', 'choix_b': 'Le prix Goncourt', 'choix_c': 'Le prix Nobel', 'choix_d': 'Le prix Booker',
            'bonne_reponse': 'B',
            'explication': 'Le prix Goncourt est le prix littéraire français le plus prestigieux, décerné en novembre.'
        },
        {
            'lecon_nom': 'Littérature',
            'texte_question': 'Qui est l\'auteur des "Fables" (Le Corbeau et le Renard...) ?',
            'choix_a': 'Molière', 'choix_b': 'Jean de La Fontaine', 'choix_c': 'Voltaire', 'choix_d': 'Racine',
            'bonne_reponse': 'B',
            'explication': 'Jean de La Fontaine est célèbre pour ses Fables inspirées d\'Ésope.'
        }
    ]

    # 9. TRADITION
    tradition_questions = [
        {
            'lecon_nom': 'Tradition',
            'texte_question': 'En Côte d\'Ivoire, quelle fête célèbre la génération chez les peuples lagunaires ?',
            'choix_a': 'L\'Abissa', 'choix_b': 'Le Popo Carnaval', 'choix_c': 'La Fête des Ignames', 'choix_d': 'Le Dipri',
            'bonne_reponse': 'A',
            'explication': 'L\'Abissa est une fête traditionnelle de réjouissance et de critique sociale chez les N\'zima (Grand-Bassam).'
        },
        {
            'lecon_nom': 'Tradition',
            'texte_question': 'Quel est le tissu traditionnel emblématique du peuple Akan (Ghana/Côte d\'Ivoire) ?',
            'choix_a': 'Le Bazin', 'choix_b': 'Le Kente (ou Kita)', 'choix_c': 'Le Bogolan', 'choix_d': 'Le Wax',
            'bonne_reponse': 'B',
            'explication': 'Le Kente (ou Kita en Côte d\'Ivoire) est le tissu royal des peuples Akan.'
        },
        {
            'lecon_nom': 'Tradition',
            'texte_question': 'Qu\'est-ce que la "dot" dans le mariage traditionnel africain ?',
            'choix_a': 'Un repas', 'choix_b': 'Une danse', 'choix_c': 'Des présents offerts par la famille du marié', 'choix_d': 'Un vêtement',
            'bonne_reponse': 'C',
            'explication': 'La dot constitue l\'ensemble des biens ou de l\'argent remis par la famille du futur époux à celle de la fiancée.'
        },
        {
            'lecon_nom': 'Tradition',
            'texte_question': 'Que symbolise le masque "Zaouli" en Côte d\'Ivoire ?',
            'choix_a': 'La guerre', 'choix_b': 'La beauté féminine', 'choix_c': 'La pluie', 'choix_d': 'La sagesse',
            'bonne_reponse': 'B',
            'explication': 'Le Zaouli, masque Gouro, rend hommage à la beauté féminine.'
        },
        {
            'lecon_nom': 'Tradition',
            'texte_question': 'Quel instrument de musique est souvent utilisé par les griots en Afrique de l\'Ouest ?',
            'choix_a': 'Le piano', 'choix_b': 'La Kora', 'choix_c': 'Le violon', 'choix_d': 'La guitare électrique',
            'bonne_reponse': 'B',
            'explication': 'La Kora est un instrument à cordes traditionnel emblématique des griots mandingues.'
        },
        {
            'lecon_nom': 'Tradition',
            'texte_question': 'Quelle fête marque le nouvel an chez les Agni (fête des ignames) ?',
            'choix_a': 'Paquinou', 'choix_b': 'L\'Abissa', 'choix_c': 'La fête des Ignames', 'choix_d': 'Le Ramadan',
            'bonne_reponse': 'C',
            'explication': 'La fête des Ignames célèbre la nouvelle récolte et marque le début de la nouvelle année en pays Akan.'
        },
        {
            'lecon_nom': 'Tradition',
            'texte_question': 'Que représente le "Poro" en pays Sénoufo ?',
            'choix_a': 'Une danse', 'choix_b': 'Un marché', 'choix_c': 'Une société initiatique', 'choix_d': 'Un plat',
            'bonne_reponse': 'C',
            'explication': 'Le Poro est une institution initiatique sociale et religieuse fondamentale chez les Sénoufo.'
        },
        {
            'lecon_nom': 'Tradition',
            'texte_question': 'Quel arbre est souvent considéré comme l\'arbre à palabres en Afrique ?',
            'choix_a': 'Le cocotier', 'choix_b': 'Le baobab', 'choix_c': 'L\'hévéa', 'choix_d': 'Le manguier',
            'bonne_reponse': 'B',
            'explication': 'Le baobab est souvent le lieu de rassemblement et de discussion (l\'arbre à palabres) dans de nombreux villages.'
        },
        {
            'lecon_nom': 'Tradition',
            'texte_question': 'Qu\'est-ce qu\'un "Griot" ?',
            'choix_a': 'Un guerrier', 'choix_b': 'Un conteur et gardien de la tradition orale', 'choix_c': 'Un forgeron', 'choix_d': 'Un chasseur',
            'bonne_reponse': 'B',
            'explication': 'Le griot est le dépositaire de la tradition orale, historien, conteur et musicien.'
        },
        {
            'lecon_nom': 'Tradition',
            'texte_question': 'Quelle est la signification du proverbe "Petit à petit, l\'oiseau fait son nid" ?',
            'choix_a': 'Il faut se dépêcher', 'choix_b': 'La patience et la persévérance mènent au succès', 'choix_c': 'Les oiseaux sont lents', 'choix_d': 'Il faut construire une maison',
            'bonne_reponse': 'B',
            'explication': 'Ce proverbe vante les mérites de la patience et de la persévérance pour accomplir de grandes choses.'
        }
    ]

    # 10. RELIGION
    religion_questions = [
        {
            'lecon_nom': 'Religion',
            'texte_question': 'Quel est le livre sacré de l\'Islam ?',
            'choix_a': 'La Bible', 'choix_b': 'La Torah', 'choix_c': 'Le Coran', 'choix_d': 'Les Védas',
            'bonne_reponse': 'C',
            'explication': 'Le Coran est le livre sacré des musulmans.'
        },
        {
            'lecon_nom': 'Religion',
            'texte_question': 'Qui est le fondateur du Christianisme ?',
            'choix_a': 'Moïse', 'choix_b': 'Jésus de Nazareth', 'choix_c': 'Mahomet', 'choix_d': 'Bouddha',
            'bonne_reponse': 'B',
            'explication': 'Le christianisme est fondé sur la vie et les enseignements de Jésus de Nazareth.'
        },
        {
            'lecon_nom': 'Religion',
            'texte_question': 'Quel jour est le jour saint hebdomadaire dans le Judaïsme ?',
            'choix_a': 'Vendredi', 'choix_b': 'Dimanche', 'choix_c': 'Shabbat (Samedi)', 'choix_d': 'Lundi',
            'bonne_reponse': 'C',
            'explication': 'Le Shabbat, qui commence le vendredi soir et finit le samedi soir, est le jour de repos hebdomadaire juif.'
        },
        {
            'lecon_nom': 'Religion',
            'texte_question': 'Où se trouve le Vatican, siège de l\'Église catholique ?',
            'choix_a': 'En France', 'choix_b': 'À Rome (Italie)', 'choix_c': 'En Espagne', 'choix_d': 'À Jérusalem',
            'bonne_reponse': 'B',
            'explication': 'Le Vatican est un État enclavé dans la ville de Rome, en Italie.'
        },
        {
            'lecon_nom': 'Religion',
            'texte_question': 'Quel prophète est central dans l\'Islam ?',
            'choix_a': 'Abraham', 'choix_b': 'Mahomet (Muhammad)', 'choix_c': 'Noé', 'choix_d': 'David',
            'bonne_reponse': 'B',
            'explication': 'Mahomet est considéré comme le dernier prophète dans l\'Islam.'
        },
        {
            'lecon_nom': 'Religion',
            'texte_question': 'Quelle religion est associée au cycle des réincarnations et au Karma ?',
            'choix_a': 'Christianisme', 'choix_b': 'Islam', 'choix_c': 'Bouddhisme / Hindouisme', 'choix_d': 'Judaïsme',
            'bonne_reponse': 'C',
            'explication': 'L\'Hindouisme et le Bouddhisme partagent les concepts de réincarnation et de Karma.'
        },
        {
            'lecon_nom': 'Religion',
            'texte_question': 'Que célèbrent les Chrétiens à Noël ?',
            'choix_a': 'La résurrection de Jésus', 'choix_b': 'La naissance de Jésus', 'choix_c': 'La descente de l\'Esprit Saint', 'choix_d': 'La fin de l\'année',
            'bonne_reponse': 'B',
            'explication': 'Noël commémore la naissance de Jésus.'
        },
        {
            'lecon_nom': 'Religion',
            'texte_question': 'Quel est le lieu de culte des Juifs ?',
            'choix_a': 'Église', 'choix_b': 'Mosquée', 'choix_c': 'Synagogue', 'choix_d': 'Temple bouddhiste',
            'bonne_reponse': 'C',
            'explication': 'La synagogue est le lieu de culte et d\'étude dans le judaïsme.'
        },
        {
            'lecon_nom': 'Religion',
            'texte_question': 'Qu\'est-ce que le Ramadan ?',
            'choix_a': 'Une fête de fin d\'année', 'choix_b': 'Le mois de jeûne dans l\'Islam', 'choix_c': 'Un pèlerinage', 'choix_d': 'Une prière quotidienne',
            'bonne_reponse': 'B',
            'explication': 'Le Ramadan est le neuvième mois du calendrier hégirien, marqué par le jeûne quotidien.'
        },
        {
            'lecon_nom': 'Religion',
            'texte_question': 'Combien de piliers compte l\'Islam ?',
            'choix_a': '3', 'choix_b': '5', 'choix_c': '7', 'choix_d': '10',
            'bonne_reponse': 'B',
            'explication': 'L\'Islam repose sur 5 piliers : la profession de foi, la prière, l\'aumône, le jeûne du Ramadan et le pèlerinage à La Mecque.'
        }
    ]

    all_questions = (sport_questions + economie_questions + cuisine_questions + 
                     medecine_questions + sciences_questions + geographie_questions + 
                     histoire_questions + litterature_questions + tradition_questions + 
                     religion_questions)

    # Fusionner avec les données de base
    final_data = []
    for q in all_questions:
        q_data = base_question.copy()
        q_data.update(q)
        final_data.append(q_data)

    df = pd.DataFrame(final_data)
    
    # Colonnes dans l'ordre attendu par le template
    columns = [
        'matiere_nom', 'lecon_nom', 'texte_question', 'type_question', 'matiere_combinee',
        'choix_a', 'choix_b', 'choix_c', 'choix_d', 'choix_e',
        'bonne_reponse', 'reponse_attendue', 'explication', 'difficulte',
        'temps_limite_secondes', 'correction_mode'
    ]
    
    # Ajouter les colonnes manquantes si nécessaire
    for col in columns:
        if col not in df.columns:
            df[col] = ''
            
    df = df[columns]
    
    output_path = r'C:\Users\HP\Desktop\questionnaires_v2.xlsx'
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Questions_ENA_Exemples', index=False)
        print(f"Fichier généré avec succès : {output_path}")

if __name__ == "__main__":
    generate_questions()
