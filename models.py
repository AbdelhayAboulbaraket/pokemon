import re
import random
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import ForeignKey, Table
import pandas as pd
from sqlalchemy.orm import backref

Base = declarative_base()

class Competence(Base):
    def __init__(self, id, nom, type, description, element, cout_energie, puissance=None, precision=None, soin_min=None, soin_max=None, energie_min=None, energie_max=None):
        self.id = id
        self.nom = nom
        self.type = type
        self.description = description
        self.element = element
        self.cout_energie = cout_energie
        self.puissance = puissance
        self.precision = precision
        self.soin_min = soin_min
        self.soin_max = soin_max
        self.energie_min = energie_min
        self.energie_max = energie_max

    __tablename__ = 'Competence'
    id = Column(Integer, primary_key=True)
    nom = Column(Text)
    type = Column(Text)
    description = Column(Text)
    element = Column(Text)
    cout_energie = Column(Integer)
    # Pour les attaques
    puissance = Column(Integer)
    precision = Column(Integer)
    # Pour les soins
    soin_min = Column(Integer)
    soin_max = Column(Integer)
    energie_min = Column(Integer)
    energie_max = Column(Integer)

association_table = Table('Possede', Base.metadata,
    Column('left_id', ForeignKey('BasePokemon.id')),
    Column('right_id', ForeignKey('Competence.id'))
)
class BasePokemon(Base):
    def __init__(self, id, nom, nom_apres, element, niveau_min, niveau_max, vie_min, vie_max, energie_min, energie_max, regeneration_min, regeneration_max, resistance_min, resistance_max, competences) -> None:
        self.id = id
        self.nom = nom
        self.nom_apres = nom_apres
        self.element = element
        self.niveau_min = niveau_min
        self.niveau_max = niveau_max
        self.vie_min = vie_min
        self.vie_max = vie_max
        self.energie_min = energie_min
        self.energie_max = energie_max
        self.regeneration_min = regeneration_min
        self.regeneration_max = regeneration_max
        self.resistance_min = resistance_min
        self.resistance_max = resistance_max
        self.competences = competences

    __tablename__ = 'BasePokemon'  
    id = Column(Integer, primary_key=True)
    nom = Column(Text)
    nom_apres = Column(Text)
    element = Column(Text)
    niveau_min = Column(Integer)
    niveau_max = Column(Integer)
    vie_min = Column(Integer)
    vie_max = Column(Integer)
    energie_min = Column(Integer)
    energie_max = Column(Integer)
    regeneration_min = Column(Integer)
    regeneration_max = Column(Integer)
    resistance_min = Column(Integer)
    resistance_max = Column(Integer)
    # Tableau de Compétences ( Agrégation )
    competences = relationship("Competence", secondary=association_table)
    children = relationship("Pokemon", back_populates="basepokemon")


# Pokemon hérite de BasePokemon ( Héritage )
class Pokemon(Base):
    def __init__(self,id, basePokemon, dans_deck_de, pokemon_de) -> None:
        self.id = id
        self.basepokemon_id = basePokemon.id
        self.niveau = basePokemon.niveau_min
        self.vie = basePokemon.vie_min
        self.energie = basePokemon.energie_min
        self.regeneration = basePokemon.regeneration_min
        self.resistance = basePokemon.resistance_min
        self.experience = 0
        self.dans_deck_de = dans_deck_de
        self.pokemon_de = pokemon_de
        self.basepokemon = basePokemon
        

    def __eq__(self, other):
        if (isinstance(other, Pokemon)):
            return self.id == other.id
    
    __tablename__ = 'Pokemon'
    id = Column(Integer, primary_key=True)
    basepokemon_id = Column(Integer, ForeignKey("BasePokemon.id"))
    niveau = Column(Integer)
    vie = Column(Integer)
    energie = Column(Integer)
    regeneration = Column(Integer)
    resistance = Column(Integer)
    experience = Column(Integer)

    basepokemon = relationship("BasePokemon", back_populates="children")

    dans_deck_de = Column(Integer, ForeignKey('Dresseur.id'))
    pokemon_de = Column(Integer, ForeignKey('Dresseur.id'))

    
    

class Dresseur(Base):
    def __init__(self, nom, pokemons, deck) -> None:
        self.nom = nom
        # Tableau de Pokémons ( Agrégation )
        self.pokemons = pokemons
        # Tableau de Pokémons ( Agrégation )
        self.deck = deck
    
    __tablename__ = "Dresseur"
    id = Column(Integer, primary_key=True)
    nom = Column(Text)
    pokemons = relationship("Pokemon", foreign_keys='Pokemon.pokemon_de')
    deck = relationship("Pokemon", foreign_keys='Pokemon.dans_deck_de')
    
def creer_dresseur(nom, session):
    basepokemons = session.query(BasePokemon).all()
    dresseur_object = Dresseur(nom, [], [])
    session.add(dresseur_object)
    session.flush()
    random_pokemons = random.sample(basepokemons, k=8)
    print([item.id for item in random_pokemons])
    random_deck = random.sample(random_pokemons, k=3)
    for random_pokemon in random_pokemons:  
        pokemon = Pokemon(None, random_pokemon, None, dresseur_object.id)
        if random_pokemon in random_deck:
            pokemon.dans_deck_de = dresseur_object.id
        session.add(pokemon)
    session.commit()

    

if __name__ == '__main__':

    while True:
        nom_utilisateur = input('Entrez le nom d\'utilisateur :')
        mot_de_passe = input("Entrez votre mot de passe: ")
        try:
            engine = create_engine(f'mysql+mysqldb://{nom_utilisateur}:{mot_de_passe}@localhost:3306/pokemon', )
            Session = sessionmaker(bind=engine, autoflush=False)
            session = Session()
        except Exception:
            print("Nom d'utilisateur ou mot de passe erroné!")
            continue
        break

    print( "--- Construire les tables de la base de données ---" )
    Base.metadata.create_all(engine)
    print( "--- Construire les tables de la base de données --- succès\n")

    print( "--- Populer la table Compétence ---" )
    df_attaques = pd.read_csv("./data/attaque.txt", sep="\t")
    df_defenses = pd.read_csv("./data/defense.txt", sep="\t")

    for index, row in df_attaques.iterrows():
        attaque = Competence(None, row['Nom'], 'Attaque', row['Description'], row['Element'], row['Cout'], row['Puissance'], row['Precision'])
        session.add(attaque)
    for index, row in df_defenses.iterrows():
        soin_min = None if str(row['Soin']) == 'nan' else row['Soin'].split('-')[0]
        soin_max = None if str(row['Soin']) == 'nan' else row['Soin'].split('-')[1]
        energie_min = None if str(row['Energie']) == 'nan' else row['Energie'].split('-')[0]
        energie_max = None if str(row['Energie']) == 'nan' else row['Energie'].split('-')[1]
        defense = Competence(None, row['Nom'], 'Defense', row['Description'], row['Element'], row['Cout'], None, None, soin_min, soin_max, energie_min, energie_max)
        session.add(defense)
    session.commit()
    print("--- Populer la table Compétence --- succès\n" )
    print( "--- Populer la table BasePokemon ---" )
    df_basepokemons = pd.read_csv("./data/pokemon.csv")
    df_basepokemons.where(pd.notnull(df_basepokemons), None)
    for index, row in df_basepokemons.iterrows():
        nom_apres = None if str(row['Apres']) == 'nan' else row['Apres']
        niveau_min = None if str(row['Niveau']) == 'nan' else row['Niveau'].split('-')[0].strip()
        niveau_max = None if str(row['Niveau']) == 'nan' else row['Niveau'].split('-')[1].strip()
        vie_min = None if str(row['Vie']) == 'nan' else row['Vie'].split('-')[0].strip()
        vie_max = soin_min = None if str(row['Vie']) == 'nan' else row['Vie'].split('-')[1].strip()
        energie_min = None if str(row['Energie']) == 'nan' else row['Energie'].split('-')[0].strip()
        energie_max = soin_min = None if str(row['Energie']) == 'nan' else row['Energie'].split('-')[1].strip()
        regeneration_min = None if str(row['Regeneration']) == 'nan' else row['Regeneration'].split('-')[0].strip()
        regeneration_max = None if str(row['Regeneration']) == 'nan' else row['Regeneration'].split('-')[1].strip()
        resistance_min = None if str(row['Resistance']) == 'nan' else row['Resistance'].split('-')[0].strip()
        resistance_max = None if str(row['Resistance']) == 'nan' else row['Resistance'].split('-')[1].strip()
        competences = [item.strip() for item in re.split(',|\[|\]', row['Competences']) if item != '']
        comps = []
        for competence in competences:
            comp = session.query(Competence).filter(Competence.nom == competence)
            comps.append(comp[0])
        basepokemon = BasePokemon(None, row['Nom Avant'], nom_apres, row['Element'], niveau_min, niveau_max, vie_min, vie_max, energie_min, energie_max, regeneration_min, regeneration_max, resistance_min, resistance_max, comps)
        session.add(basepokemon)
    session.commit()
    

    print("--- Populer la table BasePokemon --- Succès\n")
    print("--- Populer la table Dresseur et des Pokémons (Aléatoirement) ---\n")
    dresseurs = ['MT', 'Chuck Norris', 'Boogey', 'Khadra', 'Brahim', 'Mundo']
    for dresseur in dresseurs:
        creer_dresseur(dresseur, session)
    print("--- Populer la table Dresseur et des Pokémons --- Succès\n")        

