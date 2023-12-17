from Model.Data_Manager import Gestion_Data
from Model.Filtre_Manager import *
from View.GUI import GUI
import pandas as pd


class Control_poke:
    def __init__(self,data_direction):
        self.data_base=Gestion_Data(poke_data_direction=data_direction)
        self.poke_GUI=GUI()
        self.data_filtree=pd.DataFrame()

        self.initialisation_data_info()
        self.initialisation_poke_GUI()
        self.poke_GUI.mainloop()

    def initialisation_data_info(self):    
        self.poke_data=self.data_base.get_poke_data()
        self.filtres_principaux,self.types_filtres,self.filtres_valeurs=self.data_base.get_filtres()
        self.poke_arbre=self.data_base.get_poke_arbre()
        self.poke_png,self.poke_gif=self.data_base.get_poke_media()


    def initialisation_poke_GUI(self):
        #Zone de filtre
        self.poke_GUI.filtres_avancee.configuration_initiale(self.types_filtres,self.filtres_valeurs)
        self.poke_GUI.filtres_avancee.set_command_application(self.appliquer_filtres)
        self.test=False #Pour savoir si on filtre des valeurs ou pas
        
        #Zone de recherche
        self.poke_GUI.zone_recherche.configuration_box_ordre(self.types_filtres)
        self.poke_GUI.zone_recherche.configuration_affichage_resultats(self.filtres_principaux)
        self.poke_GUI.zone_recherche.set_commands(command_boutton_ordre=self.ordre_data,
                                                  command_boutton_recherche=self.recherche_data_entree)
        self.poke_GUI.zone_recherche.resultats.bind('<Double-1>', self.affichage_info_complete)  # Si double click
        self.poke_GUI.zone_recherche.resultats.bind('<Return>', self.affichage_info_complete)  # Ou si appuie sur enter)
        self.poke_GUI.affichage_cartes_pokemons.initialisation_cartes_pokemons(self.poke_data,self.poke_png)
        self.poke_GUI.affichage_cartes_pokemons.set_command_poke_affichage(self.affichage_info_complete)
        self.compteur_cartes_pokemons_affiches=30
        self.poke_GUI.affichage_cartes_pokemons.affichage_poke_liste(self.poke_data.iloc[:self.compteur_cartes_pokemons_affiches, 1])
        self.poke_GUI.affichage_cartes_pokemons.bout_set_command(self.affichage_plus)
        #Zone d'affichage des pok
        self.poke_GUI.affichage_cartes_pokemons

    def appliquer_filtres(self,filtre_type1=None,filtre_type2=None,filtre_type3=None):
        if len(filtre_type1)==0 and len(filtre_type2)==0 and len(filtre_type3)==0:
            self.poke_GUI.affichage_cartes_pokemons.affichage_poke_specifique(self.poke_data.iloc[:self.compteur_cartes_pokemons_affiches, 1])
            return

        filtrage={}

        for filtre, info in filtre_type1.items():
            if info!=(None,None):
                strategie=set_strategy(filtre,self.types_filtres[filtre][0],self.types_filtres[filtre][1],
                                       "Recherche_plage_de_valeurs")
                filtrage[filtre]=(info[0],info[1]),strategie
                # print(filtre,"max:",info[1],"min:",info[0])
        for filtre in filtre_type3:
            if len(filtre_type3)>0:
                # print(filtre[1],filtre[2])
                strategie=set_strategy(filtre[2],self.types_filtres[filtre[2]][0],self.types_filtres[filtre[2]][1],
                                       "Recherche_Simple",trie=self.poke_arbre)
                filtrage[filtre[2]]=filtre[1],strategie
        for filtre,valeurs in filtre_type2.items():
            for valeur in valeurs:
                # print(filtre,valeur[0])
                if valeur=="0":
                    valeur=True
                elif valeur=="1":
                    valeur=False
                strategie=set_strategy(filtre,self.types_filtres[filtre][0],self.types_filtres[filtre][1],
                                       "Recherche_Simple",trie=self.poke_arbre)
                filtrage[filtre]=valeur[0],strategie

        self.test=False
        for filtre,info in filtrage.items():
            strategie=info[1]
            print(strategie)
            if not self.test:
                self.data_filtree=strategie.application_filtre(strategie,self.poke_data,info[0])
                self.test=True
            else:
                self.data_filtree=strategie.application_filtre(strategie,self.data_filtree,info[0])
        if self.test :
            print(self.data_filtree)
            self.poke_GUI.affichage_cartes_pokemons.affichage_poke_specifique(self.data_filtree.iloc[:, 1])
        

        
    def recherche_data_entree(self,entree,pack_resultats=False):
        
        id_nombre=[(filtre,info_filtre) for filtre,info_filtre in self.types_filtres.items() if info_filtre==(True,'Id_Type')]
        id_nom=[(filtre,info_filtre) for filtre,info_filtre in self.types_filtres.items() if info_filtre==(False,'Id_Type')]
        
        #Si rien écrit encore
        if entree=="Nom ou numéro Pokemon" or entree=="":
            return
        if entree.isdigit():
            if len(id_nombre)==1:
                strategie=id_nombre
                Strategy_Filtrage=set_strategy(strategie[0][0],strategie[0][1][0],strategie[0][1][1])
                        #EXEMPLE:    (  "Name"     ,numerique ou pas:"True"  ,       "Id_type" )
                        #Cette methode nous retourne une classe, stocké dans la variable Strategy_Filtrage
            else:
                strategie=list(id_nombre[0])
                print(strategie)
                Strategy_Filtrage=set_strategy(strategie[0],strategie[1][0],strategie[1][1])
        else: 
            if len(id_nom)==1:
                strategie=id_nom
                Strategy_Filtrage=set_strategy(strategie[0][0],strategie[0][1][0],strategie[0][1][1],trie=self.poke_arbre)
            else:
                strategie=list(id_nom[0])
                Strategy_Filtrage=set_strategy(strategie[0],strategie[1][0],strategie[1][1],trie=self.poke_arbre)
        
        #Comme Strategy_Filtrage c'est une classe
            #On accède à la fonction aaplication_filtre() qui nous retourne les données filtrés
        self.data_filtree=Strategy_Filtrage.application_filtre(Strategy_Filtrage,self.poke_data,entree)
        data_pour_afficher=self.data_filtree[self.filtres_principaux]
                                                            #On utilise la structure d¡une liste car ordre important
        self.test=True
        if pack_resultats:
            print("Affichage des frames:")
            poke_nom=[pokemon[1] for pokemon in data_pour_afficher.values]
            self.poke_GUI.affichage_cartes_pokemons.nb_poke_resultats=len(poke_nom)
            self.poke_GUI.affichage_cartes_pokemons.affichage_par30=False
            self.poke_GUI.affichage_cartes_pokemons.configuration_affichage(None)
            self.poke_GUI.affichage_cartes_pokemons.affichage_poke_specifique(poke_nom)

        else:
            self.poke_GUI.zone_recherche.affichage_temps_reel(list(tuple(pokemon) for pokemon in data_pour_afficher.values))


    def ordre_data(self,ordre):
        if "up" in ordre:
            sens=True
        else:
            sens=False
        filtre=ordre.split("-")
        print(filtre[0])
        strat=set_strategy(filtre[0],self.types_filtres[filtre[0]][0],self.types_filtres[filtre[0]][1],strategie="Ordre")
        if not self.test:  #Si pas de valeurs filtrees, on ordonne le poke_data original
            data=strat.application_filtre(strat,self.poke_data,sens)
        else:
            print("organisation du data filtree")
            data=strat.application_filtre(strat,self.data_filtree,sens)

        print(data)
        self.poke_GUI.affichage_cartes_pokemons.affichage_poke_specifique(data.iloc[:, 1])




    def affichage_info_complete(self,event,pokemon_carte=None):
        # fct pr creer infos pkm
        def creer_info_pkm(nom, donnees):
            if nom is not None:
                dir_gif = self.poke_gif.get(nom)
                dir_img = self.poke_png.get(nom)
            else:
                dir_gif=dir_img=None
            return (nom, donnees, dir_gif, dir_img)
        
        # lst pr stocker infos pkm
        infos_pkm = []
        # obtenir idx des pkm sel ou pkm spec
        idxs = [0] if pokemon_carte else self.poke_GUI.zone_recherche.resultats.selection()
        
        # boucle pr traiter chq pkm
        for idx in idxs:
            if pokemon_carte:
                nom_pkm = pokemon_carte
            else:
                # obtenir ligne sel ds resultats recherche
                ligne_sel = self.poke_GUI.zone_recherche.resultats.item(idx)
                nom_pkm = ligne_sel["values"][1]
            
            # obtenir donnees pkm actuel
            donnees_pkm = self.poke_data.loc[self.poke_data.iloc[:, 1] == nom_pkm]
            idx_pkm = donnees_pkm.index[0]
            # ajouter infos pkm actuel
            infos_pkm.append(creer_info_pkm(nom_pkm, donnees_pkm))
            
            # traiter pkm prec et suiv
            for decalage in [-1, 1]:
                idx_voisin = idx_pkm + decalage
                if 0 <= idx_voisin < len(self.poke_data):
                    nom_voisin = self.poke_data.iloc[idx_voisin, 1]
                    donnees_voisin=self.poke_data.loc[self.poke_data.iloc[:, 1] == nom_voisin]
                    # ajouter infos pkm voisin
                    infos_pkm.append(creer_info_pkm(nom_voisin, donnees_voisin))
                else:
                # ajouter pas de pkm voisin
                    infos_pkm.append((None, None, None, None))

        # afficher infos pkm
        # maj affichage avc infos compl pkm
        self.poke_GUI.affichage_info_complete_pok(infos_pkm)

    def affichage_plus(self,affichage_par_30):
        if affichage_par_30:
            new_data=self.poke_data.iloc[self.compteur_cartes_pokemons_affiches:self.compteur_cartes_pokemons_affiches+30
                                            , 1]
            
            self.compteur_cartes_pokemons_affiches+=30
        self.poke_GUI.affichage_cartes_pokemons.affichage_poke_liste(new_data)

