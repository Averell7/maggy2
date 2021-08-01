#!/usr/bin/python
# coding: utf-8 -*-


###########################################################################
# VERSION #################################################################
###########################################################################
"""
maggy version = "2.0.0.41"
gbnew_perso version : 0.5
"""
###########################################################################
# SYSTEM LIBS #############################################################
###########################################################################

import sqlite3 as sqlite
import gtk
import os, sys, subprocess
import re

###########################################################################
# APPLICATION LIBS ########################################################
###########################################################################



###########################################################################
# CLASSES #################################################################
###########################################################################

class UserFunctions :



    def __init__(self, mag, arw, link, cursor, config, mem) :
        self.mag = mag
        self.arw = arw
        self.link = link
        self.cursor = cursor
        self.config = config
        self.mem = mem

        try :
            self.arw["button_cote"].connect("clicked", self.chercher_cote)
        except :
            print ("bouton pour les cotes manquant. Voir dans UserFunctions.py")
        try :
            self.arw["save_perso"].connect("clicked", self.save_perso)
        except :
            print ("bouton pour les notes personnelles manquant. Voir dans UserFunctions.py")
        try :
            self.arw["numeric_version"].connect("clicked", self.check_numeric_version)
        except :
            print ("bouton pour les versions numériques manquant. Voir dans UserFunctions.py")


        try :
            self.arw["@personnes"].connect("cursor-changed", self.presentation)
        except :
            print ('contrôle "@presentation" pas trouvé')


    def alert(self, message, trou = None, normal = None) :
        dialog = gtk.MessageDialog(None,0,gtk.MESSAGE_INFO,gtk.BUTTONS_CLOSE,
                               message)
        dialog.set_markup(message)
        dialog.run()
        dialog.destroy()




    def after_load(self, id_fiche, table_config, saisieActive, saisieFlipActive) :
        # launched after the load of a record in the edit window is finished
        # Effacer le champ présentation
        buf = self.arw["presentation"].get_buffer();
        buf.set_text("");

        """
        Aucun champ ne commence par un [espace].
        Les champs num, notes, compteur, temp, annee, siecle, tri_cote, compteur, datemodification et archives doivent être vides.
            Donc il suffirait de ne pas les importer. Mais si dJJ y a mis quelque chose, ce contenu manque probablement ailleurs,
            dans le champ où il devrait se trouver. (Est-il utile de donner la liste des champs qui ne doivent pas être vides ?
            Vous ne saurez pas ce qu'il faut y mettre.)
        Le champ localisation contient les deux lettres EX
        Si les champs sous-titre et complément sont vides, le titre finit par un point.
        Si l'un au moins des champs sous-titre et complément n'est pas vide, le titre finit par [espace]point-virgule.
            (Il existe une exception, mais impossible à construire en algorithme.)
        Si le champ sous-titre n'est pas vide et si le champ complément est vide, le sous-titre finit par un point.
        Si les champs sous-titre et complément ne sont pas vides, le sous-titre finit par [espace]point-virgule.
        Si le champ complément n'est pas vide, il finit par un point.
        Le champ date n'est jamais vide et finit toujours par un point.
        Le champ hauteur n'est jamais vide et finit par [espace]cm[point].
            (Il existe une exception mais dJJ ne la rencontrera pas.)
        Si le champ langue ne contient que français ou/et latin, il ne doit rien y avoir dans le champ traduction.
            (la règle inverse est difficile à formuler :
                Si le titre, le sous-titre et/ou le complément est en langue étrangère moderne,
                on en donne la traduction en français dans le champ traduction.)
        Les champs contenu et remarques, s'ils ne sont pas vides, finissent par un point.
        Vous avez déjà les règles pour remplir le format à partir de la hauteur.
        Remplacer eÌ par Ã© et Ì€ par Ã[espace]
            (Il y aura probablement d'autres caractères de ce genre venant d'un encodage inconnu,
            mais pour le moment, je n'ai rencontré que ces deux là : é et à.)

        """

        return

# ====================== Recherche d'une cote libre. =========================================
    # Les fonctions qui suivent, lancées par le bouton "Cote" de l'interface de saisie,
    # vont analyser la base pour chercher les cotes libres pour la section et le format entrés.

    def chercher_cote(self, widget = None) :

        section = self.arw["saisie@section"].get_text()
        format1 = self.arw["saisie@format"].get_text()
        siecle = self.arw["info_saisie@siecle"].get_text()
        self.section = section
        self.format1 = format1
        normal = ""
        message = ""
        message2 = ""
        trou = ""

        req = "select num, exposant, auteur, titre from complete where section like '%s' and format like '%s' and siecle = %s " % (section, format1, siecle)
        self.cursor.execute(req)

        nums = []
        exposants = {}
        for row in self.cursor :
            num = row[0]
            ex = row[1]
            if row[2] == None :
                auteur = ""
            else :
                auteur = row[2]
            if row[3] == None :
                titre = ""
            else :
                titre = row[3]

            nums.append(num)
            if num != None :
                if ex != None and ex.strip() != "" :    # Il y a un exposant
                    if not num in exposants :
                        exposants[num] = {}
                        exposants[num]['auteur'] = auteur
                        exposants[num]['titre'] = titre
                        exposants[num]['serie'] = []

                    if not ex in exposants[num]['serie'] :
                        exposants[num]['serie'].append(ex)


        series, trous, isolated, vides = self.analyse(nums, exposants)
        if len(trous) > 0 :
            trou = trous[0]
        else :
            trou = None

        if len(series) > 0 :
            normal = series[0][1]
            normal = int(normal) + 1
            normal = str(normal)

        message = u"Séries : " + repr(series)[1:-1] + "\n"          # [1:-1] pour enlever le crochet initial et final
        message += u"<b>Trous</b> : " + repr(trous)[1:-1]  + "\n"
        message += u"Numéros isolés : " + repr(isolated)[1:-1]  + "\n"
        message += str(vides) + u" fiches sans numéro."

        # Traitement des exposants
        message2 = u""
        keys = exposants.keys()
        keys.sort()



        for key in keys :
            val = exposants[key]
            val['serie'].sort()
            ex_list = ", ".join(val['serie'])

            if val['serie'][0].isalpha() :          # Brochures
                message2 += "\n" + str(key) + " : " + ex_list
                # Chercher les premières lettres libres
                libres = []
                for i in range(97,123) :
                    if chr(i) not in val['serie'] :
                        libres.append(chr(i))
                if len(libres) > 0 :
                    libres_list = ",".join(libres)
                    message2 += "\n          Libres : " + libres_list
            else :
                 message2 += "\n" + str(key) + " : " + val["auteur"] + ", " + val["titre"] + "\n          " + ex_list
        self.num_dialog(message, message2, trou, normal)

        return



    def analyse(self,nums, exposants) :
        # Cherche les séries et les trous dans une suite numérique
        # Compte également les valeurs nulles (None)

        num_series = []
        vides_serie = []
        trous = []
        vides = 0
        premier = 0
        dernier = 0
        mem = 0
        serie = 0           # série en cours


        # traiter les numéros vides
        nums2 = []
        for i in nums :
            if i == None :
                vides += 1
                continue
            else :
                nums2.append(i)

        # diviser en séries
        nums2.sort()

        if len(nums2) > 0 :
            for num in nums2 :
                if mem == 0 :
                    premier = num
                    mem = num
                    continue
                if (num == mem) or (num == mem + 1) :
                    mem = num
                    continue
                elif num == mem + 2 :           # simple trou
                    trous.append(mem + 1)
                    mem = num
                elif num == mem + 3 :           # trou deux numéros
                    trous.append(mem + 1)
                    trous.append(mem + 2)
                    mem = num

                else :
                    num_series.append([premier, mem])
                    mem = num
                    premier = num

            # terminer la série
            if mem > 0 :
                num_series.append([premier, num])

        # Extraire les séries à numéro unique
        series2 = []
        isolated = []
        for serie in num_series :
            if serie[0] == serie[1] :
                isolated.append(serie[0])
            else :
                series2.append(serie)

        return (series2, trous, isolated, vides)


    def num_dialog(self, message1, message2, trou = None, normal = None) :

        # fenêtre de dialogue ouverte par le bouton "Cote" de l'interface de saisie
##        dialog = gtk.MessageDialog(None,0,gtk.MESSAGE_INFO,gtk.BUTTONS_CLOSE,
##                               message1)
##        area = dialog.get_message_area()        # VBox à laquelle on peut ajouter des lignes
##        sw1 = gtk.ScrolledWindow()
##        textview1 = gtk.TextView()
##        button1= gtk.Button("Trou")
##        button2= gtk.Button("Normal")
##        hbox1 = gtk.HBox(2)
##        hbox2 = gtk.HBox(2)
##        entry1 = gtk.Entry()
##        entry2 = gtk.Entry()
##        hbox1.pack_start(entry1)
##        hbox2.pack_start(entry2)
##        hbox1.pack_start(button1)
##        hbox2.pack_start(button2)
##
##        sw1.add(textview1)
##        area.pack_start(sw1)
##        area.pack_start(hbox1)
##        area.pack_start(hbox2)

        self.widgets = gtk.Builder()
        self.widgets.add_from_file(os.path.join(self.mag.configdir_u, 'cotes.glade'))
        arWidgets = self.widgets.get_objects()

        self.arcotes = {}
        for z in  arWidgets:
            name = gtk.Buildable.get_name(z)
            self.arcotes[name]= z
            z.set_name(name)


        self.widgets.connect_signals(self)
        self.dialog1 = self.arcotes["dialog1"]
        self.dialog1.show_all()

        if message2 == None or message2.strip() == "" :
            self.arcotes["frame1"].hide()
        else :
            buf = self.arcotes["textview1"].get_buffer()
            buf.set_text(message2)

        if trou != None :
            self.arcotes["entry1"].set_text(str(trou))

        if normal != None :
            self.arcotes["entry2"].set_text(str(normal))
        self.arcotes["label1"].set_markup(message1)


        self.dialog1.move(500,200) # horizontale, verticale
        self.dialog1.run()
        self.dialog1.destroy()



    def set_num(self, entry) :

        # fonction lancée par le bouton de validation de l'interface précédente.

        old_num = self.arw["saisie@num"].get_text()
        new_num = entry.get_text()
        req = "select id_livre from complete where section = '%s' and format = '%s' and num = '%s'" % (self.section, self.format1, new_num)
        self.cursor.execute(req)
        if self.cursor.fetchone() != None :
            self.alert("Cette cote est déjà utilisée !")
            return
        elif old_num.strip() != "" :
            self.alert("Il y a déjà un numéro ! ")
        else :
            self.arw["saisie@num"].set_text(new_num)
            self.dialog1.destroy()
        # TODO : Avertir si un numéro existe déjà dans le champ


# ============ Gestion des versions numériques d'un document ============================

    def check_numeric_version(self, widget) :
        cote = self.arw["detail_cote"].get_text().split()

        section = cote[0]
        num = cote[1]
        format1 = cote[2]
        for path in os.walk("//192.168.1.4/textes/GB") :
            for filename in path[2] :
                filepath = os.path.join(path[0], filename)
                if os.path.isfile(filepath) :
                    cote = filename.split()
                    if (cote[0].strip() == section
                        and cote[1].strip() == num
                        and cote[2].strip() == format1) :
                            self.alert("Trouvé : " + filename)
                            if sys.platform == 'linux2':
                                subprocess.call(["xdg-open", filepath])
                            else:
                                os.startfile(os.path.normpath(filepath))




# ============ Gestion des commentaires personnels =============================

    def save_perso(self, widget) :
        data1 = get_text(self.arw["textperso1"])
        data2 = get_text(self.arw["textperso2"])
        id_livre = self.mem["selected_record"]
        req = "update complete set perso1 = '%s', perso2 = '%s' where id_livre = %d" % (data1, data2, int(id_livre))
        self.cursor.execute(req)
        self.link.commit()


    def __________presentation__________() :
        pass

    def presentation(self, treeview) :

        sel=treeview.get_selection()
        (model, arPaths) = sel.get_selected_rows()
        if model and arPaths :
            iter = model.get_iter(arPaths[0])
            id1 = model.get_value(iter, 0)
            req = "select presentation from personnes where id_personne = %s" % id1
            self.cursor.execute(req)
            row = self.cursor.fetchone()
            buf = self.arw["presentation"].get_buffer();
            if row != None and row[0] != None :
                buf.set_text(row[0])
            else :
                buf.set_text("")


# =========================================================
def analyse(f1, f2,section, format1, siecle) :

# analyse de l'utilisation des numéros dans les cotes. Sortie sur fichier.
# Rendu inutile par la fonction chercher_cote dans UserFunctions, qui fait la même chose de façon dynamique

    req = "select num from complete where section like '%s' and format like '%s' and siecle = %d" % (section, format1, siecle)
    cursor.execute(req)

    nums = []
    for row in cursor :
        nums.append(row[0])

    f1.write( str(siecle) + " " + section + " " + " " + format1 + " " )
    if len(nums) == 0 :
        f1.write("\n" + chr(9)*2 + str(len(nums)) + " fiches \n")
        return


    uf =UserFunctions("","","","","","")
    result = uf.analyse(nums)

    (series, trous, isolated, vides) = result

    f1.write( "Séries : " + repr(series) + "\n")

    # informations complémentaires
    f1.write(chr(9)*2 + str(len(nums)) + " fiches ")
    if vides > 0 :
        f1.write("; Sans numéro : " + str(vides) + "\n")
    else :
        f1.write("\n")

    complement_b = False
    if len(trous) > 0 :
        f1.write(chr(9)*2 + "manques :" + repr(trous) )
        complement_b = True
    if len(isolated) > 0 :
        f1.write(chr(9)*2 + "Isolés :" + repr(isolated) )
        complement_b = True
    if complement_b == True :
        f1.write("\n")


    f2.write( section + chr(9) + format1 + chr(9) + str(siecle) + chr(9) )
    if len(series) == 0 :
        f2.write(repr(isolated) + "\n")
    else :
        f2.write(repr(series) + "\n")

def test() :

    f1 = open("cotes.txt", "w")
    f1.write(chr(239) + chr(187) + chr(191))
    f2 = open("cotes_ref.txt", "w")


    for section in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "R",
                    "AA", "BB", "CC", "DD", "EE", "FF", "GG", "II", "KK", "LL", "MM", "NN", "OO" ] :
        print (section)
        for format1 in ["A", "B", "C", "D", "E"] :
            f1.write("\n")
            for siecle in range (20,22) :

                analyse (f1, f2, section, format1, siecle)

    f1.close()


def test2() :

    f1 = open("cotes_test.txt", "w")
    f2 = open("cotes_test2.txt", "w")
    f1.write(chr(239) + chr(187) + chr(191))



    for section in ["P", "R" ] :
        print (section)
        for format1 in ["C", "D"] :
            f1.write("\n")
            for siecle in range (20,22) :

                analyse (f1, f2, section, format1, siecle)

    f1.close()

def test3() :
    uf = UserFunctions("","",link, cursor,"","")
    section = "D"
    format1 = "D"
    siecle = "20"

    req = "select num from complete where section like '%s' and format like '%s' and siecle = %s " % (section, format1, siecle)
    cursor.execute(req)

    nums = []
    for row in cursor :
        nums.append(row[0])

    series, trous, isolated, vides = uf.analyse(nums)
    if len(trous) > 0 :
        trou = trous[0]
    else :
        trou = None

    if len(series) > 0 :
        normal = series[0][1]

        message = u"Séries : " + repr(series)[1:-1] + "\n"          # [1:-1] pour enlever le crochet initial et final
        message += u"<b>Trous</b> : " + repr(trous)[1:-1]  + "\n"
        message += u"Numéros isolés : " + repr(isolated)[1:-1]  + "\n"
        message += str(vides) + u" fiches sans numéro."

    uf.num_dialog(message, trou, normal)


def check_numeric_version(self, widget) :
        section = self.arw["detail_cote"].get_text()
        section = re.sub("\s+", " ", section).strip()       # nettoye les éventuels espaces supplémentaires

        self.alert(section)



# ==================================================================================

def main() :
    import os
    global configdir_u, link, cursor
    configdir_u = "d:/Mes Documents/en cours/maggy1.1/config"

    sqlite_file = os.path.join(configdir_u, "gbnew/gbnew.sqlite")

    link = sqlite.connect(sqlite_file)
    link.isolation_level = "DEFERRED"
    link.row_factory = sqlite.Row
    cursor = link.cursor()








if __name__ == '__main__':
    main()