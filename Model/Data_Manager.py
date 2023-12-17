import pandas as pd
import numpy as np
import os,re




class Gestion_Data:
    def __init__(self,poke_data_direction):
        self.data=poke_data_direction
        self.poke_data=pd.read_csv(poke_data_direction)

        #On classifie les filtres selon qlq criteres et on ordonne notre data
        self.poke_data_organisee,self.information_filtres=self.configuration_filtres()
        #Arbre qui va contenir toutes les lettres des noms des pokemons
        self.poke_arbre=self.configuration_poke_arbre()

        #Dico contenant les media du pokedex
        self.dico_direction_images={}
        self.configuration_media(direction_media="Model/Characters_image",type_media=".png")
        self.dico_direction_gifs={}
        self.configuration_media(direction_media="Model/GIF",type_media=".gif")


    def get_filtres(self):
        return self.information_filtres

    def get_poke_data(self):
        return self.poke_data_organisee
    
    def get_poke_arbre(self):
        return self.poke_arbre

    def get_poke_media(self):
        return self.dico_direction_images,self.dico_direction_gifs

    def configuration_filtres(self):
        filtres_valeurs_possibles = {} #Dico contenant les valeurs possibles (uniques) de chq filtre
        type_filtres = {} #classification des filtres
        for filtre in self.poke_data.columns: #On va essayer de classifier tous les filtres de la data selon qlq criteres 
            filtres_valeurs_possibles[filtre] = self.poke_data[filtre].unique().tolist()
            #On recupere les UNIQUES valeurs possibles
            
            #On fixera tout au long des criteres arbitraires
            
                # Num
            if np.issubdtype(self.poke_data[filtre].dtype, np.number):
                longeur = len(filtres_valeurs_possibles[filtre])
                if longeur <= 600: 
                    if longeur <= 10:
                        type_filtres[filtre] = True, "Categorique_Type_court"   
                    elif longeur == 2:
                        type_filtres[filtre] = True, "Booleen_Type"
                    else:
                        type_filtres[filtre] = True, "BatailleStat_Type"
                else:
                    type_filtres[filtre] = True, "Id_Type"
            # Bool
            elif self.poke_data[filtre].dtype == np.bool_:
                type_filtres[filtre] = False, "Booleen_Type"
            # Txt
            elif self.poke_data[filtre].dtype == np.object_:
                longeur = len(filtres_valeurs_possibles[filtre])
                if longeur <= 600:
                    type_filtres[filtre] = False, "Categorique_Type"
                else:
                    type_filtres[filtre] = False, "Id_Type"
            # Si aucun cas prevu
            else:
                type_filtres[filtre] = False, "Autre_Type"


        # filtres qui sont des identifiants
            #On envisage des des datas avec plusieurs identifiants (ex:pokemon_japan)
        id_type_num = [(filtre) for filtre, info in type_filtres.items() if info[1] == 'Id_Type' and info[0]]
        id_type_nom = [(filtre) for filtre, info in type_filtres.items() if info[1] == 'Id_Type' and not info[0]]
        #filtres catégoriques
        categorique_type = [(filtre) for filtre, info in type_filtres.items() if info[1] == 'Categorique_Type']
        #On combine les listes en prenant une valeur pour id_nom et num et 2 pour categorique
        #C'est les principaux filtres qu'on veut afficher, pour que l'user ait slment un apperçu.
        filtres_affiches = id_type_num[:1] + id_type_nom[:1] + categorique_type[:2]
        #Filtres qui vont être affiches dans le treeview (pour pas trop le charger)
        #Les autres colonnes restantes
        autres_cols = [col for col in self.poke_data.columns if col not in (id_type_num + id_type_nom + categorique_type)]
         # reorganise le data
        organisation = id_type_num[:1] + id_type_nom[:1] + categorique_type + autres_cols
        poke_data_organisee = self.poke_data[organisation]



        return poke_data_organisee,(filtres_affiches,type_filtres,filtres_valeurs_possibles)
    
    def configuration_poke_arbre(self):
            class Noeud():
                def __init__(self,caractere=None):
                    #Initialisasion de la classe avec un caractère non existant d'abord
                    self.enfants={} #Dictionnaire stockant les noeuds enfants
                    self.mot_fini=False  #En début de recherche on l'initialise a faux


                """Methode qui prend des mots du dico_francais et les garde dans notre 
                                                arbre                 """
                def save(self,mot):
                    #On prend un mot commençant par la racine de l'arbre
                    node=self
                    #On parcourt tous les caractère du mot
                    for caract in mot:

                        #Si caract pas présent dans les enfants du Noeud
                        if caract not in node.enfants:
                            #On ajoute un nouveau Noeud pour ce caract
                            node.enfants[caract]=Noeud(caract)
                            #Les caract ici sont les clefs <=> uniques.
                        #Sinon on se déplace dans le Noeud associé au caractère suivant
                        node=node.enfants[caract]

                    """Fin de la boucle for <=> fin du mot
                                            <=> dernier Noeud visité"""
                    #On indique alors que le mot est fini
                    node.mot_fini=True

                """    #fonction qui prend un mot et cherche s'il est présent dans l'arbre' 
                        fait précedement. Si mot présent ---> True, false sinon  """
                def cherche(self,mot):
                    node=self
                    #On regared tous les caract du mot
                    for caract in mot:
                        if caract in node.enfants:
                            node = node.enfants[caract]
                            print(caract,"présent")
                        else:
                            print("pas de noeuds enfants",caract)
                            #S'il n'est pas dans les neuds enfants, alors ce n'est pas un mot valide
                            return False
                    #On est arrivé au bout du mot
                    #Verif si dernier Noeud visité correspond à la fin du mot
                    return node.mot_fini
                
                def suggestions(self, prefix):
                    # On commence par le noeud racine
                    node = self
                    # On parcourt chaque caractère du préfixe
                    for caract in prefix:
                        # Si le caractère est présent dans les enfants du noeud actuel
                        if caract in node.enfants:
                            # On se déplace vers le noeud enfant correspondant
                            node = node.enfants[caract]
                        else:
                            # Si le préfixe n'est pas présent dans l'arbre, on retourne une liste vide
                            return None  # Pas de suggestions si le préfixe n'est pas trouvé
                    # On appelle la fonction get_mots pour récupérer tous les mots qui commencent par le préfixe
                    return self.get_mots(node, prefix)

                def get_mots(self, node, prefix):
                    # Liste pour stocker les mots trouvés
                    mots = []
                    # Si le noeud actuel marque la fin d'un mot
                    if node.mot_fini:
                        # On ajoute le préfixe à la liste des mots
                        mots.append(prefix)
                    # On parcourt tous les enfants du noeud actuel
                    for caract, enfant in node.enfants.items():
                        # On appelle récursivement get_mots sur les enfants pour trouver tous les mots
                        mots.extend(self.get_mots(enfant, prefix + caract))
                    # On retourne la liste des mots trouvés
                    return mots

            poke_arbre=Noeud()
            for poke_nom in self.poke_data_organisee.iloc[:,1].values:
                poke_arbre.save(poke_nom.lower())
            return poke_arbre

    def configuration_media(self,direction_media,type_media):
        def normalization(nom):
            # Verif si le fichier de donnees est celui des pokemons
            if self.data == "Model/pokemon.csv":
                # Rempl les caracteres speciaux par des symboles comprehensibles
                # Rempl les formes et les noms particuliers par des noms standards (par rpp a notre dossier media)
                remplacements = {
                    "Normal Forme": "", "Plant Cloak": "", "Shield Forme": "",
                    "Altered Forme": "", "Land Forme": "", "Standard Mode": "",
                    "Mr. Mime": "mr._mime", "mr. mime": "mr._mime",
                    "Mime Jr.": "mime_jr", "mime jr.": "mime_jr",
                    "HoopaHoopa Confined": "hoopa", "Zygarde": "zygarde",
                    "Flabébé": "flabebe", "'": "" , "♂": "_m", "♀": "_f"
                }
                for ancien, nouveau in remplacements.items():
                    if ancien in nom:
                        nom = nom.replace(ancien, nouveau)
                if nom in remplacements:
                    return remplacements[nom]

            # Conv les nombres en chaine de caracteres
            if isinstance(nom, (float, int)):
                nom = str(nom)
            # Separe le nom et prend la premiere partie
            nom_sep = nom.split()
            premier_mot = nom_sep[0]

            # Ajoute un tiret avant chaque majuscule qui n'est pas la premiere lettre
            nom_avec_tirets = re.sub(r'(?<!^)(?=[A-Z])', '-', premier_mot)
            # Conv en minuscules et rempl les caracteres speciaux par des tirets
            nom_normalise = re.sub(r'\W+', '-', nom_avec_tirets).lower()
            # Suppr les tirets a la fin si necessaire
            nom_normalise = re.sub(r'-+$', '', nom_normalise)

            # Gere les cas avec "X" ou "Y" a la fin du nom
            if len(nom_sep) > 2:
                if nom_sep[2].lower() == "x":
                    return nom_normalise + "x"
                elif nom_sep[2].lower() == "y":
                    return nom_normalise + "y"
            else:
                return nom_normalise
    
            
            # Définir le chemin vers le dossier contenant les GIFs
        #Pour que les noms soient "compatibles" avec notre media_data
        noms_normalises = {normalization(nom_pokemon): nom_pokemon for nom_pokemon in self.poke_data_organisee.iloc[:, 1].values}
        if type_media == ".gif":
            self.dico_direction_gifs["Mr. Mime"]="Model/GIF/mr._mime.gif"

            for fichier in os.listdir(direction_media):
                if fichier.endswith(type_media):
                    parties_nom = fichier.split('-')
                    # si pas de num apres le nom 
                    if (len(parties_nom) == 1 or
                        (len(parties_nom) > 1 and not parties_nom[-1][0].isdigit())):
                        chemin_relatif = os.path.join(direction_media, fichier)
                        nom_normalise_gif = os.path.splitext(os.path.basename(chemin_relatif))[0]
                        if nom_normalise_gif in noms_normalises:
                            self.dico_direction_gifs[noms_normalises[nom_normalise_gif]] = chemin_relatif
            i = 0
            # On verifie le nombre derreurs
            for nom in self.poke_data_organisee.iloc[:, 1].values:
                if nom not in self.dico_direction_gifs:
                    self.dico_direction_gifs[nom] = "Model/GIF/xd.gif"
                    i += 1
            print(f"{i} erreurs pour les gifs des Pokémon")

        if type_media == ".png":
            self.dico_direction_images["CharizardMega Charizard X"]="Model/Characters_image/6-mega-x.png"
            self.dico_direction_images["CharizardMega Charizard Y"]="Model\Characters_image/6-mega-y.png"
            self.dico_direction_images["MewtwoMega Mewtwo X"]="Model/Characters_image/150-mega-y.png"
            self.dico_direction_images["MewtwoMega Mewtwo Y"]="Model/Characters_image/150-mega-y.png"
            self.dico_direction_images["HoopaHoopa Unbound"]="Model/Characters_image/720-unbound.png"
            
            i = 0
            for fichier in os.listdir(direction_media):
                chemin_relatif = os.path.join(direction_media, fichier)
                if fichier.endswith(type_media):
                    parties_nom = fichier.split("-")
                    if len(parties_nom) == 1 and parties_nom != ['xd.png']:
                        num_png = int(parties_nom[0].replace(".png", ""))
                        resultat_filtre = self.poke_data_organisee.loc[self.poke_data_organisee.iloc[:, 0] == num_png]
                        if not resultat_filtre.empty:
                            nom_pokemon = resultat_filtre.iloc[:, 1].values[0]
                            self.dico_direction_images[nom_pokemon] = chemin_relatif
                        
                    if len(parties_nom) == 2:
                        mots_cles = ["Mega", "Attack", "Defense", "Speed", "Primal", "Sandy",
                                    "Trash", "Heat", "Wash", "Frost", "Fan", "Mow", "Female",
                                    "Origin", "Sky", "Therian", "Black", "White", "Resolute",
                                    "Pirouette", "Shield"]
                        if any(mot_cle.lower() in parties_nom[1].lower() for mot_cle in mots_cles):
                            num_png = int(parties_nom[0].replace(".png", ""))
                            noms_pokemons = self.poke_data_organisee.loc[self.poke_data_organisee.iloc[:, 0] == num_png].iloc[:, 1]
                            for pokemon in noms_pokemons:
                                if parties_nom[1].replace(".png", "") in pokemon.lower():
                                    self.dico_direction_images[pokemon] = chemin_relatif
            
            # Vérifier l'existence des images pour chaque Pokémon
            for nom in self.poke_data_organisee.iloc[:, 1].values:
                if nom not in self.dico_direction_images:
                    self.dico_direction_images[nom] = "Model/Characters_image/xd.png"
                    i += 1
            print(f"{i} erreurs pour les images des Pokémon")





