import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
from functools import partial


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pokedex Python GUI")
        #Initialisation taille du pokedex_GUI
        ecran_largeur = self.winfo_screenwidth()
        ecran_longeur = self.winfo_screenheight()
        self.geometry(f"{ecran_largeur-(ecran_largeur//2)}x{ecran_longeur-(ecran_longeur//2)}")
        self.minsize(500,300)

        #Initialisation fond d'ecran (avec son mode obscure)
        #On configure leur taille selon la taille de l'ecran du pc
        self.ecran=Image.open("View/fond_ecran_pokedex.jpeg").resize((ecran_largeur+20,
                                                                      ecran_longeur+25))
        self.ecran_obscur=Image.open("View/fond_ecran_dark.jpeg").resize((ecran_largeur+20,
                                                                                        ecran_longeur+15))
        self.ecran_actuel=self.ecran  #Variable qui va permettre de switch les ecrans
        

        #Initialisation du fond d'ecran 
        self.fond_ecran=Fond_Ecran(self,self.ecran,"red",ecran_principal=True)
        self.fond_ecran.pack(expand=True,fill="both")

        #Frames contenant les filtres
        self.filtres_avancee=Frame_dynamique_filtres(self,1.5,0.15,0.0502,True,0.4,0.85,1,teleport=(True,0.95))
        self.boutton_filtres_avancee=ttk.Button(self,text="Filtres",
                                              command=lambda:self.filtres_avancee.animation(self.boutton_filtres_avancee))
        self.boutton_filtres_avancee.place(relx=0.4975,rely=0.95,relwidth=0.429,relheight=0.05)

        #Ordre d'initialisation important!!!
        #Initialisation de la barre de recherche
        self.zone_recherche=Frame_Recherche_simple(self,size=ecran_longeur//60)
        self.zone_recherche.place(relx=0.005,relwidth=0.4,y=0)

        #Initialisation des réglages du Pokedex_GUI
        self.configuration=Frame_dynamique_configuration(self,-0.4,0.035,0.50,False,0.4,0.2,5)
        self.boutton_configuration=ttk.Button(self,text="Configuration",
                                                    command=self.configuration.animation).place(relx=0.92,
                                                    rely=0.95,relheight=0.05,relwidth=0.08)
        
        #Initialisation des affichages graphiques des pokemons
        self.affichage_cartes_pokemons=Frame_poke_affichage(self,self.ecran)


    def affichage_info_complete_pok(self,info):
        pokemon_principal=info[0]
        pokemon_nom=pokemon_principal[0]
        poke_data=pokemon_principal[1]
        gif_principal=pokemon_principal[2]
        image_principal=pokemon_principal[3]
        poke_info_window=Poke_Details_Window(pokemon_nom,gif_principal,image_principal,poke_data)
        for a in poke_data.columns:
            valeurs=poke_data[a].tolist()
            ttk.Label(poke_info_window,text=f"{a}:{valeurs}").pack(side="left")
        # Si on ferme le window, on indique d'arrêter lethred
        poke_info_window.protocol("WM_DELETE_WINDOW", poke_info_window.fermer_and_stop_thread)
        
        threading.Thread(target=poke_info_window.configuration_gif).start()  #On le traite à part pour pas perturber le fonctionnement de notre GUI.

    def actualisation_mode_obscur(self):
        if self.ecran_actuel==self.ecran:
            self.ecran_actuel=self.ecran_obscur #On swich d'ecran
            couleur="#113B47"
        else:
            self.ecran_actuel=self.ecran
            couleur="#2992B0"

        if self.configuration.ecran_actuel_configuration==self.configuration.image_configuration:
            self.configuration.ecran_actuel_configuration=self.configuration.image_configuration_obscure
        else:
            self.configuration.ecran_actuel_configuration=self.configuration.image_configuration

        self.fond_ecran.switch_mode_ecran(self.ecran_actuel) #On met a jour le nouveau ecran
        self.configuration.fond_ecran_configuration.switch_mode_ecran(self.configuration.ecran_actuel_configuration)
        for ecran in self.filtres_avancee.ecrans_filtres:
            ecran.config(bg=couleur)
        for pokemon,carte in self.affichage_cartes_pokemons.dico_image_carte.items():
            carte[0].configure(bg=couleur)
#Création objet Canvas pour gerer l'affichage du fond d'ecran
#Aussi pour gerer les regions de scroll possibles
class Fond_Ecran(tk.Canvas):
    def __init__(self,mere,ecran,fond="magenta",affichage_pokemon=None,ecran_principal=False,expansion=1):
        super().__init__(mere,bg=fond)
        self.image_fond_ecran=ecran
        self.mere=mere
        self.ecran_principal=ecran_principal
        
        if self.image_fond_ecran!=None:
            #Si le canvas change de taille (<=> si fenetre change de taille (car canvas occupant toute la fenêtre))
            self.bind('<Configure>', self.config_fond_ecran)
        self.affichage_pokemon=affichage_pokemon
        #attribut affichage_pokemon: On l'utilise que pour notre fenêtre top_level (info complete des pokemons)

    def config_fond_ecran(self,event=None,numb_pokemons=40): #valeur arbitraire (numb de pokemons par ecran)
        #On utilise pas l'argument event fournie par "bind"    
        
        #On va ajuster le fond d'ecran selon la taille de la fenêtre
        largeur=self.winfo_width()
        hauteur=self.winfo_height()
        # print("info ecran:",largeur,hauteur)
        
        #ratio du fond d'ecran et celui de la fenêtre:
        ratio_image=(self.image_fond_ecran.size[0]/self.image_fond_ecran.size[1])
        ecran_ratio=largeur/hauteur
  


        if ratio_image<ecran_ratio:
            x=int(largeur)
            y=int(x/ratio_image)
        else:
            y=int(hauteur)
            x=int(y*ratio_image)

        #On actualise alors la taille de l'ecran:
        ecran_actualisee=self.image_fond_ecran.resize((x,y))
        self.ecran_actualisee_tk=ImageTk.PhotoImage(ecran_actualisee)
        #Et on la recentre pour l'expandir
        self.create_image(int(largeur/2),
                          int(hauteur/2),
                          image=self.ecran_actualisee_tk,
                          anchor="center")
        if self.affichage_pokemon is not None:
            self.image_tk = ImageTk.PhotoImage(self.affichage_pokemon.resize((72,130)))

            # Obtenir les dimensions du Canvas
            largeur_canvas = self.winfo_width()
            hauteur_canvas = self.winfo_height()
            # Afficher l'image au centre du Canvas
            self.create_image(largeur_canvas*0.82, hauteur_canvas*0.85, image=self.image_tk, anchor="center")
        
        if self.ecran_principal:
            for filtre,scale in self.mere.filtres_avancee.stock_scale_tkinter.items():
                scale.dessin_slider(largeur*0.4*0.352,hauteur*0.1*0.95)
    

    def switch_mode_ecran(self,ecran):
        self.image_fond_ecran=ecran #On change d'ecran
        self.config_fond_ecran() #on actualise le fond d'ecran

#Frame personnalisée représentant la barre de recherche
class Frame_Recherche_simple(ttk.Frame):
    def __init__(self,mere,size):
        super().__init__(mere)
        self.mere=mere

        #Initialisation de la barre de recherche
        self.nom_nombre=tk.StringVar()  #Variable des entrees
        self.entree_nm_nb=ttk.Entry(self,textvariable=self.nom_nombre,font=('Helvetica', size)) #Barre de recherche
        self.entree_nm_nb.pack(fill="x")                
        self.entree_nm_nb.insert(0, "Nom ou numéro Pokemon") #Indications à l'user
        # Liaison d'événement pour effacer le texte initial lorsqu'un clic est effectué sur l'entry
        self.entree_nm_nb.bind("<FocusIn>", self.effacer_texte)
        # Liaison d'événement pour restaurer le texte initial s'il n'y a pas de texte entré
        self.entree_nm_nb.bind("<FocusOut>", self.remettre_texte)
        #Si on appuie sur la touche return
        self.entree_nm_nb.bind('<Return>', self.rechercher)

        #Boutton pour chercher les résultats
        self.afficher_frames=True #Booleen permettant de savoir si afficher les frames des pokemons ou pas
        self.boutton_recherche=ttk.Button(mere,text="chercher!")
        self.filtre_stringvar=tk.StringVar()
        self.box_ordre=ttk.Combobox(mere,textvariable=self.filtre_stringvar)
        self.boutton_ordre=ttk.Button(mere,text="Ordre")

        self.boutton_recherche.place(relx=0.4,relwidth=0.1,y=0,relheight=0.05)


        self.resultats=ttk.Treeview(self,columns=("Id_numero","Id_nom","Caract1","Caract2"),show="headings")  #""""Tableur tkinter"""""


        self.nom_nombre.trace("w", self.ecriture_actualisation)  #Bizare car obligé 3 arguments!

      
    def configuration_box_ordre(self,liste_filtres):
        filtres = tuple(f"{filtre}-up" for filtre in liste_filtres) + tuple(f"{filtre}-down" for filtre in liste_filtres)
        self.box_ordre["values"]=filtres
        self.box_ordre.place(relx=0.4,relwidth=0.1,rely=0.05,relheight=0.05)
        self.boutton_ordre.place(relx=0.4,relwidth=0.095,rely=0.05,relheight=0.05)

        self.box_ordre.bind("<<ComboboxSelected>>",
                            lambda event: self.boutton_ordre.config(text=f"Ordre par: {self.filtre_stringvar.get()}"))
        

    def configuration_affichage_resultats(self,filtres_affiches):
        longeur_frame=self.winfo_width()
        longeur_par_colonne=longeur_frame//len(filtres_affiches)
        self.resultats=ttk.Treeview(self,columns=("Id_nom","Id_numero","Caract1","Caract2"),show="headings")
        
        #On itère à la fois sur la liste des filtres et sur les colonnes de notre treeview
        for filtre, col in zip(filtres_affiches, self.resultats["columns"]):
            self.resultats.heading(col, text=filtre)  #On change les titres des colonnes
            self.resultats.column(col,width=longeur_par_colonne)  #On met une largeur uniforme pour chaque colonne
                                                                                #On pourrait les personalisé....
        

    #On peut recevoir de la methode trace un nombre k d'arguments qu'on va pas utiliser.
    def ecriture_actualisation(self,*args): 
        entree=self.entree_nm_nb.get()
        self.resultats.delete(*self.resultats.get_children()) #Pour effacer les trucs d'avant

        if entree!="" and entree!="Nom ou numéro Pokemon":
            self.resultats.pack(fill="x")

            self.pack=False #Pour afficher que en treeview et pas graphiquement
            self.boutton_recherche.invoke()
            self.pack=True  #Pourquoi conversion en str!!!!
        else:
            self.resultats.pack_forget()


    def affichage_temps_reel(self,data_set):
        for index, (nb, nm, t1, t2) in enumerate(data_set):
            self.resultats.insert(parent="", index=index, values=(nb, nm, t1, t2))


    def rechercher(self,event):
        self.boutton_recherche.invoke()  #Une nouvelle fonction car bind nous donne des arguments qu'on veut pas

    
    def effacer_texte(self,event): #Dans les deux cas on s'en sert pas du event fourni par Bind
        # Efface le texte initial lorsque l'utilisateur clique dans l'entry
        if self.nom_nombre.get() == "Nom ou numéro Pokemon":
            self.nom_nombre.set("")

        # Change la couleur du texte à noir lorsque l'utilisateur commence à taper
        self.entree_nm_nb.config(foreground="black")


    def remettre_texte(self, event):
        print("ok")
        # Restaure le texte initial si l'entry est vide

        if not self.nom_nombre.get():
            self.nom_nombre.set("Nom ou numéro Pokemon")

        # Change la couleur du texte à gris si l'entry est vide
        self.entree_nm_nb.config(foreground="grey")

        return
        x,y=self.entree_nm_nb.winfo_x(),self.entree_nm_nb.winfo_y()
        x_2,y_2=self.entree_nm_nb.winfo_width(),self.entree_nm_nb.winfo_height()
        if x<int(event.x)<x_2 and y<int(event.y)<y_2:
            print("ok")

    
    def set_commands(self,command_boutton_recherche,command_boutton_ordre):#On reçoit la commande du boutton du Controller
        self.boutton_recherche["command"]= lambda: command_boutton_recherche(self.entree_nm_nb.get(),
                                                           self.pack) #Initialisé à True!   
        self.boutton_ordre["command"]=lambda: command_boutton_ordre(self.filtre_stringvar.get())



#Frame personalisee representant les filtres à la disposition d el'user
class Frame_dynamique_filtres(ttk.Frame):
    def __init__(self, mere, pos_initial, pos_final, pos_x, side_haut, largeur, hauteur, vitesse,teleport):
        super().__init__(mere)
        self.dico_echelles={} #Ici on va stocker les valeurs des filtres qu'ils ont des echelles
        self.stock_scale_tkinter={} #Stock des widgets pour qu'il se fassent pas eliminer
        self.bouttons_choisi=[] #Filtres selectionnées
        self.reset=False
        self.ecrans_filtres=[]

        #On divise nos filtres en plusieurs onglets
        self.manager=ttk.Notebook(self)
        self.manager.place(x=0,y=0,relwidth=1,relheight=1)
        
        
        self.fond_ecran_categoriques=tk.Canvas(self,bg="#2992B0")
        self.manager.add(self.fond_ecran_categoriques,text="filtres catégoriques")
        self.ecrans_filtres.append(self.fond_ecran_categoriques)

        self.fond_ecran_bataille=tk.Canvas(self,bg="#2992B0")
        self.manager.add(self.fond_ecran_bataille,text="Bataille")
        self.ecrans_filtres.append(self.fond_ecran_bataille)

        self.fond_ecran_autres=tk.Canvas(self,bg="#113B47")
        self.manager.add(self.fond_ecran_autres,text="Autres")
        self.ecrans_filtres.append(self.fond_ecran_autres)

        #Ajustements pour actualiser le place du frame et simuler un deplacement
        self.start = pos_initial + 0.04
        self.end = pos_final - 0.04
        self.pos_x = pos_x
        self.largeur = largeur
        self.hauteur = hauteur

        self.position = pos_initial
        self.invisible_GUI = True #Si il est placé "en dehors" de l'ecran
        self.Y = side_haut
        self.vitesse = vitesse
        self.teleport=teleport #Pour afficher juste au dessus du bouton filtres
        self.place(rely=self.start, relx=self.pos_x, relheight=self.hauteur, relwidth=self.largeur)
        self.position=self.teleport[1]


    def configuration_initiale(self,info_type_filtre,filtre_valeurs):
        #D'abbord les filtres categoriques
        self.filtres_categorique_classifies={}
        filtres_categoriques=[filtre for filtre,valeur in info_type_filtre.items() if valeur[1]=="Categorique_Type"]
        
        #Pour pas afficher deux fois les mêmes bouttons, on traite les valeurs de ces bouttons
        for i, filtre in enumerate(filtres_categoriques):
            for j, autres_filtres in enumerate(filtres_categoriques):
                #pas comparer le meme filtre
                if i < j:
                    test = all(elem in filtre_valeurs[autres_filtres] or elem is None for elem in filtre_valeurs[filtre])
                    if test:
                        self.filtres_categorique_classifies[filtre]=autres_filtres

        if len(self.filtres_categorique_classifies)>0:
            for filtre_categorique in self.filtres_categorique_classifies:
                filtre = self.filtres_categorique_classifies[filtre_categorique]
                if filtre is not None :
                    valeurs_filtres=filtre_valeurs[filtre_categorique]
                    if len(valeurs_filtres)<25:
                        for index, categorie in enumerate(valeurs_filtres):
                            if f"{categorie}" != "nan":
                                self.boutton_categorie = tk.Button(self.fond_ecran_categoriques,
                                                                    text=f"{categorie}",bg="grey")
                                self.boutton_categorie.configure(command=lambda cat=categorie,type_filtre=filtre_categorique
                                                                ,boutton=self.boutton_categorie: self.boutton_appuie(cat,type_filtre,boutton))
                                col = index // (len(filtre_valeurs[filtre_categorique]) // 4)
                                fila = index % (len(filtre_valeurs[filtre_categorique]) // 4)
                                self.boutton_categorie.place(relx=col * 0.2, rely=fila * 0.07 + 0.39)
                            # self.boutton_none = ttk.Button(self.fond_ecran_categoriques, text=f"no {filtre}",
                            #                 command=lambda : self.boutton_appuie(categorie,filtre_categorique))
                            # self.boutton_none.place(relx=0.8, rely=0.6)

        else:
            for filtre_categorique in filtres_categoriques:
                valeurs_filtres = filtre_valeurs[filtre_categorique]
                if len(valeurs_filtres) < 25:
                    label = tk.Label(self.fond_ecran_categoriques, text=filtre_categorique)
                    label.place(relx=0, rely=i * 0.5)
                    for index, categorie in enumerate(valeurs_filtres):
                        if f"{categorie}" != "nan":
                            self.boutton_categorie = tk.Button(self.fond_ecran_categoriques,
                                                                text=f"{categorie}", bg="grey")
                            self.boutton_categorie.configure(command=lambda cat=categorie, type_filtre=filtre_categorique
                            , boutton=self.boutton_categorie: self.boutton_appuie(cat, type_filtre, boutton))
                            col = index // (len(filtre_valeurs[filtre_categorique]) // 4)
                            fila = index % (len(filtre_valeurs[filtre_categorique]) // 4)
                            self.boutton_categorie.place(relx=col * 0.2, rely=fila * 0.07 + 0.39 + i * 0.5)

        filtres_bataille=[filtre for filtre,valeur in info_type_filtre.items() if valeur[1]=="BatailleStat_Type"]
        #Autres filtres:
        filtres_categoriques_court=[filtre for filtre,valeur in info_type_filtre.items() if valeur[1]=="Categorique_Type_court"]
        filtres_booleen=[filtre for filtre,valeur in info_type_filtre.items() if valeur[1]=="Booleen_Type"]
        filtres_exceptions=[filtre for filtre,valeur in info_type_filtre.items() if valeur[1]=="Autre_Type"]
        filtres_autres=[filtres_categoriques_court,filtres_booleen,filtres_exceptions]
        
        label_rely = 0.005
        increment = 0.09

        num_col = 7  

        for idx, filtre in enumerate(filtres_bataille):
            col_i = idx // num_col
            lig_i = idx % num_col
            espace_x = 0.02  

            # Titres
            label = ttk.Label(self.fond_ecran_bataille, text=filtre)
            label.place(relx=0.02 + col_i * 0.50, rely=label_rely + lig_i * (increment + espace_x), relwidth=0.35, relheight=0.03)

            # Doubles échelles
            slider_rely = label_rely + 0.03 + lig_i * (increment + espace_x)
            self.echelle = DoubleSlider(self.fond_ecran_bataille, filtre=f"{filtre}", min_val=min(filtre_valeurs[filtre]),
                                        max_val=max(filtre_valeurs[filtre]), canvas_master=self) #On lui passe le master du canvas
            self.echelle.place(relx=0.02 + col_i * 0.50, rely=slider_rely, relwidth=0.35, relheight=0.07)
            self.stock_scale_tkinter[filtre] = self.echelle


        self.selections_filtres = {}

        def etat_selection(*args, filtre=None, valeur=None, var=None):
            if var.get() == 1:
                if filtre in self.selections_filtres:
                    self.selections_filtres[filtre].append((valeur,var))
                else:
                    self.selections_filtres[filtre] = [(valeur,var)]
            else:
                if self.reset:
                    pass
                else:
                    if len(self.selections_filtres[filtre])<2:
                        del self.selections_filtres[filtre]
                    else:    
                        self.selections_filtres[filtre].pop()


        for filtres_actuels in filtres_autres:
            for filtre in filtres_actuels:
                frame_filtres = ttk.Frame(self.fond_ecran_autres)
                frame_filtres.pack(side="top", fill="x", padx=5, pady=5)

                titre = ttk.Label(frame_filtres, text=filtre)
                titre.pack(side="top", fill="x")

                for valeur in filtre_valeurs[filtre]:
                    var = tk.IntVar(value=None)  
                    checkbox = ttk.Checkbutton(frame_filtres, text=valeur, variable=var)
                    checkbox.pack(side="top", fill="x")
                    
                    var.trace("w", lambda *args, filtre=filtre, valeur=valeur, var=var: etat_selection(*args, filtre=filtre, valeur=valeur, var=var))


        self.boutton_reset=ttk.Button(self.fond_ecran_categoriques,text="Reset",command=self.reset_filtres)
        self.boutton_reset.place(relx=0.01,rely=0.92,relwidth=0.4,relheight=0.07)
        
        self.boutton_application=ttk.Button(self.fond_ecran_categoriques,text="Appliquer")
        self.boutton_application.place(relx=0.45,relwidth=0.51,rely=0.92,relheight=0.07)


    def boutton_appuie(self, valeur,filtre,bout):
        #On stocke les infos des boutttons appuyés
        if len(self.bouttons_choisi)==0:
            bout.configure(bg="blue")
            self.bouttons_choisi.append((bout,valeur,filtre))
        elif len(self.bouttons_choisi)==1:
            filtre_secondaire=self.filtres_categorique_classifies[filtre]
            if filtre_secondaire is not None:
                bout.configure(bg="blue")
                self.bouttons_choisi.append((bout,valeur,filtre_secondaire))
        


    def animation(self,boutton_filtres):
        if self.invisible_GUI:
            boutton_filtres["text"]="Cacher filtres"
            
            if self.teleport[0]:
                self.place(rely=self.teleport[1], relx=self.pos_x, relheight=self.hauteur, relwidth=self.largeur)
            self.animation_entree()
        else:
            boutton_filtres["text"]="Filtres avancées"
            self.animation_sortie()


    def animation_entree(self):
        if self.Y:
            if self.position > self.end:
                self.position -= 0.008
                self.place(rely=self.position, relx=self.pos_x, relheight=self.hauteur, relwidth=self.largeur)
                self.after(self.vitesse, self.animation_entree)
            else:
                self.invisible_GUI = False
        else:
            if self.position < self.end:
                self.position += 0.008
                self.place(rely=self.position, relx=self.pos_x, relheight=self.hauteur, relwidth=self.largeur)
                self.after(self.vitesse, self.animation_entree)
            else:
                self.invisible_GUI = False


    def animation_sortie(self):
        if self.Y:
            if self.position < self.start:
                self.position += 0.008
                self.place(rely=self.position, relx=self.pos_x, relheight=self.hauteur, relwidth=self.largeur)
                self.after(self.vitesse, self.animation_sortie)
            else:
                self.invisible_GUI = True
        else:
            if self.position > self.start:
                self.position -= 0.008
                self.place(rely=self.position, relx=self.pos_x, relheight=self.hauteur, relwidth=self.largeur)
                self.after(self.vitesse, self.animation_sortie)
            else:
                self.invisible_GUI = True


    def set_command_application(self,command):
        self.boutton_application["command"]=partial(command,self.dico_echelles,self.selections_filtres,self.bouttons_choisi)


    def reset_filtres(self,set_command=None):
        self.reset=True
        for echelle in self.stock_scale_tkinter.values():
            echelle.reset()
        
        for filtre, valeurs in self.selections_filtres.items():
            for val in valeurs:
                val[1].set(0)
        self.selections_filtres.clear()
            

        for boutton in self.bouttons_choisi:
            boutton[0].configure(bg="grey") 

        self.bouttons_choisi.clear()
        self.reset=False
        self.boutton_application.invoke()

#Frame personalisée représentant les configurations à la disposition de l'user
class Frame_dynamique_configuration(ttk.Frame):
    def __init__(self, mere, pos_initial, pos_final,pos_y,side_gauche,hauteur,largeur,vitesse):
        """Pos_initial:position relx avant animation
           Pos_final: position relx après animation
           pos_y: position rely
           side_gauche:booleen determinant si le frame bouge vers la gauche (True) ou vers la droite (False)
           hauteur,largeur,vitesse:[...] """
        super().__init__(mere)

        self.mere=mere #On garde une référence de notre GUI 

        self.image_configuration=Image.open("View/configuration_light.jpeg")
        self.image_configuration_obscure=Image.open("View/configuration_obscure2.jpeg")
        self.ecran_actuel_configuration=self.image_configuration
        self.fond_ecran_configuration=Fond_Ecran(self,self.image_configuration,"yellow")
        self.fond_ecran_configuration.pack(fill="both",expand=1)
        self.fond_ecran_configuration.bind("<Button-1>",self.verificar_clic)


        self.start = pos_initial + 0.04
        self.end = pos_final - 0.04
        self.pos_y=pos_y
        self.largeur = largeur
        self.hauteur=hauteur

        self.position = pos_initial
        self.invisible_GUI = True #dans ce cas, si Frame pas visible sur le GUI
        self.Y = side_gauche  
        self.vitesse=vitesse
        self.place(relx=self.start, rely=self.pos_y, relheight=self.hauteur, relwidth=self.largeur)

    def verificar_clic(self, event):
            x1_dark = self.winfo_width() * 0.54
            y1_dark = self.winfo_height() * 0.61
            x2_dark = x1_dark + (self.winfo_width() * 0.185)
            y2_dark = y1_dark + (self.winfo_height() * 0.17)

            x1_reset = self.winfo_width() * 0.315
            y1_reset = self.winfo_height() * 0.61
            x2_reset = x1_reset + (self.winfo_width() * 0.185)
            y2_reset = y1_reset + (self.winfo_height() * 0.17)


            if x1_dark <= event.x <= x2_dark and y1_dark <= event.y <= y2_dark:
                # #Boutton permettant de switch entre mode obscure ou pas
                self.mere.actualisation_mode_obscur()
            elif x1_reset <= event.x <= x2_reset and y1_reset <= event.y <= y2_reset:
                print("reset click!")

    def animation(self):
        if self.invisible_GUI:
            self.animation_entree()
        else:
            self.animation_sortie()


    def animation_entree(self):
        if self.Y:  
            if self.position > self.end: #Si pas arivee
                self.position -= 0.008
                self.place(relx=self.position, rely=self.pos_y, relheight=self.hauteur, relwidth=self.largeur)
                self.after(self.vitesse, self.animation_entree)
            else:
                self.invisible_GUI=False #Frame visible sur le GUI
        else:  # Si droite
            if self.position < self.end: #Si pas arivee
                self.position += 0.008
                self.place(relx=self.position, rely=self.pos_y, relheight=self.hauteur, relwidth=self.largeur)
                self.after(self.vitesse, self.animation_entree)
            else:
                self.invisible_GUI=False
  

    def animation_sortie(self):
        if self.Y:  # Si gauche
            if self.position < self.start: #Si pas arivee
                self.position += 0.008
                self.place(relx=self.position, rely=self.pos_y, relheight=self.hauteur, relwidth=self.largeur)
                self.after(self.vitesse, self.animation_sortie)
            else:
                self.invisible_GUI=True #Frame pas visible sur le GUI
        else:  #Si droite
            if self.position > self.start: #Si pas arivee
                self.position -= 0.008
                self.place(relx=self.position, rely=self.pos_y, relheight=self.hauteur, relwidth=self.largeur)
                self.after(self.vitesse, self.animation_sortie)
            else:
                self.invisible_GUI=True


#Frame qui affiche tous les pokemons (graphiquement)
class Frame_poke_affichage(ttk.Frame):
    def __init__(self,mere,fond_ecran):
        super().__init__(mere)
        self.pokemons_affiches=30
        self.dico_pokemon_carte={} #Contient toutes les cartes
        self.dico_image_carte={}  #Tous les canvas qui doivent contenir une image
        self.poke_cartes_affichees=[] #Tous les pokemons affiches
        self.images_stock=[] #Toutes les images pour que le recolecteur ne les effacent pas

        self.affichage_par30=True  #Pour differencié du cas lorsqu'on on cherche par filtres.

        self.affichage_info_complete=ttk.Button(self)

        self.place(relx=0.5,rely=0.05,relwidth=0.4999,relheight=0.9)
        self.canvas=tk.Canvas(self,bg="pink",scrollregion=(0,0,self.winfo_width(),self.pokemons_affiches*330))
        self.canvas.pack(fill="both",expand=1)
        
        self.frame=ttk.Frame(self)
        self.boutton_afficher_plus=ttk.Button(self.frame,text="Afficher plus")
        # self.fond_ecran=Fond_Ecran(self.frame,fond_ecran,expand_ecran=True,region_de_scroll=(0,0,500,800))
        # self.fond_ecran.pack(fill="both",expand=1)

        

        self.scroll_bar=ttk.Scrollbar(self,orient="vertical",command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_bar.set)
        self.scroll_bar.place(relx=1,rely=0,relheight=1,anchor="ne")
        self.bind("<Configure>",self.configuration_affichage)


    def affichage_poke_liste(self,poke_nom_data,initialisation=False):
        self.pokemons_affiches+=30
        self.boutton_afficher_plus.pack_forget()
        for poke_nom in poke_nom_data:
            carte,numero=self.dico_pokemon_carte[poke_nom]
            image_carte=self.dico_image_carte[poke_nom][0]
            carte.pack(fill="both",padx=(0,15))
            self.amine=ImageTk.PhotoImage(Image.open(self.dico_image_carte[poke_nom][1]).resize((150,200)))
            self.images_stock.append(self.amine)
            image_carte.create_image(40,40,image=self.amine,anchor="nw")
            self.poke_cartes_affichees.append(carte)
        self.boutton_afficher_plus.pack(fill="x",expand=False)
        
        #         # for carte in self.poke_cartes_affichees:
        # #     carte.pack_forget()
        # if not initialisation:
        #     self.boutton_afficher_plus.pack_forget()
        #     self.pokemons_affiches+=30
        #     self.configuration_affichage(None)

    def affichage_poke_specifique(self,poke_nom_data):
        
        for carte in self.poke_cartes_affichees:
            carte.pack_forget()
            self.boutton_afficher_plus.pack_forget()
        self.poke_cartes_affichees.clear()
        for num,poke_nom in enumerate(poke_nom_data):
            if num<30:
                carte,numero=self.dico_pokemon_carte[poke_nom]
                image_carte=self.dico_image_carte[poke_nom][0]
                direction=self.dico_image_carte[poke_nom][1]
                carte.pack(fill="both",padx=(0,15))
                self.amine=ImageTk.PhotoImage(Image.open(direction).resize((150,200)))
                self.images_stock.append(self.amine)
                image_carte.create_image(80,40,image=self.amine,anchor="nw")
                self.poke_cartes_affichees.append(carte)
            else:
                self.boutton_afficher_plus.pack(fill="both",expand=1)
                
                break
        

    def configuration_affichage(self,_):
        if self.affichage_par30:
            if self.pokemons_affiches*350>=self.winfo_height():
                hauteur_fenetre_scroll=self.pokemons_affiches*275
                # self.canvas.bind_all("<MouseWheel>",lambda event: self.canvas.yview_scroll(-int(event.delta/60),"units"))
                self.scroll_bar.place(relx=1,rely=0,relheight=1,anchor="ne")

            else:
                hauteur_fenetre_scroll=self.winfo_height()
                # self.canvas.unbind_all("<MouseWheel>")
                self.scroll_bar.place_forget()
        else:
            if self.pokemons_affiches*350>=self.winfo_height():
                hauteur_fenetre_scroll=self.pokemons_affiches*275
                # self.canvas.bind_all("<MouseWheel>",lambda event: self.canvas.yview_scroll(-int(event.delta/60),"units"))
                self.scroll_bar.place(relx=1,rely=0,relheight=1,anchor="ne")

            else:
                hauteur_fenetre_scroll=self.winfo_height()
                # self.canvas.unbind_all("<MouseWheel>")
                self.scroll_bar.place_forget()

        self.canvas.config(scrollregion=(0,0,self.winfo_width(),hauteur_fenetre_scroll))
        self.canvas.create_window((0,0),window=self.frame,
                        width=self.winfo_width(),
                        height=hauteur_fenetre_scroll,
                        anchor="nw")

    def creation_poke_carte(self, nom, numero,type1,type2):
        self.carte_pokemon = ttk.Frame(self.frame)

        # Canvas para el fondo de la carta de Pokemon
        self.fond_carte_pokemon = tk.Canvas(self.carte_pokemon, bg="#2992B0")
        self.fond_carte_pokemon.pack(fill="both", expand=True)


        self.canvas_information=tk.Canvas(self.fond_carte_pokemon,bg="pink")     
        self.canvas_information.pack(side="right",fill="both",expand=True)
      

        # Canvas para la imagen del Pokemon
        self.canvas_pokemon = tk.Canvas(self.fond_carte_pokemon, bg="#2992B0")
        self.canvas_pokemon.pack(side="right", fill="both")
        self.canvas_pokemon.bind("<Double-Button-1>", lambda event, arg1=nom: self.on_carte_click(event,arg1))
        self.canvas_pokemon.bind("<MouseWheel>",lambda event: self.canvas.yview_scroll(-int(event.delta/60),"units"))



        # Label para el nombre y número del Pokemon
        label_pokemon_nom = tk.Label(self.canvas_information, text=f"{nom}", font=("Helvetica", 20), bg="grey")
        # label_pokemon_nom=tk.Canvas(self.canvas_information,bg="grey")
        label_pokemon_nom.pack(side="top", fill="x")


        label_pokemon_numero = tk.Label(self.canvas_information, text=f"#{numero}", bg="#2992B0")
        # label_pokemon_numero=tk.Canvas(self.canvas_information,bg="black")
        label_pokemon_numero.pack(side="top", fill="x")

        # Canvas para los tipos de Pokemon
        # canvas_type1 = tk.Canvas(self.canvas_information, bg="green")
        # canvas_type1.create_text(20, 60, text=type1, font=("Helvetica", 20))
        canvas_type1=tk.Label(self.canvas_information,text=f"{type1}",bg="red",font=("Helvetica", 15))
        canvas_type1.pack(side="top",fill="both",expand=True)

        if type2 != "nan":
            # canvas_type2 = tk.Canvas(self.canvas_information, bg="yellow")
            # canvas_type2.create_text(20, 60, text=type2, font=("Helvetica", 20))
            canvas_type2=tk.Label(self.canvas_information,text=f"{type2}",bg="blue",font=("Helvetica", 15))
            canvas_type2.pack(side="top",fill="both",expand=True)

        return self.carte_pokemon, self.canvas_pokemon


    def initialisation_cartes_pokemons(self,data_pokemons,data_media):
        print("initialisation cartes:")
        for index,pokemon_info in data_pokemons.iterrows():
            poke_nom=pokemon_info.iloc[1]
            poke_numero=pokemon_info.iloc[0]
            poke_1=pokemon_info.iloc[2]
            poke_2=pokemon_info.iloc[3]
            pokemon_carte=self.creation_poke_carte(poke_nom,poke_numero,f"{poke_1}",f"{poke_2}")
            self.dico_pokemon_carte[poke_nom]=pokemon_carte[0],poke_numero
            self.dico_image_carte[poke_nom]=pokemon_carte[1],data_media[poke_nom]

        print("fin initialisation")


    def bout_set_command(self,command):
        self.boutton_afficher_plus["command"]=lambda: command(self.affichage_par30)

    def set_command_poke_affichage(self,command):
        self.affichage_info_complete["command"]=lambda: command(event=None,pokemon_carte=self.poke_nom_affichage)

    def on_carte_click(self,event,nom):
        self.poke_nom_affichage=nom
        self.affichage_info_complete.invoke()



class Poke_Details_Window(tk.Toplevel): #On crée une autre fenêtre qui n'interfere pas notre fenêtre principale 
    def __init__(self,nom_pokemon,direction_gif,direction_image,data):
        super().__init__()
        self.direction_image=direction_image
        self.thread_en_marche=True #Controle du Thread

        self.title(f"Info of {nom_pokemon} ")
        #Initialisation taille du pokedex_GUI
        ecran_largeur = self.winfo_screenwidth()
        ecran_longeur = self.winfo_screenheight()
        self.geometry("890x750")
        self.size #Juste pour actualiser les info sur la taille de la fenêtre
                    #Car en t=0 début tkinter fournies les relatives puis après en pixel
        self.largeur_fenetre = self.winfo_screenwidth()
        self.hauteur_fenetre = self.winfo_screenheight()
        
        self.minsize(550,720)
        self.maxsize(900,1200)
        
        self.ecran=Image.open("View/poke_info.jpeg")
# View/pokemon__template_no_evolution_by_trueform_d3hs6u9.png
        self.details_ecran=Fond_Ecran(self,self.ecran,"red",affichage_pokemon=Image.open(direction_image))
        self.direction_gif=direction_gif
        self.details_ecran.pack(fill="both",expand=True)
        self.poke_data=data
        self.configuration_affichage_data()
    
    def configuration_gif(self,width_rel=0.5, height_rel=0.25):
        gif_pokemon = Image.open(self.direction_gif)
        self.gif_frames = []
        

        gif_largeur = int(self.largeur_fenetre * width_rel)
        gif_hauteur = int(self.hauteur_fenetre * height_rel)
        for frame in range(gif_pokemon.n_frames):
            gif_pokemon.seek(frame)
            image_frame=(gif_pokemon.copy()).resize((110,150))
            frame_photo = ImageTk.PhotoImage(image_frame)
            self.gif_frames.append(frame_photo)
        self.delai_frames_gif = gif_pokemon.info["duration"]
        self.afficher_gif(0)


    def afficher_gif(self, compteur_frames_gif, pos_x_rel=0.24, pos_y_rel=0.53):
        if self.thread_en_marche:
            frame = self.gif_frames[compteur_frames_gif]
            canvas_width = self.details_ecran.winfo_width()
            canvas_height = self.details_ecran.winfo_height()
            pos_x = int(canvas_width * pos_x_rel)
            pos_y = int(canvas_height * pos_y_rel)
            
            # Supprimer l'image précédente si elle existe
            if hasattr(self, 'image_on_canvas'):
                self.details_ecran.delete(self.image_on_canvas)
            
            # Afficher la nouvelle frame
            self.image_on_canvas = self.details_ecran.create_image(pos_x, pos_y, image=frame, anchor='center')
            
            # Planifier la mise à jour suivante
            compteur_frames_gif = (compteur_frames_gif + 1) % len(self.gif_frames)
            self.after(self.delai_frames_gif, self.afficher_gif, compteur_frames_gif, pos_x_rel, pos_y_rel)


    def afficher_image(self,largeur_rel=0.25,hauteur_rel=0.25,x_rel=0.50,y_rel=0.45):
        self.image_pokemon=Image.open(self.direction_image)
        image_largeur = int(self.largeur_fenetre * largeur_rel)
        image_hauteur = int(self.hauteur_fenetre * hauteur_rel)
        pos_x = int(self.largeur_fenetre * x_rel)
        pos_y = int(self.hauteur_fenetre * y_rel)

        print("\n config de ton window:",self.largeur_fenetre,self.hauteur_fenetre)
        print("\n config de taille image:",image_largeur,image_hauteur)
        print("\n config de position image:",pos_x,pos_y,"\n")
        self.image_pokemon_tk=ImageTk.PhotoImage(self.image_pokemon.resize((image_largeur,image_hauteur)))
        self.details_ecran.create_image(pos_x,pos_y,image=self.image_pokemon_tk,anchor="center")
        
    def configuration_affichage_data(self):
        for index,label_filtre in enumerate(self.poke_data.columns):
            valeurs_filtres=self.poke_data[label_filtre].tolist()
            info=tk.Label(self.details_ecran,text=f"{label_filtre}: {valeurs_filtres}")
            if index<8:
                info.place(relx=0.45,rely=0.08+index*0.04)
            elif 7<index<10:
                info.place(relx=0.59,rely=0.08+(index-8)*0.04)
    def fermer_and_stop_thread(self):
        self.thread_en_marche=False #Controle du Thread
        self.destroy()



class DoubleSlider(tk.Canvas):
    def __init__(self, master=None, min_val=0, max_val=100,filtre="",canvas_master=None):
        super().__init__(master, bg="#2992B0")
        self.master=canvas_master
        self.min_val = min_val
        self.max_val = max_val
        self.bleu_min = min_val  
        self.rouge_max = max_val  
        self.filtre=filtre


        self.bind("<Button-1>", self.click)
        self.bind("<B1-Motion>", self.tirer)

        self.canvas_max=tk.Canvas(self,bg="red")
        self.canvas_max.place(relx=0.55,rely=0.15,relwidth=0.4,relheight=0.4)
        self.canvas_min=tk.Canvas(self,bg="blue")
        self.canvas_min.place(relx=0.05,rely=0.15,relwidth=0.4,relheight=0.4)

        # Crear elementos de texto para los valores mínimo y máximo
        self.text_min = self.canvas_min.create_text(40, 10, text=str(self.min_val),font=("Helvetica",15), anchor="w", fill="white")
        self.text_max = self.canvas_max.create_text(40, 10, text=str(self.max_val),font=("Helvetica",15), anchor="e", fill="white")


    def dessin_slider(self, largeur_relative, hauteur_relative):
        self.width = largeur_relative 
        self.height = hauteur_relative 

        self.margin = 20  #dist entre les ronds
        self.line_y = self.height // 2  #pos de la lign

        self.delete("all") #Si ligne deja dessin avant
        self.create_line(self.margin, self.line_y, self.width - self.margin, self.line_y, fill="lightgray", width=10)
        self.bleu = self.create_oval(self.margin - 10, self.line_y - 5, self.margin + 10, self.line_y + 5, fill="blue", outline="blue", tags="thumb")
        self.rouge = self.create_oval(self.width - self.margin - 10, self.line_y - 5, self.width - self.margin + 10, self.line_y + 5, fill="red", outline="red", tags="thumb")
 

    def click(self, event):
        #il le fait tout seul le calc
        closest = self.find_closest(event.x, event.y)[0]
        if closest == self.bleu:
            self.active_thumb = self.bleu
        elif closest == self.rouge:
            self.active_thumb = self.rouge


    def tirer(self, event):
        if hasattr(self, 'active_thumb'): #Si on appuie sur un
            x = min(max(event.x, self.margin), self.width - self.margin)
            val = int(((x - self.margin) / (self.width - 2 * self.margin)) * (self.max_val - self.min_val) + self.min_val)
            if self.active_thumb == self.bleu:
                if val <= self.rouge_max:  
                    self.bleu_min = val
                    self.coords(self.active_thumb, x - 10, self.line_y - 5, x + 10, self.line_y + 5)
                    self.canvas_min.itemconfig(self.text_min, text=str(val))  #on actualise le texte


            else:
                if val >= self.bleu_min:  #pour le rouge
                    self.rouge_max = val
                    self.coords(self.active_thumb, x - 10, self.line_y - 5, x + 10, self.line_y + 5)
                    self.canvas_max.itemconfig(self.text_max, text=str(val))  
        self.actualisation_valeurs()


    def actualisation_valeurs(self):
        #On actualise les valeurs dans notre dico (de "la mere de la mere" du canvas)
        self.master.dico_echelles[self.filtre] = (self.bleu_min, self.rouge_max)

    def reset(self):
        self.bleu_min = self.min_val
        self.rouge_max = self.max_val

        self.coords(self.bleu, self.margin - 10, self.line_y - 5, self.margin + 10, self.line_y + 5)
        self.coords(self.rouge, self.width - self.margin - 10, self.line_y - 5, self.width - self.margin + 10, self.line_y + 5)
        self.canvas_min.itemconfig(self.text_min, text=str(self.min_val))
        self.canvas_max.itemconfig(self.text_max, text=str(self.max_val))

        self.master.dico_echelles.clear()

