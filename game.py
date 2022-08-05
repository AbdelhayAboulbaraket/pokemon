import random
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from models import BasePokemon, Dresseur, Pokemon, creer_dresseur
from random import randrange

def afficher_pokemon(pokemon):
    '''
    Affiche un pokémon, ses caractéristiques et ses compétences.
    '''  
    print(f'''{pokemon.basepokemon.nom}(Lvl {pokemon.niveau}, {100*pokemon.niveau + pokemon.experience}/{100*(pokemon.niveau+1)}, {pokemon.basepokemon.element}): Vie {pokemon.vie_courante}/{pokemon.vie}, Energie {pokemon.energie_courante}/{pokemon.energie} (+{pokemon.regeneration}), Resistance {pokemon.resistance}\n{', '.join([competence.nom for competence in pokemon.basepokemon.competences])}\n''')
    for index, competence in enumerate(pokemon.basepokemon.competences):
        print(f'{index}/ {competence.nom} ({competence.type}, {competence.element}, {competence.cout_energie}): {competence.description}')
def afficher_pokemons(pokemons):
    '''
    Affiche plusieurs pokémons, leurs caractéristiques et leurs compétences.
    '''
    for index, pokemon in enumerate(pokemons):
        print(f'''{index}/ {pokemon.basepokemon.nom}(Lvl {pokemon.niveau}, {100*pokemon.niveau + pokemon.experience}/{100*(pokemon.niveau+1)}, {pokemon.basepokemon.element}): Vie {pokemon.vie_courante if hasattr(pokemon, 'vie_courante') else pokemon.vie}/{pokemon.vie}, Energie {pokemon.energie}/{pokemon.energie} (+{pokemon.regeneration}), Resistance {pokemon.resistance}\n{', '.join([competence.nom for competence in pokemon.basepokemon.competences])}. {"(Mort)" if hasattr(pokemon, 'statut') and pokemon.statut == "Mort" else ""}\n''')

while True:
    nom_utilisateur = input('Entrez le nom d\'utilisateur :')
    mot_de_passe = input("Entrez votre mot de passe: ")
    try:
        engine = create_engine(f'mysql+mysqldb://{nom_utilisateur}:{mot_de_passe}@localhost:3306/pokemon', )
        Session = sessionmaker(bind=engine, autoflush=False)
        session = Session()
        session.query(Pokemon).all()
    except Exception:
        print("Nom d'utilisateur ou mot de passe erroné!")
        continue
    break



# Les coefficients multiplicateur mentionné dans le PDF. Ils servent pour le calcul des degats d'une compétence. 
coefficients_multiplicateur = {
                            'Air':{ 'Air':1, 'Eau': 1, 'Feu':0.5, 'Terre': 1.5 },
                            'Eau':{ 'Air':1.5, 'Eau': 1, 'Feu':1, 'Terre': 0.5 },
                            'Feu':{ 'Air':0.5, 'Eau': 1.5, 'Feu':1, 'Terre': 1 },
                            'Terre':{ 'Air':1, 'Eau': 0.5, 'Feu':1.5, 'Terre': 1 }
                            }

acceuil = '''#--------------------------------------------#\n
#          Bienvenue dans Pokémon!           #\n
#      Le jeu de Pokémon orienté Objet       #\n
#--------------------------------------------#\n
'''
global dresseur
global adversaire

print(acceuil)

while True:
    nom = input("Quel est votre nom? ")
    dresseurs = session.query(Dresseur).filter(Dresseur.nom == nom)
    if dresseurs.count() >= 1:
        break
    print("Ce dresseur n'existe pas. ")
dresseur = dresseurs[0]
print(f"Voilà votre dresseur: {dresseur.nom}: {len(dresseur.pokemons)} Pokemons. Le deck est:")
afficher_pokemons(dresseur.deck)

while True:
    options = '''0/ Voir vos pokemons
1/ Changer le deck
2/ Combattre un autre dresseur
3/ Creer un nouveau dresseur
4/ Combattre / Capturer un pokemon
5/ Quitter
Choisissez une option! (0-4) '''
    option_choisie = int(input(options))
    if option_choisie == 5:
        print('Bye!')
        break
    elif option_choisie == 4:
        all_base_pokemons = session.query(BasePokemon).all()
        for index, base_pokemon in enumerate(all_base_pokemons):
            print(f"{index}/ {all_base_pokemons[index].nom}")
        choix = int(input(f'{dresseur.nom}, quel pokemon voulez-vous combattre / capturer? (0-{len(all_base_pokemons)-1})'))
        pokemon_adverse = Pokemon(None, all_base_pokemons[choix], None, None)
        print('---------------------------')
        print(f'Le deck de {dresseur.nom} :')
        afficher_pokemons(dresseur.deck)
        indice_pokemon = int(input(f"{dresseur.nom}, quel pokemon voulez vous utiliser ? (0-2) "))
        dresseur_pokemon = dresseur.deck[indice_pokemon]


        dresseur_pokemon.vie_courante = dresseur_pokemon.vie
        dresseur_pokemon.energie_courante = dresseur_pokemon.energie
        dresseur_pokemon.statut = 'En vie'

        pokemon_adverse.vie_courante = pokemon_adverse.vie
        pokemon_adverse.energie_courante = pokemon_adverse.energie
        pokemon_adverse.statut = 'En vie'

        compteur_tour = 0
        combat_en_cours = True
        while combat_en_cours:
            if compteur_tour%2 == 0:
                dresseur_pokemon.energie_courante += dresseur_pokemon.regeneration
                if dresseur_pokemon.energie_courante > dresseur_pokemon.energie:
                    dresseur_pokemon.energie_courante = dresseur_pokemon.energie
                print(f"{dresseur.nom}, C'est à vous de jouer!")
                afficher_pokemon(dresseur_pokemon)
                compteur_competences = len(dresseur_pokemon.basepokemon.competences)
                print(f'{compteur_competences}/ Fuir le combat')
                print(f'{compteur_competences+1}/ Passer votre tour')
                if pokemon_adverse.vie_courante/pokemon_adverse.vie <= 0.2:
                    probabilite = round(4 * (0.2 - (pokemon_adverse.vie_courante / pokemon_adverse.vie))*100)
                    print(f'{compteur_competences+2}/ Capturer le pokémon (probabilité de succès : {probabilite}%)')
                    
                
                choix = int(input(f"{dresseur.nom}, que voulez vous faire? "))
                if choix in range(0, compteur_competences):
                    if dresseur_pokemon.basepokemon.competences[choix].cout_energie > dresseur_pokemon.energie_courante:
                        print("Vous n'avez pas l'energie suffisante pour cette competence.")
                        print('---------------------------')
                        continue

                    if dresseur_pokemon.basepokemon.competences[choix].type == 'Attaque':
                        # soustraction du cout meme si l'attaque ne passe pas.
                        dresseur_pokemon.energie_courante -= dresseur_pokemon.basepokemon.competences[choix].cout_energie
                        
                        taux_echec = randrange(100)
                        if taux_echec < dresseur_pokemon.basepokemon.competences[choix].precision:
                            cm = coefficients_multiplicateur[dresseur_pokemon.basepokemon.element][dresseur_pokemon.basepokemon.competences[choix].element]
                            degats = round(cm * (dresseur_pokemon.basepokemon.competences[choix].puissance * (4*dresseur_pokemon.niveau +2)/pokemon_adverse.resistance +2))
                            pokemon_adverse.vie_courante -= degats
                            if pokemon_adverse.vie_courante < 0 :
                                pokemon_adverse.vie_courante = 0
                                pokemon_adverse.statut = 'Mort'
                                print(f"{pokemon_adverse.basepokemon.nom} est mort. Vous ne pouvez plus le capturer!")
                                combat_en_cours = False
                                break
                            print(f'Attaque réussie ({dresseur_pokemon.basepokemon.competences[choix].nom}): {degats} degats')
                            if pokemon_adverse.statut == "En vie":
                                print(f"{pokemon_adverse.basepokemon.nom} a maintenant {pokemon_adverse.vie_courante} PV.")
                        else:
                            print('Oups! Echec critique!')

                    elif dresseur_pokemon.basepokemon.competences[choix].type == 'Defense':
                        if dresseur_pokemon.basepokemon.competences[choix].soin_min:
                            soin = randrange(dresseur_pokemon.basepokemon.competences[choix].soin_min, dresseur_pokemon.basepokemon.competences[choix].soin_max)
                            diff = dresseur_pokemon.vie - dresseur_pokemon.vie_courante 
                            if soin >= diff:
                                soin = diff
                            dresseur_pokemon.vie_courante += soin
                            print(f"Soin réussi({dresseur_pokemon.basepokemon.competences[choix].nom}): +{soin} PV")
                        elif dresseur_pokemon.basepokemon.competences[choix].energie_min:
                            energie = randrange(dresseur_pokemon.basepokemon.competences[choix].energie_min, dresseur_pokemon.basepokemon.competences[choix].energie_max)
                            dresseur_pokemon.energie_courante += energie
                            print(f"Regeneration d'énergie réussie ({dresseur_pokemon.basepokemon.competences[choix].nom}): +{energie} energie")
                    compteur_tour += 1
                    print('---------------------------')
                    
                elif choix == compteur_competences + 2:
                    taux_echec = randrange(100)
                    if taux_echec < probabilite:
                        pokemon_adverse.pokemon_de = dresseur.id
                        session.add(pokemon_adverse)
                        pokemon_adverse.vie_courante = None
                        pokemon_adverse.energie_courante = None
                        pokemon_adverse.statut = None
                        session.commit()
                        print(f"Félicitations {dresseur.nom}, vous avez pu capturer le pokémon {pokemon_adverse.basepokemon.nom}. Voici ses stats :")
                    else: 
                        print("{dresseur.nom}, malheureusement le pokémon s'est échappé.")
                    combat_en_cours = False
                    print('---------------------------')
                    
            elif compteur_tour % 2 == 1:
                pokemon_adverse.energie_courante += pokemon_adverse.regeneration
                if pokemon_adverse.energie_courante > pokemon_adverse.energie:
                    pokemon_adverse.energie_courante = pokemon_adverse.energie
                competences_disponibles = [competence for competence in pokemon_adverse.basepokemon.competences if pokemon_adverse.energie_courante >= competence.cout_energie]
                if len(competences_disponibles) > 1:
                    competence_aleatoire = random.choice(competences_disponibles)
                else:
                    compteur_tour += 1
                    print(f"{pokemon_adverse.basepokemon.nom} n'a aucune competence disponible. Il passe son tour!")
                if competence_aleatoire.type == "Attaque":
                    # soustraction du cout meme si l'attaque ne passe pas.
                    pokemon_adverse.energie_courante -= competence_aleatoire.cout_energie
                    
                    taux_echec = randrange(100)
                    if taux_echec < competence_aleatoire.precision:
                        cm = coefficients_multiplicateur[dresseur_pokemon.basepokemon.element][competence_aleatoire.element]
                        degats = round(cm * (competence_aleatoire.puissance * (4*dresseur_pokemon.niveau +2)/dresseur_pokemon.resistance +2))
                        dresseur_pokemon.vie_courante -= degats
                        print(f'{pokemon_adverse.basepokemon.nom} vous a attaqué ({competence_aleatoire.nom}): {degats} degats')
                        if dresseur_pokemon.vie_courante < 0 :
                            dresseur_pokemon.vie_courante = 0
                            dresseur_pokemon.statut = 'Mort'
                            print(f"Votre pokemon {dresseur_pokemon.basepokemon.nom} est mort. Vous avez perdu!")
                            combat_en_cours = False
                    else:
                        print('Oups! Echec critique!')
                elif competence_aleatoire.type == "Defense":
                    if competence_aleatoire.soin_min:
                        soin = randrange(competence_aleatoire.soin_min, competence_aleatoire.soin_max)
                        diff = pokemon_adverse.vie - pokemon_adverse.vie_courante 
                        if soin >= diff:
                            soin = diff
                        pokemon_adverse.vie_courante += soin
                        print(f"{pokemon_adverse.basepokemon.nom} s'est soigné ({competence_aleatoire.nom}): +{soin} PV")
                    elif competence_aleatoire.energie_min:
                        energie = randrange(competence_aleatoire.energie_min, competence_aleatoire.energie_max)
                        pokemon_adverse.energie_courante += energie
                        print(f"{pokemon_adverse.basepokemon.nom} a regeneré de l'énérgie ({competence_aleatoire.nom}): +{energie} energie")
                
                compteur_tour += 1
                print('---------------------------')


        
    elif option_choisie == 0:
        print(f"{dresseur.nom}, vous avez {len(dresseur.pokemons)} Pokemons :")
        afficher_pokemons(dresseur.pokemons)
    elif option_choisie == 1:
        print('---------------------------')
        afficher_pokemons(dresseur.deck)
        retirer_pokemon = int(input(f"{dresseur.nom}, quel pokemons voulez-vous retirer? (0-2) "))
        pokemons_deck_exclu = [pokemon for pokemon in dresseur.pokemons if pokemon not in dresseur.deck]
        afficher_pokemons(pokemons_deck_exclu)
        ajouter_pokemon = int(input(f"{dresseur.nom}, quel pokemons voulez-vous ajouter? (0-{len(pokemons_deck_exclu)-1}) "))
        dresseur.deck[retirer_pokemon].dans_deck_de = None
        pokemons_deck_exclu[ajouter_pokemon].dans_deck_de = dresseur.id
        session.commit()
        session.flush()
    elif option_choisie == 3:
        nom_nouveau_dresseur = input("Quel le nom du nouveau dresseur? ")
        creer_dresseur(nom_nouveau_dresseur, session)
    elif option_choisie == 2:
        while True:
            nom_adversaire = input('Contre qui? ')
            dresseurs = session.query(Dresseur).filter(Dresseur.nom == nom_adversaire)
            if nom_adversaire == nom:
                print('Vous ne pouvez pas jouer contre vous même! Choisissez un autre dresseur! ')
                continue
            if dresseurs.count() >= 1:
                break
            print("Ce dresseur n'existe pas.")
        print('---------------------------')
        adversaire = dresseurs[0]
        # Le premier joueur qui joue en premier
        compteur_tour = 0
        jeu_en_cours = True
        for item in dresseur.deck:
            item.energie_courante = item.energie
            item.vie_courante = item.vie
            item.statut = 'En vie'
        for item in adversaire.deck:
            item.energie_courante = item.energie
            item.vie_courante = item.vie
            item.statut = 'En vie'

        print(f"Combat JcJ entre {dresseur.nom} et {adversaire.nom}\n")
        print(f'Le deck de {dresseur.nom} :')
        afficher_pokemons(dresseur.deck)
        indice_pokemon = int(input(f"{dresseur.nom}, quel pokemon voulez vous utiliser ? (0-2) "))
        dresseur_pokemon = dresseur.deck[indice_pokemon]
        print('---------------------------')
        print(f'Le deck de {adversaire.nom} :')
        afficher_pokemons(adversaire.deck)
        indice_pokemon = int(input(f"{adversaire.nom}, quel pokemon voulez vous utiliser? (0-2) "))
        adversaire_pokemon = adversaire.deck[indice_pokemon]
        joueurs = [dresseur, adversaire]
        pokemons_joueurs = [dresseur_pokemon, adversaire_pokemon]
        print('---------------------------')
        while jeu_en_cours:
            print(f"Tour {compteur_tour+1}")
            tour_fini = False
            # regeneration de l'energie
            for pok in joueurs[compteur_tour%2].deck:
                if pok.vie_courante > 0:
                    pok.energie_courante += pok.regeneration
                    if pok.energie_courante > pok.energie:
                        pok.energie_courante = pok.energie 
            while not tour_fini:
                print(f"C'est à {joueurs[compteur_tour%2].nom} de jouer!")
                afficher_pokemon(pokemons_joueurs[compteur_tour%2])
                compteur_competences = len(pokemons_joueurs[compteur_tour%2].basepokemon.competences)
                print(f'{compteur_competences}/ Changer de pokemon')
                print(f'{compteur_competences+1}/ Passer votre tour')
                print(f'{compteur_competences+2}/ Fuir le combat')

                choix = int(input(f"{joueurs[compteur_tour%2].nom}, que voulez vous faire? (0-{compteur_competences+2}) "))
                if choix in range(0, compteur_competences):
                    if pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].cout_energie > pokemons_joueurs[compteur_tour%2].energie_courante:
                        print("Vous n'avez pas l'energie suffisante pour cette competence.")
                        print('---------------------------')
                        continue
                    if pokemons_joueurs[compteur_tour%2].statut == 'Mort':
                        print("Vous ne pouvez plus utiliser ce pokemon, il est mort.")
                        print('---------------------------')
                        continue
                    if pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].type == 'Attaque':
                        # soustraction du cout meme si l'attaque ne passe pas.
                        pokemons_joueurs[compteur_tour%2].energie_courante -= pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].cout_energie
                        
                        taux_echec = randrange(100)
                        if taux_echec < pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].precision:
                            cm = coefficients_multiplicateur[pokemons_joueurs[compteur_tour%2].basepokemon.element][pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].element]
                            degats = round(cm * (pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].puissance * (4*pokemons_joueurs[compteur_tour%2].niveau +2)/pokemons_joueurs[(compteur_tour+1)%2].resistance +2))
                            pokemons_joueurs[(compteur_tour+1)%2].vie_courante -= degats
                            if pokemons_joueurs[(compteur_tour+1)%2].vie_courante < 0 :
                                pokemons_joueurs[(compteur_tour+1)%2].vie_courante = 0
                                pokemons_joueurs[(compteur_tour+1)%2].statut = 'Mort'
                                
                            print(f'Attaque réussie ({pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].nom}): {degats} degats')
                        else:
                            print('Oups! Echec critique!')

                    elif pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].type == 'Defense':
                        if pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].soin_min:
                            soin = randrange(pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].soin_min, pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].soin_max)
                            diff = pokemons_joueurs[compteur_tour%2].vie - pokemons_joueurs[compteur_tour%2].vie_courante 
                            if soin >= diff:
                                soin = diff
                            pokemons_joueurs[compteur_tour%2].vie_courante += soin
                            print(f"Soin réussi({pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].nom}): +{soin} PV")
                        elif pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].energie_min:
                            energie = randrange(pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].energie_min, pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].energie_max)
                            pokemons_joueurs[compteur_tour%2].energie_courante += energie
                            print(f"Regeneration d'énergie réussie ({pokemons_joueurs[compteur_tour%2].basepokemon.competences[choix].nom}): +{energie} energie")
                    print('---------------------------')
                    morts = 0
                    for pok in joueurs[(compteur_tour+1)%2].deck:
                        if pok.statut == "Mort":
                            morts += 1
                    if morts == 3:
                        jeu_en_cours = False
                        tour_fini = True
                        print('---------------------------')
                        break
                    tour_fini = True
                    compteur_tour += 1
                elif choix == compteur_competences:
                    while True:
                        afficher_pokemons(joueurs[compteur_tour%2].deck)
                        indice_pokemon = int(input(f"{joueurs[compteur_tour%2].nom}, quel pokemon voulez vous utiliser? (0-2) "))
                        if joueurs[compteur_tour%2].deck[indice_pokemon].statut == "Mort":
                            print("Vous ne pouvez plus utiliser ce pokemon, il est mort.")
                            print('---------------------------')
                        else:
                            pokemons_joueurs[compteur_tour%2] = joueurs[compteur_tour%2].deck[indice_pokemon]
                            print('---------------------------')
                            break
                elif choix == compteur_competences + 1:
                    if pokemons_joueurs[compteur_tour%2].statut == "En vie":
                        tour_fini = True    
                        compteur_tour += 1
                        print('---------------------------')
                    else: 
                        print(f"Votre pokémon courant {pokemons_joueurs[compteur_tour%2].basepokemon.nom} est mort! Vous devez le changer avant de passer votre tour!")
                        print('---------------------------')
                elif choix == compteur_competences + 2:
                    jeu_en_cours = False
                    print('---------------------------')
        # Fin de jeu
        print(f'Félicitations! {joueurs[compteur_tour%2].nom} a gagné!')
        # Niveau moyen des pokémons vaincus
        niveau_moyen = sum([pok.niveau for pok in joueurs[(compteur_tour+1)%2].deck])
        for pokemon in joueurs[compteur_tour%2].deck:
            pokemon.experience = round((10 + niveau_moyen - pokemon.niveau) / 3)
            if pokemon.experience >= 100 and pokemon.niveau + 1 <= pokemon.basepokemon.niveau_max:
                pokemon.niveau += 1
                pokemon.experience = pokemon.experience % 100
                pokemon.vie += randrange(1, 5)
                pokemon.energie += randrange(1, 5)
                pokemon.resistance += randrange(1, 5)
                print(f'Félicitations! Votre pokémon {pokemon.basepokemon.nom} a atteint le niveau suivant! (Lvl {pokemon.niveau})')
            elif pokemon.experience >= 100 and pokemon.niveau + 1 > pokemon.basepokemon.niveau_max:
                if not pokemon.basepokemon.apres:
                    pokemon.experience = 100
                    pokemon.niveau = pokemon.basepokemon.niveau_max
                    pokemon.vie += randrange(1, 5)
                    pokemon.energie += randrange(1, 5)
                    pokemon.resistance += randrange(1, 5)
                    print(f'Félicitations! Votre pokémon {pokemon.basepokemon.nom} a atteint le niveau maximal! (Lvl {pokemon.niveau})')
                else:
                    evolution = session.query(BasePokemon).filter(BasePokemon.nom == pokemon.basepokemon.apres)[0]
                    pokemon.basepokemon_id = evolution.id
                    pokemon.niveau = evolution.niveau_min
                    pokemon.vie = evolution.vie_min
                    pokemon.energie = evolution.energie_min
                    pokemon.regeneration = evolution.regeneration_min
                    pokemon.resistance = evolution.resistance_min
                    pokemon.experience = 0
                    print(f"Félicitation! Votre pokémon a évolué! {pokemon.basepokemon.nom} -> {evolution.nom}")
                    pokemon.basepokemon = evolution
                    
            session.commit()
                                

            



            
            



