from abc import ABC, abstractmethod



class Filtre(ABC):
 
    @abstractmethod
    def application_filtre(self,data,valeur_filtree):
        pass

def set_strategy(filtre, test_numerique, Type, strategie="Recherche_Simple", trie=None):
    class Filtrage_Simple(Filtre):            
        def application_filtre(self, data, valeur_filtree):
            if test_numerique:
                #COMMENCENT par le num filtree
                if Type == "Id_Type":
                    return data[data[filtre].astype(str).str.startswith(str(valeur_filtree))]
                # Sinon, on filtre les données EGALES à la valeur filtrée convertie en entier
                else:
                    return data[data[filtre] == int(valeur_filtree)]
            # Si le test n'est pas numérique
            else:
                if Type == "Id_Type":
                    # On récupère les suggestions basées sur la valeur filtrée (suite des noeuds du caractère prèsent dans l'arbre)
                    suggestions = trie.suggestions(valeur_filtree.lower())  
                    # Si on a des suggestions, on filtre les données qui correspondent
                    if suggestions:   #Différent à la version 1.0 qui donnais tous les mots contenant (si il commence pas par "pi" ils pouvait qd mêne donnée Spinarak)
                        return data[data[filtre].str.lower().isin(suggestions)]
                    # Si on n'a pas de suggestions, on retourne un DataFrame vide
                    else:
                        return data.iloc[0:0]
                # Pour les autres types de chaînes de caractères, on utilise une comparaison directe
                else:
                    if Type=="Booleen_Type":
                        print("valeur_filtree:  ",valeur_filtree)
                        print("data",data[data[filtre]])
                        return data[data[filtre]==valeur_filtree]
                        # Si elle est présente, on filtre les données qui correspondent exactement
                    return data[data[filtre].str.lower() == valeur_filtree.lower()]

                #Demander laurine si pour identificator afficher slment ce qui commence par la chaine de charact
                #ou comme j'ai fais ceux que contiennent tous la chaine
    

    class Filtrage_Plage(Filtre):
            def application_filtre(self, data, valeur_filtree): #Ici valeur_filtree est un tuple
                if test_numerique:
                    if Type=="BatailleStat_Type":
                        return data[(data[filtre] >= valeur_filtree[0]) & (data[filtre] <= valeur_filtree[1])]
    

    class Random(Filtre):
            def application_filtre(self, data, valeur_filtree):
                num_pokemons = int(valeur_filtree)
                return data.sample(n=num_pokemons)

    
    class Ordre_Filtre(Filtre):
        def application_filtre(self, data, valeur_filtree=True):
            if valeur_filtree is True:
                return data.sort_values(filtre, ascending=True)
            else:
                return data.sort_values(filtre, ascending=False)    

    if strategie=="Recherche_Simple":
        return Filtrage_Simple
    elif strategie=="Recherche_plage_de_valeurs":
        return Filtrage_Plage
    elif strategie=="Random":
        return Random
    elif strategie=="Ordre":
        return Ordre_Filtre
     

