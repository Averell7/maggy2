#!/usr/bin/python
# coding: utf-8 -*-

# version 2.3.0.11 - août 2021



###########################################################################
# VERSION #################################################################
###########################################################################
# import sqlite3 --> not necessary; Franck set it lower : import sqlite3 as sqlite

#£ import json_decoder

maggy_version = "2.3.0"
print("Maggy Version : ", maggy_version)
"""
In this version :

fix bugs in predefined queries interface


TODO : dans cree_listes : ordre by a été supprimé de la version sqlite. Ce ne serait pas mal de le rétablir
mais il faudrait le faire aussi dans le configurateur

configurateur : Complement manque

"""


###########################################################################
# Notes on the base ##################################################
###########################################################################
"""
Necessary index in the database :

on words tables, an index Unique is necessary on the column of words. Otherwise there will be multiple entries for the same word

In peripheral tables, an index is necessary on the main field, otherwise inversion will take a very long time.

"""

###########################################################################
# Sorting and collating without accents ##########################################
###########################################################################


# remove accents
remove_accents1 = { "a" : "àáâãäåą",
                     "c" : "çćč",
                     "d" : "ð",
                     "e" : "èéêëęε",
                     "i" : "ìíîï",
                     "l" : "ł",
                     "n" : "ñńŋ",
                     "o" : "òóôõöøő",
                     "r" : "ř",
                     "s" : "šśß",
                     "u" : "ùúûüű",
                     "y" : "ýÿ",
                     "z" : "źżž",
                     "ae" : "æÆ",
                     "oe" : "œŒ"
                   }


remove_accents = {}
for key, value in remove_accents1.items() :
    for letter in value :
        remove_accents[letter] = key

# remove some other characters
for letter in "([<>…" :
    remove_accents[letter] = ""


###########################################################################
# SYSTEM LIBS #############################################################
###########################################################################

import os, sys
sys.path.append(os.path.abspath("./"))
import copy     # for deep copies (copy without reference)
import re, glob
from collections import OrderedDict

from optparse import OptionParser
from configparser import SafeConfigParser
from ctypes import *
import traceback
from operator import itemgetter, attrgetter
import pickle       # serialize but unreadable
import json         # serialize in a readable form
import zipfile
import io
#from collections import OrderedDict
import pprint

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Pango as pango
from gi.repository import Gio as gio
from gi.repository import cairo

##import StringMatcher
##from StringMatcher import *

Gtk.rc_parse("./gtkrc")

try :
    import _mysql
    import MySQLdb
    from MySQLdb import cursors
except :
    print("Mysql modules not installed.")


##try :
##    import pypyodbc         # for accdb tables
##except :
##    print ("pypyobdc not installed. accdb database not supported")

import sqlite3 as sqlite



###########################################################################
# LOCALISATION ############################################################
###########################################################################
import gettext
import locale
import elib_intl3
elib_intl3.install("maggy2", "share/locale")

###########################################################################
# APPLICATION LIBS ########################################################
###########################################################################

import magutils
from magutils import *
from ScriptExcept import *


# import path
sys.path.append(os.getenv("PYLIB"))


import time, datetime
#
Windows ="ntx"
osname = os.name
#

# Deepcopy Fixes
# Allows pickling objects that are not normally pickable by converting them to None
# The resulting copy won't be an exact copy
import copyreg
def _return_none(*args):
        return None
def _pickle_unpickable(instance):
    return _return_none, (None, )
copyreg.pickle(sqlite.Connection, _pickle_unpickable)
copyreg.pickle(sqlite.Cursor, _pickle_unpickable)


# ####################################################################
#            PHP compatibility functions
# ####################################################################

def strrpos(string, needle) :
    x = string.rfind(needle)
    return x

def strpos(string, needle) :
    x = string.find(needle)
    return x

def substr(string, pos, length = None) :
    if length :
        return string[pos:pos + length]
    else :
        return string[pos:]

def str_replace(search, replace, string) :
    if string == None :
        return None
    if isinstance(search, str) :
        string = string.replace(search, replace)
    if isinstance(search, list) :
        for i in range(len(search)) :
            if i >= len(replace) :
                break
            string = string.replace(search[i], replace[i])
    return string

def array_diff(ar1, ar2) :
    if isinstance(ar1, list) :
    # TODO : verify
    # This will keep all items of ar1 which are not present in ar2
    # but will left aside all keys of ar2 which are not present in ar1
    # is this really the behaviour of php ?

        ar3 = []
        for item1 in ar1 :
            if  not item1 in ar2 :
                ar3.append(item1)

    elif isinstance(ar1, dict) :
        # TODO : verify
        # This will keep all keys of ar1 which are not equal in ar2
        # but will left aside all keys of ar2 which are not present in ar1
        # is this really the behaviour of php ?
        keys1 = list(ar1.keys())
        keys2 = list(ar2.keys())
        ar3 = {}
        for key in keys1 :
            if key in keys2 :
                if ar1[key] == ar2[key] :
                    pass
                else :
                    ar3[key] = ar1[key]
            else :
                ar3[key] = ar1[key]

    return ar3

def array_intersect(ar1, ar2) :
    if isinstance(ar1, list) :
        ar3 = []
        for item1 in ar1 :
            if item1 in ar2 :
                ar3.append(item1)
## another possible version that would remove duplicates of ar1
##        set1 = set(ar1)
##        ar3 = ar1.intersection(ar2)

    elif isinstance(ar1, dict) :
        keys1 = list(ar1.keys())
        keys2 = list(ar2.keys())
        ar3 = {}
        for key in keys1 :
            if key in keys2 :
                if ar1[key] == ar2[key] :
                    ar3[key] = ar1[key]

    return ar3

def array_unique(list_a) :
    return list(set(list_a))

def array_chunk(list_a, size) :
    return [list_a[i : i + size] for i in range(0, len(list_a), size)]

def array_merge(list_a, list_b ) :
    if len(list_a) == 0 :
        return list_b
    if isinstance(list_a, list) :

        for b in list_b :
            if not b in list_a :
                list_a.append(b)

    # TODO : verify what is the exact behaviour of array_merge in php for dictionaries :
    # what happens if both arrays have the same key ? Here we keep the value of list_a
    elif isinstance(list_a, dict) :
        keys_a = list(list_a.keys())
        for key in list_b :
            if key not in keys_a :
                list_a[key] = list_b[key]
    return list_a


def array_search(item1, array_a, param = True) :        # TODO: what is param in php?
    if isinstance(array_a, list) :
        i = 0
        for data1 in array_a :
            if data1 == item1 :
                return i
            i += 1
        return None




#  ###########################################################
#             Utilities
# ############################################################

def sql_error(link, req = "", message = "") :

    error_s = utils.printExcept()
    if error_s :
        message2 = message + "\nsql_error : " + req + "\n" + error_s
        alert(message2)
        print("Error for : ", message2)
    e = sqlite.Error()

    # TODO : verify how all this functions
    e2 = e.args
    if len(e2) > 0 :
        print(e2)
    #Â£ sys.exc_clear()
    return

    """
                sql_error(link,req1);
                message = mysql_info(link) + "\n";
                if len(message) > 0 :

                    insertion_tv(buffer1,message);

                message = mysql_error(link) + "\n";
                if len(message) > 0 :

                    insertion_tv(buffer1,message);

    """

def sqlite_error(er,req = None) :
    error_s = utils.printExcept()

    #message_s = "Sqlite error : " + er.message
    if req :
        message_s += "\nfor query : " + req
    alert(message_s)
    return

def sqlite_error2(er,req = None) :
    error_s = utils.printExcept()

    message_s = "Sqlite error : " + er.message
    if req :
        message_s += "\nfor query : " + req
    alert(message_s)
    return

def config_error(missing_field, config, key) :
    message = "There is no field " + missing_field + " in " + config + "." + key
    message +="\nCheck your configuration"
    return message


def php_string(string) :
    data= re.sub("\$(\w*)", "\" + str(\g<1>) + \"", string)
    data = '"' + data + '"'
    data = data.replace("\n", " ")
    return data

def md(data) :
    if data == myDict() :
        return None
    else :
        return data

def check_key(dictionary,key) :
    if (key in dictionary) == False :
        dictionary[key] = None

    return dictionary


def v(dictionary, *keys) :  # verify is the keys exist (does not create level if it does not exist)
    temp1 = dictionary
    for key in keys :
        if not key in temp1 :
            return None
        temp1 = temp1[key]
    return temp1

def v2(dictionary, *keys) :  # verify is the keys exist (creates level if it does not exist)
    temp1 = dictionary
    keys_num = len(keys)
    for i in range(keys_num) :
        if i == 0 :
            if not keys[0] in dictionary :
                dictionary[keys[0]] = {}
        elif i == 1 :
            if not keys[1] in dictionary[keys[0]] :
                dictionary[keys[0]][keys[1]] = {}
        elif i == 2 :
            if not keys[2] in dictionary[keys[0]][keys[1]] :
                dictionary[keys[0]][keys[1]][keys[2]] = {}
        elif i == 3 :
            if not keys[3] in dictionary[keys[0]][keys[1]][keys[2]] :
                dictionary[keys[0]][keys[1]][keys[2]][keys[3]] = {}
        elif i == 4 :
            if not keys[4] in dictionary[keys[0]][keys[1]][keys[2]][keys[3]] :
                dictionary[keys[0]][keys[1]][keys[2]][keys[3]][keys[4]] = {}
        elif i == 5 :
            if not keys[4] in dictionary[keys[0]][keys[1]][keys[2]][keys[3]][keys[4]] :
                dictionary[keys[0]][keys[1]][keys[2]][keys[3]][keys[4]][keys[5]] = {}




def verif(dict1, field1) :
    if not field1 in dict1 :
        #print "field %s not found in dictionary 'inversion'" % field1
        return None
    else :
        return dict1[field1]

def convert_rtf_hexcode(string1) :


    a = re.sub(r"\\'([0-9a-e]{2})", r"\\x\1",  string1)
##    f1 = io.StringIO()
##    f1.write( "b = '")
##    f1.write(a)
##    f1.write("'")
##    exec(f1.getvalue())
##    f1.close()
##    c = unicode2(b)
##    return c
    return a    #Â£  Is this correct ??

##def debug22(string) :
##    f1 = open("debug22.txt", "a")
##    f1.write(str(string) + "\n")
##    f1.close()

def debug22(string) :
    return "my function works"

def to_utf8(value):
    if isinstance(value, str):
        return value.encode("utf-8")
    else:
        return value

"""
Dans l'array $d_logique, le dernier paramètre des array contient le critère logique construit ainsi :

    where $champ <critère logique>, avec $champ extrait de la première liste déroulante.
    Dans le critère logique lui-même <sel> est remplacé par le contenu tapé par l'utilisateur dans les zones de droite.
    Si donc on a sélectionné "personnes" "contient" et tapé "thomas", le critère devient :
        where p0.nom like "%thomas%".
    On notera que le critère est entouré de guillemets simples,
        ce qui permet d'utiliser les guillemets doubles à l'intérieur :
            'like "%<sel>%"'
"""



# List of functions proposed in the second combobox of Complex queries.
d_logique=[
    [ "contient",'where <champ> like <bin> "%<sel>%"'],
    [ "ne contient pas",'where <champ> not like <bin> "%<sel>%"'],
    [ "égal à",'where <champ> = <bin> "<sel>"'],
    [ "différent de",'where (<champ> <> <bin> "<sel>" or <champ> is null)'],
    [ "est vide",'where <champ> is null'],
    [ "n'est pas vide",'where <champ> is not null'],
    [ "commence par",'where <champ> like <bin> "<sel>%"'],
    [ "ne commence pas par",'where (<champ> not like <bin> "<sel>%" or <champ> is null)'],
    [ "finit par",'where <champ> like <bin> "%<sel>"'],
    [ "ne finit pas par",'where (<champ> not like <bin> "%<sel>" or <champ> is null)'],
    [ "supérieur strict à","where <champ> > <sel>"],
    [ "inférieur strict à","where <champ> < <sel>"]
    ]


###########################################################################
# CLASSES #################################################################
###########################################################################

### existing dict does not support multiple assignments like dict1["a"]["b"]["c"] = 1
### This will return an error : key "a" does not exist.
### To override this problem, we subclass dict to add the __missing__ method
### if an existing dict is given as argument, the new dict will be loaded with its content
##class myDict(dict) :
##
##    def __init__(self, array1 = None) :
##        # if an existing dict is given as argument, recurse its values and create the appropriate myDict
##        if array1 :
##            stack = [[array1, self]]
##            while len(stack) > 0 :
##                array1, self = stack.pop()
##                for key in array1 :
##                    if isinstance(array1[key], dict) :
##                        self[key] = myDict()
##                        stack.append([array1[key], self[key]])
##                    else :
##                        self[key] = array1[key]
##
##    def __missing__(self, arg) :
####        self[arg] = myDict()
####        return self[arg]
##        self.__setitem__(arg, myDict())
##        return self.__getitem__(arg)
##
##    # This method will test the existence of keys without creating them
##    #       as would do a simple : if dict1["a"]["b"]["c"]
##    # The syntax is : if dict1.exists(["a","b","c"])
##    # Returns True or False
##    def exists(self, args) :
##        test = self
##        try :
##            for arg in args :
##                if test.has_key(arg) == False :
##                    return False
## else :
##                    test = test[arg]
##            return True
##        except :
##            return False
##
##



class SqliteUnicode :
    #
    def __init__(self) :
        self.collation = { "a" : "àáâãäåą",
                           "e" : "eèéêëęε",
                           "i" : "iìíîï",
                           "o" : "òóôõöøő",
                           "u" : "uûü",
                           "c" : "cç",
                           "l" : "ł",
                           "n" : "ñńŋ",
                           "r" : "ř",
                           "s" : "sš",
                           "y" : "ýÿ",
                           "z" : "źżž",
                           "ae" : "æÆ",
                           "oe" : "œŒ"

                           }

        self.collation_ci = {}
        self.reg_exp = {}

        for key, value in self.collation.items() :
            for letter in value :
                self.collation_ci[letter] = value + value.upper()


        self.remove_accents = copy.deepcopy(self.collation)
        for key, value in remove_accents1.items() :
            for letter in value :
                self.remove_accents[letter] = key

        # remove some other characters
        for letter in "()[]<>…" :
            self.remove_accents[letter] = ""




        # regular expressions
        # We compile them to improve performance

        # These ones are used by collate
        self.re1 = re.compile("[àâä]")
        self.re2 = re.compile("[éèêë]")
        self.re3 = re.compile("[îï]")
        self.re4 = re.compile("[ôö]")
        self.re5 = re.compile("[ûü]")




    def replace_accents(self, string) :
    # This function will replace accentuated characters to allow a friendly like
    # e will find Ã©Ã¨Ãª etc. oe will find Å“

        string2 = ""
        for letter in string :
            if letter in self.remove_accents :
                string2 += self.remove_accents[letter]
            else :
                string2 += letter
        return string2


    def convert_to_regex(self, data) :

        c = ""
        if data in self.reg_exp :
            return self.reg_exp[data]

        reg_string = "(?ims)"     # create the regular expression
        for c in data :         # divide string in letters
            if c in "*.[]$()" :    # escape special characters
                                # TODO : are there others to escape ? What about % and ?
                reg_string += "\\" + c
            elif c == "%" :
                reg_string += ".*"
            elif c in self.collation_ci :
                reg_string += "[" + self.collation_ci[c] + "]"     # using collation_ci is not useful with (?i)
                                                                   # It should not, but presently it is for an unknown reason
            else :
                reg_string += c
        if c != "%" :           # if the last character is not %
            reg_string += "$"   # necessary to match only the whole string
        try :
            comp_reg = re.compile(reg_string)
        except re.error as e :
            print("compile error", reg_string)
        self.reg_exp[data] = comp_reg
        return comp_reg

    def like(self, a, b) :
        # On a 80000 rows table :
        # original like takes 0.032s
        # this like takes 0.25 s (about 8x)
        #print a,b
        try :
            if b == None or a == None :
                return False

            data = self.convert_to_regex(a)

            if data.match(b) :
                return True
            else :
                return False
        except :
            print("echec de like : ", a, "/", b)
            utils.printExcept()
            return False


    def like2(self, a, b) :
        # On a 80000 rows table :
        # original like takes 0.032s
        # this like takes 0.25 s (about 8x)
##        print a,b
        try :
            if b == None or a == None :
                return False
            a = self.replace_accents(a.lower())
            b = self.replace_accents(b.lower())
            a= a.replace("%", "")

            if a == b[0:len(a)]  :
                return True
            else :
                return False
        except :
            print("echec de like : ", a, "/", b)
            utils.printExcept()
            return False


    def regexp(self,a,b) :
        if b == None :
            return False
        if re.match(a,b) :
            return True
        else :
            return False

    def collate(self,string1, string2):

        #string1 = str(string1,"utf_8")
        #string2 = str(string2,"utf_8")
        string1 = string1.lower()
        string2 = string2.lower()

        string1 = self.re1.sub("a",string1)
        string1 = self.re2.sub("e",string1)
        string1 = self.re3.sub("i",string1)
        string1 = self.re4.sub("o",string1)
        string1 = self.re5.sub("u",string1)

        string2 = self.re1.sub("a",string2)
        string2 = self.re2.sub("e",string2)
        string2 = self.re3.sub("i",string2)
        string2 = self.re4.sub("o",string2)
        string2 = self.re5.sub("u",string2)

        #£ compare = cmp(string1, string2)
        # bad replacement, will work only if strings have the same length
        compare = (string1  > string2) - (string1 < string2)
        return compare

    def concat_ws(self, *args) :
        separator = args[0]
        data1 = args[1:]
        x= []
        # Remove None values
        for a in data1 :
            if a :
                x.append(a)
        return separator.join(x)


    def clean_commas(self, data1) :
        if data1 :
            data2 = re.findall("[0-9]+",data1)
            data3 =",".join(data2)
            return data3
        else :
            return data1

    def date2year(self,date1) :

        if date1 == None :
            return date1
        date1 =date1.split(",")[0]  # Delete all after a comma
        date2 = date1.split("-")
        if len(date2) < 2 :
            date2 = date1.split("/")
        if len(date2) == 3 :
            return date2[2]
        else :
            return date1


    def date2ymd(self,date1) :
        # converts dmy format to ymd to allow sorting
        # The job could be done with a regex
        separator = "-"
        if date1 == None :
            return date1
        date2 = date1.split("-")
        if len(date2) < 3 :
            date2 = date1.split("/")
            separator = "/"
        if len(date2) == 3 :
            if len(date2[0]) == 1 :
                date2[0] = "0" + date2[0]
            if len(date2[1]) == 1 :
                date2[1] = "0" + date2[1]

            return date2[2] + separator + date2[1] + separator + date2[0]
        else :
            return date1


class Import_csv :

    def __init__(self) :
        global record
        record = None

        # Setup treeview for authors
        self.store1 = Gtk.ListStore(int,int,str)
        mag.arw["s_treeview21"].set_model(self.store1)
        cr = Gtk.CellRendererText()
        colnew = Gtk.TreeViewColumn("id", cr, text=1);
        colnew.set_resizable(True);
        #colnew.set_reorderable(True);
        #colnew.set_sort_column_id(j);
        #colnew.set_clickable(True);
        #colnew.connect("clicked", "list_click_column");
        mag.arw["s_treeview21"].append_column(colnew);
        mag.arw["s_treeview21"].connect('row-activated', self.detail);
        mag.arw["s_treeview21"].connect('cursor-changed', self.detail);
        colnew = Gtk.TreeViewColumn("nom", cr, text=2);
        colnew.set_resizable(True);
        mag.arw["s_treeview21"].append_column(colnew);

        # Setup treeview for book titles
        self.store2 = Gtk.ListStore(str)
        mag.arw["s_treeview22"].set_model(self.store2)
        colnew = Gtk.TreeViewColumn("Title", cr, text=0);
        mag.arw["s_treeview22"].append_column(colnew);


        # Verify if columns collector_author and ISBN exist
        # TODO ++ : rendre générique
##        try :
##            query = "select collector_auteur from complete "
##            cursor.execute(query)
##        except :
##            query2 = "ALTER TABLE complete ADD COLUMN collector_auteur TEXT NULL "
##            cursor.execute(query2)
##
##        try :
##            query = "select ISBN from complete "
##            cursor.execute(query)
##        except :
##            query2 = "ALTER TABLE complete ADD COLUMN ISBN INTEGER NULL "
##            cursor.execute(query2)

    def detail(self, treeview):
        # Called by the change of selection in the authors list, shows the books of this author in the right treeview

        global mem, config, config_info, popup_saisie, listes, query
        global tab_conversion, periph_tables, treeview_data, affichage;

        sel=treeview.get_selection();
        (model, arPaths) = sel.get_selected_rows();
        if arPaths :
            iter = model.get_iter(arPaths[0])
            author_s = model.get_value(iter, 2);
            query3 = 'select titre from complete where auteur like "' + author_s + '" or collaborateur like "' + author_s + '"'
            cursor.execute(query3)
            model2 = mag.arw["s_treeview22"].get_model()
            model2.clear()
            for record in cursor :
                model2.append([record[0]])
            query = 'select presentation from personnes where nom like "' + author_s + '"'
            cursor.execute(query)
            data1 = cursor.fetchone()
            presentation = data1["presentation"]
            if presentation != None :
                buff1 = mag.arw["s_presentation"].get_buffer()
                buff1.set_text(presentation)

    def delete_event(self, window, event,param =1)  :

        if param == 1 :
            Gtk.main_quit()
            return False

        else :
            return True


    def OnDelete(self,)   :
        if  True :
            return False

        else :
            return True


    def gtk_widget_hide(self, widget)   :
        window = widget.get_toplevel()
        window.hide()


    def gtk_main_quit(self, widget = None)   :

        Gtk.main_quit()
        os._exit(0)


    def close_window(self, widget)   :
        window = widget.get_toplevel()
        window.hide()


    def loadfile(self, filename_u = None) :


        if filename_u == None :
            chooser = Gtk.FileChooserDialog(title=_('_Open Configuration'),
                    action=Gtk.FILE_CHOOSER_ACTION_OPEN,
                    buttons=(Gtk.STOCK_CANCEL,
                        Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OPEN,
                        Gtk.ResponseType.OK))
            chooser.set_current_folder(configdir_u)
            chooser.set_show_hidden(True)  #Test : does not work. Why ??

            filter_all = Gtk.FileFilter()
            filter_all.set_name(_('All files'))
            filter_all.add_pattern('*')
            chooser.add_filter(filter_all)

            filter_ini = Gtk.FileFilter()
            filter_ini.set_name(_('TXT files'))
            filter_ini.add_pattern('*.txt')
            chooser.add_filter(filter_ini)
            chooser.set_filter(filter_ini)

            response = chooser.run()
            if response == Gtk.ResponseType.OK:
                filename = chooser.get_filename()
                filename_u = str(filename,"utf-8")            # convert utf-8 to unicode for internal use

            elif response == Gtk.ResponseType.CANCEL:
                print((_('Closed, no files selected')))
                chooser.destroy()
                return
            chooser.destroy()

        f1 = open(filename_u,"r")
        # If BOM present, skip the first three bytes
        isBOM_s = f1.read(3)
        if isBOM_s == chr(239) + chr(187) + chr(191) :  # There is a BOM, skips it
            pass
        else :
            f1.seek(0)                             # No BOM, come back to beginning of file
        fields = f1.readline().strip()              # strip necessary to get rid of the \n
        fields = fields.split(chr(9))

        fields_a = {}
        try:
            f2 = open(os.path.join(configdir_u, "collector_fields_table.txt"), "r")
        except :
            alert("Could not open collector_fields_table.txt\nCheck if it is present in your config")
        BOM(f2)
        fields_data = f2.readlines()
        f2.close()
        for line in fields_data :
            try :
                name,widget = line.split("=")
                fields_a[name.strip()] = widget.strip()
            except :
                continue

        records_l = []
        while True :
            data1 = f1.readline()
            if (data1 == "") or (data1 == None) :
                break
            data1 = data1.split(chr(9))
            i = 0
            record = {}
            for data2 in data1 :

                if len(data2.strip()) > 0 :
                    collectorfieldname = fields[i]
                    #print fieldname, " = ", data2
                    if collectorfieldname in fields_a :
                        maggyfieldname = fields_a[collectorfieldname]
                        if maggyfieldname[0:1] == "+" :
                            maggyfieldname = maggyfieldname[1:]
                            if maggyfieldname in record :
                                temp = record[maggyfieldname]
                                record[maggyfieldname] = temp + "\n" + data2
                        else :
                            record[maggyfieldname] = data2

                    else :
                        print("field %s not found in collector_fields_table.txt" % collectorfieldname)
                i += 1
            #print record
            records_l.append(record)

        f1.close()
        return records_l






    def insert_into(self, table, data_a, **kwargs) :

        query = "insert into " + table
        fields_a = []
        values_a = []
        for field in data_a :
            if field in kwargs :
                value = kwargs[field]
            else :
                value = data_a[field]
                if field.lower() == "hauteur" :
                    try :
                        tmp1 = int(value)
                        value = str(tmp1 / 10) + " cm."
                    except :
                        pass
                if field.lower() == "pages" :
                    if value.strip() != "" :
                        value += " p."

            value = value.replace("'", "''")        # escape single quotes
            fields_a.append(field)
            values_a.append("'" + value + "'")
        fields_s = "(" + implode(",", fields_a) + ")"
        values_s = "(" + implode(",", values_a) + ")"


        query = "insert into complete " + fields_s + " values " + values_s
        return query


    def check_next_author(self, *params) :      # TODO: change the name of the function, next doesn't make sense
        # Loads the next record and checks author and other data
        # TODO : Not generic, should be a plugin

        required = self.arw["s_record_spin"].get_value_as_int()
        required = required - 1         # computers start at 0, humans start at 1

        if required < 0 :
            required = 0

        if required >= len(self.records) :
            alert("Last record has been reached")
            return
        else :
            record = self.records[required]
            self.record = record

        # populate the list with possible authors
        mydata = self.check_author(record)
        store1 = mag.arw["s_treeview21"].get_model()
        store1.clear()
        self.arw["s_author"].set_text("")

        if mydata :
            #self.arw["s_author"].set_markup("<b>" + mydata[0] + "</b>")
            self.arw["s_author"].set_text(mydata[0])
            if mydata[1] :
                for proposal in mydata[1] :
                    store1.append(proposal)
            sel = self.arw["s_treeview21"].get_selection()
            sel.select_path("0")

        # add title with original author and title
        title_s = ""
        sub_title_s = ""
        height_s = ""
        date_s = ""
        for a in record :
            if a.lower() == "titre" :
                title_s = record[a]
            elif a.lower() == "sous-titre" :
                sub_title_s = record[a]
            elif a.lower() == "hauteur" :
                height_s = record[a]
            elif a.lower() == "date" :
                date_s = record[a]
        self.arw["s_record"].set_markup("<b>" + title_s + "</b>\n" + sub_title_s  )
        self.detail(self.arw["s_treeview21"])       # Show book titles in the right list
        self.arw["s_record_label2"].set_text("/ " + str(self.len_records))

        # calculate century from date
        try :
            if int(date_s) >2000 :
                self.arw["s_siecle"].set_text("21")
            elif int(date_s) > 1900 and int(date_s) <= 2000 :
                self.arw["s_siecle"].set_text("20")
            else :
                self.arw["s_siecle"].set_text("")
        except :
            pass     # non critical function

        # Add cote size
        try :
            if int(height_s) >= 350 :
                self.arw["s_cote_size"].set_text("A")
            elif int(height_s) >= 270 :
                self.arw["s_cote_size"].set_text("B")
            elif int(height_s) >= 220 :
                self.arw["s_cote_size"].set_text("C")
            elif int(height_s) >= 170 :
                self.arw["s_cote_size"].set_text("D")
            elif int(height_s) > 0 :
                self.arw["s_cote_size"].set_text("E")
            else :
                self.arw["s_cote_size"].set_text("")
        except :
            self.arw["s_cote_size"].set_text("")   # non critical function

    def previous_record(self, *params) :
        val = self.arw["s_record_spin"].get_value_as_int()
        self.arw["s_record_spin"].set_value( val - 1)

    def next_record(self, *params) :
        val = self.arw["s_record_spin"].get_value_as_int()
        self.arw["s_record_spin"].set_value( val + 1)


    def accept_as_is(self, *params) :
        author = self.arw["s_author"].get_text()
        self.accept(author)

##    def accept_new(self, *params) :
##        author = self.arw["s_entry21"].get_text()
##        self.accept(author)

    def accept_list(self, *params) :
        author = get_text(self.arw["s_treeview21"], col=2)
        self.accept(author)

    def accept_no_author(self, *params) :
        self.accept(0)


    def accept(self, author) :
        # add the two calculated fields
        self.record["format"] = self.arw["s_cote_size"].get_text()
        self.record["siecle"] = self.arw["s_siecle"].get_text()
        (id_livre, auteur_s) = self.insert_into_complete(author)
        self.insert_in_concerne([[id_livre, auteur_s]], "auteur")
        self.check_next_author()

    def skip_record(self, *params) :
        global record
        self.check_next_author()


    def insert_into_complete(self, author) :


            if author == 1 :
                query = self.insert_into("complete", self.record)         # import record as is
            elif author == 0 :
                query = self.insert_into("complete", self.record, collector_auteur="")      # import record with no author
            elif not author :
                query = self.insert_into("complete", self.record)           # import record with no author
            elif len(author) > 0 :
                query = self.insert_into("complete", self.record, collector_auteur=author)      # import record with choosen author
            else :
                print("This should not happen. author is : ", author)
                query = self.insert_into("complete", self.record)         # import record as is

            try :
                cursor.execute(query)
                link.commit()
                cursor.execute("select max(id_livre) from complete")
                id_livre = cursor.fetchone()[0]
                cursor.execute("select collector_auteur from complete where id_livre = " + str(id_livre))
                auteur_s = cursor.fetchone()[0]
                return (id_livre, auteur_s)

            except Exception as error:
                print("======> ERREUR : ", error)
                return (None, None)

            #self.check_next_author()

    def insert_in_concerne(self, mydata, fonction) :

        print(len(mydata))
        i = 0
        for data1 in mydata :
            i += 1
            if i % 10 == 0:
                print(".", end=' ')
            auteur = data1[1]
            id_livre = data1[0]
            if auteur :
                auteur = auteur.encode("utf8")
                separator  = config["ini"]["output"]["field_separator"]
                sep = auteur.split(separator)
                for myauteur in sep :
                    myauteur = myauteur.strip()
                    myauteur = myauteur.replace("'", "''")
                    query = "select id_personne from personnes where nom like '" + myauteur + "' "
                    try :
                        cursor.execute(query)
                        result = cursor.fetchone()
                        if result == None :
                            query = "insert into personnes (nom) values ('%s')" % myauteur
                            cursor.execute(query)


                            query = "select id_personne from personnes where nom like '%s'" % myauteur
                            cursor.execute(query)
                            result = cursor.fetchone()

                        if result :
                            id_personne = result[0]
                            query = "insert into concerne (id_livre, id_personne, fonction) values (%s,%s,'%s')" % (id_livre, id_personne, fonction)
                            #print query
                            cursor.execute(query)
                            if i % 100 == 0:
                                print(i, end=' ')


                        else :
                            print("This should not happen. myauteur is : ", myauteur)
                    except Exception as error:
                        print(("Didn't work:", error))
        link.commit()



    def check_author(self, data_a) :
        global extension
        #get author
        auteur_s = None
        for a in data_a :
            if a == "collector_auteur" :
                auteur_s = data_a[a]
                break
        if not auteur_s :
            return None

        # put the name uppercase
        auteur_u = unicode2(auteur_s)
        auteur_detail = auteur_u.split(",")
        auteur_detail[0] = auteur_detail[0].upper()
        auteur_u = ",".join(auteur_detail)

        # Extract list of persons
        req = "select * from personnes"
        cursor.execute(req)
        personnes_a = cursor.fetchall()

        personnes_a2 = []
        for row in personnes_a :
            personnes_a2.append([row["id_personne"],row["nom"]])

        compteur1 = 0
        compteur2 = 0
        level_i = 4



        s_results = []
        s_results1 = []
        s_results2 = []
        extension = SqliteUnicode()

        for row in personnes_a2 :       # try match
            auteur2 = row[1]
            auteur2_u = auteur2.lower()
            auteur2_detail = auteur2.split(",")

            # similitude
            test1 = extension.convert_to_regex(auteur_detail[0].lower().strip() + "%")
            if test1.match(auteur2_detail[0].lower().strip()) :
                if len(auteur_detail) > 1 :
                    if unicode2(auteur_detail[1].lower().strip()) in auteur2_u :
                        level_i = 2
                        if len(auteur_detail) > 2 :
                            if unicode2(auteur_detail[2].lower().strip()) in auteur2_u :
                                level_i = 3

                if len(auteur_detail) > 1 :
                    if level_i > 1 :
                        s_results2.append([level_i, row[0], row[1]])
                    else :
                        s_results1.append([level_i, row[0], row[1]])
                else :
                    s_results.append([level_i, row[0], row[1]])

        if len(s_results2) > 0 :
            s_results = s_results2

        if len(s_results) == 0  :       #if match does not work, try by inverting 1 and 2
            for row in personnes_a2 :
                auteur2 = row[1]
                auteur2_u = auteur2.lower()
                auteur2_detail = auteur2.split(",")

                # similitude
                if len(auteur_detail) > 1 :
                    test2 = extension.convert_to_regex(auteur_detail[1].lower().strip() + "%")
                    if test2.match(auteur2_detail[0].lower().strip()) :
                        level_i = 1
                        if unicode2(auteur_detail[0].lower().strip()) in auteur2_u :
                            level_i = 2
                            if len(auteur_detail) > 2 :
                                if unicode2(auteur_detail[2].lower().strip()) in auteur2_u :
                                    level_i = 3

                        s_results.append([level_i, row[0], row[1]])


        if len(s_results) == 0 and len(auteur_detail) > 1 :     # if it still does not work, try search
            for row in personnes_a2 :
                auteur2 = row[1]
                auteur2_u = auteur2.lower()
                auteur2_detail = auteur2.split(",")

                # similitude
                level_i = 0
                test2 = extension.convert_to_regex(auteur_detail[0].lower().strip() + "%")
                if test2.search(auteur2_detail[0].lower().strip()) :
                    level_i = 1
                    if len(auteur_detail) > 1 :
                        if unicode2(auteur_detail[1].lower().strip()) in auteur2_u :
                            level_i = 2
                            if len(auteur_detail) > 2 :
                                if unicode2(auteur_detail[2].lower().strip()) in auteur2_u :
                                    level_i = 3

                    s_results.append([level_i, row[0], row[1]])

        # TODO: separate the authors at the ;

        s_results.sort()
        s_results.reverse()

        if len(s_results1) > 0 :
            s_results.append([0, 0,""])

        for data1 in s_results1 :
            s_results.append(data1)

        if s_results :
            return  (auteur_u, s_results)


        else :
            return (auteur_u, None)




    def search_persons(self, *params) :
        text1 = self.arw["s_entry21"].get_text()
        req = "select id_personne, nom from personnes where nom like '" + text1.lower() + "%'"

        cursor.execute(req)
        store1 = mag.arw["s_treeview21"].get_model()
        store1.clear()
        for row in cursor :
            store1.append([0, row[0], row[1]])





class db_utilities :

    def __init__(self) :
        pass

    # connexion à  la base de données
    # If a proper sqlite file is found, load it

    @staticmethod
    def sqlite_escape_quotes(string):
        value = string.replace("'", "''")        # escape single quotes
        value = value.replace('"', '""')        # escape double quotes
        return value


    def load_sqlite(self, db_file_s) :


        #db_active_file = os.path.split(db_file_s)[1]
        db_active_file = db_file_s
        db_type = "sqlite"
        link = sqlite.connect(db_file_s)
        # optimize performances
        link.isolation_level = "DEFERRED"
        link.row_factory = sqlite.Row
        cursor = link.cursor()
        extension = SqliteUnicode()


        link.create_collation("france", extension.collate)
        link.create_function("regexp", 2, extension.regexp)
        #link.create_function("like", 2, extension.like)
        link.create_function("concat_ws", -1, extension.concat_ws)
        link.create_function("clean_commas", 1, extension.clean_commas)
        link.create_function("date2year", 1, extension.date2year)
        link.create_function("date2ymd", 1, extension.date2ymd)

        # retrieve structure
        db_structure= {}


        """SELECT name FROM sqlite_master
        WHERE type  IN (?,?)
        AND name NOT LIKE ?
        UNION ALL SELECT name FROM sqlite_temp_master
        WHERE type IN (?,?)
        ORDER BY 1','table','view','sqlite_%','table','view') ;
        """

        req= "select name from sqlite_master where type in ('table')"
        cursor.execute(req)
        result = cursor.fetchall()
        for a in result :
            for b in a :
                db_structure[b] = {}
                req = "PRAGMA table_info (" + b + ")"
                cursor.execute(req)
                for s in cursor :
                    db_structure[b][s[0]] = s[1]
                    db_structure[b][s[1]] = s[0]

        return (link, cursor, db_structure, db_active_file)


    def mysql_db_structure(self, cursor) :


        table_def = {}
        index_def = {}
        constraint_def = {}
        errors_count = 0

        # Extract mysql structure
        # Extract tables list
        cursor.execute("show tables")

        tables = []
        for row in cursor :
            key = list(row.keys())[0]
            name = row[key]
            try :
                cursor.execute("show columns from " + name)   # Test the validity of the table name.
                                                              # We have seen a database with a table named "1" which was impossible to handle with sql commands
                tables.append(name)
            except :
                print(("WARNING : Unable to handle table " + name + "\nCheck if there is no problem with it."))


        for name in tables :


            table_def[name] = {}
            index_def[name] = {}

            # extract columns
            cursor.execute("show columns from " + name)
            columns = cursor.fetchall()
            for col in columns :
                keys = list(col.keys())
                colname = col['Field']
                table_def[name][colname] = {}
                table_def[name][colname]['type'] = col['Type']
                table_def[name][colname]['null'] = col['Null']
                table_def[name][colname]['primary'] = col['Key']
                table_def[name][colname]['default'] = col['Default']
                table_def[name][colname]['autoinc'] = col['Extra']





        return(table_def)



    def db_compare(self, *params) :

        central_table = "registre"      # TODO extract from config
        primary_key = "idpersonne"

        chooser = Gtk.FileChooserDialog(title=_('_Open Configuration'),
                action=Gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons=(Gtk.STOCK_CANCEL,
                    Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OPEN,
                    Gtk.ResponseType.OK))
        chooser.set_current_folder(configdir_u)
        chooser.set_show_hidden(True)  #Test : does not work. Why ??

        filter_all = Gtk.FileFilter()
        filter_all.set_name(_('All files'))
        filter_all.add_pattern('*')
        chooser.add_filter(filter_all)

        filter_ini = Gtk.FileFilter()
        filter_ini.set_name(_('sqlite files'))
        filter_ini.add_pattern('*.sqlite')
        filter_ini.add_pattern('*.db3')
        chooser.add_filter(filter_ini)
        chooser.set_filter(filter_ini)

        response = chooser.run()
        if response == Gtk.ResponseType.OK:
            filename = chooser.get_filename()
            filename_u = str(filename,"utf-8")            # convert utf-8 to unicode for internal use

        elif response == Gtk.ResponseType.CANCEL:
            print((_('Closed, no files selected')))
            chooser.destroy()
            return
        chooser.destroy()

        new_records_a = []
        (link2,cursor2,db_structure2,db_active_file2) = self.load_sqlite(filename_u)


        # create columns list

        cursor.execute("select * from " + central_table)
        row = cursor.fetchone()
        list_cols = list(row.keys())


        info = self.arw['s_info10'];
        buffer1 = info.get_buffer();
        buffer1.set_text("");

        treeview = mag.arw["s_compare_tree"]
        model1 = treeview.get_model()

        cursor.execute("select * from " + central_table)
        #cursor2.execute("select * from complete")
        i = 0

        for row in cursor :
            id1 = row[primary_key]
            i += 1

            cursor2.execute("select * from %s where %s = %s" % (central_table, primary_key, id1))
            row2 = cursor2.fetchone()

            if row2 :

                for field in list_cols :
                    #print field
                    #print row[field]
                    if field in list(row2.keys()) :
                        #print row2[field]
                        if row[field] != row2[field] :
                            model1.append([str(id1), field, row[field], row2[field]])

            else :
                new_records_a.append(id1)   # new records in base1


        # new records
        insertion_tv(buffer1, "\n terminé\n")
        insertion_tv(buffer1, str(i) + "records")
        temp = "\n\n NEW RECORDS :  "

        for rec in new_records_a :
            temp += str(rec) + " ,  "
        insertion_tv(buffer1, temp)

        # deleted records
        deleted_a = []
        cursor2.execute("select * from " + central_table)
        for row2 in cursor2 :
            id2 = row2[primary_key]
            cursor.execute("select * from %s where %s = %s" % (central_table, primary_key, id2))
            row = cursor.fetchone()

            if not row :
                deleted_a.append(id2)

        temp = "\n\n DELETED RECORDS :  "
        for rec in deleted_a :
            temp += str(rec) + " ,  "
        insertion_tv(buffer1, temp)


    def is_field(self, cursor, table, field, coltype = None) :

            if not table in db_structure :
                alert("Table "+ table + " does not exist !")
                return False
            found = False
            if db_type == "sqlite" :
                req = "PRAGMA table_info(" + table + ")"
                cursor.execute(req)
                found = False
                for row in cursor :
                    if row[1] == field :
                        found = True


            elif db_type == "mysql" :

                cursor.execute("DESCRIBE " + table  + " " + field);
                result = cursor.fetchall()
                if len(result) > 0 :
                     found = True


            elif db_type == "accdb" :
                cursor.execute("select * from " + table)
                data1 = cursor.description
                for line in data1 :
                    if line[0] == field.lower() :
                        found = True

            if not found :
                if db_type == "accdb" and coltype.lower() == "text" :
                    coltype = "MEMO"
                #insertion_tv(buffer1, "g_" + table + " not present, we should create it")
                print(table + "." + field + " not present, we should create it")
                req = "ALTER TABLE $table ADD COLUMN $field $coltype"
                req1 = eval(php_string(req))
                cursor.execute(req1)
                link.commit()

            return found


class explode_db :
    # this version works in sqlite only
    def __init__(self) :
        global config, separaor
        self.separator  = config["ini"]["output"]["field_separator"]

    @staticmethod
    def escape_quotes(string):
        value = string.replace("'", "''")        # escape single quotes
        value = value.replace('"', '""')        # escape double quotes
        return value

    def explode_insert_in_concerne(self, list_noms, fonction) :
        print("insert in concerne : %d records" % len(list_noms))
        i = 0
        for data in list_noms :
            i += 1
            if i % 100 == 0:
                while Gtk.events_pending():
                    Gtk.main_iteration()
                print(i, end=' ')
            auteur = data[1]
            auteur = self.escape_quotes(auteur)
            id_livre = data[0]
            if auteur == None :
                return
            sep = auteur.split(self.separator)
            for myauteur in sep :
                if myauteur.strip() == "":
                    continue
                myauteur = myauteur.strip()
                # try if there is an exact match
                query = "select id_personne, nom from personnes where nom like '" + myauteur + "' "       # TODO generic (and below)
                cursor.execute(query)
                result = cursor.fetchone()
                if result :
                    id_personne = result[0]
                    myfonction = self.escape_quotes(fonction).encode("utf-8")
                    query = "insert into concerne (id_livre, id_personne, fonction) values (%s,%s,'%s')" % (id_livre, id_personne, myfonction)
                    #print query
                    try:
                        cursor.execute(query)
                    except:
                        print("Error for query :", query)

                else :
                    query = "select id_personne, nom from personnes where nom like '%" + myauteur + "%' "       # TODO generic (and below)
                    choice = None
                    cursor.execute(query)
                    result = cursor.fetchall()
##                    dialog = mag.arw["s_import_dialog"]
##                    treeview = mag.arw["s_import_treeview2"]
##                    mag.arw["s_import_label"].set_text(myauteur)
##                    model = treeview.get_model()
##                    model.clear()
##                    for row in result :
##                        model.append([str(row[0]), str(row[1])])




##                    choice = dialog.run()
                    choice = 2

                    if choice == 1 :
                        id_personne = get_sel_row_data(treeview, 0, 0)
                    elif choice == 2 :
                        query = "insert into personnes (nom) values ('%s')" % myauteur
                        cursor.execute(query)


                        query = "select id_personne from personnes where nom like '" + myauteur + "' "
                        cursor.execute(query)
                        result = cursor.fetchone()
                        id_personne = result[0]

                    else :
                        continue

                    myfonction = self.escape_quotes(fonction).encode("utf-8")
                    query = "insert into concerne (id_livre, id_personne, fonction) values (%s,%s,'%s')" % (id_livre, id_personne, myfonction)
                    #print query
                    cursor.execute(query)
                    #
                    # update central
                    query = "select nom from personnes where id_personne =" + str(id_personne)
                    cursor.execute(query)
                    result = cursor.fetchone()
                    selected_name = self.escape_quotes(result[0])
                    query = "update complete set auteur = '%s' where id_livre = %s" % (selected_name.encode("utf-8"), id_livre)
                    cursor.execute(query)
##                    dialog.hide();

        link.commit()
##                except Exception as error:
##                    print("Didn't work:", error)


    def explode_insert_in_chartreuse(self, list_noms) :

        print ("insert in chartreuse : %d records" % len(list_noms))
        i = 0
        for data in list_noms :
            i += 1
            if i % 100 == 0:
                while gtk.events_pending():
                    gtk.main_iteration()
                print(i, end='')
            chartreuse = data[1]
            id_livre = data[0]
            #auteur = self.escape_quotes(auteur)
            sep = chartreuse.split(self.separator)
            for mychartreuse in sep :
                mychartreuse = mychartreuse.strip()
                mychartreuse = mychartreuse.replace("'", "''").encode("utf-8")
                query = "select id_chartreuse from chartreuses where chartreuse like '%" + mychartreuse + "%' "
                try :
                    cursor.execute(query)
                    result = cursor.fetchone()
                    if result == None :
                        query = "insert into chartreuses (chartreuse) values ('%s')" % mychartreuse
                        cursor.execute(query)

                        query = "select id_chartreuse from chartreuses where chartreuse like '%" + mychartreuse + "%' "
                        cursor.execute(query)
                        result = cursor.fetchone()

                    if result :
                        id_chartreuse = result[0]
                        query = "insert into maison (id_livre, id_chartreuse) values (%s,%s)" % (id_livre, id_chartreuse)
                        cursor.execute(query)


                    else :
                        print("Error for ", mychartreuse)
                except Exception as error:
                    if "UNIQUE constraint failed:" in error.message:
                        pass
                    else:
                        print("Didn't work:", error)
        link.commit()

##        print("insert in chartreuse : %d records" % len(list_noms))
##        i = 0
##        for data in list_noms :
##            i += 1
##            if i % 100 == 0:
##                while Gtk.events_pending():
##                    Gtk.main_iteration()
##                print(i, end=' ')
##            auteur = data[1]
##            id_livre = data[0]
##            auteur = auteur
##            sep = auteur.split(self.separator)
##            for mychartreuse in sep :
##                mychartreuse = mychartreuse.strip()
##                mychartreuse = mychartreuse.replace("'", "''").encode("utf-8")
##                query = "select id_chartreuse from chartreuses where chartreuse like '%" + mychartreuse + "%' "
##                try :
##                    cursor.execute(query)
##                    result = cursor.fetchone()
##                    if result :
##                        id_personne = result[0]
##                        query = "insert into maison (id_livre, id_chartreuse) values (%s,%s)" % (id_livre, id_personne)
##                        cursor.execute(query)
##
##
##                    else :
##                        print(mychartreuse)
##                except Exception as error:
##                    if "UNIQUE constraint failed:" in error.message:
##                        pass
##                    else:
##                        print(("Didn't work:", error))
##        link.commit()

    def explode_insert_in_collection(self, list_noms) :
        print("insert in collections : %d records" % len(list_noms))
        i = 0
        for data in list_noms :
            i += 1
            if i % 100 == 0:
                while Gtk.events_pending():
                    Gtk.main_iteration()
                print(i, end=' ')
            collection = data[1]
            id_livre = data[0]
            sep = collection.split(self.separator)
            for mycollection in sep :
                mycollection = mycollection.strip()
                mycollection = mycollection.split(",")[0]  # 1 contains the number
                mycollection = mycollection.replace("'", "''")
                query = "select id_collection from collections where collection like '%" + mycollection + "%' "
                try :
                    cursor.execute(query)
                    result = cursor.fetchone()
                    if result == None :
                        query = "insert into collections (collection) values ('%s')" % mycollection
                        cursor.execute(query)
                        query = "select id_collection from collections where collection like '%" + mycollection + "%' "
                        cursor.execute(query)
                        result = cursor.fetchone()
                    if result :
                        id_collection = result[0]
                        query = "insert into serie (id_livre, id_collection) values (%s,%s)" % (id_livre, id_collection)
                        cursor.execute(query)

                    else :
                        print("\nError for ", mycollection)
                except Exception as error:
                    if "UNIQUE constraint failed:" in error.message:
                        pass
                    else:
                        print("\nDidn't work:", error, "Query was : \n", query)
        link.commit()

    def explode_insert_in_theme(self, list_noms) :
        print("insert in theme : %d records" % len(list_noms))
        i = 0
        for data in list_noms :
            i += 1
            if i % 100 == 0:
                while Gtk.events_pending():
                    Gtk.main_iteration()
                print(i, end=' ')
            theme = data[1]
            id_livre = data[0]
            sep = theme.split(self.separator)
            for mytheme in sep :
                mytheme = mytheme.strip()
                mytheme = mytheme.replace("'", "''")
                query = "select id_theme from themes where theme like '%" + mytheme + "%' "
                try :
                    cursor.execute(query)
                    result = cursor.fetchone()
                    if result == None :
                        query = "insert into themes (theme) values ('%s')" % mytheme
                        cursor.execute(query)

                        query = "select id_theme from themes where theme like '%" + mytheme + "%' "
                        cursor.execute(query)
                        result = cursor.fetchone()

                    if result :
                        id_theme = result[0]
                        query = "insert into sujet (id_livre, id_theme) values (%s,%s)" % (id_livre, id_theme)
                        cursor.execute(query)
                        #print ".",

                    else :
                        print("\n ===========> Error for ", mytheme)
                except Exception as error:
                    if "UNIQUE constraint failed:" in error.message:
                        pass
                    else:
                        print("\nDidn't work:", error, "Query was : \n", query)
        link.commit()


    def explode_insert_in_langue(self, list_noms) :
        print("insert in langue : %d records" % len(list_noms))
        i = 0
        for data in list_noms :
            i += 1
            if i % 100 == 0:
                while Gtk.events_pending():
                    Gtk.main_iteration()
                print(i, end=' ')
            langue = data[1]
            id_livre = data[0]
            langue = langue
            sep = langue.split(self.separator)
            for mylangue in sep :
                mylangue = mylangue.strip()
                query = "select id_langue from langues where langue like '%" + mylangue + "%' "
                try :
                    cursor.execute(query)
                    result = cursor.fetchone()
                    if result == None :
                        query = "insert into langues (langue) values ('%s')" % mylangue
                        cursor.execute(query)
                        query = "select id_langue from langues where langue like '%" + mylangue + "%' "
                        cursor.execute(query)
                        result = cursor.fetchone()
                    if result :
                        id_langue = result[0]
                        query = "insert into parle (id_livre, id_langue) values (%s,%s)" % (id_livre, id_langue)
                        cursor.execute(query)
                        #print ".",

                    else :
                        print("\nError for ", mylangue)
                except Exception as error:
                    if "UNIQUE constraint failed:" in error.message:
                        pass
                    else:
                        print("\nDidn't work:", error, "Query was : \n", query)
            link.commit()

    def explode_full_db(self, widget = None) :

        query = "select id_livre, auteur, collaborateur, biographie, vedette, theme, chartreuse, collection, langue  from complete"
        cursor.execute(query)

        self.auteur = []
        self.collaborateur = []
        self.biographie = []
        self.vedette = []
        self.chartreuse = []
        self.collection = []
        self.theme = []
        self.langue = []



        for row in cursor :
            for field in ["auteur", "collaborateur", "biographie", "vedette", "theme", "chartreuse", "collection", "langue"] :

                if row[field] :
                    command = "self." + field + ".append([row[0], row['" + field + "']])"
                    eval(command)

        query = "delete from concerne"
        cursor.execute(query)

        print("")
        print("auteur")
        self.explode_insert_in_concerne(self.auteur, "auteur")
        print("")
        print("collaborateurs")
        self.explode_insert_in_concerne(self.collaborateur, "collaborateur")
        print("")
        print("biographie")
        self.explode_insert_in_concerne(self.biographie, "biographie")
        print("")
        print("vedette")
        self.explode_insert_in_concerne(self.vedette, "vedette")


        query = "delete from maison"
        cursor.execute(query)

        query = "delete from serie"
        cursor.execute(query)

        query = "delete from sujet"
        cursor.execute(query)

        query = "delete from parle"
        cursor.execute(query)
        link.commit()

        print("")
        print("chartreuse")
        self.explode_insert_in_chartreuse(self.chartreuse)
        print("")
        print("collection")
        self.explode_insert_in_collection(self.collection)
        print("")
        print("theme")
        self.explode_insert_in_theme(self.theme)
        print("")
        print("langue")
        self.explode_insert_in_langue(self.langue)
        link.commit()


    def explode_field(self, field, gateway, peripheral) :

        query = "select id_livre, " + field +  " from complete"  # TODO generic
        cursor.execute(query)

        self.field_data = []

        for row in cursor :
            if row[field] :
                    command = "self.field_data.append([row[0], row['" + field + "']])"
                    eval(command)

        query = "delete from " + gateway
        cursor.execute(query)

        self.insert_in_concerne(self.field_data, "auteur")


class TextBuffer (Gtk.TextBuffer) :
    tag_def = []
    def __init__(self)  :
        parent.__init__()

class ParsePangoMarkup :

    def __init__(self, buffer1, html_str)  :
        self.buffer1 = buffer1
        self.html_str = html_str


    def apply_style(self, buffer1, tag, tag_attributes, start, end)  :
        tag_def = buffer1.tag_def    #...    tag_def = &buffer.tag_def
                                                # pango code => textview tag code
        tag_mapping = {'b' : ['weight', gi.repository.Pango.Weight.BOLD],
                       'i' : ['style', gi.repository.Pango.Style.ITALIC],
                       'u' : ['underline', gi.repository.Pango.Underline.SINGLE],
                       'sup' : ['rise', 5000],
                       'sub' : ['rise', -5000],
                       'size' : 'size',
                       'foreground' : 'foreground',
                       'background' : 'background',
                       'color' : 'foreground',
                       'face' : 'family',
                       'font' : 'font' }


        if tag=='span' :
            for  k in tag_attributes  :
                v = tag_attributes[k]
                k2 = tag_mapping[k]
                tag_name = k2+'@'+v
                self.setup_tag(buffer1, tag_name, k2, v)
                try:
                    buffer1.apply_tag(tag_def[tag_name], start, end)
                except:
                    print ("Pango error (1) to fix for tag", tag_def, tag_name, "\n")


        else :
            (property1, value) = tag_mapping[tag]
            self.setup_tag(buffer1, tag, property1, value)
            try:
                buffer1.apply_tag(tag_def[tag], start, end)
            except:
                print ("Pango error (2) to fix for tag", tag, "\n")

    def go(self)  :
        buffer1 = self.buffer1
        buffer1.tag_def = {}        # added ???
        tag_def = buffer1.tag_def    #...        tag_def = &buffer1.tag_def
        html_str = self.html_str

        output = ''
        regexp = '(?si)(.*?)<(/?)([A-Z][A-Z0-9]*)\s*([^>]*)>(.*)'
        contents = html_str
        found = re.match(regexp, contents)
        id1 = 0
        tags = []
        while (found) :


            iter1 = buffer1.get_end_iter()
            buffer1.insert(iter1, found.group(1) )
            closetag = found.group(2)
            htmltag = found.group(3)
            attributes = found.group(4)

            if closetag=='/' :
                (tag_id, tag, tag_attributes) = self.retrieve_begin_tag(tags, htmltag)
                if tag=='' :
                    print("warning>>> mismatched tag!\n")

                else :
                    start = buffer1.get_iter_at_mark(buffer1.get_mark('mark'+ str(tag_id)))

                end = buffer1.get_end_iter()
                self.apply_style(buffer1, tag, tag_attributes, start, end)

            else :
                iter1 = buffer1.get_end_iter()
                buffer1.create_mark('mark'+ str(id1), iter1, True)
                tags.append([id1, htmltag, self.process_attributes(attributes)])
                id1 += 1


            contents = found.group(5)
            found = re.match(regexp, contents)

        iter1 = buffer1.get_end_iter()
        buffer1.insert(iter1, contents)

        str1 = output
        return str1


    def process_attributes(self, attributes_str)  :
        if attributes_str=='' :
            return []

        attributes = {}
        matches = re.findall('(?si)([A-Z][A-Z0-9_]*)\s*=\s*["|\'](.*?)["|\']', attributes_str)   # TODO : there was , PREG_SET_ORDER
        if matches :
            for  match in matches  :
                attributes[match[0]] = match[1]
            return attributes

        else :
            return []


    def retrieve_begin_tag(self, tags, close_tag)   :  #...    function retrieve_begin_tag(&tags, close_tag)  :
        for i in range(len(tags)-1, -1, -1) : #               for (i = count(tags)-1| i>=0| --i)
            (tag_id, tag, tag_attributes) = tags[i]
            if tag == close_tag :
                del tags[i]
                # TODO ???? tags = array_values(tags)
                return [tag_id, tag, tag_attributes]

        return ('', "", [])


    def setup_tag(self, buffer1, tag_name, property_name, value)  :
        tag_def = buffer1.tag_def    #...    tag_def = &buffer.tag_def
        if tag_name not in tag_def :
            tag_table = buffer1.get_tag_table()
            tag_def[tag_name] = Gtk.TextTag()
            tag_def[tag_name].set_property(property_name, value)
            tag_table.add(tag_def[tag_name])





class connect() :
    # Base class for all other class
    def __init__(self) :
        pass


# ========================================================================================
# zoomx : window used for editing peripheral tables, in the input window
# ========================================================================================

class zoomx() :

    # parameters :

    MODEL_ROW_INTERN = 1001
    MODEL_ROW_EXTERN = 1002         # unused
    MODEL_ROW_MOTION = 1004

    TARGETS = [('MODEL_ROW_INTERN', Gtk.TargetFlags.SAME_WIDGET, MODEL_ROW_INTERN),
            ('MODEL_ROW_EXTERN', Gtk.TargetFlags.OTHER_APP, MODEL_ROW_EXTERN),
            ('MODEL_ROW_MOTION', 0, MODEL_ROW_MOTION)]

    def __init__(self, treeview)  :

        global arWidgets, config, config_info, periph_tables, mem, popup_saisie, tab_conversion

        self.widgets = Gtk.Builder()
        self.widgets.add_from_file('./data/zoom1.glade')
        arWidgets = self.widgets.get_objects()

        self.arZoom = {}
        for z in  arWidgets:
            try :
                name = Gtk.Buildable.get_name(z)
                self.arZoom[name]= z
                z.set_name(name)
            except :
                pass

        del arWidgets

        self.dialog = self.arZoom['window1']

        # retrieve information about the models to use

        list_name = treeview.get_name()
        periph_config = utils.get_extension(list_name)  # name of the peripheral table
        table = periph_tables2[periph_config]['table']
        gateway = periph_tables2[periph_config]['gateway']                       # gateway name
        id_type = periph_tables2[periph_config]['id_type']

        clists = []
        for  key  in config['xtabs']  :
            val = config['xtabs'][key]
            if v(config,'peripheral',val['table_def'],'table') != None :
                if config['peripheral'][val['table_def']]['table'] == table :
                    clists.append( val['treeview'])     # list name


        # TODO: if there is no corresponding search list, we will get an error because clists will remain empty
        if len(clists) == 0 :
            alert (_(" There is no Search list for this table.\n There is no way to populate the list"))
            return

        if magutils.widget_type(mag.arw[clists[0]]) != "GtkTreeView" :
            alert (clists[0] + _(""" is not a GtkTreeView.
Either your control has not a valid name
or the list does not exist."""))
            return


        targets = [ ['text/plain', 0, 1], ['TEXT', 0, 2], ['STRING', 0, 3] ]

        # ============ Left list ===========================

        nb = self.arZoom['notebook1']

        for  i in range(len(clists))  :
            clist = clists[i]
            if clist not in mag.arw :     # TODO ????
                continue



            if i > 0 :
                # TODO: added to speed up the transfer. we will see later how to improve things
                # if more than one page add tabs to the notebook


                sw = Gtk.ScrolledWindow()

                nb.append_page(sw)
                new_list = Gtk.TreeView()
                self.arZoom['treeleft'+ str(i)] = new_list
                sw.add(new_list)

            else :
                sw = self.arZoom['scrolledwindow0']


            config_list = tab_conversion[clist]
            type = config['xtabs'][config_list]['type']
            table_def = config['xtabs'][config_list]['table_def']

            # Is there a definition in config / gateway_data ?
            col_data = {}
            if 'gateway_data' in config :
                if table in config['gateway_data'] :         # Is there are additional columns definition
                    col_data = config['gateway_data'][table]


            model1 = mag.arw[clist].get_model()
            left = self.arZoom['treeleft'+ str(i)]
            left.set_model(model1)
            cell_renderer_left = Gtk.CellRendererText()
            # added first column
            colnew= Gtk.TreeViewColumn("", cell_renderer_left, text=0)
            if "width" in col_data :
                if int(col_data['width']) > 0 :
                    # if width is defined
                    colnew.set_sizing(2)             # 2 = GTK_TREE_VIEW_COLUMN_FIXED
                    colnew.set_fixed_width(int(col_data['width']))
                    colnew.set_resizable(True)

            left.append_column(colnew)

            left.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, self.TARGETS, Gdk.DragAction.COPY)
            left.connect("drag_data_get", self.drag_data_get_data) #$left->connect("drag_data_get", array($this,"drag_data_get_data"));


            # add additional columns defined in config / gateway_data
            # These are the columns in the list just on the left

            if col_data :
                for  key  in col_data['cols']  :
                    cols = col_data['cols'][key]
                    field_name = cols['field']
                    field = 2  # TODO: how to find this?
                    width  =  100                  # if width not defined, 100 by default
                    if 'width' in cols :
                        if not isinstance(cols['width'], int) :
                            if cols['width'].isdigit() :
                                width = int(cols['width'])

                    colnew = Gtk.TreeViewColumn("", cell_renderer_left, text=field)
                    colnew.set_sizing(2)             # 2 = GTK_TREE_VIEW_COLUMN_FIXED
                    colnew.set_fixed_width(width)
                    colnew.set_resizable(True)
                    left.append_column(colnew)



            # search for the return column
            tab = tab_conversion[clist]
            table_data = config['xtabs'][tab]
            col = left.get_column(0)
            ref_field = get_option("r",table_data['options'])      # field specified for cross-reference in definition table
            ref_column = None
            for  num  in table_data['cols']  :
                val = table_data['cols'] [ num ]

                if ('field' in val) and val['field'] == ref_field :
                    ref_column = num


            if ref_column and int(ref_column) > 0 :
                col.set_cell_data_func(cell_renderer_left, mag.renvois, ref_column)



            # details
            treeselect=self.arZoom['treeleft'+ str(i)].get_selection()
            treeselect.connect('changed',self.details, table, id_type,left, col_data)

            nb.set_tab_label_text(sw,tab)                  # tab titles


        # ============ Right List ===========================


        model2 = treeview.get_model()
        right = self.arZoom['treeright']
        right.set_model(model2)
        right.connect("key-press-event", mag.effacer_ligne) #$right->set_reorderable(True);
        treeselect=self.arZoom['treeright'].get_selection()
        treeselect.connect('changed',self.additional_data_show, table, id_type,right)


        cell_renderer = Gtk.CellRendererText()
        columns = treeview.get_columns()
        k = 1
        for  col  in columns  :
            colwidth = col.get_width()
            title = col.get_title()
            colnew = Gtk.TreeViewColumn(title, cell_renderer, text=k)
            colnew.set_sizing(2)             # 2 = GTK_TREE_VIEW_COLUMN_FIXED
            colnew.set_resizable(True)
            colnew.set_fixed_width(colwidth)
            right.append_column(colnew)
            k += 1

        if len(columns) > 1 :       # if there is more than one column


            index = 0
            data = config_info['gateways'][gateway]['data']
            for  key  in data  :
                val = data [ key ]
                if len(val['field']) > 0 :
                #Create a label
                    label = Gtk.Label(val['field'])
                    self.arZoom['vbox_data'].pack_start(label, True, True, 0)
                    # Create a text combobox.
                    combo = Gtk.ComboBoxText()
                    #combo.child.connect('changed', self.changed_cb)
                    combo.set_active(0)


                    #Â£  gtk_alignment_set has been deprecated since version 3.14 and should not be used in newly-written code. Use GtkWidget alignment and margin properties
                    #Â£ alignment = Gtk.Alignment(0.5, 0, 0, 0) # note 2
                    #alignment.add(combo)
                    #self.arZoom['vbox_data'].pack_start(alignment,label, True, True, 0)
                    self.arZoom['vbox_data'].pack_start(combo, True, True, 0)

                    field = val['field']
                    req = eval(php_string("select distinct $field from $gateway order by $field"))
                    if val['type'] == "list" :

                        # preload the list of values
                        cursor.execute(req)
                        #model2 = combo.get_model()
                        for line in cursor :
                            txt = line[field]
                            if txt == "" or txt == None:
                                continue
                            combo.append_text(str(txt))
                    combo.set_active(0)
                    index+= 1
                    mag.arw['zoom_combo'+ str(index)] = combo

        # Connect the buttons
        self.arZoom['insertion'].connect('clicked', self.insertionx )
        self.arZoom['closeButton'].connect('clicked', self.closex)
        self.arZoom['view_details'].connect('clicked', self.view_details)
        self.arZoom['save_position'].connect('clicked', self.save_position)
        self.arZoom['tapez_saisie'].connect('changed', self.tapez_saisiex,clists)
        self.arZoom['edit'].connect('clicked', self.edit_clicked,clists)
        mag.arw['tapez_saisie'] = self.arZoom['tapez_saisie']
        self.arZoom['add_entry_button'].connect('clicked', self.add_entry,table,clists)

        # Add-ons


        # drag and drop for both edit lists

        right.enable_model_drag_dest(self.TARGETS, Gdk.DragAction.DEFAULT)
        right.connect("drag_data_received", self.drag_data_received_data)
        # reorganize the destination list (= drag and drop the list onto itself)
        right.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, self.TARGETS, Gdk.DragAction.COPY|Gdk.DragAction.MOVE) #$right->connect("drag-data-get", array($this, "drag_data_get_data"));
        right.connect("drag-data-get", self.drag_data_get_data)


        """
        Modèle de Archeotes configurator

        # lists
        for widget in [self.arw["exclude_list"],
                self.arw["versions_list"],
                self.arw["md5_list"],
                self.arw["compress_list"],
                self.arw["crypt_list"],
                self.arw["cryptnames_list"]] :

            widget.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,
                    self.TARGETS_IV,
                    Gtk.gdk.ACTION_MOVE)

            widget.enable_model_drag_dest(self.TARGETS_IV,
                    Gtk.gdk.ACTION_DEFAULT)
            widget.connect('drag_data_get', self.lists_dnd_get_data)
            widget.connect('drag_data_received', self.dnd_received_data)

        """

        self.dialog.set_modal(True)

        # resize dialog
        if 'zoom1' in config['ini'] :
            h = config['ini']['zoom1']["h"]
            w = config['ini']['zoom1']["w"]
            self.dialog.set_default_size(w, h)
            self.dialog.set_resizable(True)



        self.dialog.show_all()

        if 'zoom1' in config['ini'] :
            x = config['ini']['zoom1']["x"]
            y = config['ini']['zoom1']["y"]
            self.dialog.move(x, y)

        self.arZoom['scrolledwindow3'].hide()


    def drag_data_get_data(self, treeview, context, data, target_id, etime)  :
        global additional_data

        treeselection = treeview.get_selection()
        (model, iter1) = treeselection.get_selected()
        if iter1==None :
            return
        listpath = model.get_string_from_iter(iter1)

        #name = treeview.get_name()
        try :                           # this function is used for left and right lists with different models
            id1 = model.get_value(iter1, 20)
        except :
            id1 = ""
        nom = model.get_value(iter1, 0)

        data1 = json.dumps([listpath, nom, id1])
        data.set(Gdk.TARGET_STRING, len(data1), [ord(d) for d in data1])



    def drag_data_received_data1(self, widget, context, x, y, data, info, time)  :
        # ############  unused  ####################
        model = widget.get_model()
        drop_info = widget.get_dest_row_at_pos(x, y)
        (dest_path, position) = drop_info

        #data1 = base64_decode(data.data)
        data2 = pickle.loads(data1)
        #name = array_shift(data2)



        if name == widget.get_name() :

            # reorder


            if drop_info :

                dest_iter = model.get_iter(dest_path)
                src_selection = widget.get_selection()
                (src_model, src_iter) = src_selection.get_selected()



                if position == Gtk.TREE_VIEW_DROP_BEFORE : src_model.move_before(src_iter,dest_iter)


                elif (position == Gtk.TREE_VIEW_DROP_AFTER
                    or Gtk.TREE_VIEW_DROP_INTO_OR_BEFORE
                    or Gtk.TREE_VIEW_DROP_INTO_OR_AFTER) :
                        src_model.move_after(src_iter,dest_iter)



        else : # copy
            ncol = model.get_n_columns()
            if (count(data2) > ncol)  : data2  =   array_slice(data2,0,ncol)
            else : data2  =  array_pad(data2,ncol,"")



            if drop_info :

                    if position == Gtk.TREE_VIEW_DROP_BEFORE : model.insert(dest_path[0], data2)


                    elif (position == Gtk.TREE_VIEW_DROP_AFTER
                        or Gtk.TREE_VIEW_DROP_INTO_OR_BEFORE
                        or Gtk.TREE_VIEW_DROP_INTO_OR_AFTER) :
                            model.insert(dest_path[0] + 1, data2)          # dropped after the selected line


            else : model.append(data2)

    def drag_data_received_data(self, treeview, context, x, y, data, target_id, etime):
        # Handles received data by drag and drop. As always for dnd, it is not simple...

        # For options lists, we use only the destination and position.
        #   - From the destination name, we extract the name of the xxxx_code entry
        #     and we get the data from there. Hence, we take in account the selections
        #     about yes / no, path / name / ext / size etc.
        #   - Then an if selects the proper xxxx_add function to run, the action which
        #     normally triggered by the add button, but we pass it the information
        #     on the position of the drop.

        model = treeview.get_model()
        numcols = model.get_n_columns()
        info_depot = treeview.get_dest_row_at_pos(x, y)
        try:
            data1 = data.data
        except:
            pass
        try:
            data1 = data.get_data()
        except:
            pass
        try:
            data1 = data.get_text()
        except:
            pass
        (listpath_s,name_s, id1) = json.loads(data1)


        # reorder list (set reorderable does not work when dnd is explicitly set)
        if target_id == 1001 :
            source_iter = model.get_iter_from_string(listpath_s)
            donnees = []
            for i in range(numcols) :
                donnees.append(model.get_value(source_iter,i))

            if info_depot:
                chemin, position = info_depot
                myIter = model.get_iter(chemin)

                if (position == Gtk.TREE_VIEW_DROP_BEFORE
                        or position == Gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
                    model.insert_before(myIter, donnees)
                else:
                    model.insert_after(myIter, donnees)
            else:
                model.append(donnees)

            if context.action == Gtk.gdk.ACTION_MOVE:
                context.finish(True, True, etime)

            return

        # data from Treeview
        if target_id == 1004 :

            # Format path
            data1 = []

            data1.append(id1)
            data1.append(name_s)
            # additional columns
            columns =  treeview.get_columns()
            if len(columns) > 1 :
                for i  in range( 1, len(columns)) :
                    if mag.arw['zoom_combo' + str(i)] :
                        data1.append(mag.arw['zoom_combo' + str(i)].get_active_text())

            data1 = array_pad(data1,numcols,"")


            # insert data in the model
            if info_depot:
                chemin, position = info_depot
                myIter = model.get_iter(chemin)

                if (position == Gtk.TREE_VIEW_DROP_BEFORE
                        or position == Gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
                    model.insert_before(myIter, data1)
                else:
                    model.insert_after(myIter, data1)
            else:
                model.append(data1)


        while Gtk.events_pending():
            Gtk.main_iteration()

        return True


    def insertionx (self, widget)  :
        global central_table, main_field, stores, listes

        nb = self.arZoom['notebook1']
        tab=nb.get_current_page()
        left = self.arZoom['treeleft' + str(tab)]
        right = self.arZoom['treeright']
        model1 = left.get_model()
        model2 = right. get_model()

        arIter=iter_sel(left)
        values = []

        for  iter in arIter  :

            id=model1.get_value(iter,20)
            nom=model1.get_value(iter,0)
            values.append(id)
            values.append(nom)  # additional columns
            columns =  right.get_columns()
            if len(columns) > 1 :
                for i  in range( 1, len(columns)) :     #... for (i = 1| i < count(columns)| i+= 1)
                    if mag.arw['zoom_combo' + str(i)] :
                        values.append(mag.arw['zoom_combo' + str(i)].child.get_text())

            append(model2,values)



    def tapez_saisiex(self, widget, clists)  :
        global config, tab_conversion

        nb = self.arZoom['notebook1']
        tab=nb.get_current_page()
        clist = clists[tab]
        source = tab_conversion[clist]
        type = config['xtabs'][source]['type']
        if type == "list" :

            mag.refresh_list("", source,'tapez_saisie', complement = " ")       # use a not None complement to override the complement and get a full listing





    def additional_data(self, entry,treeview,field,index)  :



        data = entry.get_text()
        model = treeview.get_model()
        iter1 = iter_sel(treeview,True)
        if iter1 :
            model.set(iter1,index + 2,data)
        else :
            alert("pas de ligne sélectionnée");




    def additional_data_show(self, widget, table,id_type,treeview)  :# show data in comboboxes when a line is clicked :

        for  z in ['1','2','3','4','5','6','7','8','9']  :
            if 'zoom_combo'+z in mag.arw:
                text = get_sel_row_data(treeview,0,int(int(z) + 1))
                model = mag.arw['zoom_combo'+z].get_model()
                mag.arw['zoom_combo'+z].set_active(2)





    def details(self, widget, table,id_type,left, col_data)  :
        global config, periph_tables

        text = ""
        popups = ""
        id = get_sel_row_data(left,0,20)
        if int(id) > 0 :
            query = eval(php_string("select * from $table where $id_type = $id"))
            cursor.execute(query)
            fiche = fetch_array(cursor, table)
            if 'details' in col_data :
                code = col_data['details']
                (text,popups) = mag.parse_code(fiche,code)

        mag.detail_text(self.arZoom['textview1'], text, popups)



    def edit_clicked(self, window,tab)  :
        global mem

        mem['edit_mode'] = 1
        self.arZoom['window1'].set_modal(False)        # allow the window to go behind
        x = mag.arw["clist5"].path()
        mag.arw['s_notebook'].set_current_page(0)
        #win=mag.arw["s_window"].window # bring list to front

##        win.raisex()


        #mag.arw['s_notebook1'].set_show_tabs(False)
        mag.arw['s_notebook1'].set_current_page(tab - 1)



    def view_details(self, button)  :

        if button.get_active() == True :
            self.arZoom['scrolledwindow3'].show()
            button.child.set_text(_('Hide details'))

        else :
            self.arZoom['scrolledwindow3'].hide()
            button.child.set_text(_('Show details'))




    def add_entry(self, widget, table,clists)  : # this code is derived from the periph_add function:

        global config, periph_tables, tab_conversion, arWidgets, arZoom, link

        nb = self.arZoom['notebook1']
        tab=nb.get_current_page()
        clist = clists[tab]
        source = tab_conversion[clist]
        right = self.arZoom['treeright']
        id_type = periph_tables[table]['id_type']
        mainfield = periph_tables[table]['main_field']


        nom1 = self.arZoom['add_entry'].get_text()
        nom1b = mag.Chaine_guillemets(nom1)
        if len(nom1) > 0 :
            query = eval(php_string("select $id_type from $table where $mainfield = $nom1b"))
            cursor.execute(query)
            sql_error(link)
            #if mysql_num_rows(result)==0 :
            result = cursor.fetchone()
            if result == None :

                # If the new name does not exist yet, we add


                # mysql req = eval(php_string("insert into $table set $mainfield = $nom1b"))
                req = eval(php_string("insert into $table ($mainfield) values ($nom1b)"))
                #ok=mysql_query(req)
                cursor.execute(req)
                sql_error(link,req)

            else :
                alert (nom1 + _(" already exists."))


        # add to the list on the right
        values = {}
        # get the id of the new name
        cursor.execute(eval(php_string("select $id_type from $table where $mainfield = $nom1b")))
        result = cursor.fetchone()
        values[0] = result[0]
        values[1] = nom1
        # additional columns
        columns =  right.get_columns()
        if len(columns) > 1 :
            for i  in range( 1, len(columns)) :     #... for (i = 1| i < count(columns)| i+= 1)
                if mag.arw['zoom_combo'+ str(i)] :

                    values[i+1] = mag.arw['zoom_combo'+str(i)].child.get_text()




        model = right.get_model()
        values = array_pad(values,len(columns),"");

        append(model,values)
        # refresh the display
        tab = tab_conversion[clist]
        type = config['xtabs'][tab]['type']
        if type == "list" :
            mag.refresh_list(tab,'tapez_saisie')

        else :
            self.actualiser(clist)
            self.collapse(clist,2)







    # save the size and position of the window
    def save_position(self, widget = None)  :

        global config, dialog

        (x,y) = self.dialog.get_position()
        (w, h) = self.dialog.get_size()
        if not "zoom1" in config['ini'] :
            config['ini']['zoom1'] = {}
        config['ini']['zoom1']["x"] = x
        config['ini']['zoom1']["y"] = y
        config['ini']['zoom1']["h"] = h
        config['ini']['zoom1']["w"] = w

        save_settings()






    def closex(self, widget)  :
        self.ok = 1
        self.dialog.destroy()







##def prompt2(fields)  :
##    prompt = Prompt2(fields)
##
##    new_value = []
##    defaults = []
##    if not prompt.ok :
##        return
##    print fields
##    for  key in fields  :
##        value = fields[key]
##        defaults.append( value[0])   # valeurs par défaut
##
##
##
##    for i in range(0,len(fields)) :     #... for(i=0| i<count(fields)| += 1i)
##        temp = prompt.entry[i].get_text()
##        if temp.strip() == "" :
##            temp = defaults[i]
##
##        new_value.append( temp)
##
##    return new_value




class Prompt :
# displays a dialog to ask for input


    def __init__(self, fields)  :
        # fields is a dictionary. Each entry will display an entry.
        # entries have two possible forms :
        # Simple form :
        #       title : default
        #
        # Advanced form :
        #       title : [default, select, values]
        #       default = value which will be selected in the combo
        #       select : sql query which will return the list of the combobox
        #       values : list of the combobox
        # TODO : all this is probably not yet implemented

        self.entry = {}
        self.ok = 0

        dialog = Gtk.Dialog('Edit', None, Gtk.DIALOG_MODAL|Gtk.DIALOG_NO_SEPARATOR)
        table = Gtk.Table()
        self.display_table(table, fields)
        dialog.vbox.pack_start(table)

        button = Gtk.Button('  OK  ')
        alignment = Gtk.Alignment(0, 0, 0, 0)
        alignment.add(button)
        button.connect('clicked', self.on_button)
        row = len(fields)
        table.attach(alignment, 1, 2, row, row+1, Gtk.FILL, Gtk.SHRINK)

        self.dialog = dialog
        dialog.show_all()
        win=dialog.window   # get the GdkWindow
        win.set_keep_above(True)


    def run(self) :
        result = self.dialog.run();
        self.dialog.destroy();
        return self.reponse


    def display_table(self, table, fields)  :
        global entry
        row = 0


        for  label in fields  :
            value = fields [label]
            if isinstance(value, str) :
                value = [value,None,None]
            label = Gtk.Label(label)


            self.entry[row] = Gtk.Entry()


            alignment = Gtk.Alignment(1, .5, 0, 0)
            alignment.add(label)
            table.attach(alignment, 0, 1, row, row+1)
            table.attach(self.entry[row], 1, 2, row, row+1)


            if isset(value[1]) :
                req = value[1]

                cursor.execute(req)
                sql_error(link,req)
                for line in cursor :
                    self.model[row].append([line[0]])

            #$self->entry[$row]->set_text($value[0]);

            row += 1







    # simulate button click when user press enter
    def on_enter(self, entry, button)  :
        button.clicked()


    def on_button(self, button)  :
        self.ok = 1
        self.reponse = []
        for entry1 in self.entry :
            self.reponse.append(self.entry[entry1].get_text())
        self.dialog.destroy()
        return


class Prompt2A :
# displays a dialog with comboboxes


    def __init__(self, fields)  :
        # fields is a dictionary. Each entry will display a combobox.
        # entries have two possible forms :
        # Simple form :
        #       title : default
        #
        # Advanced form :
        #       title : [default, select, values]
        #       default = value which will be selected in the combo
        #       select : sql query which will return the list of the combobox
        #       values : list of the combobox
        # TODO : all this is probably not yet implemented

        self.entry = {}
        self.combo = {}
        self.model = {}
        self.ok = 0

        dialog = Gtk.Dialog('Edit', None, Gtk.DIALOG_MODAL|Gtk.DIALOG_NO_SEPARATOR)
        table = Gtk.Table()
        self.display_table(table, fields)
        dialog.vbox.pack_start(table)

        button = Gtk.Button('  OK  ')
        alignment = Gtk.Alignment(0, 0, 0, 0)
        alignment.add(button)
        button.connect('clicked', self.on_button)
        row = len(fields)
        table.attach(alignment, 1, 2, row, row+1, Gtk.FILL, Gtk.SHRINK)

        self.dialog = dialog
        dialog.show_all()
        win=dialog.window   # get the GdkWindow
        win.set_keep_above(True)


    def run(self) :
        result = self.dialog.run();
        self.dialog.destroy();
        return self.reponse


    def display_table(self, table, fields)  :
        global entry
        row = 0


        for  label in fields  :
            value = fields [label]
            if isinstance(value, str) :
                value = [value,None,None]
            label = Gtk.Label(label)

##            self.combo[row] = Gtk.ComboBoxEntry()
##            self.model[row] = Gtk.ListStore(str)
##            self.combo[row].set_model(self.model[row])
##            self.combo[row].set_text_column(0)
            self.combo[row] = Gtk.combo_box_entry_new_text()
            self.entry[row] = self.combo[row].get_child()
            # add completion to the entry
##            completion = Gtk.EntryCompletion
##            completion.set_model(self.model[row])
##            completion.set_text_column(0)
##            self.entry[row].set_completion(completion)


##            self.entry[row].connect("changed","allchars","entry")
            alignment = Gtk.Alignment(1, .5, 0, 0)
            alignment.add(label)
            table.attach(alignment, 0, 1, row, row+1)
            table.attach(self.combo[row], 1, 2, row, row+1)


            if isset(value[1]) :
                req = value[1]

                cursor.execute(req)
                sql_error(link,req)
                for line in cursor :
                    self.model[row].append([line[0]])

##                result = mysql_query(req)
##                sql_error(link,req)
##                for i  in range( 0, mysql_num_rows(result)) :     #... for (i = 0| i < mysql_num_rows(result)| i+= 1)
##                    line = mysql_fetch_row(result)
##                    self.model[row].append([line[0]])


            #$self->entry[$row]->set_text($value[0]);

            row += 1







    # simulate button click when user press enter
    def on_enter(self, entry, button)  :
        button.clicked()


    def on_button(self, button)  :
        self.ok = 1
        self.reponse = []
        for entry1 in self.entry :
            self.reponse.append(self.entry[entry1].get_text())
        self.dialog.destroy()
        return



class ask_for_config:
    def __init__(self) :
        #dialog = Gtk.Dialog(title=None, parent=None, flags=0, buttons=None)
        self.dialog = Gtk.Dialog(title='Configuration choice', parent=None, flags=Gtk.DialogFlags.MODAL, buttons=("OK", 1, "Cancel", 0));
        self.combo = Gtk.ComboBoxText();
        temp = glob.glob("config/*");

        for val in temp :
            if os.path.isdir(val) :
                dir_name = val[7:]
                if dir_name[0:1] != "#" :
                    self.combo.append_text(dir_name);
        self.combo.set_active(0);
        self.dialog.vbox.pack_start(self.combo, True, True, 0);
        self.dialog.show_all();

    def run(self) :
        result = self.dialog.run();
        reponse = self.combo.get_active_text();
        self.dialog.destroy();
        return reponse

class maglist() :

    """ the flow of the program when the user clicks the "Record" buttons is not evident. Some explanations

        - The button launchs the function ok_liste
                cette fonction en collaboration avec les fonctions ok_liste_b
                et lancerRecherche rassemble les données des champs inversés et fait la synthèse des différentes listes
                avant de passser le résultat à la fonction chercher
                qui va lancer la routine de recherche et d'affichage.
        - ok_liste launchs ok_list_b
                DESCRIPTION: Rassemble les données inversées pour les rangs sélectionnés dans une liste
        - then ok_liste will handle the combination of different selections, if required
        - finally it will return

    """

    def __init__(self) :
        #global maggy, arw
        #maggy = mag
        #self.arw = arw
        self.ok_list_disable = False
        pass


    def build_listes(self) :
        t1 = time.time()
        global  mem, listes, cr;
        global  node, affichage, link;
        global  config, tab_conversion, popup_condition;

        self.build_listes_errors = []


        # create lists

        # deleted because it takes a lot of time. For the first sort, MySQL can take care of it
        tab_conversion = {}
        for key  in config['xtabs'] :
            val = config['xtabs'][key ]

            liste = config['xtabs'][key]['treeview'];
            tab_conversion[liste] = key;
            # list name => configuration name



        listes = {}
        # creation of templates (ListStore or TreeStore depending on the type of list).
        for tab  in config['xtabs'] :
            table_data = config['xtabs'][tab ]

            treeview = table_data["treeview"];
            if table_data["type"] == "tree" :

                listes[treeview] = Gtk.TreeStore(str,str,str,str,str,str,str,str,str,str,str,str,
                str,str,str,str,str,str,str,str,str,str,str,str);

                self.configure_list(treeview);

                self.build_tree(treeview);



            else :

                listes[treeview] = Gtk.ListStore(str,str,str,str,str,str,str,str,str,str,str,str,
                str,str,str,str,str,str,str,str,str,str,str,str,
                str,str,str,str,str,str,str,str,str,str,str,str);
                # an easier way could be :
                #model = Gtk.ListStore(*([str] * ncols))
                #which creates exactly ncols columns of type str.


                self.configure_list(treeview);

                entry = table_data["entry"];
                if 'table' in table_data :
                    table = table_data["table"];
                complement = table_data["treeview"];

                if len(entry.strip()) > 0 :


                    if entry in self.arw :

                        self.arw[entry].connect("changed", self.refresh_list,tab);

                    else :
                        self.build_listes_errors.append(["Entry", entry])
                        #alert(_("Entry %s does not exist") % entry)


                if link :
                    refresh_b = True
                    if 'options' in table_data :
                        opt = table_data['options']
                        if opt != None :
                            options = opt.split(",");
                            for z in options :
                                if z.strip().lower() == "n" :  # if parameter n, do not call the list at all
                                    refresh_b = False
                    if refresh_b == True :
                        self.refresh_list2(tab);


##            t2 = time.time()
##            print "build : ", (t2-t1)
##            t1 = t2


##        t2 = time.time()
##        print " time22 : fin build ", (t2-t1)
##        t1 = t2


        # positionnement automatique du curseur

        for z in config['xtabs'] :
            if 'entry' in z :
                object1 = z['entry']
                if object in self.arw :
                    entry = self.arw[object]
                    entry.connect('map-event','curseur');



        # valeur par défaut pour l'affichage : on prend les données de la première table centrale

        try :
            temp = list(config['central'].keys())
            result = config['central'][temp[0]]['result'];
            details = config['central'][temp[0]]['details'];
        except :
            print("The configuration of the central table %s is incomplete" % temp[0])

        if result and details :

            self.choisir_affichage(result,details);






        # load comboboxes defined in the parameters
        if 'combobox' in config :
            listStore = None
            for key  in config['combobox'] :
                val = config['combobox'][key]

                if not 'combobox' in val :
                    return
                if not val['combobox'] in self.arw :
                    print(val['combobox'],"does not exist")
                    continue
                widget = self.arw[val['combobox']];
                type = widget_type(widget);


                if 'query' in val :
                    req = val['query'];
                else :
                    req = ""
                if len(req) > 0 :

                    # if a query is defined to fill the combobox
                    listStore = Gtk.ListStore(str,str);
                    try :
                        cursor.execute(req);
                    except sqlite.Error as er :
                        sqlite_error2(er,req);

                    fiche = 1
                    while fiche :
                        try :           # Instead of returning none, as sqlite, the obdc pilot used for access databases generates a fatal error
                            fiche = cursor.fetchone()
                        except :
                            fiche = None


                        if fiche :
                            try :
                                data = fiche[0];
                                if len(fiche) > 1 :
                                    data2 = fiche[1]
                                else :
                                    data2 = ""
                                listStore.append([data,data2]);
                            except :                            # for mysql
                                data = fiche[list(fiche.keys())[0]];
                                if len(list(fiche.keys())) > 1 :
                                    data2 = list(fiche.keys())[1]
                                else :
                                    data2 = ""
                                listStore.append([data,data2]);





                if (widget) :
                    if type  in ["GtkComboBox", "GtkComboBoxEntry", "GtkComboBoxText"]:

                        cell_renderer = Gtk.CellRendererText();
                        combo = widget;
                        if listStore :

                            combo.set_model(listStore);
                            combo.pack_start(cell_renderer, True);

                            completion = Gtk.EntryCompletion();
                            completion.set_model(listStore);
                            completion.set_text_column(0);

                            if type == "GtkComboBoxEntry" :

                                combo.set_text_column(0);
                                entry = combo.child
                                entry.set_completion(completion);
                            else :
                                combo.add_attribute(cell_renderer, "text", 0);
                else :
                    self.build_listes_errors.append(["The combobox", val['combobox']])
                    #alert(_(" The combobox %s does not exist") % val['combobox'])

##        t2 = time.time()
##        print " time25 : ", (t2-t1)
##        t1 = t2

        popup_condition = {}
        # Does not improve performance much. You need at least 28 for sorting by ratings
        if 'popup' in config and isinstance(config['popup'], dict):

            for key  in config['popup'] :
                val = config['popup'][key ]

                if len(val['condition'])>0 :

                    req = val['condition']
                    try :
                        cursor.execute(req)
                    except :
                        sql_error(link,req, "Error in popup definition : condition")
                        continue
                    result = cursor.fetchall()
                    n = len(result)
                    popup_condition[key] = []
                    for row in result :
                        popup_condition[key].append(list(row.keys())[0])


    def configure_list(self, name) :

        global listes, cr, config, config_info, tab_conversion, checkbox_list, periph_tables;

        if not name in self.arw :

            print(name + _(" not found !!"));
            return;

        # defaults
        hauteur = 12
        points = int(10)


        if 'line_height' in config['ini']['lists'] :
            try :
                hauteur = int(config['ini']['lists']['line_height'])
            except : hauteur = 12
        else :
            hauteur = 12

        if 'font_size' in config['ini']['lists'] :
            points = int(config['ini']['lists']['font_size'])


        cr = {}
        cr[name] = Gtk.CellRendererText();
        cr[name].set_property('height', hauteur);
        cr[name].set_property('family', config['ini']['lists']['font']);
        cr[name].set_property('size-points', points);


        treeview=self.arw[name];
        if magutils.widget_type(treeview) != "GtkTreeView" :
            alert(name + _(" is not a GtkTreeView. \nVerify your configuration"));
            return;

        store=listes[name];
        treeview.set_model(store);
        treeselect=treeview.get_selection();
        treeselect.set_mode(3);     # multiple selection
        treeselect.connect('changed', self.detail_liste);
        treeview.connect('button-press-event', self.update_active_list)


        # Create the columns, make it resizable and sortable

        tab = tab_conversion[name];
        table_data = config['xtabs'][tab];
        # table data
        coldef = table_data['cols'];



        for key  in coldef :
            val = coldef[key ]

            if 'width' in coldef[key] :
                if coldef[key]['width'] != "" :     # if a width is defined for the column
                    coltype = 'text';
                    if 'options' in coldef[key] :
                        pango = get_option("pango",coldef[key]['options']);
                        if pango == 1 :
                            coltype = 'markup';     # put markup instead of text to use pango

                    if "title" in coldef[key] :
                        col_title = coldef[key]['title']
                    else :
                        col_title = ""

                    colnew = Gtk.TreeViewColumn(col_title, cr[name], text=int(key));
                    colnew.set_sizing(2);
                    # 2 = GTK_TREE_VIEW_COLUMN_FIXED
                    colnew.set_fixed_width(int(coldef[key]['width']));
                    colnew.set_resizable(True);
                    colnew.set_reorderable(True);
                    # colnew.set_clickable(True);

                    # make it sortable and let it sort after model column j
                    colnew.set_sort_column_id(int(key));

                    # add the column to the view
                    treeview.append_column(colnew);



        # checkboxes: construction of the checkbox_list array that will be used by creer_liste and ok_liste_b

        k = 22;

        if 'check' in table_data :
            if table_data['check'] :

                table_def = table_data['table_def'];
                try :
                    central_def = config_info['periph_def'][table_def]['central_def'];
                    central_table = config['central'][central_def]['table'];


                    for key  in table_data['check'] :
                        val = table_data['check'][key ]



                        if (val['field'] == "#"
                            or val['field'] == "i_data_" + central_table) :

                            # if the inverted field is the global field
                            index = 21;
                            val['field'] = "i_data_" + central_table;

                        else :

                            index = k;
                            k+= 1;

                        # checkbox_list contains data like : [checkbutton1] => [i_people , 21]
                        v2(checkbox_list,name)
                        checkbox_list[name][val['checkbox']] = [val['field'],index]
                except :
                    print("error in configuration")          # TODO


        # couleurs pour les renvois ; elles sont gérées par une fonction

        col = treeview.get_column(0);
        ref_field = get_option("r",table_data['options']);  # field specified for cross-reference in definition table
        #print "===>", ref_field
        for key  in table_data['cols'] :
            val = table_data['cols'][key ]
            if 'field' in val :
                if val['field'] == ref_field :
                    ref_column = int(key)
                    if ref_column > 0 :
                        col.set_cell_data_func(cr[name], self.renvois, ref_column);

        treeview.show();


    def update_active_list(self, widget, *params) :
        #launched by the button-press-event of the search lists, and other events,
        # sets the value for self.active_list
        # which will be used by the switch database functions
        self.active_list = widget


    def curseur(self, widget) :

        widget.grab_focus();



    #TODO 0 : optimize
    # function to color the return lines
    # last parameter indicates the column of the model that contains the cross reference

    def renvois(self, column, cell, model, iter, colrenvoi) :

        global colors;

        cross_ref_color_f = self.colors['s_reference']['f'];
        cross_ref_color_b = self.colors['s_reference']['b'];
        renvoi = model.get_value(iter, colrenvoi);


        if renvoi and len(renvoi) > 0 :

            if cross_ref_color_f :

                cell.set_property('foreground', cross_ref_color_f);

            if cross_ref_color_b :

                #cell.set_property('background', cross_ref_color_b);
                pass


        else :

            cell.set_property('foreground', '#000000');
            #cell.set_property('background', '#ffffff');









    def ____fonctions_pour_les_listes_normales____() :
        pass


    def compter(self, x) :

        if not x :
            return ""

        temp = x.split(",")
        compte=len(temp);
        if len(x) == 0 :
            compte="";

        return compte;





    def refresh_list(self, widget, tab, entry = None, complement = None) :


        """==================================================================================================
        FONCTION   : refresh_list
        DESCRIPTION: Attend 1 seconde avant de lancer la mise à jour des listes quand il y a moins de trois
        caractères dans une zone "tapez", afin d'éviter un temps de réponse très long de la frappe

        PARAMETRES : tous les paramètres sont passés à refresh_list2, voir cette fonction.

        NOTE SUR LE FONCTIONNEMENT DU TIMER : le timer possède deux paramètres. Le premier est le délai en millisecondes.
        Le deuxième est une fonction qui sera appelée immédiatement lorsque le timer est créé.
        Cette fonction aura pour but de renvoyer : soit rien -. le timer s'arrête
        soit le nom d'une fonction (qui peut éventuellement être elle-même)
        Cette fonction sera exécutée au bout du délai fixé par le premier paramètre.
        Si cette fonction renvoie quelque chose (n'importe quoi, il semble), le timer continue à fonctionner et
        exécutera de nouveau la fonction après qu'un nouveau délai aura passé. Ceci continuera jusqu'à ce que
        la fonction cesse de renvoyer quelque chose, ou bien jusqu'à la destruction du timer par la fonction
        source_remove.
        Cette procédure à deux degrés peut sembler complexe, mais elle permet à la fonction appelée directement
        par le timer de faire un choix entre les actions à exécuter en fonction de l'état du programme. Cela
        offre donc une grande souplesse. Ci-dessous l'exemple le plus simple où la fonction appelée par le timer
        (timer1) lui renvoie simplement le nom de la fonction à exécuter après le délai.
        Les autres paramètres de timeout_add seront simplement passés à la fonction appelée (la deuxième,
        ci-dessous refresh_list2). Si la première fonction a besoin de paramètres, il faudra les inclure
        normalement entre les parenthèses de cette fonction.

        ===================================================================================================
        """


        global mem, config;

        table_data = config['xtabs'][tab];

        if entry == None :

            entry = table_data["entry"];

        if 'timer1' in mem :
            if mem['timer1'] != None :
                gi.repository.GLib.source_remove(mem['timer1']);

        a=self.arw[entry].get_chars(0,-1);
        # search for the active word, i.e. eliminate everything that precedes a logical operator
        e = re.split("[&+/_]", a)[0];

        if len(e.lstrip()) <3 :
            if ((e != "") and(e != " ")) or(a == "") :      # ignorer les espaces après un séparateur, mais prendre en compte le cas où le champ est tout à fait vide


                if 'type_delay' in config['ini']['lists'] :
                    mem['timer1'] = gi.repository.GLib.timeout_add(int(config['ini']['lists']['type_delay']),self.timer1,tab, entry, complement);
                else :
                    self.refresh_list2(tab,entry,complement);

        else :

            self.refresh_list2(tab,entry,complement);

    def timer1(self, tab, entry, complement) :
        self.refresh_list2(tab,entry,complement)
        if mem["timer1"]:
            gi.repository.GLib.source_remove(mem['timer1'])
        return "refresh_list2";


    """==================================================================================================
    FONCTION   : refresh_list2
    DESCRIPTION: Envoie les commandes à la fonction cree_liste quand les données de la zone "tapez" ont changé

    PARAMETRES : tab = nom de la configuration de la liste
    entry (optionnel) = zone tapez sur laquelle prendre les données
    ===================================================================================================
    """

    def refresh_list2(self, tab,entry = None, complement = None) :


        global config, periph_tables, mem, listes, preview_req, statistiques;


        if 'timer1' in mem :
            if mem['timer1'] != None:
                gi.repository.GLib.source_remove(mem['timer1']);
            mem['timer1'] = None


        table_data = config['xtabs'][tab];

        liste = table_data["treeview"];
        if entry == None :
            entry = table_data["entry"];

        config_table = table_data["table_def"];
        # TODO IMPORTANT selection of word tables
        if not config_table in config['peripheral'] :
            if not config_table in config['words'] :
                print((_("WARNING : table %s does not seem to exist, or information missing for this table") % config_table))
                return
            else :
                table = config['words'][config_table]['table'];
                champ = config['words'][config_table]['main_field'];

        else :
            if (not 'table' in config['peripheral'][config_table] or
                not 'main_field' in config['peripheral'][config_table]) :
                    print("FATAL ERROR : table ", config_table, " improperly configured")
                    return
            else :
                table = config['peripheral'][config_table]['table'];
                champ = config['peripheral'][config_table]['main_field'];
                order_field = champ
                if 'order' in config['peripheral'][config_table] :
                    order_field = config['peripheral'][config_table]['order']


        if complement == None :             # if complement has been sent by the caller (zoomx) use the value sent.
                                        # This feature is used to avoid using complement and get a full listing in the edit boxes
            if "complement" in table_data :
                complement = table_data["complement"]
            else :
                complement = ""

        if not liste in self.arw :
            return
        treeview =self.arw[liste];


        store = listes[liste];
        if entry in self.arw :
            a=self.arw[entry].get_text();

            # handle jokers
            a = a.replace("*", "%")
            a = a.replace("?", ".")


        opt = table_data['options'];
        if opt :

            options = opt.split(",");
            for z in options :

                if z.strip().lower() == "n" :

                    if a=="" :
                        a=">>>";        # little trick to clear the list if you delete all the characters in the "type" area
                    if a=="$" :
                        a="";       # to display the list from the beginning, use the $ character




        # handling multiple selections; "&" means AND, "+" or "/" means OR and "_" means EXCEPT
        a = a.replace("_", ";_")
        a = a.replace("+", ";+")
        a = a.replace("&", ";&")
        a = a.replace("/", ";")


        a=a.strip()
        mot=a.split(";")


        selection = {}
        sel=treeview.get_selection();
        # mémorisation des lignes sélectionnées (id_livre et groupe)
        (model, arPaths) = sel.get_selected_rows();
        if arPaths :
            for path in arPaths :
                iter = model.get_iter(path);
                idlivre = model.get_value(iter, 20);
                groupe = model.get_value(iter, 19);
                if groupe not in selection :
                    selection[groupe] = []
                selection[groupe].append(idlivre)

        self.ok_list_disable = False
        sel.unselect_all()
        store.clear();
        self.ok_list_disable = False

        for i in range(0, len(mot)) : #(i=0; i<len(word); i+= 1)
## if mot[i] == "" :
## word[i] = "a"

            param = (i + 1);
            if mot[i][0:1]=="_" :

                param= param * (-1);
                mot[i]=mot[i][1:];

            if mot[i][0:1]=="+" :

                mot[i]=mot[i][1:];

            if mot[i][0:1]=="&" :

                param= (i + 101);
                mot[i]=mot[i][1:];


            num = self.cree_listes(mot[i].strip(),table,champ,liste,complement,param,selection);


        # display the number of records
        if entry + '_#' in self.arw :

            set_text(self.arw[entry + '_#'],num);


        # field exclude
        if entry + '_x' in self.arw :

            exclure=get_text(self.arw[entry + '_x']);
            exclure=str_replace(["/","&",";\n"],[";"],exclure);      # TODO: ?? is it right?
            e=explode(";",exclure);
            for mot in e :

                if mot!="" :
                    cree_listes(mot.strip(),table,champ,liste,complement,-1,selection)

    # end of function refresh_list

    """==============================================================================
    FONCTION   : cree_liste
    DESCRIPTION: Crée les listes de sélection

    PARAMETRES : mot = chaîne utilisée pour la requête sql
    table = paramètre pour "from" de la requête sql (nom de la table à utiliser)
    champ = champ utilisé par la requête sql
    liste = liste concernée
    complement = complément de commande pour la requête sql
    groupe =
    selection = array des lignes sélectionnées lors de l'appel, pour conserver cette sélection si possible

    ==============================================================================
    """

    def cree_listes(self, mot,fromx,champ,liste,complement,groupe, selection) :

        global config, mem, listes, preview_req, style_exclure, statistiques
        global c_colonnes, tab_conversion, config, periph_tables, checkbox_list, link
        global cr, colors;

        treeview =self.arw[liste];
        store = listes[liste];

        #word = self.String(word)
        limite=config['ini']['lists']["max_lines"];
        if limite.isdigit() and int(limite) < 1 :
            limite = 100;

        # N.B. : in the sqlite version, order by has been removed and should be put in complements
        # TODO : why ? presently we restored order by in its normal place
        if db_type == "sqlite" :
            req="select * from %s where %s like '%s%%' %s  order by %s collate france limit %s" % (fromx, champ, mot, complement, champ, str(limite));
        elif db_type == "mysql" :
            req="select * from %s where %s like '%s%%' %s order by %s limit %s" % (fromx, champ, mot, complement, champ, str(limite));
        elif db_type == "accdb" :
            req="select * from %s where %s like '%s%%' %s order by %s " % (fromx, champ, mot, complement, champ);

        try :
            cursor.execute(req)
        except :
            print("Erreur SQL dans cree_listes")
            sql_error(link,req);

            return

        result = cursor.fetchall()
        num = len(result)


        #return

        try:
            tab = tab_conversion[liste];
            list_data = config['xtabs'][tab];
            # table data
            primary_key = periph_tables[fromx]['id_type'];
            # name of the primary field
            central_def = periph_tables[fromx]['central_def'];
            table_def = list_data['table_def'];
            options = list_data['options'];
            color_field = get_option("c",options);
            central_table = config['central'][central_def]['table'];
        except :
            print("Definition for list ", liste, " is not complete")
            return

        if db_type == "accdb" :             # access driver returns fields name in lower case
            central_table = central_table.lower()

        coldef = list_data['cols'];

        for i in range(0,num) : #(i=0; i<num; i+= 1)

            try :                           # TODO : Access hangs if cursor has no data ...
                fiche=result[i]
            except :
                return
            if fiche == None :
                return

            values = [];
            values = array_pad(values,36,"");

            for key  in coldef :
                val = coldef[key ]
                key_i = int(key)        # json does not store keys as integers
                if 'field' in val :
                    field = val['field'];
                else :                  # incomplete configuration. Non fatal error
                    continue            # TODO: error message
                if field[0:1] == '#' :

                    # extract the name of the inverted field
                    temp = field[1:];
                    if field == "#" :
                        temp = "i_data_" + central_table;
                    if not db_type == "accdb" :          # TODO: with accdb, error: Row object has no attribute 'keys
                        if temp in list(fiche.keys()) :
                            values[key_i] = self.compter(fiche[temp])

                elif field == "" :
                    values[key_i] = "";

                elif "," in field :
                    out = "";
                    for f in field.split(",") :
                        if fiche[f] :
                            out += fiche[f];
                    values[key_i] = to_utf8(out)

                else :
                    try :       # TODO problem here with archives
                        values[key_i] = to_utf8(fiche[field])
                    except :
                        debug = "juste  pour avoir un point d'arrêt"
                        pass


            if color_field and color_field in fiche :
                values[17]= self.colors[fiche[color_field]]['f']
                values[18]= self.colors[fiche[color_field]]['b']
            else :
                values[17] = '#000000';
                values[18] = '#ffffff';
            values[19]=groupe;
            if not db_type == "accdb" :          # TODO: with accdb, error: Row object has no attribute 'keys
                if primary_key in list(fiche.keys()) :
                    try:
                        values[20]=fiche[primary_key]
                    except:
                        print("Error for list, primary_key ", liste, primary_key)
            if not db_type == "accdb" :          # TODO: with accdb, error: Row object has no attribute 'keys
                if ('i_data_' + central_table) in list(fiche.keys()) :
                    thisvalue = fiche['i_data_' + central_table];
                    if isinstance(thisvalue, str):
                            thisvalue = thisvalue.encode("utf-8")
                    values[21] = thisvalue

            if liste in checkbox_list :
                # TODO 00 : optimize ?? doing this for each row must slow down a bit.
                for val in checkbox_list[liste] :
                    data1 = checkbox_list[liste][val]
                    try :
                        values[data1[1]] = fiche[data1[0]]
                    except :
                        continue


            values1 = []
            for value in values:
                values1.append(x2str(value))  # insure all is str
            try:
                listes[liste].append(values1);
            except:
                print ("===>Error in cree_listes")

            # avoid the slower append(list,values) function

            # hint: exclude
            if groupe < 0 :
                n=len(liste)
                liste.set_row_style(n-1,style_exclure);

# self.arw['type8_lines'].set_text(num);

        # couleurs de la liste ; elles sont prises de la colonne définie par le paramètre color


        col = treeview.get_column(0);
        if color_field :

            col.add_attribute(cr[liste],'foreground', 17);
            col.add_attribute(cr[liste],'cell-background', 18);


    ## values = [];
    ## add an empty line to separate the groups
    ## append(store,values);
    ##
    ## n=count_store(store);


    ## restore selection for rows that were selected before the refresh
    # RTF does not support utf8 directly
    ## sel = treeview.get_selection();
    ## for i in range(0, n) : #(i=0; i<n; i+= 1)
    ##
    ## name = store.get_value(arIters[i],20);
    ## group = store.get_value(arIters[i],19);
    ## if isset(selection[group]) and in_array(name,selection[group]) :
    ##
    ## sel.select_iter(arIters[i]);





        return num;




    def refresh_all_lists(self) :


        global config;

        for tab  in config['xtabs'] :
            table_data = config['xtabs'][tab ]

            treeview = table_data["treeview"];
            if table_data["type"] == "tree" :

                self.build_tree(treeview);

            else :

                self.refresh_list2(tab);



    def refresh_active_lists(self) :
        global config


        for tab  in config['xtabs'] :
            table_data = config['xtabs'][tab ]

            treeview = table_data["treeview"];
            if treeview == self.active_list.get_name() :
                self.refresh_list2(tab)





## if table_data["type"] == "tree" :
## self.build_tree(treeview);
##
## else :
## self.refresh_list2(tab);







    """==============================================================================
    FONCTIONS   : textbox, entry, text_box
    DESCRIPTION: deux petits utilitaires utilisés par la fonction suivante (detail_liste)
    Ils inscrivent dans le contrôle box le texte lu dans la colonne colonne du rang row de la liste cliste

    ==============================================================================
    """

    def textbox(box,colonne,model,iter,effacer = 0) :

        if effacer == 1 :

            texte ="";

        else :

            texte=model.get_value(iter, colonne);

        set_text(self.arw[box],texte);


    def entry(box,colonne,model,iter,effacer = 0) :

        if effacer == 1 :

            texte = "";

        else :

            texte=model.get_value(iter, colonne);


        set_text(self.arw[box], texte);



    """==============================================================================
    FONCTION   : detail_liste
    DESCRIPTION: affiche les détails dans les cadres de droite quand on sélectionne une ligne d'une liste
    PARAMETRES : cliste - liste concernée
    row - rang actif
    col - renvoyé par le système ; ne semble pas fonctionner (toujours -1)
    i - numéro de la liste
    ==============================================================================
    """

    def detail_liste(self, selection) :

        # print ("detail_liste  (ligne 3993)")
        # note 2
        global query;
        global config, tab_conversion;
        while Gtk.events_pending() :
            Gtk.main_iteration();

        datadef = {}

        (model, arPaths) = selection.get_selected_rows();
        if len(arPaths) > 0 :

            effacer = 0;
            iter = model.get_iter(arPaths[0]);
            # first line selected

        else :

            effacer = 1;
            iter = None;

        # if there is no selection, delete

        temp = selection.get_tree_view();
        list_name = Gtk.Buildable.get_name(temp)
        config_name = tab_conversion[list_name];
        table_data = config['xtabs'][config_name];

        col_def = table_data['cols'];

        for key  in col_def :
            val = col_def[key ]

            # extract the data

            if 'detail' in val :
                if len(val['detail']) > 0 :
                    # if the field 'detail' contains data
                    datadef[key] = val;


        for z in datadef :

            model_field = int(z)
            # extract the column number
            # model_field -= 1; # model fields start at 0 and not at 1
            if effacer == 1 :
                texte ="";
            else :
                texte=model.get_value(iter, model_field);

            if not datadef[z]['detail'] in self.arw :
                print(datadef[z]['detail'], "does not seem to exist (4044) ")
            else :
                widget = self.arw[datadef[z]['detail']];
                magutils.set_text(widget,texte);




        while (Gtk.events_pending()) :

            Gtk.main_iteration();

        # number of records returned by the current selection
        if list_name + "_#" in self.arw :

            in_liste = self.ok_liste_b("",list_name);
            in_liste = array_unique(in_liste);
            n=len(in_liste);
            msg = (_("This search returns %d records.") % n)
            set_text(self.arw[list_name + "_#"],msg);


        while (Gtk.events_pending()) :

            Gtk.main_iteration();







    """==============================================================================
    FONCTION   : ok_liste
    DESCRIPTION: lancée par les boutons "FICHES", cette fonction en collaboration avec les fonctions ok_liste_b
    et lancerRecherche rassemble les données des champs inversés et fait la synthèse des différentes listes
    avant de passser le résultat à la fonction chercher
    qui va lancer la routine de recherche et d'affichage.
    ==============================================================================
    """

    def ok_liste(self, treeview, option = 'combine', dummy = None) :

        global mem, config, config_info, popup_saisie, listes, query
        global tab_conversion, periph_tables, treeview_data, affichage;
        try:
            self.i += 1
        except:
            self.i = 1
        #print ("====>  ok_liste", str(self.i))
        if self.ok_list_disable == True:
            return
        listes_combinees = []
        query = {}
        # statements
        self.active_list = treeview
        self.arw['s_combine_status'].set_text("");


        if 'edit_mode' in mem :
            if mem['edit_mode'] == 1 :
                # if the button was used in edit mode
                mem['edit_mode'] = 0;
                self.arw['s_notebook1'].set_show_tabs(True);
                self.montrer('window4');
                popup_saisie.set_modal(True);
                return;

        if magutils.widget_type(treeview) == "GtkTreeView" :

            # if the function is called by a control linked to a list, or by the list itself
            nom_liste1 = Gtk.Buildable.get_name(treeview)
            # is there a selection (function is launched by the signal "cursor changed"
            # the first time the tab is opened, with no selection, which provokes
            # an annoying alert

            sel = treeview.get_selection()
            (model, arPaths) = sel.get_selected_rows();
            if len(arPaths) == 0 :
                return                      # no selection, return

            # search for data in the list
            liste_data = treeview_data[nom_liste1];
            in_liste = self.ok_liste_b(treeview,nom_liste1);





        if option == "combinexx" :  #Â£

            # function called by window button combine
            logic = []
            store=listes['combine'];

            if len(store) > 0 :

                # if the list is loaded
                ar_iter = array_iter(store);

                row1 = store[ar_iter[0]];
                nom_liste1 = row1[1];
                liste_data = treeview_data[nom_liste1];

                for iter in ar_iter :

                    row = store[iter];
                    if row[2] == 1 :

                        logic.append(row[3] + (row[4] * 2 ) + (row[5] * 3));
                        # 1, 2 or 3 depending on the radio button selected
                        listes_combinees.append(row[1]);
                        # add the selected lists



            num = len(listes_combinees);


            i = 0;
            for nom_liste2 in listes_combinees :        # create the book_id lists to combine

                if nom_liste2 in ["s_complex1", "s_complex2", "s_complex3"] :
                    z = substr(nom_liste2,-1);
                    mem ['critere' + str(i)] = self.lancerRecherche(z)      # if the queries are complex, launchSearch is used

                else :                                          # if it is about lists, the ok_liste_b function is used
                    in_liste = self.ok_liste_b(treeview,nom_liste2);
                    mem ['critere' + str(i)] = in_liste

                print((i, mem['critere' + str(i)]))

                i+= 1;


            for i in range(1, num) :               # logical treatment if there are several lists to combine

                if logic[i] == 1 :      # OR
                    temp=array_merge(mem ['critere'+str(i)], mem['critere'+str(i-1)])
                    mem['critere'+str(i)]=temp;

                elif logic[i] == 2 :    # AND
                    temp=array_intersect(mem ['critere'+str(i)], mem['critere'+str(i-1)])
                    mem ['critere'+str(i)]=temp;

                elif logic[i] == 3 :    #NOT (EXCEPT)
                    temp=array_diff(mem ['critere'+str(i-1)], mem['critere'+str(i)])
                    mem ['critere'+ str(i)]=temp;




            if num>1 :

                in_liste=temp;

            for z in [1,2,3,4,5,6,7,8,9] :
                mem['critere'+ str(z)]=""      # reset to zero



        # TODO ? if list_name1 != "complex" :

        if len(in_liste) > 0 :
            ids_list = ",".join(in_liste)
            query["ids"] = "(" + ids_list + ")"
        else :
            query["ids"] = "()"



        if len(query["ids"])>2 :

            page = mem['result_page']      # TODO: bug: return {}



            # parameters to store for the active result list
            periph_def = liste_data['table_def'];
            if v(config,'peripheral',periph_def,'central_def') :
                central_def = config['peripheral'][periph_def]['central_def']
            else :
                central_def = config['words'][periph_def]['central_def'];

            v2(affichage,page)
            affichage[page]['central_def'] = central_def;
            affichage[page]['table_def'] = liste_data['table_def'];
            affichage[page]['main_table'] = config['central'][central_def]['table'];
            # TODO: it would be better to delete these two lines and do the calculations in place, otherwise when calling directly a parked query, it doesn't work.
            affichage[page]['main_id_field'] = config['central'][central_def]['id_main'];
            result =  liste_data['result_def'];
            details = liste_data['details_def'];

            self.choisir_affichage(result,details);
            self.chercher();

            details_tab = affichage[page]['details_tab'];
            if isinstance(details_tab, str) :
                if details_tab.isdigit() :
                    details_tab = int(details_tab)
                else :
                    details_tab = 0
            if details_tab > 0 :
                self.arw['s_notebook3'].set_current_page(int(details_tab) -1);
            else :
                self.arw['s_notebook3'].set_current_page(0);

            self.montrer('window2',1);

        else :

            cw = self.arw['s_combine'];
            if cw.has_toplevel_focus() :

                self.arw['s_combine_status'].set_text(_("This search doesn't give any result"));

            else :

                alert(_("This search doesn't give any result"));






    """==============================================================================
    FONCTION   : ok_liste_b
    DESCRIPTION: Rassemble les données inversées pour les rangs sélectionnés dans une liste
    PARAMETRES : treeview - inutilisé
    nom_liste - nom de la liste correspondant au bouton utilisé
    RENVOI     : la liste des id_livre
    ==============================================================================
    """

    def ok_liste_b(self, treeview, nom_liste) :

        global mem,listes,in_liste, checkbox_list, msg;
        temp6 = "";
        groupe = {}

        in_liste = []
        liste_ligne = []
        arIter = []
        temp = []
        inv = []
        t2 = []
        liste=self.arw[nom_liste];
        if self.verify_button(liste) == False :
            return


        sel=liste.get_selection();
        (model, arPaths) = sel.get_selected_rows();
        if arPaths :
            # create an array of selected lines
            for path in arPaths :
                arIter.append(model.get_iter(path))


        if liste and (len(arPaths) > 0) :


            z = model.get_value(arIter[0], 0);
            # first name selected
            mem['nom_requete']=z;



        # process the checkboxes

        if nom_liste in checkbox_list :

            for key  in checkbox_list[nom_liste] :
                val = checkbox_list[nom_liste][key ]

                if key in self.arw :
                    if self.arw[key].get_active() :
                        inv.append(val[1])
                else :
                    msg = _('checkbox %s unknown') % key
                    alert(msg);
        else :
            inv=[21]      # the i_data field is in column 21


        if (nom_liste != 'clist4') and(len(arIter)>0) :

            # for queries, in_liste is already calculated

            for z in arIter :

                temp.append(model.get_value(z,19));

            # identification of groups

            groupes=array_unique(temp)
            groupes = temp


            for z in arIter :
                # extract the logical operator whose code is in field 19
                logique19=model.get_value(z,19)
                if logique19 == '' :
                    print("Erreur sur champ logique 19")
                    logique19 = 0
                logique19 = int(logique19)

                # For the history, a readable heading is formed.
                if isset(temp6) :  # no logical operator is needed at the beginning
                    if logique19 <  0 :
                        temp6 += " SAUF ";
                    elif logique19 > 100 :
                        temp6 += " ET ";
                    else :
                        temp6 += " OU ";

                temp6 += model.get_value(z,0);
                mem['elements_req']= temp6;

                if inv :                # inv contains the number of the field(s) that contain(s) the ids of the records.
                                        # le champ 21 correspond à "tout". S'il y a des cases à cocher sélectionnées,
                                        # they will have their own field.
                    for j in inv:           # for each field

                        t=model.get_value(z,j);
                        if t :
                            if len(t)>0 :
                                t2 = t.split(",")
                                #line_list=array_merge(line_list,t2)

                # constitution of groups
                if logique19 in groupe :            # If there is already a group corresponding to this logical operator, we add the data to the group
                    temp2 = groupe[logique19];
                    groupe[logique19]=array_merge(t2,temp2);
                else :                              # otherwise a new group is created
                    groupe[logique19]=t2            # TODO: local variable 't2' referenced before assignmen


            # combine the groups
            for z1 in groupes :
                if z1 == "" :
                    z1 = 0
                z = int(z1)     # group numbers

                if z<0 :            # if operator is _ (NOT)
                    in_liste=array_diff(in_liste,groupe[z]);
                elif z>100 :        # if operator is & (AND),
                    in_liste=array_intersect(in_liste,groupe[z]);

                else :              # otherwise we simply add the results (OR)
                    in_liste=array_merge(in_liste,groupe[z]);



## temporarily
## ll2 = []
## for a in in_liste :
## if a != "" :
## ll2.append(a)
## return ll2


        return in_liste;




    # function used for parked queries





    def reset_controls(self, widget, group = None) :
    # this function will reset a group of controls defined in the configuration :
        global config

        if not group :              # if group not given, we take it from the reset button name
            name = widget.get_name();
            group = substr(name,strrpos(name,'@')+1);

        for key, val  in config['combobox'].items() :

            if 'group' in val and val['group'] == group :
                if 'combobox' in val  and val['combobox'].strip() != "" :
                    combo = self.arw[val['combobox']]
                    type_s = widget_type(combo)
                    if type_s == "GtkComboBox" :
                        if combo.get_has_entry() :
                            set_text(combo.child, "")
                        else :
                            combo.set_active(-1)
                    else :
                        set_text(self.arw[val['combobox']],"")

                elif 'entry' in val and val['entry'].strip() != "" :
                    entry = self.arw[val['entry']]
                    set_text(self.arw[val['entry']],"");








    # #############################################################################################################
    #
    # =========================== functions for the list with tree(for themes) =========================


    def build_tree(self, name) :


        global config, tab_conversion, order_field, node, listes, cr
        global periph_tables, couleurs_themes, colors;

        coldef = {}
        node = {}

        if not name in self.arw :
            self.build_listes_errors.append(["The treeview", name])
            # only the selection is loaded
            return;


        try :
            tab = tab_conversion[name];
            table_data = config['xtabs'][tab];
            # table data
            table_def = table_data['table_def'];
            table = config['peripheral'][table_def]['table'];
            primary_key = config['peripheral'][table_def]['id_type'];
            # name of the primary field
            central_def = config['peripheral'][table_def]['central_def'];
            central_table = config['central'][central_def]['table'];
        except :
            print("Configuration for treeview %s seems incomplete" % name)
            return


        keys = list(table_data.keys())
        for z in keys :
            # extract the datax fields
            if z[0:3] == "col" :
                numcol = z[3:]
                if isinstance(numcol, str):
                    if numcol.isdigit():
                        numcol = int(numcol)
                    else:
                        numcol = 0
                if numcol>0 :
                    coldef[numcol] = table_data[z];


        req = "select * from %s order by %s" % (table, order_field) ;
        try :
            cursor.execute(req)
        except :
            sql_error(link, req);
            return

        data = cursor.fetchall()
        num=len(data)

        options = table_data['options'];
        color_field = get_option("c",options);

        coldef = table_data['cols'];

        for i in range(1, num) : #(i=1; i<=num; i+= 1)


            fiche=data[i];
            values = {};
            values = array_pad(values,24,"");
            try:
                id = fiche[primary_key];
            except:
                print("Error for primary_key ", primary_key)

            if isset(coldef) :

                for key  in coldef :
                    val = coldef[key ]
                    key = int(key)

                    # todo 00: optimize to speed up
                    field = val['field'];
                    if field[0:1] == '#' :

                        # extract the name of the inverted field
                        temp = field[1:];
                        if field == "#" :

                            temp = "i_data_" + central_table;
                        if temp in list(fiche.keys()) :
                            values[key] = self.compter(fiche[temp]);
                        else :
                            values[key] = ""

                    elif field == "" :

                        values[key] = "";

                    else :
                        try :       # TODO: problem here with archives
                            values[key] = fiche[field];
                        except :
                            pass
                            # print "Error for: key = ", key, " or ", "field = ", field

            # colors for the tree
            try :
                niveau = int(fiche["niveau"])
            except :
                niveau = 0
            if niveau > 3 :
                niveau = 0
            values[17] = self.colors[niveau]['f']
            values[18] = self.colors[niveau]['b']


## if fiche[color_field] :
## values[17] = self.colors[fiche[color_field]]['f']
## values[18] = self.colors[fiche[color_field]]['b']
## try :
## level = int(fiche["level"])
## except:
# no data in the list, so "display" is not initialized. We have to work around the problem
## if level > 3 :
## level = 3
## values[17] = self.colors[level]['f']
## values[18]= self.colors[level]['b']
## else :
## values[17] = '#000000' # foreground
## values[18] = '#bb88bb' # background
            # values[19]=group group is not defined in this function
            values[20]=fiche[primary_key];
            if 'i_data_' + central_table in list(fiche.keys()) :
                values[21]=fiche['i_data_' + central_table];

            parent=fiche["parent"];
            niveau=fiche["niveau"];

            values1 = []                     # insure all is str
            for value in values:
                values1.append(x2str(value))

            try:
                if ((parent in node) == False) :
                    node[id]= listes[name].append(None,values1);
                else :

                    node[id]= listes[name].append(node[parent],values1);
            except:
                print("====> Error in build tree")



        self.collapse(name,2);

        # theme tree colors;
        # they are taken from the column defined by the color parameter
        ctree = self.arw[name];
        ctree.set_reorderable(True);
        col = ctree.get_column(0);


        if color_field :
            if name in cr :
                col.add_attribute(cr[name],'foreground', 17);
                col.add_attribute(cr[name],'cell-background', 18);
            else :
                print("debug : ", name, "was not found in cr")


        # la propriété cell-background évite le quadrillage qui se produit avec background

        # activer les lignes pointillées dans l'arbre des thèmes
        ctree.set_enable_tree_lines(True);
        # this does not work when the colors are set by the cell renderer.







    def collapse(self, name,action) :

        global node, mem

        if not name in self.arw :

            return;

        ctree = self.arw[name];
        sel=ctree.get_selection();


        if action == 4 :
            ctree.expand_all();

        elif action == 1 :
            ctree.collapse_all();
            path = {0 : 0}
            ctree.expand_row(path,False);

        elif action == 2 :
            sel.select_all();
            (model, arPaths) = sel.get_selected_rows();
            for path in arPaths :
                ctree.expand_row(path,False);            sel.unselect_all();

        elif action == 3 :
            (model, arPaths) = sel.get_selected_rows();
            for path in arPaths :
                ctree.expand_row(path,True);





    def tree_expand_all(self, list) :

        global node, mem, tab_conversion;

        if self.verify_button(list) == False :

            return;

        list_name = list.get_name();
        self.arw[list_name].expand_all();


    def tree_collapse_all(self, list) :

        global node, mem, tab_conversion;

        if self.verify_button(list) == False :

            return;

        list_name = list.get_name();
        ctree= self.arw[list_name];
        ctree.collapse_all();

        path = {0 : 0}
        ctree.expand_row(path,False);       # TODO erreur ici :  TypeError: could not convert path to a GtkTreePath


    def tree_expand_1(self, list) :

        global node, mem, tab_conversion;

        if self.verify_button(list) == False :

            return;

        list_name = list.get_name();
        ctree = self.arw[list_name];
        sel=ctree.get_selection();


        sel.select_all();
        (model, arPaths) = sel.get_selected_rows();
        for path in arPaths :

            ctree.expand_row(path,False);

        sel.unselect_all();



    def tree_expand(self, list) :

        global node, mem, tab_conversion;

        if self.verify_button(list) == False :

            return;

        list_name = list.get_name();
        ctree = self.arw[list_name];
        sel=ctree.get_selection();

        (model, arPaths) = sel.get_selected_rows();
        for path in arPaths :

            ctree.expand_row(path,True);


    """
        function actualiser : this function refreshes the list of results of a searchlist row.
        it is useful to be able to see the changes made in the edit window.
    """
    def actualiser(self, mylist) :

        global listes  ;

        if self.verify_button(mylist) == False :

            return;

        try :
            name = mylist.get_name();
        except :
            name = mylist
            mylist = self.arw[mylist];


        store = mylist.get_model();
        store.clear();
        self.build_tree(name);
        self.arw[name].show();



    # self.arw['tree_list1'].connect_simple("toggled", "update",'clist1');


    """==============================================================================
    FONCTION   : index_maj
    DESCRIPTION: Met à jour le champ ordre de la table thèmes pour refléter les changements faits dans l'interface
    et assurer qu'ils seront conservés au prochain chargement.
    ==============================================================================
    """


    def index_maj(self, mylist) :


        global link, tab_conversion, config, order_field;

        if self.verify_button(mylist) == False :

            return;

        list_name = mylist.get_name();
        config_name = tab_conversion[list_name];
        table_data = config['xtabs'][config_name];
        table = table_data['table_def'];
        id_type = config['peripheral'][table]['id_type'];
        treeview = self.arw[list_name];

        sel=treeview.get_selection();
        self.tree_expand_all(mylist);
        sel.select_all();
        # expand the tree, in case it is not already expanded.
        num = sel.count_selected_rows();
        (model, arPaths) = sel.get_selected_rows();


        ordre=0;
        for path in arPaths :


            iter = model.get_iter(path);
            id = model.get_value(iter, 20); # theme id


            niveau = len(path) - 1;
            if niveau > 0 :         # if the theme is not at the root
                path=path[:-1]        # remove the final element from the path to get the path of the parent
                iter = model.get_iter(path);
                id_parent = model.get_value(iter, 20);# id of the parent
            else :
                id_parent = "null";

            requete = eval(php_string("update $table set $order_field=$ordre, parent=$id_parent, niveau=$niveau where $id_type = $id"))
            ok=cursor.execute(requete);
            sql_error(link, requete);
            ordre+= 1;

        link.commit()
        self.actualiser(mylist);

    """  couleur du bouton pour rappel enregistrement. Mais le signal sur reorder list ne fonctionne pas,
    et on ne peut pas détecter les changements.
    Donc ce code est gardé en attente de la correction de php-gtk2 sur ce point.

    style_standard=self.arw['recherche1'].get_style();
    texte=self.arw['index_maj'].child;
    texte.set_style(style_standard);
    self.arw['index_maj'].set_style(style_standard);
    """




    # ================================ UPDATE =====================================================


    # TREATMENT OF THE ACTIONS

    """==============================================================================
    FONCTION   :
    DESCRIPTION:

    ==============================================================================
    """



    def item_delete(self, list1) :

        global config, config_info, periph_tables, link, tab_conversion;

        if self.verify_button(list1) == False :

            return;

        list_name = list1.get_name();
        config_list = tab_conversion[list_name];
        list_data = config['xtabs'][config_list];
        config_table = list_data['table_def'];
        table_data = config['peripheral'][config_table];

        table = table_data['table'];
        liste = list_data['treeview'];
        id_type = table_data['id_type'];
        mainfield = table_data['main_field'];
        entry = list_data['entry'];



        sel=self.arw[liste].get_selection();
        # debug: resize was 0. This mechanism does not work. It should make the resize not happen
        (model, arPaths) = sel.get_selected_rows();
        n3=len(arPaths);

        if n3==0 :
            alert(_("No line selected. Aborting"));
            return;

        elif n3>1 :
                message(_("more than one line"));
                return;

        else :

            iter = model.get_iter(arPaths[0]);
            # value first line
            id = model.get_value(iter, 20);




        req = eval(php_string("select $mainfield from $table where $id_type = $id"))
        ok=cursor.execute(req);
        sql_error(link, req);
        #nom=mysql_result(ok,0,0);
        nom = cursor.fetchone()[0]

        question = yes_no_dialog("Voulez-vous vraiment effacer : %s - %s ?" % (table, nom))
        if question == True :


            ok=cursor.execute(eval(php_string("delete from $table where $id_type = $id")))
            link.commit()

            alert(nom + _(" deleted"));

            if config_info['search_lists'][list_name]['type'] == "tree" :

                self.actualiser(list1);

            else :

                self.refresh_list2(config_list);







    def item_update(self, list1) :

        # update command for tree serach lists

        global config, periph_tables, link, tab_conversion;

        if self.verify_button(list1) == False :

            return;

        list_name = list1.get_name();
        config_list = tab_conversion[list_name];
        list_data = config['xtabs'][config_list];
        config_table = list_data['table_def'];
        table_data = config['peripheral'][config_table];


        table = table_data['table'];
        liste = list_data['treeview'];
        id_type = table_data['id_type'];
        mainfield = table_data['main_field'];
        entry = list_data['entry'];
        gateway = table_data['gateway'];
        options = list_data['options'];
        renvoi = get_option("r",options);


        sel = self.arw[liste].get_selection();
        (model, arPaths) = sel.get_selected_rows();
        n3=len(arPaths);

        if n3==0 :

            alert(_("No line selected. Aborting."));
            return;

        elif n3>1 :
            message(_("more than one line"));
            return;
        else :
            iter = model.get_iter(arPaths[0]);      # value first line
            id = model.get_value(iter, 20);         # value of the id


        temp = {}
        len_store = get_store_length(model)
        for ii in range (0, len_store) :

            temp[ii] = model.get_value(iter,ii);





        for z in list_data['cols'] :

            # extract the data fields

            widgetname = z['detail'];
            if len(widgetname) > 0 :

                datafield = z['field'];
                contenu = self.Chaine_guillemets(get_text(self.arw[widgetname]));
                datadef[datafield] = contenu;





        # content of the main field

        nom1 = datadef[mainfield];


        if len(renvoi) > 0 :

            ok=cursor.execute("select mainfield from table where id_type=id");
            ancien_nom=self.Chaine(mysql_result(ok,0));

            if (ancien_nom != nom1) and(ancien_nom != "") :

                # if the name has been changed
                req="select mainfield from table where renvoi like '%ancien_nom%' ";
                cursor.execute(req);
                result = cursor.fetchall()
                sql_error(link,req);
                num = len(result);
                if num>0 :

                    for i in range(0, num) :

                        noms += result[i] + " -";

                    msg = sprintf(_("Warning ! There are %d  cross-reference(s) on %s . See records : \n %s "), num, ancien_nom, noms);
                    alert(msg);




        # different treatment depending on whether the new name is already used or not


        cursor.execute("select id_type from table where mainfield= binary nom1");
        exist = cursor.fetchall()
        if len(exist) > 0 :

            test = exist[0][0]

        if isset(test) and  test!=id and len(gateway) >0  :

            # if the new name exists and if it has been changed
            req = "update gateway set id_type=test where id_type=id";
            # copy the entries from one theme to another
            maj=cursor.execute(req);
            sql_error(link,req);
            req = "delete from table where id_type=id";
            # delete the entries of the old name
            ok=cursor.execute();
            sql_error(link, req);
            alert(table + "." + mainfield + _(" renamed."));


        else :

            # If the name has not changed
            req="update table set ";
            for key  in datadef :
                val = datadef[key ]

                req += key + "=".val + ",";

            # fields and data
            req = substr(req,0,len(req) -1);
            # remove the final comma
            req += " where id_type = id";
            # Update the data in the device table
            ok=cursor.execute(req) ;
            sql_error(link, req);






        if list_data['type'] == "tree" :

            self.actualiser(liste);
            self.collapse(liste,2);

        else :

            self.refresh_list2(list1);




    def item_new(self, list1) :


        global config, periph_tables, tab_conversion, link;

        if self.verify_button(list1) == False :

            return;

        list_name = list1.get_name();
        config_list = tab_conversion[list_name];
        list_data = config['xtabs'][config_list];
        config_table = list_data['table_def'];
        table_data = config['peripheral'][config_table];


        table = table_data['table'];
        liste = list_data['treeview'];
        id_type = table_data['id_type'];
        mainfield = table_data['main_field'];
        entry = list_data['entry'];



        dialog1 = Prompt2A({"Nom à ajouter à la liste :" : ""});
        reponse = dialog1.run()
        nom1 = reponse[0];
        if nom1 != 2 :

            nom1=self.Chaine_guillemets(nom1);
            result=cursor.execute(eval(php_string("select $id_type from $table where $mainfield = $nom1")))
            #if mysql_num_rows(result)==0 :
            if cursor.fetchone() == None :

                # If the new name does not exist yet, we add
                #req=eval(php_string("insert into $table set $mainfield = $name1"))
                req=eval(php_string("insert into $table ($mainfield) values ($nom1)"))
                ok=cursor.execute(req);
                sql_error(link,req);
                link.commit()

            else :

                alert(nom1 + _("exists already !"));



        if list_data['type'] == "tree" :

            self.actualiser(list1);
            self.collapse(liste,2);

        else :

            self.refresh_list2(list1);



    def inverser(self, widget) :

        global config, periph_tables, order_field, link;

        info = self.arw['s_info10'];
        buffer1 = info.get_buffer();
        buffer1.set_text("");
        if not "tempx" in db_structure :
            self.create_tempx()

        # inversion of the peripheral tables

        # list of tables to invert
        todo_a = {}



        for key in config['peripheral'] :
            val = config['peripheral'][key ]

            try :
                table = val['table'];
                id_type = val['id_type'];
                main_field = val['main_field'];
                central_def = val['central_def'];
                if 'linked_field' in val :
                    linked_field = val['linked_field'];
                else :
                    linked_field = None
                id_main = config['central'][central_def]['id_main'];
                central_table = config['central'][central_def]['table'];
                i_data = "i_data_" + central_table;

                gateway = None
                if 'gateway' in val and len(val['gateway'].strip()) > 0 :
                    gateway = val['gateway']


                todo_a["peripheral_" + key] = [table, id_type, main_field, central_def, gateway, linked_field, id_main, central_table, i_data, "" ]
            except :
                insertion_tv(buffer1, _("impossible to invert table ") +  key + "\n")
                utils.printExcept()
                continue

        # end of for key in config['peripheral'] :


        # Inversions defined in the configuration (config.py)
        if 'inversion' in config :
            for key in config['inversion'] :
                val = config['inversion'][key]

                table_def = val['table_def'];
                table = config['peripheral'][table_def]['table'];
                if 'gateway' in periph_tables[table] and len(periph_tables[table]['gateway'].strip()) > 0:
                    gateway = periph_tables[table]['gateway'];
                else :
                    gateway = None
                id_type = periph_tables[table]['id_type'];
                main_field = periph_tables[table]['main_field'];
                if 'linked_field' in periph_tables[table] :
                    linked_field = periph_tables[table]['linked_field'];
                else :
                    linked_field == None
                central_def = periph_tables[table]['central_def'];
                central_table = config['central'][central_def]['table'];
                id_main = config['central'][central_def]['id_main'];
                if 'condition' in val and len(val['condition'].strip()) > 0 :
                    condition = "and " + val['condition'];
                else :

                    condition = "";

                condition = str_replace('"',"'",condition);
                i_data = val['invert_field'];

                todo_a["inversion_" + key] = [table, id_type, main_field, central_def, gateway, linked_field, id_main, central_table, i_data, condition ]

        # End of if config.has_key('inversion') :

        # Execute

        for key in todo_a :
            (table, id_type, main_field, central_def, gateway, linked_field, id_main, central_table, i_data, condition) = todo_a[key]


            # if there is a gateway
            if gateway != None :
                # check the existence of the i_data field and create it if necessary.
                db_utils.is_field(cursor, table, i_data, "TEXT")


                if db_type == "mysql" :
                    req0 = "update $table t set $i_data = ("
                    req0 += " select group_concat(distinct $id_main order by $order_field separator ',')"
                    req0 += " from $gateway g "
                    req0 += " where t.$id_type = g.$id_type "
                    if condition.strip() != "" :
                        req0 += condition
                    req0 += ")"

                elif db_type == "sqlite" :
                    req0 = "update $table set $i_data = ("
                    req0 += " select group_concat(distinct $id_main)"
                    req0 += " from $gateway "
                    req0 += " where $table.$id_type = $gateway.$id_type "
                    if condition.strip() != "" :
                        req0 += condition
                    req0 += ")"

                elif db_type == "accdb" :
                    req0 = "select distinct $id_main, $table.$id_type"
                    req0 += " from $table, $gateway "
                    req0 += " where $table.$id_type = $gateway.$id_type"

                req1 = eval(php_string(req0))
                # TODO order on line 2 of this request. (?)
                print(req1)   # TODO DEBUG


                # display in the TextView
                message = _("Inversion of table ") + table + _("; creating field ") + i_data + "\n"
                insertion_tv(buffer1,message);
                #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87

                while (Gtk.events_pending()) :
                    Gtk.main_iteration();

                t1 = time.time()

                # TODO DEBUG !
                try :
                    result = cursor.execute(req1);
                except :
                    sql_error(link, req1)

                if db_type == "accdb" :     # Access dose not support group_concat, so we must finish the job...

                    data2 = {}
                    data1 = cursor.fetchall()
                    for row in data1 :
                            bookid = str(row[id_main])
                            author = str(row[id_type])
                            if not author in data2 :
                                data2[author] = bookid
                            else :
                                data2[author] += "," + bookid

                    for author in data2 :
                        bookids = data2[author]
                        req2 = "update $table set $i_data = '$bookids' where $id_type = $author"
                        req2 = eval(php_string(req2))
                        try :
                            cursor.execute(req2)
                        except :
                            "Echec pour (55) : ", req2


                t2 = time.time()
                #debug22(t2 - t1)
                link.commit()


                insertion_tv(buffer1,"OK\n")

            # invert tables without gateway

            else :

                # check the existence of the i_data field and create it if necessary.
                db_utils.is_field(cursor, table, i_data, "TEXT")

                if db_type == "mysql" :
                    req1 = """update $table t set $i_data = (
                            select group_concat(distinct $id_main order by $id_main separator ',')
                            from $central_table c
                            where c.$linked_field = t.$id_type
                            group by t.$id_type)""";

                elif db_type == "sqlite" :
                    req1 = """update $table set $i_data = (
                            select group_concat(distinct $id_main)
                            from $central_table
                            where $central_table.$linked_field = $table.$id_type)"""

                elif db_type == "accdb" :
                    req1 = """select $central_table.$id_main, $table.$id_type
                             from $central_table, $table
                             where $central_table.$linked_field = $table.$id_type"""

                req1 = eval(php_string(req1))
                # TODO order at line 2 of this request.

                # display in the TextView
                pos = strpos(req1,"=");
                titre = substr(req1,0,pos);
                message = titre + "\n";
                insertion_tv(buffer1,message);
                #Â£ info.scroll_to_mark(buffer1.get_insert(), 0);

                while (Gtk.events_pending()) :
                    Gtk.main_iteration();
                cursor.execute(req1);
                sql_error(link,req1);

                if db_type == "accdb" :     # access does not support group_concat, so we have to do it ourselves

                    data2 = {}
                    data1 = cursor.fetchall()
                    for row in data1 :
                            bookid = str(row[id_main])
                            author = str(row[id_type])
                            if not author in data2 :
                                data2[author] = bookid
                            else :
                                data2[author] += "," + bookid

                    for author in data2 :
                        bookid = data2[author]
                        req2 = "update $table set $i_data = '$bookid' where $id_type = $author"
                        req2 = eval(php_string(req2))
                        try :
                            cursor.execute(req2)
                        except :
                            "Echec pour (55) : ", req2

                # terminate
                link.commit()

        message =  " =====================================\n\n"
        message += _("End of inversion process")
        message += "\n\n =========================================\n\n"
        insertion_tv(buffer1, message)
        #Â£ info.scroll_to_mark(buffer1.get_insert(), 0)

        #TODO: refresh_all_lists()?


    def create_tempx(self) :

        if db_type == "mysql" :
            cursor.execute("DROP TABLE IF EXISTS tempx")
            req = """CREATE TABLE `tempx` (
                `word` varchar(128) collate utf8_unicode_ci NOT Null,
                `record` int(10) unsigned NOT Null,
                PRIMARY KEY  (`word`,`record`)
                ) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;""";             # TODO mysql: there was: collate collation


        elif db_type == "sqlite" :
            cursor.execute("DROP TABLE IF EXISTS [tempx]")
            req = """CREATE TABLE [tempx] (
                [word] TEXT  NULL,
                [record] TEXT  NULL,
                PRIMARY KEY ([word],[record])
                );"""

        elif db_type == "accdb" :
            req = """CREATE TABLE [tempx] (
                   [word] TEXT (50),
                   [record] INTEGER
                ) """

        try :
            cursor.execute(req)
        except :
            utils.printExcept()


    def invert_words(self, widget) :


        global config, order_field, link;

        info = self.arw['s_info10']
        buffer1 = info.get_buffer();
        #buffer1.set_text("");

        # Prepare tables
        if not "tempx" in db_structure :
            self.create_tempx()




            # TODO: mysql

## req1 = "ATTACH DATABASE ':memory:' as inmemory"
## cursor_execute(cursor,req1)
## print req1
## conn = sqlite.connect(":memory:")
## self.cursor2 = conn.cursor()

## if db_type == "sqlite" :
## cursor.execute(sqlite_req)
## elif db_type == "accdb":
## cursor.execute(access_req)
## link.commit()

        # first delete the temp table
        # mysql cursor.execute("truncate words_table");
        for key  in config['words'] :
            val = config['words'][key ]
            words_table = val['table'];
            cursor.execute("delete from " + words_table )

        cursor.execute("delete from tempx")
        sql_error(link, "");


        # perform inversion

        for key  in config['words'] :           # For each defined inversion
            val = config['words'][key ]         # get info from config file

            words_table = val['table'];
            id_type = val['id_type'];
            word_field = val['main_field'];
            central_def = val['central_def'];
            fields = val['fields'];



            # update and invert the words table
            arI_data = []
            for key in fields :
                val = fields[key]
                self.invert_words2(val['field'],info,words_table, central_def, word_field, id_type);
                arI_data.append("i_" + val['field'])

            link.commit()

        # create i_data field

        insertion_tv(buffer1,_("Global field creation\n"))          # display
        #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87
        while (Gtk.events_pending()) :
            Gtk.main_iteration();


        i_global = "i_data_" + config['central'][central_def]['table'];
        #checking the existence / creation of the field :
        db_utils.is_field(cursor, words_table, i_global, "TEXT")


        i_data = implode(",",arI_data)

        if db_type == "sqlite" or db_type == "mysql" :
            req = "update $words_table set $i_global = concat_ws(',', $i_data)"
        elif  db_type == "accdb" :
            # TODO: This will work ONLY if there is a single element
            req = "update $words_table set $i_global = $i_data";


        req = eval(php_string(req))
        result = cursor.execute(req);
        sql_error(link,req);
        link.commit()


        # delete records that do not return anything
        insertion_tv(buffer1,"Deletion of empty records\n");            # display
        #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87
        while (Gtk.events_pending()) :
            Gtk.main_iteration();


        where = implode(" is null and ", arI_data);

        requete = "select * from $words_table where $where  is null"
        requete = eval(php_string(requete))
        cursor.execute(requete);
        sql_error(link,requete);
        data1 = cursor.fetchall()


        for fiche in data1 :

            requete2 = "delete from $words_table where $id_type = " + str(fiche[0]) ;
            requete2 = eval(php_string(requete2))
            ok2=cursor.execute(requete2);



        cursor.execute("delete from tempx")

        link.commit()

        message =  " =====================================\n\n"
        message += _("End of inversion process") + "\n"
        if db_type == "sqlite" :
            message += _("Now compressing database") + "\n"
            insertion_tv(buffer1,message);
            #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87
            while (Gtk.events_pending()) :
                Gtk.main_iteration();
            cursor.execute("VACUUM")
            message = "\n"

        message += _("Process terminated")
        message += "\n\n =========================================\n\n"
        insertion_tv(buffer1,message);





    def invert_all(self, widget) :

        self.inverser("");
        self.maj_table_centrale("");
        self.invert_words("");

    def clean_inverted_tables(self, widget) :
        # TODO : make generic
        for table in ["concerne", "sujet", "maison", "serie", "parle"] :
            req = "delete from " + table + " where id_livre not in (select id_livre from complete)"
            cursor.execute(req)
            link.commit()

    def invert_words2(self, champ, info, words_table, central_def, word_field, id_type) :

        buffer1 = info.get_buffer()

        message = _("Inversion of words tables started\n")
        insertion_tv(buffer1,message);
        #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87
        while (Gtk.events_pending()) :
            Gtk.main_iteration();

        if db_type == "accdb" :
                champ = champ.lower()
        self.create_tempx()
        mots_vides = []   # TODO: load list of empty words
        mots = []

        main_field = config['central'][central_def]['id_main'];
        central_table = config['central'][central_def]['table'];


        # load the data of the complete table
        requete2 = "select $main_field, $champ from $central_table ";
        requete2 = eval(php_string(requete2))
        cursor.execute(requete2);


        # loop over all the records
        for fiche in cursor :

            contenu=fiche[champ];
            if contenu == None :
                continue

            # delete the 3 bytes characters which are not well treated by mbstring
            contenu = str_replace(["…","†","–"], [" ", " ", " "], contenu);
            # replace the Å“ Å’ characters that the user will not be able to type
            contenu = str_replace(["œ","Œ","æ","Æ"], ["oe","oe","ae","ae"], contenu);
            # put everything in lower case because the system is case sensitive
            contenu=contenu.lower()


            contenu =unicode2(contenu)
            ex1 = re.findall("(?u)\w+",contenu);   # division into words

            # delete duplicates
            ex=array_unique(ex1);

            for k in range(len(ex)) :
              try :
                # if the word is not in the list of empty words
                if (not ex[k] in mots_vides) and (len(ex[k])>1) :
                    mot1 = ex[k]
                    mots.append("('" + mot1 + "'," + str(fiche[main_field]) + ")");
              except :
                print("======>", len(mots), repr(contenu), repr(ex1), repr(ex[k]))


        count = len(mots);
        message = _("array created for") + " " + champ + " ---  " +  str(count) + " " + _("words")
        insertion_tv(buffer1,message);
        #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87
        while (Gtk.events_pending()) :
            Gtk.main_iteration();



        #f1=fopen("c:/temp2/mots.tmp","w");

## for key in mots :
## val = words[key ]
## fputs(f1,val . chr(10));

        #fclose(f1);

        #cursor.execute("delete from tempx");
        #cursor.execute("SET SESSION max_allowed_packet=16*1024*1024");

        #req="load data infile 'c:/temp2/mots.tmp' ignore into table tempx";
        # cursor.execute(req);

        # TODO : this is OK for mysql
## ar_data = array_chunk(words,10000);
##
## for data in ar_data :
##
##
## mysql_query = "insert ignore into tempx VALUES ";
## data2 = implode(",", data);
## mysql_query += data2
## sqlite_query += data2
##
## cursor_execute(self.cursor2, sqlite_query, mysql_query)

        #cursor.execute("delete from tempx")

        if db_type == "mysql" :
            # Divide the list in 1000 items lists

            for i in range (0, len(mots), 1000) :
                mots2 = mots[i:i + 1000]
                data = ",".join(mots2)
                req1 = "insert ignore into tempx VALUES "
                req1 += data

        else :
            if db_type == "sqlite" :
                req1 = "insert or ignore into tempx VALUES ";
            elif db_type == "accdb" :
                req1 = "insert into tempx VALUES ";

            for data in mots :
                req2 = req1 + data
                cursor.execute(req2)


        link.commit()
        message = " --- " + _("data loaded") + " "
        insertion_tv(buffer1,message);
        #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87
        while (Gtk.events_pending()) :

            Gtk.main_iteration();


        i_field = "i_" + champ;

        #checking the existence / creation of the field :
        db_utils.is_field(cursor, words_table, i_field, "TEXT")


        # insert in words table the words which are not yet present
        req2 = """insert into $words_table ($word_field)
                select distinct word from tempx
                where tempx.word not in (select $word_field from $words_table)"""
        req2 = eval(php_string(req2))
        cursor.execute(req2)
        link.commit()


        if db_type == "mysql" :
            req3 = """update $words_table set $i_field = (
                select group_concat(distinct record separator ',')
                from tempx
                where $words_table.$word_field = tempx.word)""";

        if db_type == "sqlite" :
            req3 = "update $words_table set $i_field = (select group_concat(distinct record ) from tempx where $words_table.$word_field = tempx.word)"

        elif db_type == "accdb" :
            req3 = "select distinct record from $words_table, tempx where $words_table.$word_field = tempx.word"

        req3 = eval(php_string(req3))
        cursor.execute(req3);
        sql_error(link,req3);



        if db_type == "accdb" :     # access does not support group_concat, so we have to do it ourselves

            req = "select $word_field from $words_table"
            req = eval(php_string(req))
            cursor.execute(req)
            words_list = cursor.fetchall()

            for row in words_list :
                word1 = row[0]
                req = "select record from tempx where word like '" + word1 + "'"
                cursor.execute(req)
                row = cursor.fetchone()
                data2 = str(row["record"])
                data1 = cursor.fetchall()
                for row in data1 :
                    record = str(row["record"])
                    data2 += ", " + str(record)



                req2 = "update $words_table set $i_field = '$data2' where $word_field like '$word1'"
                req2 = eval(php_string(req2))
                try :
                   cursor.execute(req2)
                except :
                   "Echec pour (55) : ", req2

        # Terminate
        link.commit()

        message = " --- " + _("Ended\n")
        insertion_tv(buffer1,message);
        #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87
        while (Gtk.events_pending()) :
            Gtk.main_iteration();



    def maj_table_centrale(self, widget) :

        global config, config_info, order_field, periph_tables2, link

        def verif(dict1, field1) :
            if not field1 in dict1 :
                #print "field %s not found in dictionary 'inversion'" % field1
                return None
            else :
                return dict1[field1]

        info = self.arw['s_info10'];
        buffer1 = info.get_buffer();
        try :
            separator = config['ini']['output']['field_separator']
        except :
            separator = "; "

        todo_a = {}

        # create standard generated fields for peripheral tables with or without gateway


        for key  in periph_tables2 :
            val = periph_tables2[key ]


            try :
                table = verif(val, "table");
                gateway = verif(val,'gateway');
                id_type = verif(val,'id_type');
                name = verif(val,'main_field');
                central_def = verif(val,'central_def');
                linked_field = verif(val,'linked_field');
                main_field = verif(config['central'][central_def],'id_main');
                central_table = verif(config['central'][central_def], 'table');
                fieldname = "g_" + table
                content = table + "." + name
                condition = ""

                todo_a ["standard_" + key] = [table, gateway, id_type, name, central_def, linked_field, main_field, central_table, condition, fieldname, content]

            except :
                insertion_tv(buffer1,"impossible to update " + key + "\n")
                #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87
                #print config['central'][central_def]
                continue

        # create generated fields defined in the [inversion] section of config.php
        # TODO : security if a field is missing
        temp =list(periph_tables.keys());

        if 'inversion' in config :
            for key in config['inversion'] :
                val = config['inversion'][key]

                try :
                    table_data = config['peripheral'][val['table_def']];
                    table = table_data['table'];
                    condition = val['condition'];



                    if 'gateway' in table_data and len(table_data['gateway'].strip()) > 0 :
                        gateway = table_data['gateway']
                    else :
                        gateway = None
                    id_type = table_data['id_type'];
                    name = table_data['main_field'];
                    central_def = table_data['central_def'];
                    if 'linked_field' in table_data and len(table_data['linked_field'].strip()) > 0 :
                        linked_field = table_data['linked_field']
                    else :
                        linked_field = None
                    main_field = config['central'][central_def]['id_main'];
                    central_table = config['central'][central_def]['table'];

                    if 'central_field' in val and len(val['central_field'].strip()) > 0 :
                        fieldname = val['central_field'];
                    else :
                        fieldname = "g_table" + "_" + element;


                    if 'content' in val and len(val['content'].strip()) > 0 :
                        content = val['content'];
                    else :
                        content = table + "." + name

                    todo_a ["inversion_" + key] = [table, gateway, id_type, name, central_def, linked_field, main_field, central_table, condition, fieldname, content]

                except :
                    insertion_tv(buffer1,"impossible to update " + key + "\n")
                    #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87
                    #print config['central'][central_def]
                    continue


        for key in todo_a :

            t1 = time.time()
            (table, gateway, id_type, name, central_def, linked_field, main_field, central_table, condition, fieldname, content) = todo_a[key]


            if gateway != None :            # tables with gateway

                # check presence of field
                db_utils.is_field(cursor, central_table, "g_" + table, "TEXT")


                if main_field == None :
                    insertion_tv(buffer1,_("main field not present"))
                    #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87
                    continue

                if db_type == "mysql" :

                    req1 = """update $central_table set $fieldname = (
                        select group_concat(distinct $content order by $gateway.$order_field separator '$separator' )
                        from $table
                        left join $gateway on ($table.$id_type=$gateway.$id_type)
                        where $central_table.$main_field=$gateway.$main_field"""
                    if condition != "" :
                        req1 += " and $condition "
                    req1 += ")"

                else :

                    req1 = "update $central_table set $fieldname = ("
                    req1 += "select group_concat($content, '$separator') from $table "           # TODO: there was a separate $content, but not supported as is by sqlite
                    req1 += "join $gateway on ($table.$id_type=$gateway.$id_type) "
                    req1 += "where $central_table.$main_field = $gateway.$main_field "
                    if condition != "" :
                        req1 += " and $condition "
                    req1 += ")"


            else :      # table without gateway

                # check presence of field
                if db_type == "accdb" :
                    # Search the field type
                    req1 = "select " + name + " from " + table
                    cursor.execute(req1)            # TODO handle error
                    temp = cursor.description
                    a = cursor.description[0]
                    if a[1] == str or a[1] == str :
                        if a[2] < 255 :
                            type_s = "TEXT (" + str(a[2]) + ")"
                        else :
                            type_s = "MEMO"
                    elif a[1] == int :
                        type_s = "INTEGER"
                    elif a[1] == float :
                        type_s = 'FLOAT'
                    elif a[1] == bool :
                        type_s = "YESNO"
                    elif a[1] == datetime.datetime :
                        type_s = "DATETIME"
                    else :
                        type_s = "MEMO"

                    db_utils.is_field(cursor, central_table, fieldname, type_s)


                if linked_field == None :
                    print(_("linked field not present for ") + key)   # TODO: specify messaging
                    continue
                req1 = "update $central_table set $fieldname = ("
                req1 += "select $name from $table "
                req1 += "where $central_table.$linked_field = $table.$id_type)"

            req2 = eval(php_string(req1))


            message = _("updating field ") + central_table + "." + fieldname
            insertion_tv(buffer1,message);
            #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87

            while (Gtk.events_pending()) :

                Gtk.main_iteration();


            if db_type != "accdb" :
                try :
                    result = cursor.execute(req2)
                except :
                    print("Error for : ", req2)
                    utils.printExcept()
                link.commit()

            else :          # ##### ACCESS ##############
                            # Access does not have the function group_concat, and complains for a simple nested select.So we do the job for it

                if gateway != None :

                    if main_field == None :
                        insertion_tv(buffer1,_("main field not present"))
                        #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87
                        continue

                    req1 = "select distinct $content from $table "
                    req1 += "join $gateway on ($table.$id_type=$gateway.$id_type) "
                    req1 += "where $central_table.$main_field = $gateway.$main_field ";
                    req1 = eval(php_string(req1))


## req1 = "update $central_table set g_$table = ("
## req1 += "select group_concat(distinct $table.$name) from $table "
## req1 += "join $gateway on ($table.$id_type=$gateway.$id_type) "
## req1 += "where $central_table.$main_field = $gateway.$main_field )"


                else :      # table without gateway

                    if linked_field == None or linked_field.strip() == "":
                        print(_("linked field not present"))   # TODO: specify messaging
                        continue
                    req1 = "select $content as content, $central_table.$main_field from $table, $central_table "
                    req1 += "where $central_table.$linked_field = $table.$id_type"
                    req1 = eval(php_string(req1))

                    cursor.execute(req1)

                    data1 = cursor.fetchall()
                    for row in data1 :
                        bookid = row[main_field]
                        content_s = row["content"]
                        if content_s :
                            content_s = content_s.replace("'", "''")          # escape the quotes
                        req2 = "update $central_table set $fieldname = '$content_s' where $main_field = $bookid"
                        req2 = eval(php_string(req2))
                        cursor.execute(req2)

                    link.commit()



            t2 = time.time()
            insertion_tv(buffer1," -  " + _("duration") + " : " + str(int(t2 - t1)) + " " + _("seconds") + "\n")
            #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87



            """
            message = mysql_info(link) + "\n";
            if len(message) > 0 :
                insertion_tv(buffer1,message);
            """


##        # create generated fields defined in the [inversion] section of config.php
##        # TODO : security if a field is missing
## temp =periph_tables.keys();
##
## if 'inversion' in config :
## for key in config['inversion'] :
## val = config['inversion'][key]
##
## table_data = config['peripheral'][val['table_def']];
## table = table_data['table'];
## condition = val['condition'];
##
##
## gateway = table_data['gateway'];
## if gateway.strip() == "" : # TODO : nothing for simple relations
## continue
## id_type = table_data['id_type'];
## name = table_data['main_field'];
##
## central_def = table_data['central_def'];
## main_field = config['central'][central_def]['id_main'];
## central_table = config['central'][central_def]['table'];
##
## if len(val['central_field'].strip()) > 0 :
## fieldname = val['central_field'];
## else :
##
## fieldname = "g_table" + "_" + element;
##
##
## if len(val['content'].strip()) > 0 :
## content = val['content'];
## else :
##
## content = "$table.$name";


## MySQL version
## req1 = """update central_table set fieldname = (
## select group_concat(distinct content order by gateway.order_field separator ' separator ' )
## from table
## left join gateway on (table.id_type=gateway.id_type)
## where central_table.main_field=gateway.main_field
## and condition)""";

## req1 = "update $central_table set $fieldname = ("
## req1 += "select group_concat(distinct " + content + ") from $table "
## req1 += "join $gateway on ($table.$id_type=$gateway.$id_type) "
## req1 += "where $central_table.$main_field = $gateway.$main_field "
## req1 += "and $condition)"
## req1 = eval(php_string(req1))
##
## pos = strpos(req1,"=");
## title = substr(req1,0,pos);
## insert_tv(buffer1,title)
## info.scroll_to_mark(buffer1.get_insert(), 0);   # Kksou 87
##
## while (Gtk.events_pending()) :
## Gtk.main_iteration();
##
##
##
## t1 = time.time()
## try :
## result = cursor.execute(req1)
## except:
## print "====> Failed for: ", req1
## t2 = time.time()
## insert_tv(buffer1, " - time: " + str(int(t2 - t1)) + "seconds")
## info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87
## link.commit()
## message = mysql_info(link) + "\n";
## if len(message) > 0 :
##
## insert_tv(buffer1,message);
##
## info.scroll_to_mark(buffer1.get_insert(), 0);
## # Kksou 87
        message =  " =====================================\n\n"
        message += _("End of Central table update")
        message += "\n\n =========================================\n\n"


        insertion_tv(buffer1, message)
        #Â£ info.scroll_to_mark(buffer1.get_insert(), 0); # Kksou 87


    def importx() :
        # unused. Probably a first try, unfinished


        global config, central_table, periph_tables, order_field, link;

        for val in config['import'] :


            central_def = val['central_def'];
            periph_def = val['periph_def'];
            central = config['central'][central_def]['table'];
            id_central = config['central'][central_def]['id_main'];
            periph = config['peripheral'][periph_def]['table'];
            field = config['peripheral'][periph_def]['main_field'];
            id_periph = config['peripheral'][periph_def]['id_type'];
            gateway = config['peripheral'][periph_def]['gateway'];

            req = "insert ignore into periph (field) select distinct field from central";
            ok=cursor.execute(req);
            sql_error(link,req);


            req2 = """insert ignore into gateway (id_central,id_periph)
                    select c.id_central, p.id_periph
                    from central c ,periph p
                    where c.field = p.field """;
            ok=cursor.execute(req);
            sql_error(link,req);


    def choisir_affichage(self, display = None, details = None) :
        # this important function updates the "display" dictionary
        # which will be used to know what are the parameters for the active page
        # to use to display the data (affichage = display in French)
        # TODO : this function could be improved.
        global affichage, tris_predefinis, config, d_from, mem, alias;

        temp0 = []
        temp1 = []
        temp2 = []
        temp4 = []
        temp5 = []
        alias = {}


        page = mem['result_page'];
        v2(affichage,page)
        affichage[page][0] = display;
        columns = config['result'][display]['cols'];
        tris_predefinis = config['result'][display]['sort'];

        # TODO : this programming could be improved. What will happen if a parameter is missing ? the lists will not be coherent
        for key in columns :
            z = columns[key]
            if 'field' in z :
                temp0.append(z['field'])
            if 'width' in z :
                temp1.append(z['width'])
            if 'visible' in z :
                temp2.append(z['visible'])
            if 'options' in z :
                temp4.append(z['options'])
            if 'title' in z :
                temp5.append(z['title'])

        affichage[page]['select'] = implode(",", temp0)
        if config['result'][display]['from'] == "<etoile>" :
            affichage[page]['from'] = d_from;
        else :
            affichage[page]['from'] = config['result'][display]['from'];

        affichage[page]['width'] = temp1;
        affichage[page]['visible'] = temp2;
        affichage[page]['options'] = temp4;
        affichage[page]['title'] = temp5;
        affichage[page]['db_active'] = (link, cursor, db_structure, db_active_file)

        for i in range(0,10) :
            mem['config_liste'][i]=0;

        # set result list and details

        affichage[page]['details'] = config['details'][details];
        affichage[page]['details_def']=details.strip()
        affichage[page]['details_tab'] = config['details'][details.strip()]['details_tab']
        affichage[page]['result_def']=display.strip()


        # sort menu
        if isset(self.arw['s_sort_button']) :

            menu = Gtk.Menu();
            if isset(tris_predefinis) :

                for key  in tris_predefinis :
                    val = tris_predefinis[key ]
                    if val :
                        item = Gtk.MenuItem(val['name']);
                        item.connect("activate", self.trie_liste, val);
                        menu.add(item)



            self.arw['s_sort_button'].set_menu(menu);
            menu.show_all();


        # list of aliases
        for key in range(0, len(temp5)) :
            val = temp5[key]
            if len(val) > 0 :
                alias[val.strip()] = temp0[key].strip()





    #def verify_button : check that the parameter is a TreeView to avoid crashing the program:
    def verify_button(self, liste) :



        if widget_type(liste) != 'GtkTreeView' :

            alert(_("Your button is misconfigured, \nyou must select a list as parameter."));
            return False;

        else :

            return True;



"""


    # ==============================================================================
    # Unused.
    def cree_liste2(liste) :

        global , config, mem, listes, preview_req, style_exclure, statistiques,
        c_colonnes, tab_conversion, config, periph_tables, checkbox_list, link;


        list_name = liste.get_name();
        list_def = tab_conversion[list_name];
        list_data  = config['xtabs'][list_def];
        table_data = periph_tables[list_data['table_def']];

        table = table_data['table'];
        mainfield = table_data['id_main'];
        ids = get_sel_row_data(liste,0,21);

        for (k = 0; k < 30; k+= 1)

            xxx[k] = get_sel_row_data(liste,0,k);



        limite=config['ini']['lists']["max_lines"];
        if limite < 1 :

            limite = 100;

        req="select * from table where mainfield in (ids) order by mainfield limit limite";


        ok=cursor.execute(req);
        sql_error(link,req);
        num=mysql_num_rows(ok);


        # tab = tab_conversion[list];
        # table_data = config['xtabs'][tab];
        # table data
        # primary_key = periph_tables[from]['id_type'];
        # name of the primary field

        # coldef = table_data['cols'];

        treeview =self.arw['treeview_test'];
        model = treeview.get_model();
        model.clear();
        coldef = array("numfoudre","produit");


        for (i=0; i<num; i+= 1)

            fiche=cursor.fetchone()
            values = array();
            values = array_pad(values,36,"");


            for key  in coldef :
     val = coldef[key ]

                #field = val['field'];
                field = val;
                values[key] = fiche[field];


            model.append(values);
            # avoid the slower append(list,values) function




    """

class edit() :


    def fermer_saisie(self, widget) :

        self.verifier_modification()
        self.montrer ('window2',1)



    def effacer_ligne(self,liste, key) :

        n=key.keyval
        if n==65535 :       # touche Suppr
            x=iter_sel(liste,True)
            if isset(x) == False :
                alert (_("Nothing selected."))
            else :
                store = liste.get_model()
                store.remove(x)


    def open_zoom(self, widget, event = None) :
    # for CTRL + z; but you would have to reconnect key-press-event
        #if (($event->keyval==Gdk::KEY_z or $event->type==Gdk::KEY_Z)
        # and $event->state == 4)
        if event == None or event.button == 1 :

            zoom = zoomx(widget)
            return True




    # function that expands or collapses a branch of the theme tree in the input interface

    def arbre2(self, widget,event)   :
        global central_table, main_field

        if event.type==gdk._2BUTTON_PRESS :

            # action on double click



            sel=widget.get_selection()
            (model, arPaths) = sel.get_selected_rows()
            for  path in arPaths  :

                widget.expand_row(path,True)



    """=================================================================================================
    FONCTION   : load_fiche
    DESCRIPTION: rrésidu d'une fonction qui servait à calculer l'id_fiche de la fiche à charger
    quand on fait un appel à partir de la liste des fiches à éditer
    Sert maintenant seulement à mettre en global les variables
    PARAMETRES : $liste_fiches -> liste des fiches à éditer
    $active -> numéro de la fiche dans cette liste
    RETOURNE :   rien
    ==================================================================================================
    """


    def load_fiche(self, liste_fiches,active,table_config = None)  :
        global w4_ids, w4_index, mem, affichage, config

        w4_ids=liste_fiches
        w4_index=active

        if not isset(table_config) :
            page = mem['result_page']
            table_config = affichage[page]['central_def']


        self.load_fiche2(liste_fiches[active], table_config)






    """=================================================================================================
    FONCTION   : load_fiche2
    DESCRIPTION: charge une fiche dans l'interface de saisie
    PARAMETRES : $id_livre -> fiche à charger
    RETOURNE :   rien
    ==================================================================================================
    """
    def load_fiche2(self, id_fiche, table_config = None)  :
        global central_table, main_field, order_field, config, periph_tables
        global add, mem, stores, link, affichage, saisieActive, saisieFlipActive

        if isset(table_config) :
            mem['saisie_table_config'] = table_config

        else :
            table_config = mem['saisie_table_config']


        table_data = config['central'][table_config]
        saisieActive = self.arSaisie[table_data['edit']]
        saisieFlipActive = self.arSaisieFlip[table_data['edit']]
        central_table = table_data['table']
        main_field = table_data['id_main']
        t_periph_tables = list((periph_tables).keys())    # list of peripheral tables


        req="select * from " + central_table + " where " + main_field + "=" + str(id_fiche)
        cursor.execute(req)
        sql_error(link, req)
        fiche=cursor.fetchone()


        for  z  in saisieActive  :
            val = saisieActive [ z ]
            if widget_type(self.arw[z]) == "GtkTreeView" :

                # with gateway (n:n)
                # load peripheral tables

                treeview = val[0]
                periph_config = val[1]
                data = periph_tables2[periph_config]

                table = data['table']
                gateway = data['gateway']
                id_type = data['id_type']
                field = data['main_field']

                req = "select $table.$field, $gateway.* from $gateway,$table where $main_field=$id_fiche "
                req += " and $gateway.$id_type=$table.$id_type order by $gateway.$order_field"
                req = eval(php_string(req))

                cursor.execute(req)
                sql_error(link, req)

                if isset(stores[table]) :
                    i = 0
                    stores[table].clear()
                    while True :

                        values= {}
                        fiches=cursor.fetchone()
                        if not fiches :
                            break
                        # essential data: primary key and name
                        values[0] = fiches[id_type]
                        values[1] = fiches[field]
                        # additional data

                        if table in self.additional_data :
                            j = 2
                            for  val2 in self.additional_data[table]  :
                                field2 = val2['field']
                                values[j] = fiches[field2]
                                j+= 1

                        append(stores[table],values)
                        i+= 1

                else :
                    message = (_("There is a problem with the object which corresponds to the table %s \n which does not seem to exist. Verify your configuration or your glade file \n or your database.") % (table))
                    alert(message)



            else : # peripheral table without gateway (1:n)
                if val[1] in t_periph_tables :
                    table = val[1]
                    id_type = periph_tables[table]['id_type']
                    field = periph_tables[table]['main_field']
                    linked_field = periph_tables[table]['linked_field']
                    if linked_field.strip() != "" and linked_field in list(fiche.keys()) :
                        try :                                   # 0.9 compatibility
                            value1 = int(fiche[linked_field])
                            req = "select " + field + " from " + val[1] + " where " + id_type + " = " + str(value1)
                            cursor.execute(req)
                            sql_error(link, req)
                            result = cursor.fetchone()
                            data2 = result[0]

                        except :
                            data2 = fiche[linked_field]            # 0.9 compatibility
                    else :
                        data2 = ""

                    set_text(self.arw[z],data2)

                else :
                    if val[1] in list(fiche.keys()) :
                        set_text(self.arw[z],fiche[val[1]])
                    else :
                        alert (_("Field " + val[1] + " not found in " + central_table ))


# # window title
# # TODO 1 : not good, make it configurable
## title_window=window["section"]+""+window["num"]+""+window["superscript"]+""+window["format"]
## title_fenetre+=""+mb_substr(card["author"],0,30)+""+mb_substr(card["title"],0,70) # $mem['window4']=$title_fenetre;
# # $self.arw['window4']->set_title($title_fenetre);

        if hasattr(mag.myfunctions, "after_load") :
            try:
                mag.myfunctions.after_load(id_fiche, table_config, saisieActive, saisieFlipActive)
            except:                               # TODO : this does not work, alert message is not shown
                error_text =  utils.printExcept()
                alert("Error in function after_load in your userfunctions.py file\n" + error_text)



        # store data for recall recording
        mem["saisie_avant"] = self.memoriser_fiche()




    """=================================================================================================
    FONCTION   : nouv_fiche
    DESCRIPTION: crée une nouvelle fiche soit vide soit par copie d'une fiche existante
    PARAMETRES : $bouton -> inutilisé
    $action -> si "nouvelle", la fiche créée est vide, sinon on fait une copie de la fiche existante
    RETOURNE :   rien
    ==================================================================================================
    """
    def nouv_fiche(self, bouton,action = "nouvelle")  :

        global central_table, main_field, saisieFlipActive, link, config, mem

        self.montrer('window4')
        # If the user starts directly with a new record, use the first central definition
        if central_table == None :
            if count(config["central"]) == 1 :
                temp = list(config["central"].keys())
                central_table = config["central"][temp[0]]["table"]
                main_field = config["central"][temp[0]]["id_main"]
                mem['saisie_table_config'] = temp[0]
        self.verifier_modification()

        try :
            req = eval(php_string("select max($main_field) from $central_table"))
            cursor.execute(req)
            sql_error(link, req)
        except :
            sql_error(link, req)
            return
        result = cursor.fetchone()
        nouvelle = result[0]
        nouvelle = str(int(nouvelle) + 1)

        if  action == "nouvelle" :
        #a little trick to simplify the code: create an empty record, load it, delete it.
            cursor.execute(eval(php_string("insert into $central_table ($main_field) values ($nouvelle)")))
            mag.load_fiche2(nouvelle)      # load this empty record, which is the easiest way to delete all the fields
            cursor.execute(eval(php_string("delete from $central_table where $main_field = $nouvelle")))



        else :
            widget = saisieFlipActive[main_field]
            self.arw[widget].set_text(nouvelle)  # Duplicate: we simply keep the fields and put the new $main_field
            mem['saisie_avant'] = {}                               # reset the comparison array, since the form is new
            self.memoriser_fiche()


    def dupliquer(self, *params)  :
        self.nouv_fiche("","duplicate")

    """=================================================================================================
    FONCTION   : saisie_suivante
    DESCRIPTION: charge la fiche suivante dans l'interface de saisie
    PARAMETRES : aucun
    RETOURNE :   rien
    ==================================================================================================
    """
    def saisie_suivante(self, widget)  :
        global central_table, main_field, w4_ids, w4_index

        self.verifier_modification()
        w4_index=w4_index+1
        if w4_index < len(w4_ids) :
            fiche=w4_ids[w4_index]
            self.load_fiche2(fiche)

        else : w4_index=w4_index-1



    """=================================================================================================
    FONCTION   : saisie_precedente
    DESCRIPTION: charge la fiche précédente dans l'interface de saisie
    PARAMETRES : aucun
    RETOURNE :   rien
    ==================================================================================================
    """
    def saisie_precedente(self, widget)  :
        global central_table, main_field, w4_ids, w4_index

        self.verifier_modification()
        w4_index=w4_index-1
        if w4_index >= 0 :
            fiche=w4_ids[w4_index]
            self.load_fiche2(fiche)

        else : w4_index=w4_index+1





    #=================================================================================================
    #FUNCTION: store_file
    #DESCRIPTION: lit les données de l'interface de saisie. Utilisée pour vérifier s'il y a eu modification
    #PARAMETERS: complete: if True, records literal data from peripheral tables,
    # used to export data
    #RETURN: $array of field contents
    #==================================================================================================

    def memoriser_fiche(self, complet = False)   :
        global central_table, main_field, saisieActive, stores

        out = {}
        for  key  in saisieActive  :
            val = saisieActive [ key ]

            if val[2] in ["GtkEntry", "GtkTextView", "GtkComboBoxEntry", "GtkComboBox"] :
                out[key] = get_text(self.arw[key])

            elif val[2] == "GtkTreeView" :
                out[key]=""
                store = self.arw[key].get_model()
                if isset(store) :
                    len_store = get_store_length(store)
                    temp =[]

## if complete == False :
                for row in store :
                    temp2 = []
                    for data1 in row :
                        temp2.append(data1)

                    temp.append(repr(temp2))
                out[key] = temp
## else :
## table = active input[key][1]
## if table in periph_tables:
## id_type = periph_tables[table]['id_type']
## mainfield = periph_tables[table]['main_field']

## get additional data in the gateway
## if "gateway_fields" in periph_tables[table] :
## gateway_fields = periph_tables[table]["gateway_fields"]

## print " dddddddebug"
## for row in store:
## for i in range(len_store):
## if row[i] != "" :
## print "---", row[i]
## temp_row = []
## id1 = row[0]
## req = eval(php_string("select $mainfield from $table where $id_type = $id1"))
## cursor.execute(req)
## #temp_row.append(cursor.fetchone()[0])
## print " ===", cursor.fetchone()[0], row[1]
##
## additional fields in gateway
## #for field1 in gateway_fields :



## out[key] = temp

        return out


    def save_record(self, *args) :
        if not 'save_record' in mem :
            mem['save_record'] = []

        data1 = self.memoriser_fiche(True)
        mem['save_record'].append(data1)


    def save_all_records(self, *args) :
        global central_table, main_field, w4_ids, w4_index

        if not 'save_record' in mem :
            mem['save_record'] = []

        w4_index = 0                    # load first record
        fiche=w4_ids[w4_index]
        self.load_fiche2(fiche)

        mem_index = w4_index
        while True :                    # loop on all records
            data1 = self.memoriser_fiche(True)
            mem['save_record'].append(data1)
            self.saisie_suivante("")
            if mem_index == w4_index :
                break
            mem_index = w4_index

        alert(str(mem_index + 1) + _(" records added in memory"))


    def paste_record(self, *args)   :
        global central_table, main_field, saisieActive, stores

        if not 'save_record' in mem :
            mem['save_record'] = []
        if len(mem["save_record"]) > 0 :
            fiche = mem["save_record"].pop(0)
        else :
            alert(_("no more records in list"))
            return False

        self.nouv_fiche("")

        for  key  in saisieActive  :
            val = saisieActive [ key ]

            if val[1] == main_field :       # the main field (primary key) cannot be changed
                continue

            if val[2] in ("GtkTextView", "GtkEntry") :
                if key in fiche :
                    set_text(self.arw[key], fiche[key])

            elif val[2] == "GtkTreeView" :
                if key in fiche :
                    store = self.arw[key].get_model()
                    if isset(store) :
                        len_store = get_store_length(store)
                        store.clear()

                        for line1 in fiche[key] :
                            data1 = eval(line1)
                            additional = []
                            if len(data1) < 2 :
                                continue
                            item = data1[1]
                            if len(data1) > 2 :
                                additional = data1[2:]


                            table = saisieActive[key][1]
                            id_type = periph_tables[table]['id_type']
                            mainfield = periph_tables[table]['main_field']
                            item2 = self.Chaine_guillemets(item)        # escape ' in chains
                            req = eval(php_string("select $id_type from $table where $mainfield like $item2"))
                            cursor.execute(req)
                            row = cursor.fetchone()
                            if row :
                                temp = [row[0]]
                            else :
                                # TODO: what if the id is not found (new author...)?
                                req = eval(php_string("select $mainfield from $table where $id_type = " + data1[0]))
                                cursor.execute(req)
                                t1 = cursor.fetchone()[0]
                                message =_("Original name : %s\n Present name : %s \n\nAccept ?") % (item, t1)
                                question  = yes_no_dialog(message)
                                if question == True :
                                    temp = [data1[0]]
                                else :
                                    alert(_("Please, note that there is a problem with this record"))
                                    continue
                            temp.append(item)
                            temp += additional
                            temp = array_pad(temp, len_store, "")
                            store.append(temp)

        return True


    def paste_all_records(self, *args) :
        global central_table, main_field, saisieActive, stores

        if not 'save_record' in mem :
            mem['save_record'] = []
        if len(mem["save_record"]) == 0 :
            alert(_("no records in list"))
            return False
        else :
            i = 1
            l = len(mem["save_record"])
            while True :
                if len(mem["save_record"]) > 0 :
                    self.paste_record()
                    self.update_fiche()
                    if "info_label" in self.arw :
                        self.arw["info_label"].set_text( _("record ") + str(i) + "/" + str(l))
                    i += 1
                    while (Gtk. events_pending()) :
                        Gtk.main_iteration();

                else :
                    return True




    def paste_record1(self, *args)   :
        # This version (currently unused) pastes data only if there is no data yet. I don't know what was the idea
        global central_table, main_field, saisieActive, stores

        if len(mem["save_record"]) > 0 :
            fiche = mem["save_record"].pop(0)
        else :
            alert(_("no more records in list"))
            return False

        for  key  in saisieActive  :
            val = saisieActive [ key ]

            if val[2] == "GtkEntry" :
                if key in fiche :
                    existing_text = self.arw[key].get_text()
                    if len(existing_text.strip()) == 0 :
                        self.arw[key].set_text(fiche[key])

            elif val[2] == "GtkTextView" :
                if key in fiche :
                    existing_text = get_text(self.arw[key])
                    if len(existing_text.strip()) == 0 :
                        set_text(self.arw[key], fiche[key])

            elif val[2] == "GtkTreeView" :
                if key in fiche :
                    store = self.arw[key].get_model()
                    if isset(store) :
                        len_store = get_store_length(store)

                        for item in fiche[key] :
                            # TODO : look for the id
                            #tmp1 = re.findall(".*@(.*)", key)
                            table = saisieActive[key][1]
                            id_type = periph_tables[table]['id_type']
                            mainfield = periph_tables[table]['main_field']
                            item2 = self.Chaine_guillemets(item)        # escape ' in chains
                            req = eval(php_string("select $id_type from $table where $mainfield like $item2"))
                            cursor.execute(req)
                            for row in cursor :
                                temp = []
                                id1 = row[0]
                                temp.append(id1)
                                temp.append(item)
                                temp = array_pad(temp, len_store, "")
                                store.append(temp)
                            # TODO: what if the id is not found (new author...)?

        return True





    """=================================================================================================
    FONCTION   : verifier_modification
    DESCRIPTION: lit les données de l'interface de saisie. Utilisée pour vérifier s'il y a eu modification
    PARAMETRES :
    RETOURNE :   True si modification, False sinon
    ==================================================================================================
    """
    def verifier_modification(self)  :
        global central_table, main_field, mem
        # check the content of the form for validation reminder
        mem["saisie_apres"] = self.memoriser_fiche()

        ar_tmp = array_diff(mem["saisie_apres"], mem["saisie_avant"])   # what was added
        mem["added"] = ar_tmp
        zz1 = len(ar_tmp)
        ar_tmp = array_diff(mem["saisie_avant"], mem["saisie_apres"])   # what was deleted
        mem["suppressed"] = ar_tmp
        zz2 = len(ar_tmp)
        if (zz1 > 0) or (zz2 > 0) :

            if zz2 > zz1 :
                zz1 = zz2
            ask = False
            if ("autosave_check" in self.arw) and (self.arw["autosave_check"].get_active() == True) :
                    self.update_fiche()
            else :
                question = yes_no_dialog ("Au moins %d champs modifiés mais pas enregistrés. Enregistrer ?" % zz1)
                if  question == True :
                    self.update_fiche()


    """=================================================================================================
    FONCTION   : update_fiche
    DESCRIPTION: enregistre dans une fiche les données de l'interface de saisie
    PARAMETRES : aucun
    RETOURNE :   rien
    ==================================================================================================
    """
    def update_fiche(self, widget = None)  :

        global config, config_info, central_table, main_field, modified_field, saisieActive, saisieFlipActive, mem, stores, mots_vides, link, periph_tables

        set1 = []
        enregistrer = 0
        main_field_control = saisieFlipActive[main_field]
        avant = mem["saisie_avant"]
        apres = self.memoriser_fiche()
        t_periph_tables = list(periph_tables.keys())    # list of peripheral tables

        if isset(main_field_control) :
            id_livre=get_text(self.arw[main_field_control]) # check if the record exists, if not create it
            req = eval(php_string("select $main_field from $central_table where $main_field = $id_livre"))
            cursor.execute(req)
            result = cursor.fetchone()
            if not result :
                req = eval(php_string("insert into $central_table ($main_field) values ($id_livre)"))
                cursor.execute(req)

        else :
            alert(_("There is no object in the interface for the primary key %s, impossible to save the record") % main_field)
            return


# if function_exists("before_update") :
##
## before_update(book_id, set1) #... before_update(book_id, &set1)


        # record standard fields

        for  z  in saisieActive  :
            val = saisieActive [ z ]
            if val[2] == "GtkEntry" or val[2] == "GtkTextView" or val[2] == "GtkComboBox" or val[2] == "GtkComboBoxEntry" :
                contenu = get_text(self.arw[z])
                contenu=self.Chaine_guillemets(contenu)
                if (contenu)=="" :

                    contenu='null'


                name = val[1]
                if val[1] in t_periph_tables :

                    self.update_periph1(id_livre, name, contenu)            # device table - 1:n relationship (no gateway)


                else : set1.append( name + "=" + contenu)                    # central table


            elif val[2] == "GtkTreeView" :                 # Peripheral table record
                self.update_periph (id_livre,val[1])




        # central table registration
        set2 = ",".join(set1)

        req= eval(php_string("update $central_table set $set2 WHERE $main_field = $id_livre"))
        ok=cursor.execute(req)
        sql_error(link, req)

        link.commit()


        if hasattr(mag.myfunctions, "after_update") :
            mag.myfunctions.after_update(id_livre, set1, mem)


        # update of inverted data

        # processing the peripheral tables. It's simple because we already have the ids array

        for  key in saisieActive  :
            val = saisieActive[key]
            if val[2] == "GtkTreeView" :
                table = periph_tables2[val[1]]['table']
                widget = val[0]
                gateway= periph_tables[table]['gateway']
                id_type = periph_tables[table]['id_type']
                field = periph_tables[table]['main_field']
                inv = "i_data_" + central_table

                if not widget in avant :
                    avant[widget] = []

                if not widget in apres :
                    apres[widget] = []


                effacer = array_diff(avant[widget],apres[widget])
                ajouter = array_diff(apres[widget],avant[widget])

                if len(effacer) > 0 :
                    self.donnees_inverses (id_livre,effacer,table,id_type,inv,"effacer")


                if len(ajouter) > 0 :

                    self.donnees_inverses (id_livre,ajouter,table,id_type,inv,"ajouter")







## processing of word tables.
##
## words_tables = config_info['central_tables'][central_table]['words']
## wtd = words_tables.split(",")
## for words_table_def in wtd :
##
## if config["words"][words_table_def] :
##
##
## del (add, delete)
## type = []
## table_data = config["words"][words_table_def]
## Wtable = table_data['table']
## Wid_type = table_data["id_type"]
## Wmain_field = table_data['main_field']
## inv = "i_data_" + central_table
## for fields in table_data['fields'] :
## temp = fields['field'] # field concerned
## type.append( saisieFlipActive[temp]) # matching control
##
##
## for z in type :
##
## delete2 = []
## add2 = []
##
## words_before = process_words(before[z])
## words_after = process_words(after[z])
##
## if is_[words_before] == False :
##
## forward_words = []
##
##
## if is_[words_after] == False:
##
## next_words = []
##
##
##
##
## delete = array_diff(words_before,words_after)
## add = array_diff(words_after,words_before)
## convert words to word_id; There was 'binary' in the queries ( ... = binary '$z3')
## we don't know why, and it was causing duplicate key errors when adding mpts to the table
## for z3 in delete :
## ok = cursor.execute("select $Wid_type from $Wtable where $Wmain_field = '$z3'")
## if mysql_num_rows(ok) > 0 :
##
## delete2.append( mysql_result(ok,0,0))
##
##
##
## for z3 in add :
## if not (in_[z3, empty_words]) and (len(z3)>1):
## ok = cursor.execute("select $Wid_type from $Wtable where $Wmain_field = '$z3'")
## if mysql_num_rows(ok) > 0 :
## add2.append( mysql_result(ok,0,0))
##
##
## else: # if the word does not exist, it must be added to the words table
##
## if isset(z3) and z3 != "" :
## req="insert into $Wtable set $Wmain_field='$z3'"
## ok=cursor.execute(req)
## sql_error(link,req)
## ok = cursor.execute("select $Wid_type from $Wtable where $Wmain_field= '$z3'")
## add2.append( mysql_result(ok,0,0))
##
##
##
## if count(delete2) > 0 :
##
## data_inverses (book_id,delete2,Wtable,Wid_type,inv, "delete")
##
##
## if count(add2) > 0 :
##
## data_inverses (book_id,add2,Wtable,Wid_type,inv, "add")
##
##
##


        mem['saisie_avant'] = apres
        del apres
        link.commit()




    #=================================================================================================
    # FUNCTION: update_periph
    # DESCRIPTION: save in a file the data for the peripheral tables with gateway (n:n)
    # PARAMETERS: $id_book -> record to process
    # $store -> modèle d'où proviennent les données. Cette fonction est aussi utilisée par
    # table edition which uses a different model.
    # RETURN: a string with the values separated by ;
    # ==================================================================================================


    def update_periph (self, id_livre, table_config, store = None)  :
        global central_table, main_field, order_field, config, save, stores, listes, link, periph_tables, mem

        noms=[]

        table = periph_tables2[table_config]['table']
        gateway= periph_tables2[table_config]['gateway']
        id_type = periph_tables2[table_config]['id_type']
        field = periph_tables2[table_config]['main_field']

        req = eval(php_string("delete from $gateway where $main_field = $id_livre"))
        res=cursor.execute(req)
        sql_error(link, req)


        if store == None :

            store = stores[table]


        arIter = array_iter(store)
        nb = len(arIter)


        for i in range(0,nb) :     #... for(i=0| i<nb| i+= 1)
            ordre=i+1
            id1=store.get_value(arIter[i],0)
            nom=store.get_value(arIter[i],1)

            if nom in noms :
                alert(nom + _(" is already present in the list. Check if it is OK."))



            fields = [main_field, id_type]
            values = [id_livre, id1]

            # MySQL :req=eval(php_string("insert into $gateway SET $main_field = $id_book,$id_type = $id ,"))
            req=eval(php_string("insert into $gateway ($main_field, $id_type )  values ($id_livre, $id1) "))

            if table in self.additional_data :

                j=2
                for  k in range(len(self.additional_data[table]))  :
                    additional = self.additional_data[table][k ]
                    addval = store.get_value(arIter[i],j)
                    fields.append(additional['field'])
                    if not addval :
                        addval = ""
                    values.append("'" + addval + "'")
                    j+= 1
                fields.append(order_field)
                values.append(ordre)
                fields = implode(",", fields)
                values = implode(",", values)

                req = eval(php_string("insert into $gateway ($fields) VALUES ($values)"))

            res=cursor.execute(req)
            sql_error(link, req)
            link.commit()
            noms.append(nom)

## update i_data_xxx not up to speed; need to find the id of the person, chartreuse etc.
## i_data = "i_data" + central_table
## req = eval(php_string("select $i_data from $table where $id_type = "))
## print req, "++++++"
## cursor.execute(req)

        # update central table
        noms=implode(" ;",noms)
        data=noms
        noms = self.Chaine_guillemets(noms)

        field = 'g_' + table # check presence of field

        if db_type == "sqlite" :
            # This pragma returns: index, column name, data type, whether or not the column can be NULL, and the default value for the column.
            req = "PRAGMA table_info(" + central_table + ")"
            cursor.execute(req)
            found = False
            for row in cursor :
                if row[1] == field :
                    found = True
            if not found :
                print("column not present, is this really normal ?")

        elif db_type == "mysql" or db_type == "accdb" :

            cursor.execute("DESCRIBE " + central_table + "  " + field)
            if cursor == None :
                 cursor.execute("ALTER TABLE " + central_table + " ADD COLUMN " + field + " MEMO")


        req=eval(php_string("update $central_table set $field=$noms where $main_field=$id_livre"))
        res=cursor.execute(req)
        sql_error(link, req)
        link.commit()
        return data




    """=================================================================================================
    FONCTION   : update_periph1
    DESCRIPTION: enregistre dans une fiche les données pour les tables périphériques sans passerelle (1:n)
    PARAMETRES : $id_livre -> fiche à traiter
    $store -> modèle d'où proviennent les données. Cette fonction est aussi utilisée par
    l'édition en tableau qui utilise un modèle différent.
    RETOURNE :   une chaîne avec les valeurs séparées par des ;
    ==================================================================================================
    """

    def update_periph1 (self, id_livre, table, data, store = None)  :
        global central_table, main_field, order_field, config, save, stores, listes, link, periph_tables, mem

        noms=[]

        id_type = periph_tables[table]['id_type']
        field = periph_tables[table]['main_field']
        linked_field = periph_tables[table]['linked_field']
        #$req = "select id_collection from collections where collection = "Atopia""
        req = eval(php_string("select $id_type from $table where $field = $data"))
        cursor.execute(req)
        sql_error(link, req)

        #data2 = mysql_result(res, 0, 0)
        result = cursor.fetchone()
        if result :
            data2 = result[0]
        else :
            data2 = None

        if (data2 == None) and (data != None) and data != 'null' :
            req = eval(php_string("insert into $table ($field) values ($data)"))
            cursor.execute(req)
            sql_error(link, req)

            req = eval(php_string("select $id_type from $table where $field = $data"))    # copy. We could also search for lastinserted
            cursor.execute(req)
            sql_error(link, req)
            result = cursor.fetchone()
            if result :
                data2 = result[0]
            else :
                data2 = None

        if data2 == None :
            data2 = "null"

        req = eval(php_string("update $central_table set $linked_field = $data2  WHERE $main_field = $id_livre"))
        res=cursor.execute(req)
        sql_error(link, req)


        """ / update central table

        $field = 'g_'.$table;
        // vérification de la présence du champ
        $result = cursor.execute("DESCRIBE $central_table $field");
        if (mysql_num_rows($result) == 0)
        cursor.execute("ALTER TABLE $central_table ADD COLUMN $field TEXT");


        $req="update $central_table set $field=$noms where $main_field=$id_livre";
        $res=cursor.execute($req); sql_error($link, $req);
        return $data;
        """

        link.commit()




    """=================================================================================================
    FONCTION   : donnees_inverses
    DESCRIPTION: ajoute ou efface (selon la valeur de $action) des éléments dans les données inverses
    Fonction appelée par update_fiche
    PARAMETRES : $id_livre -> fiche à traiter
    $ids -> valeurs à ajouter ou enlever
    $type -> champ inversé à traiter
    $action -> action à réaliser (ajouter ou enlever)
    RETOURNE :   rien
    ==================================================================================================
    """
    def donnees_inverses (self, id_livre,ids,table,id_type, inv, action)  :

        global central_table, main_field, link


        for  z1 in ids  :
            z2 = eval(z1)       # This field is created by repr() because it is a list. We must retrieve the list
            z = z2[0]           # and then retrieve the first item of the list
            req = eval(php_string("select $inv from $table where $id_type = $z"))
            cursor.execute(req)
            sql_error(link, req)
            idata = cursor.fetchone()[inv]

            idata = explode(",",idata)


            if action == "ajouter" :
                if not id_livre in idata :
                    idata.append(id_livre)

            elif action == "effacer" :
                if id_livre in idata :
                    idata.remove(id_livre)
                else :
                    print("on demandait d'effacer " + id_livre + " de " + repr(idata))


            idata = array_unique(idata)
            # deleting commas at the beginning or end of a string (this can happen when a record has an empty field)
            s_idata = implode(",",idata)
            if s_idata[0:1] == "," :
                s_idata = s_idata[1:]


            if s_idata[-1:] == "," :
                s_idata = s_idata[0:-1]


            if s_idata == "" :
                idata_final = "null"
            else : idata_final = "'" + s_idata + "'"

            req = eval(php_string("update $table set $inv = $idata_final where $id_type = $z"))
            ok = cursor.execute(req)




    """=================================================================================================
    FONCTION   : traiter_mots
    DESCRIPTION: extrait les mots à partir d'une chaîne. Fonction utilisée pour la génération des données
    inversées
    PARAMETRES : chaîne à traiter
    RETOURNE :   array des mots contenus dans la chaîne d'entrée
    ==================================================================================================
    """

    def traiter_mots(self, source) :
    # the following code is taken from explode.php. Be sure to keep it the same in both places

        # delete the 3 bytes characters which are not well treated by mbstring
        contenu = str_replace(["…","†","–"], " ", source)

        contenu=mb_strtolower(contenu,"UTF-8")   # put everything in lower case because the system is case sensitive

        # preg_match_all("|\w+|",$content,$output); Does not work in utf8
        ex2=[]
        z2=0                         # word division engine
        while (z2<len(contenu)) :

            mb_ereg_search_init (contenu)
            mb_ereg_search_setpos(z2)
            mb_ereg_search ("(\w+)",contenu)
            z1=mb_ereg_search_getregs()
            z2=mb_ereg_search_getpos()
            out.append(z1[0])

        return(out)



    """=================================================================================================
    FONCTION   : annee_et_siecle
    DESCRIPTION: calcule une année utilisable en fonction de la valeur de date qui n'est pas toujours
    une année complète, par exemple : 20e siècle. Calcule le siècle
    PARAMETRES : aucun
    RETOURNE :   rien
    ==================================================================================================
    """


    def periph_delete(self, treeview)  :
        global arWidgets, config, config_info, periph_tables, link, tab_conversion

        if self.verify_button(treeview) == False :
            return

        list_name = treeview.get_name()
        config_list = tab_conversion[list_name]
        list_data = config['xtabs'][config_list]
        config_table = list_data['table_def']
        table_data = config['peripheral'][config_table]

        table = table_data['table']
        liste = list_data['treeview']
        id_type = table_data['id_type']
        mainfield = table_data['main_field']
        entry = list_data['entry']



        sel=self.arw[liste].get_selection() # debug: resize was 0. This mechanism does not work. It should make the resize not happen
        (model, arPaths) = sel.get_selected_rows()
        n3=len(arPaths)

        if n3==0 :
            alert(_("No line selected. Aborting."))
            return

        elif n3>1 :
            message(_("Please, select only one line."))
            return

        else :
            iter = model.get_iter(arPaths[0]) # value first line
            id = model.get_value(iter, 20)

        req = "select $mainfield from $table where $id_type = $id"
        req1 = eval(php_string(req))
        cursor.execute(req1)
        sql_error(link, req)
        res = cursor.fetchone()
        name=res[0]

        question = yes_no_dialog(_("Do you really want to delete") + " : %s - %s ?" % (table, name))
        if question == True :

            req = "delete from $table where $id_type = $id"
            req1 = eval(php_string(req))
            cursor.execute(req1)
            sql_error(link, req)
            link.commit()

            alert(name + _(" deleted"))

            if config_info['search_lists'][list_name]['type'] == "tree" :
                self.actualiser(list_name)

            else :
                self.refresh_list2(config_list)






    def periph_update(self, treeview)  :


        global arWidgets, config, periph_tables, link, tab_conversion

        if self.verify_button(treeview) == False :
            return
        datadef = {}
        list_name = treeview.get_name()
        config_list = tab_conversion[list_name]
        list_data = config['xtabs'][config_list]
        config_table = list_data['table_def']
        table_data = config['peripheral'][config_table]


        table = table_data['table']
        liste = list_data['treeview']
        id_type = table_data['id_type']
        mainfield = table_data['main_field']
        entry = list_data['entry']
        gateway = table_data['gateway']
        options = list_data['options']
        renvoi = get_option("r",options)


        sel = self.arw[liste].get_selection()
        (model, arPaths) = sel.get_selected_rows()
        n3=len(arPaths)

        if n3==0 :
            alert(_("No line selected. Aborting."))
            return

        elif n3>1 :
            alert(_("more than one line"))
            return

        else :
            iter = model.get_iter(arPaths[0]) # value first line
            id = model.get_value(iter, 20) # value of the id

        # The 3 following lines are unused. Delete ?
        temp = {}
        for ii  in range( 0, 25) :     #... for (ii = 0| ii < 25| ii+= 1)
            temp[ii] = model.get_value(iter,ii)

        for  key, value in list_data['cols'].items()  :          # extract the data fields
            if 'detail' in value :
                widgetname = value['detail']
                if len(widgetname) > 0 :
                    datafield = value['field']
                    contenu = get_text(self.arw[widgetname])
                    datadef[datafield] = contenu

        # content of the main field

        nom1 = unicode2(datadef[mainfield])


        if (renvoi != None) and (len(renvoi) > 0) :

            query = eval(php_string("select $mainfield from $table where $id_type=$id"))
            cursor.execute(query)
            sql_error(link,query)
            result = cursor.fetchone()
            ancien_nom = result[mainfield]


            if (ancien_nom != nom1) and(ancien_nom != "") :
            # if the name has been changed
                ancien_nom=self.Chaine(ancien_nom)
                req = eval(php_string("select $mainfield from $table where $renvoi like '%$ancien_nom%' "))
                cursor.execute(req)
                rows = cursor.fetchall()
                num = len(rows)

                if num > 0 :
                    noms = ""
                    for i in range(0,num) :
                        noms += rows[i][0] + " -"

                    msg = _("Warning ! There are %d  cross-reference(s) on %s . See records : \n %s ") %  ( num, ancien_nom, noms)
                    alert(msg)



        # different treatment depending on whether the new name is already used or not

        # mysql: "select $id_type from $table where $mainfield= binary $name1"
        req = eval(php_string("select $id_type from $table where $mainfield like '$nom1'"))
        cursor.execute(req)
        rows = cursor.fetchall()
        num = len(rows)
        if num > 0 :
            test = rows[0][id_type]
        else :
            test = None

        if test != None and  int(test) != int(id) and len(gateway) > 0  :     # if the new name exists and if it has been changed
            req = eval(php_string("update $gateway set $id_type=$test where $id_type=$id")) # copy the entries from one theme to another
            cursor.execute(req)
            sql_error(link,req)
            req = eval(php_string("delete from $table where $id_type=$id")) # delete the entries of the old name
            cursor.execute(req)
            sql_error(link, req)
            alert(table + "." + mainfield + _(" renamed."))


        else : # If the name has not changed
            req= eval(php_string("update $table set "))
            for  key  in datadef  :
                val = datadef [ key ]
                req += key + "= '" + val+ "',"

            # fields and data
            req = substr(req,0,len(req) -1) # remove the final comma
            req += eval(php_string(" where $id_type = $id")) # Update the data in the device table
            cursor.execute(req)
            sql_error(link, req)


        link.commit()



        if list_data['type'] == "tree" :
            self.actualiser(liste)
            self.collapse(liste,2)

        else :
            self.refresh_list2(config_list)




    def periph_new(self, treeview)  :

        global config, arWidgets, periph_tables, tab_conversion, link

        if self.verify_button(treeview) == False :
            return

        list_name = treeview.get_name()
        config_list = tab_conversion[list_name]
        list_data = config['xtabs'][config_list]
        config_table = list_data['table_def']
        table_data = config['peripheral'][config_table]


        table = table_data['table']
        liste = list_data['treeview']
        id_type = table_data['id_type']
        mainfield = table_data['main_field']
        entry = list_data['entry']



        dialog=Prompt({"Nom à ajouter à la liste :" : ""})
        reponse = dialog.run()
        nom1 = reponse[0]

        if nom1 != 2 :
            nom1=self.Chaine_guillemets(nom1)
            req = "select $id_type from $table where $mainfield = $nom1"
            req1 = eval(php_string(req))
            cursor.execute(req1)
            sql_error(link, req1)
            res = cursor.fetchall()

            if len(res) == 0 :
            # If the new name does not exist yet, we add
                mysqlreq="insert into $table set $mainfield = $nom1"
                sqlitereq = "insert into $table ($mainfield) values ($nom1)"
                req1 = eval(php_string(sqlitereq))
                cursor.execute(req1)
                link.commit()


            else :
                alert(nom1 + _("exists already !"))


        if list_data['type'] == "tree" :
            self.actualiser(liste)
            self.collapse(liste,2)

        else :
            self.refresh_list2(config_list)





class complex_queries :


    global arWidgets, perso, d_champs, d_logique, d_champs_liste, d_logique_liste

    def complex_queries_build(self, widget = None) :


        for i in range(1,4) :     #... for (i=1| i<4| i+= 1)
            self.arw["s_combo_champ"+str(i)].connect("changed", self.affreq)
            self.arw["s_combo_logic"+str(i)].connect("changed", self.affreq)
            self.arw["s_entry"+str(i)].connect("changed", self.affreq)


        # complex queries
        self.arw["s_radio_etoile"].connect("clicked", self.affreq)
        self.arw["s_radio_centrale"].connect("clicked", self.affreq)

        self.arw["s_ExecButton1"].connect("clicked", self.start_query,1)
        self.arw["s_ExecButton2"].connect("clicked", self.start_query,2)
        self.arw["s_ExecButton3"].connect("clicked", self.start_query,3)
        self.arw["s_boutonRAZ"].connect("clicked", self.RAZ)

        self.arw["s_simplifier11"].connect("clicked", self.simplifier_req_complexe)
        self.arw['s_complex_combine_button'].connect("clicked",self.open_combine,self.arw["s_central_table_combo"])

## if perso['simplify_complexes'] == 1 :
## self.arw["s_simplifier11"].set_active(True)
##
## if self['search_on'] == "complete":
## self.arw["s_radio_centrale"].set_active(True)



        # set comboboxes


        cell_renderer = Gtk.CellRendererText()
        stores["champs"]= Gtk.TreeStore(str,str,str)

        parent = None

        if 'fieldlist' in config :

            for  key  in config['fieldlist']  :
                z = config['fieldlist'][ key ]
                if key != 'from' and type(z) != str :
                    if 'nom' in z and 'etoile' in z and 'centrale' in z :
                        z2 = [z['nom'],z['etoile'],z['centrale']]
                        if z['niveau'] == 1 :
                            stores["champs"].append(parent,z2)
                        else : parent = stores["champs"].append(None,z2)


        for i in range(1,4) :

            self.arw["s_combo_champ" + str(i)].set_model(stores["champs"])
            self.arw["s_combo_champ" + str(i)].pack_start(cell_renderer, True)
            #self.arw["s_combo_field" + str(i)].set_attributes(cell_renderer, text=0)
            self.arw["s_combo_champ" + str(i)].set_wrap_width(1)



        cell_renderer = Gtk.CellRendererText()
        stores["logic"]= Gtk.ListStore(str,str)
        for  z in d_logique  :
            stores["logic"].append(z)



        for i in range(1,4) :

            self.arw["s_combo_logic" + str(i)].set_model(stores["logic"])
            self.arw["s_combo_logic" + str(i)].pack_start(cell_renderer, True)
            self.arw["s_combo_logic" + str(i)].add_attribute(cell_renderer, "text", 0)
            self.arw["s_combo_logic" + str(i)].set_wrap_width(1)



        # load table selection combo
        stores["central"]= Gtk.ListStore(str)
        combo = self.arw['s_central_table_combo']
        combo.set_model(stores['central'])
        combo.pack_start(cell_renderer,True)
        combo.add_attribute(cell_renderer, "text", 0)

        for  key  in config['central']  :
            val = config['central'][ key ]
            stores['central'].append([key])
        combo.set_active(0)

        # load result list selection combo
        stores["result"]= Gtk.ListStore(str)
        combo = self.arw['s_result_list_combo']
        combo.set_model(stores['result'])
        combo.pack_start(cell_renderer, True)
        combo.add_attribute(cell_renderer, "text", 0)
        self.load_result_combo('result')
        combo.set_active(0)

        # load selection combo for the details area
        stores["details"]= Gtk.ListStore(str)
        combo = self.arw['s_details_zone_combo']
        combo.set_model(stores['details'])
        combo.pack_start(cell_renderer, True)
        combo.add_attribute(cell_renderer, "text", 0)
        self.load_result_combo('details')
        combo.set_active(0)


        # Combine window
        cr_toggle = {}
        listes['combine'] = Gtk.ListStore(str,str,bool,bool,bool,bool)

        combi = self.arw['s_combine_list']
        combi.set_model(listes['combine'])
        combi.set_reorderable(True)
        selection = combi.get_selection()
        selection.set_mode(0)

        cell_renderer = Gtk.CellRendererText()
        combi.append_column(Gtk.TreeViewColumn("Liste", cell_renderer, text=0)) #$combi->append_column(new GtkTreeViewColumn("List", $cell_renderer, 'text', 1));

        cr_toggle[2] = Gtk.CellRendererToggle() #$cr_toggle[2]->set_property('activatable',True);
        cr_toggle[2].connect('toggled', self.combi_logic_toggled, 2)
        combi.append_column(Gtk.TreeViewColumn("", cr_toggle[2], active=2))

        titles = { 3:"OU", 4:"ET", 5:"SAUF"}
        for  z in [3,4,5]  :
            cr_toggle[z] = Gtk.CellRendererToggle()
            cr_toggle[z].set_property('activatable',True)
            cr_toggle[z].set_property('radio',True)
            cr_toggle[z].connect('toggled', self.combi_logic_toggled, z)
            combi.append_column(Gtk.TreeViewColumn(titles[z], cr_toggle[z], active=z))



        self.arw["s_bouton12"].connect("clicked", self.ok_liste,"combine")
        self.arw["s_combi_raz"].connect("clicked", self.combi_raz)



        self.RAZ("")


    def open_complex(self, widget = None)  :
        self.montrer("s_complex",3)


    def open_queries(self, widget = None)  :
        self.montrer("s_requetes",1)



    def load_result_combo(self, action)  :
        global stores, config_info, config

        central_def = get_text(self.arw['s_central_table_combo'])
        central = config['central'][central_def]['table']
        if central in config_info['central_tables'] :
            if action in config_info['central_tables'][central] :
                temp = config_info['central_tables'][central][action]
                if temp :
                    data = temp.split(",")
                    if action in stores :
                        stores[action].clear()
                        for  val in data  :
                            stores[action].append([val])





    def simplifier_req_complexe(self, widget)  :
        global arWidgets
        # List of objects whose display is suppressed by the Simplify button, in the Complex queries tab.
        liste = ["s_requete1","s_requete2","s_requete3", "s_label944","s_label_recherche_sur","s_radio_etoile","s_radio_centrale","s_binary"]
        if self.arw['s_simplifier11'].get_active()==True :
            for  z in liste  :

                self.arw[z].hide()


            self.arw['s_label_simplifier11'].set_text(_("Advanced Options"))

        else :
            for  z in liste  :
                self.arw[z].show()
            self.arw['s_label_simplifier11'].set_text(_("Simplify"))


    def combi_raz()  :
        global arWidgets

        for  key  in self.arw  :
            val = self.arw [ key ]
            if substr(key,0,5) == "combi" :
                if widget_type(val) == "GtkToggleButton" :
                    val.set_active(False)




    def open_combine(self, widget)   :
        global config, mem, config_info, arWidgets, listes

        self.arw['s_combine_status'].set_text("")
        type = widget_type(widget)

        if type == "GtkTreeView":

            # user interface button
            list_name = widget.get_name()
            table = config_info['search_lists'][list_name]['peripheral_table']

        elif type == "GtkComboBox" :
            list_name = get_text(widget)     # complex queries button
            table = config['central'][list_name]['table']
        else :
            alert (_("Your button is misconfigured, \nyou must select a list as parameter."))
            return

        if list_name.startswith('sp_'):
            if 'combine_active_sp' not in mem:
                mem['combine_active_sp'] = []
            active_mem = mem['combine_active_sp']
        else:
            if "combine_active" not in mem:
                mem["combine_active"] = []
            active_mem = mem['combine_active']

        page = self.arw['s_notebook1'].get_nth_page(self.arw['s_notebook1'].get_current_page())
        label = self.arw['s_notebook1'].get_tab_label(page)
        active_key = (table, list_name)

        if active_key not in active_mem:
            active_mem.append(active_key)
            if not list_name.startswith('sp_'):
                label.set_markup('<b><span foreground="red">' + label.get_text() + "</span></b>")
        else:
            active_mem.remove(active_key)
            if not list_name.startswith('sp_'):
                label.set_markup(label.get_text())

        listes['combine'].clear()
        for key in config_info['search_lists']  :
            val = config_info['search_lists'][key]
            if (val['peripheral_table'], val['treeview']) in active_mem:
                listes['combine'].append([val['name'],key,1,1,0,0])

        # multiple criteria
        # check current selection
        central_def = get_text(self.arw['s_central_table_combo'])
        if central_def in config['central']:
            combi_table = config['central'][central_def]['table']
            for active in active_mem:
                if active[0] == combi_table:
                    # if the table is the same
                    for  z in [1,2,3]  :
                        listes['combine'].append([_("complex query") + str(z),"s_complex" + str(z),0,1,0,0])

        if len(active_mem) > 1:
            # show the dialog if there is more than one active
            self.montrer('s_combine',3)


    def combi_logic_toggled(self, renderer, row, column)  :
        global arWidgets, listes

        list = listes['combine']



        if column == 2 : #The value has been toggled -> we need to invert the current value
            iter = list.get_iter(row)
            list.set(iter, 2, not list.get_value(iter, 2))


        elif column == 3 :
            iter = list.get_iter(row) #The value has been toggled -> we need to change the current value of buttons
            list.set(iter, 3, 1)
            list.set(iter, 4, 0)
            list.set(iter, 5, 0)


        elif column == 4 :
            iter = list.get_iter(row)
            list.set(iter, 4, 1)
            list.set(iter, 3, 0)
            list.set(iter, 5, 0)


        elif column == 5 :
            iter = list.get_iter(row)
            list.set(iter, 5, 1)
            list.set(iter, 3, 0)
            list.set(iter, 4, 0)









    """==============================================================================
    FONCTION   : start_query()
    DESCRIPTION:
    PARAMETRES :
    RETOUR     :
    ==============================================================================
    """
    def start_query(self, bouton,critere)  :
        global arWidgets, query, mem, config, config_info, affichage

        if self.arw["s_requete" + str(critere)].get_text()!="" :

            in_liste= self.lancerRecherche(critere)  # return an array of found records
            query["ids"] = "(" + implode(",",in_liste) + ")"
            if len(query["ids"])>2 :


                z=self.arw["s_requete"+ str(critere)].get_chars(0, -1)           # The where clause is used as a name
                mem['nom_requete'] = z[0:6]
                # parameters to store for the active result list
                central_def = get_text(self.arw['s_central_table_combo'])
                page = mem['result_page']
                affichage[page]['central_def'] = central_def
                result = get_text(self.arw['s_result_list_combo'])
                details = get_text(self.arw['s_details_zone_combo'])

                self.choisir_affichage(result,details)
                self.chercher()
                self.montrer('window2',1)

            else : alert(_("This search does not give any result."))

        else :
            alert (_("No criteria given !"))



    """==============================================================================
    FONCTION   : RAZ
    DESCRIPTION:
    PARAMETRES :
    RETOUR     :
    ==============================================================================
    """
    def RAZ(self, widget)  :

        global arWidgets

        liste = [ "s_entry1","s_entry2","s_entry3", "s_requete1","s_requete2","s_requete3", ]

        for  z in liste  :

            self.arw[z].set_text("")





    """==============================================================================
    FONCTION   : construitWhere
    DESCRIPTION:
    PARAMETRES :
    RETOUR     :
    ==============================================================================
    """
    def construitWhere(self, x)  :

        global arWidgets, d_champs, d_logique, d_champsinv, d_logiqueinv, link
        # table to process
        if self.arw['s_radio_etoile'].get_active() :

            table="etoile"


        else : table="centrale"

        # selected parameter
        sel =self.arw["s_entry" + str(x)].get_text()
        # condition applied

        combobox = self.arw['s_combo_logic' + str(x)]
        model = combobox.get_model()
        logic1 = model.get_value(combobox.get_active_iter(), 1)


        # field to which it applies

        combobox = self.arw['s_combo_champ' + str(x)]
        model = combobox.get_model()
        if table=="etoile" :

            champ1 = model.get_value(combobox.get_active_iter(), 1)


        if table=="centrale" :

            champ1 = model.get_value(combobox.get_active_iter(), 2)




        # query construction
        logic2=logic1.replace("<sel>",sel)
        if self.arw['s_binary'].get_active()== True :

            logic2=logic2.replace("<bin>","binary")


        else : logic2=logic2.replace("<bin>","")
        logic3=logic2.replace("<champ>",champ1)
        # special treatment for broad title
        if champ1=="titre_sl" :

            condition = substr(logic2,5)

            titres_sl=["titre","sous_titre","complement","traduction"]
            for  t in titres_sl  :
                logic3=condition.replace("<champ>",t)
                logic4+="("+logic3+") or "

            logic3 = "where "+logic4
            logic3 = substr(logic3,0,len(logic3) - 4)     # excess "gold" is removed.



        where_s=" " + logic3 + " "


        self.arw["s_requete"+ str(x)].set_text(where_s)



    """==============================================================================
    FONCTION   : lancerRecherche
    DESCRIPTION: renvoie un array des fiches trouvées
    PARAMETRES :
    RETOUR     :
    ==============================================================================
    """
    def lancerRecherche(self, x)  :
        global  arWidgets, config, config_info,d_champs, d_logique, d_champsinv, d_logiqueinv, link, ids


        central_def = get_text(self.arw['s_central_table_combo'])
        central_table = config['central'][central_def]['table']
        id_main = config['central'][central_def]['id_main']
        from1 = config['central'][central_def]['from']

        ids=[]  # reset to zero
        where=self.arw["s_requete" + str(x)].get_text()
        if self.arw['s_radio_etoile'].get_active() :

            requete=eval(php_string("select $central_table.$id_main from $from1 $where group by $central_table.$id_main"))


        else :
            requete=eval(php_string("select $id_main from $central_table $where group by $id_main")) # echo $query;

        # execute
        cursor.execute(requete)
        #sql_error(link,query)
        for row in cursor :    #... for (i=0| i<n| i+= 1)
            ids.append(row[0])

        return ids


    # function launchSearch( $x)



    """==============================================================================
    FONCTION   : affreq
    DESCRIPTION:
    PARAMETRES :
    RETOUR     :
    ==============================================================================
    """

    def affreq(self, widget = None)  :
        global query, mem


        if self.arw["s_requete1"].get_text()=="liste" :

            query[1]=mem['in_liste1']


        elif self.arw["s_combo_logic1"].get_active() > -1 :
            query[1]= self.construitWhere(1)   # return an array of found records

        if self.arw["s_requete2"].get_text()=="liste" :

            query[2]=mem['in_liste2']


        elif self.arw["s_combo_logic2"].get_active()> -1 :
            query[2]= self.construitWhere(2)

        if self.arw["s_requete3"].get_text()=="liste" :

            query[3]=mem['in_liste3']


        elif self.arw["s_combo_logic3"].get_active()> -1 :
            query[3]= self.construitWhere(3)



# ================================= Predefined queries ==============================
class predef_queries :
    def __init__(self) :
        self.queries = {}

    def predef_query_build(self)  :

        treeview = self.arw['s_clist4']
        treeview.set_model(Gtk.ListStore(str,str,str,str,str,str,str,str, str, str))
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Title', renderer, text=0)
        treeview.append_column(column)
        treeview.append_column(Gtk.TreeViewColumn('Title', renderer, text=1))
        treeview.connect('row-activated', self.predef_query_detail)
        treeview.connect('cursor-changed', self.predef_query_detail)
        treeview.set_reorderable(True)


        self.fields = { 0 : "name",
                     1 : "query",
                     2 : "parameters",
                     3 : "comment",
                     4 : "central_def",
                     5 : "names",
                     6 : "widths",
                     7 : "details",
                     8 : "result",
                     9 : "config"}

        # mise à  jour

        for key in [0,4,7,8] :
            name = self.fields[key]
            self.arw["s_" + name + "4"].connect("changed", self.predef_query_update, key, name)

        for key in [1,2,3,5,6] :
            name = self.fields[key]
            buffer1 = self.arw["s_" + name + "4"].get_buffer()
            buffer1.connect("changed", self.predef_query_update, key, name)

        self.arw["s_config4"].connect("toggled", self.predef_query_update, 4, "config")

        # load combobox details

        combo = self.arw['s_details4']
        combo.set_model(stores['details'])
        combo.pack_start(renderer, True)
        combo.add_attribute(renderer, "text", 0)
        stores['details'].clear()
        for  key  in config['details']  :
            stores['details'].append([key])



        # load "central" combobox

        combo = self.arw['s_central_def4']
        combo.set_model(stores['central'])
        combo.pack_start(renderer, True)
        combo.add_attribute(renderer, "text", 0)
        stores['central'].clear()
        for  key  in config['central']  :
            stores['central'].append([key])


        # load combobox "result

        combo = self.arw['s_result4']
        combo.set_model(stores['result'])
        combo.pack_start(renderer, True)
        combo.add_attribute(renderer, "text", 0)
        stores['result'].clear()
        for  key  in config['result']  :
            stores['result'].append([key])


    def predef_query_load(self)  :
        global link, queries, configdir

        php_source = os.path.join(configdir_u, "queries.php")
        py_source = os.path.join(configdir_u, "queries.py")

        # maggy 2.0 migration : convert php to py, if not yet done
        if not os.path.exists(py_source) :
            if os.path.exists(php_source) :
                magutils.php_array_to_py(php_source, py_source)

        if os.path.exists(py_source) :
            f1 = open(py_source, "r")
            data = f1.read()
            f1.close()
            try :
                self.queries1 = eval(data)
            except :
                alert(_("The file queries.py is invalid"))

# # test OrderedDict
## f1 = open(os.path.join(configdir_u, u "queries-od.py"), "r")
## data = f1.read()
## f1.close()
## try :
## self.queries1 = eval(data)
## except:
## alert(_("The file queries-od.py is invalid"))

            # Order keys
            self.queries = OrderedDict()
            keys = list(self.queries1.keys())
            keys.sort()
            for key in keys :
                self.queries[key] = self.queries1[key]
        else :
            self.queries = OrderedDict()
            #self.queries = {}



        model = self.arw['s_clist4'].get_model()
        model.clear()


        if self.queries :

            for  key in self.queries  :
                data = self.queries[key]
                data2 = []
                for  key, name in self.fields.items()  :
                    if name in data :
                        data2.append( to_utf8(data[name]))
                    else :
                        data2.append("")

                append(model,data2)




    def predef_query_detail(self, selection) :
    # note 2
        global mem
        mem['update_query'] = 0

        selection = self.arw['s_clist4'].get_selection()
        (model, arPaths) = selection.get_selected_rows()
        if isset(arPaths) :
            effacer = 0
            iter = model.get_iter(arPaths[0]) # first line selected

        else :                  # if there is no selection, delete
            effacer = 1
            iter = null


        for key, name in self.fields.items() :
            if effacer == 1 :
                texte =""
            else :
                texte=model.get_value(iter, key)
            widget = self.arw["s_"+ self.fields[key] + "4"]
            set_text(widget,texte)

        # RadioButton

        texte=model.get_value(iter, 9)
        if texte == '1' :
            self.arw["s_config4"].set_active(True)
        else :
            self.arw["s_config4_0"].set_active(True)

        mem['query_name'] = model.get_value(iter, 0)
        mem['update_query'] = 1





    def predef_query_save(self, widget)  :
        # Saves the data displayed in the self.queries dictionary,
        # and saves this dictionary in the queries.py file

        line_name = get_text(self.arw["s_name4"])       # name of active query
        for key, option in self.fields.items() :
            text = get_text(self.arw["s_" + option + "4"])
            self.queries[line_name][option] = text

        f1 = open(os.path.join(configdir_u,"queries.py"),"w")
        pp = pprint.PrettyPrinter(indent = 1, width = 100)
        data = pp.pformat(self.queries)

        f1.write(data)
        f1.close()

        f2 = open(os.path.join(configdir_u,"queries-od.py"),"w")
        data = utilities.dict_or_OrdDict_to_formatted_str(self.queries, mode='OD')
        f2.write('OrderedDict([\n' + data + '])')
        f2.close()


    def predef_query_new(self, widget)  :

        model = self.arw['s_clist4'].get_model()
        name = _("New query")
        iter1 = append(model,[name])
        self.queries[_("New query")] = {}
        return iter1


    def predef_query_duplicate(self, widget) :
        global link, queries, mem

        iter1 = self.predef_query_new("")

        sel = self.arw['s_clist4'].get_selection()
        (model, arPaths) = sel.get_selected_rows()
        n3=len(arPaths)

        if n3==0 :
            alert(_("No line selected. Aborting."))
            return

        elif n3>1 :
            alert(_("More than one line selected. Aborting."))
            return

        else :
            iter = model.get_iter(arPaths[0])


        # get data

        fields =  { 5 : "details",
                    6 : "central_def",
                    1 : "query",
                    2 : "widths",
                    3 : "comment",
                    4 : "parameters"}
        for  key in fields :
            field = fields[key]
            text = get_text(self.arw["s_" + field + "4"])
            self.queries[_("New query")][field] = text
            model.set(iter1,key,text)






    def predef_query_delete(self, widget)  :

        sel = self.arw['s_clist4'].get_selection()
        (model, arPaths) = sel.get_selected_rows()
        n3=len(arPaths)

        if n3==0 :
            alert(_("No line selected. Aborting."))
            return

        elif n3>1 :
            alert(_("More than one line selected. Aborting."))
            return

        else :
            iter = model.get_iter(arPaths[0]) # value first line
            name = model.get_value(iter,0)
            del self.queries[name]
            model.remove(iter)




    def predef_query_update(self, widget,col, name)  :
        # In conjunction with the signals set in predef_query_build(),
        # this function updates the dictionary when something is changed in the form

        global link, queries, mem

        if mem['update_query'] == 0 :
            return
        sel = self.arw['s_clist4'].get_selection()
        (model, arPaths) = sel.get_selected_rows()
        n3=len(arPaths)

        if n3==0 :
            alert(_("No line selected. Aborting."))
            return

        elif n3>1 :
            alert(_("More than one line selected. Aborting."))
            return

        else :
            iter = model.get_iter(arPaths[0])       # value first line


            if name == "name" :                     # if the name was changed,
                text = get_text(self.arw["s_name4"])                    # new name}
                self.queries[text] = self.queries[mem['query_name']]    # old name
                self.queries[text]['name'] = text                       # set new name
                del (self.queries[mem['query_name']])                   # delete old name
                model.set(iter,col,text)                                # set new name in tree
                mem['query_name'] = text                                # new name in memory


            else :                                  # if other controls were changed
                line_name = get_text(self.arw["s_name4"])
                text = get_text(self.arw["s_" + name + "4"])
                self.queries[line_name][name] = text
                model.set(iter,col,text)
# if name == "config"






    # function used to launch parked requests with a button

    def lancer_requete(self, button) :

        name = button.get_name()
        req_name = substr(name,strrpos(name,'@')+1);
        # name of the query
        self.ok_requetes("",req_name);


    def ok_requetes(self, bouton, req = None) :

        global queries, mem, link, style_theme2, affichage;
        page = mem['result_page'];
        # destination
        liste2 = self.arw['s_list2' + str(page)];
        index = 0;

        if req :                        # if function was launched by lancer_requete() (just above)

            fiche = self.queries[req];
            largeurs = ""
            names = ""
            comment = ""
            parameters = ""
            central_def = ""
            use_config = 1
            result = ""
            details = ""

            requete=fiche['query'];
            titre=fiche['name'];
            if 'widths' in fiche :
                largeurs=fiche['widths'];

            if 'names' in fiche :
                names=fiche['names'];

            if 'comment' in fiche :
                comment = fiche['comment'];

            if 'parameters' in fiche :
                parameters = fiche['parameters'];

            if 'central_def' in fiche :
                central_def = fiche['central_def'];

            if 'config' in fiche :
                use_config = fiche['config'];

            if use_config == 0 :
                if 'details' in fiche :
                    details = fiche['details'];
                else :
                    try :
                        details = config['central'][central_def]['details']
                    except :
                        details = ""
                if 'result' in fiche :
                    result = fiche['result'];



        else :

            requete=get_text(self.arw['s_query4']);         # we take the request not from the list but from the text area to allow modification

            titre=get_text(self.arw['s_name4']);
            largeurs=get_text(self.arw['s_widths4']);
            names=get_text(self.arw['s_names4']);
            comment = get_text(self.arw['s_comment4']);
            parameters = get_text(self.arw['s_parameters4']);
            details = get_text(self.arw['s_details4']);
            central_def = get_text(self.arw['s_central_def4']);
            result = get_text(self.arw['s_result4']);
            use_config = get_text(self.arw['s_config4']);



        # process the parameters
        arPrompt = {}
        index1 = []
        result2 = {}
        if len(parameters.strip()) > 0 :

            arParam1 = parameters.split(";")
            if len(arParam1[len(arParam1)-1].strip()) == 0 :
                tmp = arParam1.pop

            for z in arParam1 :

                temp = z.split(",");
                index+= 1;
                params = {}
                if temp[0].strip() == "?" :

                    # popup requested
                    label = select = default = values = ""
                    ifnull = None                       # TODO : ifnull "" or None ?
                    for i in range(1, len(temp)) :

                        temp2 = temp[i].split("=",2);      # TODO: attention 1 or 2? There were 2
                        # creation of the parameter list
                        if (len(temp2) == 1) and(i == 1) :  # the first parameter can contain the label without "text ="
                            label = temp2[0];
                        else :
                            params[temp2[0].strip()] = temp2[1];

                    # processing of parameters
                    if "label" in params :
                        label = params["label"];

                    if "select" in params :
                        select = params["select"];

                    if "default" in params :
                        default = params["default"];

                    if "ifnull" in params :
                        ifnull = params["ifnull"];

                    if "values" in params :
                        values = explode("|",params["values"]);

                    arPrompt[label] = [default,select,values];

                    index1.append([index, ifnull])          # memorize the line numbers




                else :

                    # data taken in a control

                    widget_name = temp[0].strip()
                    if widget_name.strip() == "" :      # If there is an empty line
                        continue
                    if not widget_name in self.arw :
                        print(widget_name, "does not seem to exist (8500)")
                        continue
                    text = get_text(self.arw[widget_name]);
                    # processing of parameters
                    for i in range(1, len(temp)) : #(i = 1; i <= len(temp); i+= 1)

                        temp2 = temp[i].split("=",2)
                        params[temp2[0].strip()] = temp2[1];


                    if "ifnull" in params and(text.strip() == "") :
                        text = params["ifnull"];
                    if "choice" in params :

                        choice = params['choice'].split("|");
                        if text == 1 :
                            text = choice[0]
                        else :
                            text = choice[1]


                    result2[index] = text;

            if len(arPrompt) > 0  :

                dialog1 = Prompt2A(arPrompt)    # open the popup if needed
                result1 = dialog1.run()

                for i in range(len(index1)) :           # and process its result
                    if (isset(index1[i][1])) and(result1[i].strip() == "") : # if needed replace with the value of ifnull
                         result2[index1[i][0]]= index1[i][1];
                    else :
                        result2[index1[i][0]] = result1[i]

            # replace the parameters in the query

            # split
            out1 = requete.replace("[", "|||[")
            out1 = out1.replace("]", "]|||")

            # separate values between []
            out2 = out1.split("|||")
            text = "";
            for val in out2 :

                if val[0:1] == "[" :        # if it is an optional code

                    val = val.replace("[", "")         # remove the brackets
                    val = val.replace("]", "")
                    param = re.search("{(\d*)}",val);                 # read the parameter in param
                    num_param = int(param.group(1));

                    # if there is a value, add the text after replacing the parameter
                    if num_param in result2 :
                        if result2[num_param] != None :
                            if result2[num_param].strip() != "" :
                                val = re.sub("{\d*}",result2[num_param],val);
                                text +=val;


                else :

                    text += val;


            requete = text;

        mem['historique']="non";
        mem['nom_requete'] = titre;
        mem['tri_actif']="non";
        # no internal sorting for parked queries
        mem['config_liste'][page] = 0;
        # reconfigure the list

        if use_config == 1 :        # if "use central table configuration" is active
                                    # we use the data from the central table configuration
            result = config['central'][central_def]["result"]
            details = config['central'][central_def]["details"]
            if not page in affichage :
                affichage[page] = affichage[0]
            affichage[page]['central_def'] = central_def;
            affichage[page]['main_table'] = config['central'][central_def]['table']
            affichage[page]['main_id_field'] = config['central'][central_def]['id_main']
            self.choisir_affichage(result,details)
            # if "use central table configuration" is active, override some values
            if 'result' in config['central'][central_def] :
                affichage[page]['result_def'] = config['central'][central_def]['result']
            if 'details' in config['central'][central_def] :
                affichage[page]['details_def'] = config['central'][central_def]['details']
        else :


            if len(details.strip()) > 0 :
                v2(affichage, page)
                affichage[page]['details_def'] = details;
                # TODO: display[page]['result_def'] = result;
            if len(central_def.strip()) > 0 :
                affichage[page]['central_def'] = central_def;
                affichage[page]['main_table'] = config['central'][central_def]['table']
                affichage[page]['main_id_field'] = config['central'][central_def]['id_main']


        self.arw["s_textview_query"].get_buffer().set_text(requete)

        # change to the proper tab
        try :
            tab_s = config["details"][details]["details_tab"]
            if tab_s and isinstance(tab_s, str) :
                tab_i = int(tab_s) - 1
                self.arw["s_notebook3"].set_current_page(tab_i)
        except :
            error_s = utils.printExcept()
            pass    # not critic, stay on first tab. Error message not necessary


        # =========== Execute ================
        if use_config == 1 :            # if "use central table configuration" is active
                                        # we build the ids list
            cursor.execute(requete)
            ids_list = []
            for row in cursor :
                ids_list.append(str(row[0]))
            query["ids"] = "(" + ",".join(ids_list) + ")"
            self.chercher()
        else :
            self.chercher(requete);

            arLargeurs= largeurs.split(",");
            titles = names.split(",")


            for i in range(0,35) : #(i=0; i<35; i+= 1)

                # width of columns and titles
                col=liste2.get_column(i);
                try :
                    col.set_fixed_width(int(arLargeurs[i]));
                    if i < len(titles) :
                        col.set_title(titles[i])
                except :
                    col.set_fixed_width(10);



            mem['config_liste'][page] = 2;      # indicate that this query is a parked query


            range_i = min(query['num_fields'], 40)
            for i in range(range_i) :

                # all columns are visible (but not more than 40, current maximum of the list)
                col = liste2.get_column(i);
                col.set_visible(True);
                for z in list(self.colonnes_resultat[page].keys()) :

                    self.colonnes_resultat[page][z][1] = 1;





        self.montrer('window2', resize = 0);
        self.arw["s_requetes"].hide()



class Maggy(maglist, edit, complex_queries, predef_queries, explode_db, db_utilities, Import_csv) :


    # parameters :

    MODEL_ROW_INTERN = 1001
    MODEL_ROW_EXTERN = 1002         # unused
    MODEL_ROW_MOTION = 1004


    TARGETS = [('MODEL_ROW_INTERN', Gtk.TargetFlags.SAME_WIDGET, MODEL_ROW_INTERN),
            ('MODEL_ROW_EXTERN', Gtk.TargetFlags.OTHER_APP, MODEL_ROW_EXTERN),
            ('MODEL_ROW_MOTION', 0, MODEL_ROW_MOTION)]

    def __init__(self):
        t1 = time.time()
        # Load the On line Help with the appropriate language
        #fnameHelp = _("restore_help_uk.txt")
        #fHelp = open(fnameHelp, "rb")
        #dataHelp = fHelp.read(5000)
        #fHelp.close()

        global stores, affichage, configdir_u
        self.colonnes_resultat = {}
        self.configdir_u = configdir_u
        self.separator  = config["ini"]["output"]["field_separator"]

        self.colors = {}
        for a in [0, 1, 2, 3, 's_reference'] :
            self.colors[a] = {}

        self.colors[0]['f'] = '#000000'
        self.colors[0]['b'] = '#ffffff'

        self.colors[1]['f'] = '#000000'
        self.colors[1]['b'] = '#e1be2a'

        self.colors[2]['f'] = '#000000'
        self.colors[2]['b'] = '#70a0ad'

        self.colors[3]['f'] = '#292bbe'
        self.colors[3]['b'] = '#dad7b8'

        self.colors['s_reference']['f'] = '#dcba68'
        self.colors['s_reference']['b'] = '#ffffff'


        # initialization

        # mem['result_page'] = d_resultat; # d_resultat doesn't exist ???
        mem['colonnes_conserver'] = 0;
        mem['tri_actif'] = "oui";
        mem['ecran'] = "max";
        mem['config_liste'] = {}
        for i in range(0, 10) :
            mem['config_liste'][i]=0;


        self.selected= {}
        self.cancel_request_b = False

        self.program_dir = os.path.abspath('.').replace('\\', '/')

        self.widgets = Gtk.Builder()
        self.widgets.add_from_file(os.path.join(configdir_u, configname_u + '.glade'))
        arWidgets = self.widgets.get_objects()

        for z in  arWidgets:
            if isinstance(z, Gtk.Buildable):
                name = Gtk.Buildable.get_name(z)
                arw[name]= z
                z.set_name(name)

        self.arw = arw

        self.widgets.connect_signals(self)

        # Build system windows
        self.widgets2 = Gtk.Builder()
        self.widgets2.add_from_file('./data/maggy.glade')
        arWidgets2 = self.widgets2.get_objects()

        for z in arWidgets2 :
            try :
                name = Gtk.Buildable.get_name(z)
                name2 = "s_" + name
                Gtk.Buildable.set_name(z, name2)
                self.arw[name2]= z
            except :
                pass

        self.widgets2.connect_signals(self)
        #self.widgets2.connect_signals(ml)


        # widget lists
        self.arWindows = {}
        self.arHPaned = {}
        self.arLabels = {}
        self.arEntries = {}
        self.arTextView = {}
        self.arButtons = {}
        self.arDetails = {}

        for key in self.arw :
            val = self.arw[key]

            type = widget_type(val);
            if (type == "GtkWindow"):
                self.arWindows[key] = val;
            elif (type == "GtkHPaned"):
                self.arHPaned[key] = val;
            elif (type == "GtkVPaned"):
                self.arHPaned[key] = val;
            elif (type == "GtkLabel"):
                self.arLabels[key] = val;
            elif (type == "GtkButton"):
                self.arButtons[key] = val;
            elif (type == "GtkEntry"):
                self.arEntries[key] = val;
            elif (type == "GtkTextView"):
                self.arTextView[key] = val;

        # resize the windows to the recorded value

        if 'position' in config['ini'] :
            for window in config['ini']['position'] :
                if window in self.arw :
                    self.arw[window].show()
                    win=self.arw[window].get_window();        # get the GdkWindow
                    if win :
                        h = config['ini']['position'][window]["h"];
                        w = config['ini']['position'][window]["w"];
                        x = config['ini']['position'][window]["x"];
                        y = config['ini']['position'][window]["y"];
                        win.move_resize(x, y, w, h);
# if window != "s_window" :
## self.arw[window].hide()

        # Wait until the window is resized before setting the Hpaned position, otherwise it will be changed when resizing
        while (Gtk. events_pending()) :
            Gtk.main_iteration();


        # positioning of Hpaned and Vpanes
        if 'Hpaned' in config['ini'] :
            for key in config['ini']['Hpaned'] :
                val = config['ini']['Hpaned'][key]
                if key in self.arw :
                    self.arw[key].set_position(val)

        while (Gtk. events_pending()) :
            Gtk.main_iteration();

        # Hide the windows we have shown
        if 'position' in config['ini'] :
            for window in config['ini']['position'] :
                try :
                    self.arw[window].hide()
                except :
                    pass

        # show the main window
        self.arw["s_window"].show()

        # load the codes of the detail areas from the widgets

        for config1 in config['details'] :
            if 'container' in config['details'][config1] :
                container = config['details'][config1]['container']
                data1 = []
                group1 = widget_group(container,self.arw)
                for widget in group1 :
                    code = get_text(widget)
                    if len(code.strip()) > 0 :
                        data1.append([ Gtk.Buildable.get_name(widget), code])
                if config1 in config_info['details'] :
                    config_info['details'][config1]['zones2'] = {}
                    i = 0
                    for data2 in data1 :
                        config_info['details'][config1]['zones2'][i] = {}
                        config_info['details'][config1]['zones2'][i]['widget'] = data2[0]
                        config_info['details'][config1]['zones2'][i]['code'] = data2[1]
                        i += 1


                else :
                    print(config1, _(" is not defined in config_info['details']"))


        # delete text of code so that it does not appear in the window

        for config1 in config['details'] :
            if 'container' in config['details'][config1] :
                container = config['details'][config1]['container']
                group1 = widget_group(container,self.arw)
                for widget in group1 :
                    set_text(widget,"")


        self.arw["s_window"].connect("delete-event", self.delete_event,1);
        self.arw["s_tri"].connect("delete-event", self.delete_event,0);
        self.arw["s_columns"].connect("delete-event", self.delete_event,0);
        self.arw["s_options"].connect("delete-event", self.delete_event,0);
        self.arw["s_combine"].connect("delete-event", self.delete_event,0);
        self.arw["s_history"].connect("delete-event", self.delete_event,0);
        self.arw["s_complex"].connect("delete-event", self.delete_event,0);
        self.arw["s_tools"].connect("delete-event", self.delete_event,0);
        self.arw["s_window"].connect("destroy", self.delete_event,1);




        # ================= Search result window =====================================
        self.arw["s_notebook2"].connect_after("switch-page",self.switch_nb2);
        # sort
        # The creation of the menu for the button is managed by the function choose_display in lists.php
        self.arw["s_bouton_tri_exec"].connect("clicked", self.trie_liste);
        # printing
        if 's_print_button' in self.arw :
            menu = Gtk.Menu();
            files = glob.glob(os.path.join(configdir_u, "models/*.*"))
            for val in files :

                path, name = os.path.split(val)
                item = Gtk.MenuItem(name);
                item.connect("activate", self.impression, name);
                menu.add(item);
            self.arw['s_print_button'].set_menu(menu);
            menu.show_all();

        # Buttons for history
        self.arw["s_ok-historique"].connect("clicked", self.ok_historique);



        # Building result lists that are not built in Glade

        for j in range(0,40) :
            cr_editable[j] = Gtk.CellRendererText();
            cr_editable[j].connect("edited", self.edit_list,j); # this procedure allows the cell-renderer to return the column number

        for i in range(0,10) :  # (i=0; i<=9; i++):
            # the model
            stores[i] = Gtk.ListStore(str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str);
            modelsort[i] = Gtk.TreeModelSort(stores[i]);
            # note 1
            self.arw['s_list2' + str(i)] = Gtk.TreeView(modelsort[i]);
            treeview=self.arw['s_list2' + str(i)];
            treeview.connect('row-activated', self.detail, i);
            treeview.connect('cursor-changed', self.detail, i);
            # treeview.modify_font(font);
            # Â£Â£ : it works if you remove the call to the font function.
            treeselect=treeview.get_selection();
            treeselect.set_mode(3);
            # multiple selection
            treeview.connect("button-press-event", self.details_edition);
            treeview.set_enable_search(True);
            # kksou 332
            treeview.set_search_column(2);
            #kksou 333 Does not work for the moment
            #view.set_search_entry(search_entry); #kksou 334
            #treeview.set_search_equal_func('compare_func'); # kksou 335
            """ def compare_func(model, column, key, iter) :
                val = model.get_value(iter, column);
                # note 3
                val = strip_tags(val);
                # note 4
                if (preg_match("/"+key/+"", val))
                    # note 5:
                    return False;
                    # note 6
                     else :
                    return True;
            """
            #treeview.set_rubber_banding(True); # kksou 331
            # create and set columns
            for j in range(0,40) : # (j=0; j<40; j++):
                colnew = Gtk.TreeViewColumn(str(j), cr_editable[j], text=j);
                # pango is managed in the function search
                colnew.set_sizing(2);
                # 2 = GTK_TREE_VIEW_COLUMN_FIXED
                colnew.set_resizable(True);
                colnew.set_reorderable(True);
                colnew.set_sort_column_id(j);
                colnew.set_clickable(True);
                #colnew.connect("clicked", "list_click_column");
                treeview.append_column(colnew);
            self.arw['s_scrolledwindow2' + str(i)] = Gtk.ScrolledWindow();
            child = self.arw['s_scrolledwindow2' + str(i)];
            child.set_policy(1,1);
            child.add(treeview);
            label = Gtk.Label("Page_" + str(i));
            menu = Gtk.Label("Page_" + str(i));
            self.arw['s_notebook2'].insert_page_menu(child, label, menu, i);

        # history
        cell_renderer2 = Gtk.CellRendererText();
        # ?? titles = array_pad(c_titles.get('history'),10," "); c_titles does not exist
        stores['historique'] = Gtk.ListStore(str,str,str,str,str,str,str,str,str,str);
        treeview=self.arw['s_historique'];
        treeview.set_model(stores['historique']);
        treeselect=treeview.get_selection();
        treeselect.set_mode(3);
        # multiple selection
        for j in [0,1] :
            colnew = Gtk.TreeViewColumn(" ", cell_renderer2, text=j);
            colnew.set_max_width(400);
            colnew.set_resizable(True);
            # make it sortable and let it sort after model column 1
            colnew.set_sort_column_id(j);
            # add the column to the view
            treeview.append_column(colnew);

        # edit
        self.arw['s_notebook2'].show_all();
        self.arw['s_notebook2'].popup_enable();
        #??self.arw['s_notebook2'].set_current_page(mem['result_page']);
        self.arw['s_notebook2'].set_current_page(0);

        # Detailed display at the bottom of the Search Result screen
        # It is now done entirely in glade
        """ Le formatage des textview exige une tagtable.
        pour pouvoir utiliser la mÃªme tagtable pour plusieurs textview,
        il faut créer des textbuffers en leur attribuant cette table (cela ne peut pas Ãªtre modifié aprÃ¨s)
        enfin attribuer les buffers ainsi créé aux textview.
        Pour formater les labels, il faut utiliser le pango markup language,
        et attribuer le texte avec .set_markup au lieu de set_text.
        Voir plus bas (fonction Detail) pour detail_cote par exemple
        """

        # Sort window - columns
        stores['liste_cols'] = Gtk.ListStore(str,bool,int,bool,bool);       # If it is true that 32 = int and 20 = bool !
        self.arw['s_liste_colonnes'].set_model(stores['liste_cols']);
        self.arw['s_liste_colonnes'].set_reorderable(True);
        # add columns to the column selection list
        cell_renderer = Gtk.CellRendererText();
        colnew = Gtk.TreeViewColumn(" ", cell_renderer, text=0);
        self.arw['s_liste_colonnes'].append_column(colnew);
        cell_renderer2 = Gtk.CellRendererToggle();
        cell_renderer2.connect("toggled", self.toggle_cols);
        colnew = Gtk.TreeViewColumn(" ", cell_renderer2, active=1);
        self.arw['s_liste_colonnes'].append_column(colnew);
        colnew = Gtk.TreeViewColumn(" ", cell_renderer, text=2);
        self.arw['s_liste_colonnes'].append_column(colnew);

        # Sort combobox
        for z in [1,2,3] :
            self.arw['s_combo_tri' + str(z)].set_model(stores['liste_cols']);
            #Â£ self.arw['s_combo_tri' + str(z)].set_text_column(0); Unused for comboboxtext

## import dialog
##        stores['import_dialog'] = Gtk.ListStore(str,str);       # If it is true that 32 = int and 20 = bool !
## self.arw['s_import_treeview3'].set_model(stores['import_dialog']);
## cell_renderer = Gtk.CellRendererText();
## colnew = Gtk.TreeViewColumn(" ", cell_renderer, text=1);
## self.arw['s_import_treeview4'].append_column(colnew);

        # Compare tab
        treeview = self.arw["s_compare_tree"]
        model1 = Gtk.ListStore(str,str,str,str)
        treeview.set_model(model1)
        cr = Gtk.CellRendererText()
        for j in range(0,4) : # (j=0; j<40; j++):
            colnew = Gtk.TreeViewColumn(str(j), cr, text=j);
## colnew.set_sizing(2);
## 2 = GTK_TREE_VIEW_COLUMN_FIXED
            colnew.set_resizable(True);
## colnew.set_reorderable(True);
            colnew.set_sort_column_id(j);
            colnew.set_clickable(True);
            #colnew.connect("clicked", "list_click_column");
            treeview.append_column(colnew);


##        fx = open("listes3.py", "r")
## exec(fx)
## fx.close()

        t2 = time.time()
        #print "time2:", (t2-t1)
        t1 = t2

        self.build_listes()             # build search lists

        t2 = time.time()
        #print "time41:", (t2-t1)
        t1 = t2




        # font size setting
        self.fonte1 = pango.FontDescription("sans 10")

        self.police(self.arw,self.fonte1);       # initialize font size for all objects


        """
        # for the whole interface
        # connection of zoom on textview and entry

        foreach (self.arw as key : widget)
            type = widget_type(widget);
            if (type == "GtkTextView"):
                widget.connect('button-press-event','zooms','TextView');
            elif (type == "GtkEntry"):
                widget.connect('button-press-event','zooms','Entry');
        load_config_menu();         # configuration window menu
        set_config_dialog();        # configure the lists de la fenÃªtre de configuration
        """


        # construction and configuration of the lists and entries of the input interface

        """ constitution de la liste de widgets de chaque interface de saisie.
        l'array arSaisie contiendra des array avec :
        nom de l'objet dans Glade,
        nom du champ (fin du nom d'objet),
        type d'objet
        """

        self.arSaisie = {}
        self.arSaisieFlip = {}
        container = []
        self.additional_data = {}


        # create the group of container objects defined as input area
        for  key  in config['central']  :
            val = config['central'][key]
            if 'edit' in val :

                container.append( { 'table' : val['table'].strip(), 'edit' : val['edit'].strip()})



        for  val in container  :
            table_fields = []
            cont = val['edit']
            table = val['table'] # create the list of fields in the table
            query = "select * from " + table
            cursor.execute(query)
            temp1 = cursor.description
            for value in temp1 :
                table_fields.append(value[0])

            group = widget_group(cont,self.arw)
            if not group :
                alert(_("This container is not valid for edition : ") + cont)



            # extract the objects containing the input indicator (@)

            t_periph_tables = list(periph_tables.keys())    # list of peripheral tables  => obsolete
            t_periph_config = []                      # we use config names to allow several peripheral configurations for the same table
            for key1 in list(config["peripheral"].keys()) :
                if "config_name" in config["peripheral"][key1] :
                    t_periph_config.append(config["peripheral"][key1]["config_name"])
                else :
                    message = config_error ("config_name", "config.peripheral", key1)
                    alert(message)



            for  widget in group  :
                nomObjet = Gtk.Buildable.get_name(widget)
                pos = strrpos(nomObjet,"@")
                if pos == -1 :      # if the indicator is not present, ignore
                    pass



                else :
                    nomChamp = substr(nomObjet,(pos + 1))       # we extract the field name from the object name
                    if (nomChamp in table_fields          # if the control is for an existing field
                       or nomChamp in t_periph_tables       # or a peripheral table defined => ogbsolete
                       or nomChamp in t_periph_config) :
                            type = widget_type(widget)
                            v2(self.arSaisie,cont,nomObjet)
                            v2(self.arSaisieFlip,cont,nomChamp)
                            self.arSaisie[cont][nomObjet] = [nomObjet,nomChamp,type]     # add it to the array $self.arSaisie
                            self.arSaisieFlip[cont][nomChamp] = nomObjet       # and to the inverted array, which makes it easy to find the object that is used to edit a certain field

                    else :
                        alert(_("You have an edit control for the field %s \nbut this field does not exist in the table %s." % (nomChamp, table)))





        # creation of the lists of the input interface

        arTreeView = []
        # lists of gateway data
        cell_renderer = Gtk.CellRendererText()
        # list the TreeView of the input interfaces
        for  key in self.arSaisie  :
            container = self.arSaisie[key]
            for key2 in container  :
                val = container[key2]
                if val[2] == "GtkTreeView" :
                    try :
                        periph_config = periph_tables2[val[1]]

                        table = periph_config["table"]
                        arTreeView.append( {'config' : val[1], 'table' : table, 'widget' : val[0]})
                    except:
                        print("Configuration of edit interface %s is probably incomplete" % val[1])



        if arTreeView :
            for  val in arTreeView  :
                treeview = self.arw[val['widget']]
                table = val['table']

                stores[table]= Gtk.ListStore(str,str,str,str,str,str,str,str,str,str,str,str)
                treeview.set_model(stores[table])
                # configure the lists
                treeview.connect("key-press-event",self.effacer_ligne)
                treeview.connect("button-press-event",self.open_zoom)
                treeview.set_reorderable(True)
                treeview.set_headers_visible(False)
                # add columns

                colnew = Gtk.TreeViewColumn("", cell_renderer, text=1)
                colnew.set_sizing(2)             # 2 = GTK_TREE_VIEW_COLUMN_FIXED
                if 'cols' in val and val['cols'][0]['width'] > 0 :

                    colnew.set_fixed_width(val['cols'][0]['width'])


                else : colnew.set_fixed_width(200)
                colnew.set_resizable(True)
                treeview.append_column(colnew)
                # columns for additional data
                if val['config'] in periph_tables2 :
                    if ('gateway_data' in config) and (val['config'] in config['gateway_data']) :
                        data = config['gateway_data'][val['config']]['cols']
                        if data :
                            j = 2
                            for  key2 in data  :
                                val2 = data[key2]
                                if len(val2['field']) > 0 :
                                    title = val2['title']
                                    if table not in self.additional_data :
                                        self.additional_data[table] = []
                                    self.additional_data[table].append(val2)
                                    colnew = Gtk.TreeViewColumn(title, cell_renderer, text=j)
                                    colnew.set_sizing(2)             # 2 = GTK_TREE_VIEW_COLUMN_FIXED
                                    colnew.set_fixed_width(int(val2['width']))
                                    colnew.set_resizable(True)
                                    treeview.append_column(colnew)
                                    j+= 1


        self.queries = {}
        self.complex_queries_build()
        self.predef_query_build()
        self.predef_query_load()


        # display errors

        message = ""
        if len(self.build_listes_errors) > 0 :
            for title,widget in self.build_listes_errors :
                message += title + " " + widget + _(" does not exist\n")
            alert(message)
        # end of BuildDialog() function

        # load plugins

        if "myfunctions" in globals() :
            try :
                self.myfunctions = myfunctions.UserFunctions(self, self.arw, link, cursor, config, mem)
            except :
                message = utils.printExcept()       # error not critical, the program must not stop
                alert(_("UserFunctions has errors. Impossible to load. \nPlease check your 'userfunctions.py' file. The error is :\n\n %s" % message))
                print(message)


        # show the tab defined in the configuration
        v2(config["ini"], "gui", "start_tab")
        start_s = config["ini"]["gui"]["start_tab"]
        try :
            if int(start_s) > 0 :
                self.montrer(start_s)
        except :        # undefined or invalid
            alert (_("The value for the tab shown at startup is invalid :"), start_s)

        print ("end of ini")

# self.arw["button8"].connect("clicked", test.toto )


    def delete_event(self, window, event,param =1)   :

        if param == 1 :
            Gtk.main_quit()
            return False

        else :
            return True


    def OnDelete(self,)   :
        if  True :
            return False

        else :
            return True


    def gtk_widget_hide(self, widget)   :
        window = widget.get_toplevel()
        window.hide()


    def gtk_main_quit(self, widget = None)   :

        Gtk.main_quit()
        os._exit(0)


    def close_window(self, widget)   :
        window = widget.get_toplevel()
        window.hide()

    def call_user_func(self, func_name, fiches) :
        command_s = "data = self.myfunctions." + func_name.strip() + "(fiches)"
        exec(command_s)

        return data

    def switch_gb(self, *args) :
        global link, cursor, db_structure, db_active_file

        try :
            (link, cursor, db_structure, db_active_file) = db_active[2]
        except :
            (self.link2, self.cursor2, self.db_structure2, self.db_active_file2) = self.load_sqlite("config/Portes/gb.sqlite")
            db_active[2] = (self.link2, self.cursor2, self.db_structure2, self.db_active_file2)
            (link, cursor, db_structure, db_active_file) = db_active[2]
        self.refresh_active_lists()
        self.highlight_label("label_switch2")

    def switch_portes(self, *args) :
        global link, cursor, db_structure, db_active_file

        (link, cursor, db_structure, db_active_file) = db_active[1]

        self.refresh_active_lists()
        self.highlight_label("label_switch1")


    def highlight_label(self, label) :

        for label1 in ["label_switch1", "label_switch2"] :
            mytext = self.arw[label1].get_text()
            self.arw[label1].set_text(mytext)

        mylabel = self.arw[label]
        mytext = mylabel.get_text()
        mylabel.set_markup('<b><span foreground="red">' + mytext + "</span></b>")


    def next_line(self, widget, event = None, treeview = None, mode = "+") :
        treeview = self.arw['s_list20']

        selection = treeview.get_selection()
        (model, arPaths) = selection.get_selected_rows()
        if arPaths :
            path = arPaths[0][0] # first line selected
            if mode == "+" :
                nextpath = (path+1,)
            else :
                nextpath = (path-1,)
            selection.unselect_path(path)
            selection.select_path(nextpath)
            self.detail(treeview)

    def previous_line(self, widget, event = None, treeview = None) :
        self.next_line("", mode = "-")

    def ______Chercher_Trier____________() :
        pass

    """==============================================================================
    FONCTION   : chercher
    DESCRIPTION: Fonction d'affichage pour le résultat de recherche. Exécute la requête et affiche le résultat sous forme de liste
    PARAMETRES : req1 : si ce paramètre est donné, il sera utilisé comme requête,
    sinon la valeur par défaut sera utilisée avec les id-livre contenus dans query['ids']
    changetitre : si 0, le titre ne sera pas changé. Sinon (défaut = 1) il le sera
    avec une valeur extraite de mem['nom_requete']
    RETOUR     :
    ==============================================================================
    """
    def chercher(self, req1 = "", changetitre = 1, ajouter=0) :

## global query, , config, config_info,
## display, stores, modelsort, order, timing,
## link, result, col_view, mem,
## d_fieldsinv, fieldnames, result, cr_editable ;

        global col_view



        page = mem['result_page'];
        col_view = {}
        clist = self.arw['s_list2' + str(page)];
        store = stores[page];

        if req1!="" :               # if a query is given, execute it
            req=req1 ;
        else :

            ids=query["ids"];       # otherwise build query from the list of ids

            # some cleaning of eventual anomalies
            ids=re.sub(",+", ",", ids);     # if there are empty selections, it generates commas in the list of ids that follow each other and make the query fail. We replace them with a single comma
            ids = ids.replace("(,", "(")    # suppression de la virgule en début de parenthèse
            ids = ids.replace(",)", "(")    # delete the comma at the end of the parenthesis


            table_config =affichage[page]['central_def'];
            table_data = config['central'][table_config];
            mainfield =  table_data['table'] + "." + table_data['id_main'];


            select = affichage[page]['select'];
            fromx   = table_data['from'];
            if fromx.strip() == "" :                 # if no particular from clause defined, take the name of the table
                fromx =  table_data['table']
            #order = display[page]['order'];
            req = "select " + select + " from " + fromx
            req += " where " + mainfield + " in " + ids
            """req += " group by " + mainfield + order"""



        if page in affichage :   # TODO: predefined queries do not use the "display" dict

                p = affichage[page]
                if 'width' in p :
                    width = p['width'];     # list of widths for each column
                else :
                    width = ""

                if 'visible' in p :
                    visible = p['visible'];
                else :
                    visible = ""

## if 'width' in p :
## width = p['width'];
## else :
## width = ""

                if 'options' in p :
                    options = p['options'];
                else :
                    options = ""

                if 'title' in p :
                    title = p['title'];
                else :
                    title = "x"


        else :
            width = ""
            visible = ""
            options = ""
            title = "x"


        # history
        v2(resultat,'page' + str(page),'requete')
        resultat['page' + str(page)]['requete']=req; # stored for the list refresh function
        nom_his = mem['nom_requete'];
        elements = mem['elements_req'];

        if page in affichage :
            test = copy.deepcopy(affichage[page])
            test["db_active"] = ""      # represent an object, and db_active first two items are objects (link and cursor)
                                        # history does not need these values
                                        # TODO, : in history after eval(val2) perhaps add display[page] = db_active to prevent further problems ?
            val2 =repr(test)

        else :
            val2 = None
        values=[nom_his,elements,val2,req]

        # history
        for j in range(len(values),10) :
            values.append("")

        if mem['historique'] != "non" :
            stores['historique'].append(values);
        else :
            mem['historique']="";

        mem['elements_req'] = "";


        # show title in tab
        if changetitre != 0 :
            active_page = self.arw['s_notebook2'].get_nth_page(page);
            text = mem['nom_requete'][0:25]
            self.arw['s_notebook2'].set_tab_label_text(active_page,text);
            self.arw['s_notebook2'].set_menu_label_text(active_page,mem['nom_requete']);

        # ========= And now execute query ========================

        try :
            cursor.execute(req)
        except :
            print("Error for : ", req)

        sql_error(link,req);
        result_a = cursor.fetchall()

        if ajouter == 0 :
            store.clear();


        fields_names = cursor.description           # list of fields in the query


        # width, titles and visibility of columns

        if mem['config_liste'][page] == 0 :         # if list not yet configured
            for k in range(0,40) :

                if k < len(title) :
                    if isinstance(title[k],str) :
                        nom = title[k]
                    else :
                        nom = " "
                elif k in fields_names :                # if there was a * in the select
                    nom = fields_names[k][0]
                else :
                    nom = " "

                col=clist.get_column(k);                # set width if defined
                try :
                    if width[k] :
                        col.set_fixed_width(int(width[k]));
                except :
                    pass

                col.set_title(nom);
                """pango = get_option("pango",options[k]);
                if pango == 1 :
                    coltype = 'markup';

                # put markup instead of text to use pango
                else :

                    coltype = 'text';
                """
                coltype = 'text'
                renderer = cr_editable[k]
                col.set_attributes(renderer, text=k);

                if len (visible) > k :
                    if visible[k]=='1' or visible[k]== 1  :
                        col.set_visible(True);
                        col_view[k]=1;

                    else :
                        col.set_visible(False);


            mem['config_liste'][page] = 1;
        #clist.freeze_child_notify(); # no concrete effect


        store.clear()

        # detach store to make the process faster for long lists
        if len(result_a) > 200 :
            clist.set_model(None)
            # destroy the sort is necessary, otherwise the growth of the display time is exponential
            if page in modelsort :
                    del modelsort[page]

        # populate the store
        i = 0
        data2 = []
        if db_type != "mysql" :
            for z in result_a :
                data1 = []
                for a in z :
                    data1.append(a)
                data2.append(data1)
        else :                      # mysql results are presented in a different format
            fields = []             # create the list of fields
            for z in fields_names :
                fields.append(z[0])
            for z in result_a :
                data1 = []
                for a in fields :
                    data1.append(z[a])
                data2.append(data1)
                data1 = []


        for data1 in data2 :
            append(store,data1, datatype = "str");
            if i % 100 == 0 :
                status_text = str(i) + _(" records")
                self.arw["status"].set_text(status_text);

                while (Gtk.events_pending()) :
                    Gtk.main_iteration();
            i += 1


        status_text = str(i) + _(" records")
        self.arw["status"].set_text(status_text);

        # reattach store and modelSort (if they were detached)
        if len(result_a) > 200 :
            modelsort[page] = Gtk.TreeModelSort(store);
            clist.set_model(modelsort[page])

        # select first line to force display of the details
        # TODO : this approach is not the most beautiful and provokes a blinking
        first = modelsort[page].get_iter_first();
        sel = clist.get_selection();
        if first :
            sel.select_iter(first);


        clist.grab_focus();


        # memorize the number of cards
        query["num_rows"]=i
        query["num_fields"]=get_store_length(store);
        if not 'status' in mem :
            mem['status'] = {}
        mem['status'][page] = status_text;



        self.colonnes_resultat[page]= {}



        # memorize the list of columns for the function Sort / Columns

        for k in range(len(fields_names)) :
            data = ['','',0,'','']          # default width = 0
            if k < len(title) :
                nom = title[k]        # name of column
                data[0] = nom
            if k < len(visible) :
                data[1]=visible[k]
            if k < len(width) :
                data[2]=width[k]
                if data[2] == '' :
                    data[2] = 0               # default width = 0
            data[3] = k

            v2(self.colonnes_resultat,page,nom)
            self.colonnes_resultat[page][nom] = data




        if mem['tri_actif']=="non" :
            mem['tri_actif']="oui";

        else :

            # sort_list(display[page][aff]['sort']['default sort']);
            # sorter selon le tri par défaut
            # supprimé parce que prend beaucoup de temps. Pour le premier tri, MySQL peut s'en charger
            # moreover the command is no longer up to date.
            pass



        while (Gtk. events_pending()) :
            Gtk.main_iteration();

        #timer(5);


## if timing==1 :
## result = timer('result');
## alert(result);


    """===========================================================================
    FONCTION   : trie_liste
    DESCRIPTION: trie les colonnes
    PARAMETRES :
    RETOURNE :
    ==============================================================================


    """

    def replace_accents(self, string) :
    # This function will replace accentuated characters to allow a friendly like
    # e will find Ã©Ã¨Ãª etc. oe will find Å“
        global remove_accents

        string2 = ""
        for letter in string :
            if letter in remove_accents :
                string2 += remove_accents[letter]
            else :
                string2 += letter
        return string2



    def trie_liste(self, widget, criteres = None) :


        global tri1, tri2, result, query, timing, mem, tris_predefinis;

        tristore= []
        colonnes={}
        alpha={}
        ascen={}

        #t4=getmicrotime();

        page = mem['result_page'];

        liste=self.arw["s_list2" + str(page)];      # Get the list and its model
        treemodelsort=liste.get_model();
        store=treemodelsort.get_model();
        lignes=len(store);

        # Get sort parameters
        if criteres == None :           # if sorting is controlled by the sort window, get the data from this window
            if widget == self.arw["s_bouton_tri_exec"] :
                for i in range(0, 3) :
                    j=i+1;
                    colonnes[i]=get_text(self.arw['s_combo_tri' + str(j)]);
                    if self.arw['s_descendant' + str(j)].get_active() :
                        ascen[i]="-";
                    else :
                        ascen[i]="+";

                    if self.arw['s_numerique' + str(j)].get_active() :
                        alpha[i]="n";
                    else :
                        alpha[i]="a";

                    num_colonnes=3;

        else :

            # process the parameters
            # delete empty criteria

            todel = []          # necessary to prevent RuntimeError: dictionary changed size during iteration
            for key  in criteres :
                val = criteres[key]
                if len(val) == 0 :
                    todel.append(key)
            for key in todel :
                del criteres[key]




            num_colonnes=len(criteres);         #Number of columns on which sort is done
            i=0;
            for data in criteres :
                n1=strpos(data," ");
                alpha[i] = "a";     # defaults : alphabetical and increase
                ascen[i] = "+";

                if n1 == 0 :            # if no parameters
                    colonnes[i] = data;
                else :
                    colonnes[i] = substr(data,0,n1);
                    switchs = substr(data,n1);
                    if strpos(switchs,"d")!=0 :     # parameter d = decrease
                        ascen[i] = "-";

                    if strpos(switchs,"n")!=0 :     # parameter n = numeric
                        alpha[i] = "n";

                i+= 1;

        # transform names into column numbers
        col = {}
        for i in range(0, num_colonnes) :
            if colonnes[i] in self.colonnes_resultat[page] :
                col[i]=self.colonnes_resultat[page][colonnes[i]][3];



        # sort
        temp={}
        arIter=array_iter(store);
        for i in range(0, lignes) :
            for j in range(0, num_colonnes) :

                if j in col :         # if a criteria is defined
                    temp[j] = store.get_value(arIter[i],col[j]);

                    # TODO: be careful, if it is utf-8 and not unicode, problems. Check.
                    if temp[j] == None :
                        temp[j] = ""
                    v1 = temp[j].decode("utf8")
                    v2=v1[0:30]                # N'améliore pas beaucoup les performances. Il faut au moins 28 pour le tri par cotes
                    v2 = v2.lower()                  # sort insensible à la casse
                    v3 = self.replace_accents(v2)        # handling of accents
                    temp[j] = v3;

                    if ascen[j]=='+' and temp[j]=="" :      # handling of anonyms
                        temp[j]="ZZZ";


                    if alpha[j]=='n' :                      # sort numérique
                        temp[j]=temp[j].rjust(10,'0')


                    if ascen[j]=='-' and alpha[j]=='n' :    # descending numeric sorting
                        temp[j]= str(int(10000000000) - int(temp[j]))


                    if ascen[j]=='-' and alpha[j]!='n' :    # TODO: descending alphabetical sort
                        v2 = temp[j].encode("hex")
                        v3 = v2.ljust(10,"0")
                        v4 = v3[0:10]
                        v5 = int(v4,16)
                        v6= 100000000000000 - v5;
                        temp[j]= str(v6)





            final1="";
            for z3 in temp :
                final1 += temp[z3] + "      ";

            final2 = final1 + str(i)        # to avoid duplicates that make the arrayflip function fail below

            tristore.append([final2, i])



        # sorting completion

        # Sort the list
        arIter = array_iter(store);
        x2 = sorted(tristore)
        n = len(x2);

        # Create a list of new positions of the lines
        i = 0
        new_order = []
        for item1 in x2 :
            new_order.append(x2[i][1])
            i += 1

        # Sort the treestore
        store.reorder(new_order)




    def ________________DETAIL______________() :
        pass
    # =========================================================
    # The following functions handle the display in the details area
    # ==========================================================#
    """==============================================================================
    FONCTION   : Detail
    DESCRIPTION: en lien avec detail_text, affiche le texte dans la zone d'affichage détaillé
    en bas de l'écran Résultat de recherche.
    PARAMETRES : liste : treeview qui appelle la fonction (nécessaire pour trouver l'id de la fiche)
    RETOURNE :
    ===============================================================================
    """

    def detail(self, liste, *args) :

        global central_table, main_field, config, affichage, mem;

        page = mem['result_page'];
        nom_details = v(affichage,page,'details_def')
        if not nom_details :
            return

        details = config_info['details'][nom_details];
        central_table_data = config['central'][details['central_def']];

        if len(details['central_def'].strip()) > 0 :
            table = central_table_data['table'];
            field = central_table_data['id_main'];

        else :

            table = central_table;
            # normally to be deleted
            field = main_field;


        id1 = get_sel_row_data(liste,0,0);
        mem["selected_record"] = id1
        if isset(id1) :
            if isinstance(id1, str) and id1.isdigit() :
                cursor.execute("select * from %s where %s = %s" % (table, field, id1));
                #if ok :
                f=fetch_array(cursor,table)
                if f :
                    if 'zones2' in details :                # this is configured in __init__ (search "zones2")
                        for key in details['zones2'] :
                            data = details['zones2'][key]
                            code = data['code'];
                            widget = self.arw[data['widget']]
                            #code = magutils.get_text(widget)
                            (text,popups) = self.parse_code(f,code,id1, table, field);

                            self.detail_text(widget,text,popups);
                        if hasattr(mag, 'myfunctions') and hasattr(mag.myfunctions, "after_details") :
                            mag.myfunctions.after_details(id1)





    def parse_code(self, f, code, id = "", table = "", field = "", type = None) :

## global buffers, config, TagTable, central_table, main_field
        global popup_condition

        central_table = table
        main_field = field
        params = {}
        text = ""
        popups = []
        popup_condition = {}

        field_separator = config['ini']['output']['field_separator'];

        code = unicode2(code)

        # split
        out1 = code.replace("[", "|||[")
        out1 = out1.replace("]", "]|||")
        # separate values between []
        out2 = out1.split("|||")
        for val in out2 :
            params = {}
            if val[0:1] == "[" :
                # if it is a field
                # remove the [ ]
                temp = val.replace("[", "")
                temp = temp.replace("]", "")

                if type == "integer" :
                    temp = int(temp)

                # handling escaped commas
                temp2 = temp.replace(r'\\,','$')   # sometimes they are escaped twice
                temp2 = temp2.replace(r'\,','$')   # replace commas, to be able to split correctly
                ar = temp2.split(",")
                # TODO 0: check if there is a parameter
                ar2 = []
                for val in ar :
                    ar2.append(val.replace('$',","))  # restore commas replaced above

                if len(ar2) == 1 :                   # if there is no parameter
                    temp = str(temp)                # TODO : unicode is not supported. This is just a quick trick but it will not support accents
                    if (f != None) and (temp in list(f.keys())) :
                        value = f[temp]
                        if value == None :
                            value = " "
                        text += str(value)
                else :
                    for i in range(1,len(ar2)) :       # TODO: (i = 1; i <= len(ar); i+= 1)
                        temp2 = ar2[i].split("=",1)
                        # creation of the parameter list
                        if len(temp2) > 1 :
                            params[temp2[0].strip()] = temp2[1];


                    field = ar2[0];
                    field = convert_rtf_hexcode(field)
                    # Depending on the program, the code may be already written in utf-8, so let us try :
                    #if isinstance(field, str) :
                    #    field = field.encode("utf-8")  # field names are written in utf-8


                    # processing of parameters

                    if "before" in params :
                        if field in list(f.keys())  :

                            if f[field] and (f[field].strip() != ""):   #When there is no result, don't add "before"
                                text +=(params["before"]);



                    # Body text, three solutions:
                    # 1) select clause, 2) repetitive field, 3) simple field
                    if "select" in params :
                        req = params["select"] + eval(php_string(" from $central_table where $main_field = $id"))
                        cursor.execute(req)
                        res = cursor.fetchone()
                        if res :
                            out = str(res[0])
                        text +=(out);

                    elif "function" in params :
                            text += self.call_user_func(params["function"],f)

                    elif "separator" in params :
                        value = params["separator"];
                        # separating characters
                        if field in list(f.keys()) :
                            if f[field] :
                                names = f[field].split(field_separator)
                            else :
                                names = []
                        else :
                            names = []
                        artemp = []
                        for z in names :
                            bip = 0;
                            z = z.strip()           # removal of blanks

                            if "popup" in params :
                                pop = 1;
                                value2 = params['popup'].strip()
                                if value2 in popup_condition :
                                    if not z in popup_condition[value2] :
                                        pop = 0;


                                if pop == 1 :
                                    popup = "[" + z + "]";
                                    popups.append([popup,value2])
                                    artemp.append(popup)
                                    bip = 1;
                            if bip == 0 :
                                artemp.append(z);
                        text += implode(value,artemp);

                    else :
                        if field in list(f.keys()) :
                            if f[field] :
                                text +=f[field]

                    if "popup" in params and "separator" not in params :
                        if field in list(f.keys()):
                            value2 = params['popup'].strip()
                            popup = "[" + f[field] + "]";
                            popups.append([popup,value2]);
                            text += popup;

                    if "after" in params :
                        if field in list(f.keys()) :
                            if f[field] :
                                if f[field].strip() != "" :
                                    text +=(params["after"]);




            else :

                text +=(val);

        return [text,popups]

    def detail_text(self, widget, text,popups) :


        if magutils.widget_type(widget) == "GtkLabel" :         # for labels
            widget.set_markup(text);

        elif magutils.widget_type(widget) == "GtkEntry" :
            widget.set_text(text);

        elif magutils.widget_type(widget) == "GtkTextView" :        # for the textview

            w = widget.get_buffer()
            z = w.get_tag_table()

            buffer_copy = Gtk.TextBuffer()          # defined in rt_zoom.php;set the tag_table to zero
            tag_haut = Gtk.TextTag();         # hence the need to reload the top tag
            #Â£ tag_haut.set_property("name", "haut")
            tag_haut.set_property("rise",-8000);    # this tag is used to put links at text level
            tt = buffer_copy.get_tag_table();

            tt.add(tag_haut);

            parse_pango_markup = ParsePangoMarkup(buffer_copy, text);       # convert pango markup to tags
            parse_pango_markup.go();
            #buffer_copy.set_text(text) # depends on deleting the two lines above
            widget.set_buffer(buffer_copy);                          # display du résultat

            match_start = buffer_copy.get_start_iter();
            match_end = buffer_copy.get_end_iter();


            if popups:
                for val in popups :                                 # processing links
                    start_iter = buffer_copy.get_start_iter();      # find the position in the buffer
                    (match_start,match_end) = start_iter.forward_search(val[0], 0, None);     # kksou 148
                    buffer_copy.place_cursor(match_end);
                    buffer_copy.delete(match_start,match_end);      # delete text
                    val2 = str_replace(["[","]"],["",""],val[0])
                    self.ajouter_lien(widget,val2,val[1])              # replace with link



    """==============================================================================
    FONCTION   : ajouter_lien
    DESCRIPTION: insère un bouton de lien dans un TextView, ce qui permet de simuler un lien hypertext
    PARAMETRES : textview: le textview concerné
    nom : le nom qui s'affichera dans le lien
    type1 : Le modèle de popup à utiliser (voir dans la configuration)
    RETOURNE : rien
    ===============================================================================
    """

    def ajouter_lien(self,textview,nom,model) :

## if is_object(textview) == False :
## alert(textview. _(" is not an object"));
## return;

        if not model in config['popup'] :
            print(( "popup " + model + " is not configured"))
            return

        _nom = nom.strip()
        _nom = _nom.replace("'", "''")        # escape the '
        type1 = config['popup'][model]['type']
        code = config['popup'][model]['code']
        table_def = config['popup'][model]['table_def']
        table = config['peripheral'][table_def]['table']
        field = periph_tables[table]['main_field']
        req =  eval(php_string("SELECT * FROM $table WHERE $field = '$_nom'"))

        buffer1 = textview.get_buffer();
        iter1 = buffer1.get_iter_at_mark(buffer1.get_insert());

        cursor.execute(req)
        fiches = cursor.fetchone()
        (text, popups) = self.parse_code(fiches,code,"")
        if not text or not text.strip():
            buffer1.insert(iter1, nom)
            return

        anchor = buffer1.create_child_anchor(iter1);
        iter2 = buffer1.get_iter_at_mark(buffer1.get_insert());
        iter2.backward_char();
        buffer1.apply_tag_by_name("haut",iter2,iter1);

        # Create link button
        if nom != None :
            link_button1 = Gtk.LinkButton(None, nom);
            link_button1.connect('clicked', self.on_linkbutton, nom,model);

            link_button1.show();
            textview.add_child_at_anchor(link_button1,anchor);

        # Add tooltip
        link_button1.set_tooltip_markup(text)

    def on_linkbutton(self, linkbutton, url, model) :


        global config, periph_tables;

        url = url.strip()
        type = config['popup'][model]['type'];
        code = config['popup'][model]['code'];



        if type == "photo" :
            tot = zoom_images(url);

        elif type == "query" :

            req = config['popup'][model]['query'];
            req = str_replace('field',url,req);
            cursor.execute(req);
            fiches = cursor.fetchone()

            (text,popups) = self.parse_code(fiches,code,"");
            alert(text);


        else :


            table_def = config['popup'][model]['table_def'];
            table = config['peripheral'][table_def]['table'];
            field = periph_tables[table]['main_field'];
            if db_type == "sqlite" :
                url = url.replace("'", "''")
            req =  eval(php_string("SELECT * FROM $table WHERE $field = '$url'"))
            # TODO: escape ' for mysql
            cursor.execute(req);
            fiches = cursor.fetchone()

            (text,popups) = self.parse_code(fiches,code,"");
            alert(text);





    def detail_plein_ecran(self, button,event) :

        global mem;
        x = event.button;

        if mem['detail_plein_ecran']==0 :

            if x == 1 :
                # left button
                self.arw['s_vpaned1'].set_position(2000);
                mem['detail_plein_ecran']=1;

            else :

                self.arw['s_vpaned1'].set_position(0);
                mem['detail_plein_ecran']=1;


        else :

            position_i = config['ini']["Hpaned"]['s_vpaned1']
            self.arw['s_vpaned1'].set_position(position_i);
            mem['detail_plein_ecran']=0;


        return False;


    def switch_nb2(self, a = None, b = None, c = None) :

        # This function is launched when the current page changes in the result window
        global link, cursor, db_structure, db_active_file
        nb=self.arw['s_notebook2'];
        page = nb.get_current_page();
        if page == -1 :     # There is not yet a page active
            return
        current_page=nb.get_nth_page(page);
        liste = self.arw['s_list2' + str(page)];
        # line = result['line_active'][page];
        if page < 0 :
            return;

        if page <10 :
            mem['result_page'] = page;

            if page in affichage and "db_active" in affichage[page] :
                if affichage[page]["db_active"][3] != db_active_file :
                    self.arw["db_active_file"].set_text(affichage[page]["db_active"][3])
                    link, cursor, db_structure, db_active_file = affichage[page]["db_active"]
                    self.refresh_all_lists()
            v2(mem,'status')
            if page in mem['status'] :
                self.arw["status"].set_text(mem['status'][page])
            # TODO : Add an if, otherwise crash if the control does not exist
            label = nb.get_tab_label(current_page);
            text=label.get_text();
            self.arw['s_onglet_actif'].set_text(text);


            details_tab = v(affichage,page,'details_tab');

            if isinstance(details_tab, str) and details_tab.isdigit() :
                if int(details_tab) > 0 :
                    self.arw['s_notebook3'].set_current_page(int(details_tab) -1);
            else :
                self.arw['s_notebook3'].set_current_page(0);


            self.detail(liste);


    def impression(self, widget, option) :

        global mem, config, config_info, affichage
        page = mem['result_page'];
        liste = self.arw['s_list2' + str(page)];
        model=liste.get_model();


        #printfile = MessageBox("Name of the output file ", "output file",10001,None,perso['repertoire_impression']);

        dialog = Gtk.FileChooserDialog("File Save", None, Gtk.FILE_CHOOSER_ACTION_SAVE,
        (Gtk.STOCK_OK, Gtk.ResponseType.OK), None);
        dialog.show_all();
        if dialog.run() == Gtk.ResponseType.OK :
            file1 = dialog.get_filename();      # get the input filename


        dialog.destroy();

        iters=iter_sel(liste);
        if len(iters) < 2 :
            # if there is no selection, we save everything
            iters=array_iter(model);

        else :

            button1_s = _("All")        # labels of buttons
            button2_s = _("Selection")
            button1_s = button1_s.encode("utf-8")
            button2_s = button2_s.encode("utf-8")
            dialog = Gtk.Dialog(title=_("Records to export"),
                                parent = None,
                                flags = Gtk.DIALOG_MODAL |Gtk.MESSAGE_QUESTION,
                                buttons = (button1_s, 1, button2_s, 2));
            dialog.show_all();
            if dialog.run() == 1 :          # if user chooses to print all
                iters=array_iter(model);
            dialog.destroy();

        # Seek extension
        tmp, extension = os.path.splitext(option);

        # extract format

        f1 = open(os.path.join(configdir_u, "models", unicode2(option)))

        before = "";
        after = "";
        text_format = ""

        if extension == ".txt" :
            text_format = f1.read()

        elif (extension == ".htm") or(extension == ".html") :

            index = 0
            body = ""


            data = f1.readlines()
            for line in data :

                if re.match("(?i).*</body>", line) :
                    index = 2;

                if index == 0 :
                    before += line;
                else :
                    if index == 1 :
                        body += line;
                    else :
                        after += line;

                if re.match("(?i).*<body>", line) :
                    index = 1;
            text_format = body;

        elif (extension == ".rtf") :


            data = f1.read()
            data = data.replace("\n", "")       # is replaced because TextMaker may insert end of lines everywhere
            find = re.findall(r"(?ms)(.*?)(\\trowd.*\\row[ }]*)(.*})",data)[0]  # selects beginnning and end of the table
            before = find[0]
            text_format = find[1]
            #text_format += r"\pard\widctlparadjustright \par " # adds a line between records
                                                                    # TODO: make it customizable
            after = find[2]


        f1.close()

        # generate output file
        tmp, ext = os.path.splitext(file1);
        if ext == "" :
            file1 = file1 + extension;

        f1 = open(file1,"w");
        f1.write(before)


        if v(config, 'print', option, 'type') :
            if config['print'][option]['type'] == "liste" :

                # TODO 0: this is not a widget if widget_type(model) == "GtkTreeModelSort" :

                source_model = model.get_model();


                for iter in iters :
                    iter2 = model.convert_iter_to_child_iter(iter);
                    row = source_model[iter2];
                    text = self.parse_code(row,text_format,"","integer");
                    #text = self.parse_code(row,format,"");
                    fputs(f1,text[0]);


        else :


            central_def = affichage[page]['central_def'];
            table = config['central'][central_def]['table'];
            id_field = config['central'][central_def]['id_main'];

            lines = []
            for s in iters :
                id1 = model.get_value(s, 0)


                req = eval(php_string("select * from $table where $id_field = $id1"))
                cursor.execute(req);
                while True :
                    fiche = fetch_array(cursor, table)
                    if not fiche :
                        break
                    text = self.parse_code(fiche,text_format);


                    if text :
                        if (extension == ".rtf") :      # correct the line ends, because \n is without effect in Rtf and we lose the line ends
                            text[0] = text[0].replace("\n", "\\\n")

                        #  RTF ne supporte pas directement l'utf8
                        # Characters not recognized by cp1252 are replaced by their xml code, written: &#xxx;
                        # we replace &# by \u, which gives a valid rtf code for unicode : \uxxx

                        try :
                            text2 = text[0].encode("cp1252")
                            f1.write(text2)
                        except :
                            text2 = text[0].encode("cp1252", "xmlcharrefreplace")
                            text2 = text2.replace("&#", r"\u")
                            f1.write(text2)






        f1.write(after)
        f1.close();



##
## tmp, ext = os.path.splitext(file1);
## if ext == "" :
## file1 = file1 + "." + extension;
## f1.write(record[0])
## for i in range(1,len(record)) :
## f1.write(r"\widctlparadjustright { \par }")
## f1.write(record[i])






    def impression2(self, widget, option) :         # old version - no longer used

        global mem, config, config_info, affichage;
        page = mem['result_page'];
        liste = self.arw['s_list2' + str(page)];
        model=liste.get_model();

        #printfile = MessageBox("Name of the output file ", "output file",10001,None,perso['repertoire_impression']);

        dialog = Gtk.FileChooserDialog("File Save", None, Gtk.FILE_CHOOSER_ACTION_SAVE, # note 2
        [Gtk.STOCK_OK, Gtk.ResponseType.OK], None);
        dialog.show_all();
        if dialog.run() == Gtk.ResponseType.OK :
            file = dialog.get_filename();
            # get the input filename

        dialog.destroy();


        iters=iter_sel(liste);
        if len(iters) < 2 :
            # if there is no selection, we save everything
            iters=array_iter(model);

        else :

            ar_selection = {"tout" : _("All"), "selection" : _("Selection")}
            selection =    MessageBox(_("Records to export"),"sortie",9,ar_selection);
            if selection != "selection" :
                iters=array_iter(model);





        file = file + "." + config['print'][option]['extension'];
        f1 = fopen(file,"w");
        fputs(f1, config['print'][option]['before']);

        format = config['print'][option]['code'];

        if config['print'][option]['type'] == "liste" :

            # TODO 0: this is not a widget if widget_type(model) == "GtkTreeModelSort" :

                source_model = model.get_model();


        for iter in iters :
            iter2 = model.convert_iter_to_child_iter(iter);
            row = source_model[iter2];
            text = self.parse_code(row,format,"","integer");
            fputs(f1,text[0]);


        else :


            table = affichage[page]['main_table'];
            id_field = affichage[page]['main_id_field'];

            for s in iters :
                lines.append(model.get_value(s, 0))

            ids=implode(",",lines);
            req = "select * from table where id_field in (ids)";
            cursor.execute(req);

            while True :
                fiche = cursor.fetchone()
                if fiche == None :
                    break
                text = parse_code(fiche,format);
                outputText = utf8_decode(text[0]);
                # TODO: put this as parameter
                fputs(f1,outputText);




        fputs(f1, config['print'][option]['after']);
        fclose(f1);




    # =========================================================
    # The following functions handle list editing mode
    # ==========================================================
    def mode_edition(self, widget) :

        """==============================================================================
    DESCRIPTION:  affiche ou cache à la place de la zone détail
    la zone d'écran qui permet l'édition en liste
    ==============================================================================
    """
        global cr_editable;


        if self.arw['s_edition_liste'].get_active() == True :
            # self.arw['s_edit_frame'].show();
            # self.arw['scrolledwindow1'].hide();
            for j in range(0,40) :
                cr_editable[j].set_property('editable', True);


        else :

            # self.arw['s_edit_frame'].hide();
            # self.arw['scrolledwindow1'].show();
            for j in range(0,40) :
                cr_editable[j].set_property('editable', False);


    def details_edition(self, widget,event) :


        if self.arw['s_edition_liste'].get_active() == True :
            self.detail_edition(widget,event);


    """==============================================================================
    DESCRIPTION:  fonction appelée par un signal sur la liste. Cette fonction cherche
    le titre de la colonne pour déterminer le type de données et affiche le fenêtre d'édition
    ==============================================================================
    """
    def detail_edition(self, widget,event) :

        global mem, stores, listes, alias;
        # alias is defined in the choose_display function

        x=event.x;
        y=event.y;
        path = widget.get_path_at_pos(int(x),int(y));
        state = event.state;
        event_type = event.type.value_name # TODO : is this OK ?


        if isset(path) :
            treemodelsort = widget.get_model();
            model=treemodelsort.get_model();
            iter = model.get_iter(path[0]);
            id= model.get_value(iter, 0);

            title = path[1].get_title();
            # column title
            # TODO alias
            if title in alias :
                title = alias[title];

            cols=widget.get_columns();
            colnum=array_search(path[1],cols,True);
            mem['edition_colonne_active'] = colnum;
            data = model.get_value(iter, colnum);


        if 'zoomy' in mem and mem['zoomy']:
            mem['zoomy'].dialog.destroy();

        if substr(title,0,2) == "g_" :
            table = substr(title,2);
            zoom = zoomy(table, id);

        else :
            if state == 4 :
                zoom = zoom(data);
                text = mem['zoom_text'];
                model.set(iter, colnum, text);
                edit_list("","",text,"");
            else:
                zoom = None


        mem['zoomy'] = zoom;
        mem['type_liste_edition']=event_type;
        mem['titre_liste_edition']=title;



    def edit_list(self, cr,path,texte,col) :

        """ appelée par les cell_renderer de l'édition en mode liste et par le bouton Enregistrer dans compléte, via

    """

        update = 0;
        central_table_fields = {}
        page = mem['result_page'];
        sheet=self.arw['s_list2' + str(page)];
        treemodelsort = sheet.get_model();
        store = treemodelsort.get_model();
        id_livre = get_sel_row_data(sheet,0,0);

        (path2,colonne) = sheet.get_cursor();
        champ=colonne.get_title();
        # TODO alias
        if champ in alias :
            champ = alias[champ];

        iter=store.get_iter(path);
        id = store.get_value(iter,0);


        # search for the table and its main field #: optimize by putting in display
        central_def = affichage[page]['central_def'];
        table = config['central'][central_def]['table'];
        id_main = config['central'][central_def]['id_main'];
        central_table_fields[table] = {}

        # TODO 00 : optimize ? it's a bit cumbersome to do this at each edition
        # Create the list of fields of the central table

        # List of numeric types
        numeric = ['int', 'float', 'bool', 'bit', 'dec', 'double', 'real', 'numeric', 'fixed']

        # TODO: if for mysql
## cursor.execute("show columns from table");
## for i in range(0, mysql_num_rows(result)) :
## data = cursor.fetchone()
## field = data['Field'];
## type = data['Type'];
## type_num = "";
## for val in numeric :
## if strpos(type,val) > 0 : type_num = "num";
##
## central_table_fields[table][field] = type_num;

        req = "PRAGMA table_info(" + table + ")"
        cursor.execute(req)
        for row in cursor :
            field = row[1];
            type_num= row[2]
            central_table_fields[table][field] = type_num;




        texte1 = texte;
        if champ in central_table_fields[table] :

            if central_table_fields[table][champ] == "num" :
                if texte=="" :
                    texte='null';

            else :
                texte = self.Chaine_guillemets(texte);

            update = 1;

        if update == 1 :

            req = eval(php_string("update $table set $champ = $texte where $id_main = $id_livre"))
            ok=cursor.execute(req);
            sql_error(link, req);
            link.commit()
            #self.arw['s_edition_state'].set_text(mysql_info(link));

            # update the displayed list with the data stored in the complete table
            if col != "" :
                store.set(iter, col, texte1);




        else :

            alert(sprintf(_("Editing the field %s is not allowed."), champ));


    def Enregistrer(self) :

        global config, mem;

        page = mem['result_page'];
        liste = self.arw['s_list2' + str(page)];
        id_livre = get_sel_row_data(liste,0,0);
        colnum = mem['edition_colonne_active'];



        text = get_text(self.arw['s_edition_text']);
        (path,col) = liste.get_cursor();
        edit_list("",path,text,colnum);



        # update the displayed list with the data stored in the complete table
        treemodelsort=liste.get_model();
        store=treemodelsort.get_model();
        (path,col) = liste.get_cursor();
        iter=store.get_iter(path);
        store.set(iter,colnum,text);




    def zooms(self, widget,event,typex) :


        # for CTRL + z; but you would have to reconnect key-press-event
        # if (event.keyval==gdk.KEY_z or event.type==gdk.KEY_Z :
        # and event.state == 4)


        if (event.type==gdk._2BUTTON_PRESS
            and(event.state == 4 or event.state == 8)) :
            # with CTRL or ALT

            if typex == "TextView" :
                if event.state == 4 :
                    zoom = zoom(widget)

                else :

                    zoom = rt_zoom(widget);

            elif typex == "Entry" :
                zoom = zoom(widget);

            widget.emit_stop_by_name('button-press-event');
            return True;

        else :

            return False;













    def police(self, objets, fonte,action = 0,incr = 0) :

        """==============================================================================
        FONCTION   : police
        DESCRIPTION: modifie la taille de police des objets
        PARAMETRES : vide et event . inutilisés, sont envoyés par le bouton de commande
        action . + pour augmenter, autre chose pour réduire
        incr . valeur d'augmentation par millième de point
        objets . array d'objets qui seront modifiés.
        RETOURNE :   rien
        ==============================================================================
        """
        global  mem;

        x = fonte.get_size();
        if action == "+" :
            x = x + incr;
        else :
            x = x - incr;
        fonte.set_size(x);

        for z in objets :
            val = objets[z]
            type = widget_type(val);
            if type in ["GtkButton", "GtkComboBox", "GtkComboBoxEntry"]:
                text = objets[z].get_child();
                text.modify_font(fonte)
            try :
                objets[z].modify_font(fonte);
            except :
                pass

    def font_up(self, widget, event = None) :
        #for group in[self.arTextView, self.arEntries] :
        for group in[self.arw] :
            self.police(group, self.fonte1, "+", 1000)

    def font_down(self, widget, event = None) :
        for group in[self.arw] :
            self.police(group, self.fonte1, "-", 1000)

    def reinit_list(self, widget) :


        global  mem;

        page = mem['result_page'];
        liste = self.arw['s_list2' + str(page)];
        sortmodel = liste.get_model();
        store = sortmodel.get_model();
        store.clear();
        mem['config_liste'][page] = 0;






    def Chaine(self, chai) :

        #trans2={"'" : "\'", '"' : "\"', "\" : "\\\\"}
        if db_type == "mysql" :
            return str_replace(['\\',"'",'"'], ['\\\\', "\\'", '\\"'], chai)
        elif db_type == "sqlite" :
            return str_replace("'", "''", chai)

    def Chaine_guillemets(self, chai) :

        if chai=="" :
            final="null";

        else :
            if db_type == "mysql" :
                chai = chai.replace("\\", "\\\\")
                chai = chai.replace("'","\\'")
                chai = chai.replace('"', '\\"')

            elif db_type == "sqlite" :
                chai = chai.replace("'","''")
            final = "'" + chai + "'"

        return final




    def drag_data_get_data2(self, treeview, context, data, target_id, etime) :

        treeselection = treeview.get_selection();
        (model, iter) = treeselection.get_selected();
        if iter==None :
            return;

        name = treeview.get_name();
        id = model.get_value(iter, 20);
        nom = model.get_value(iter, 0);


        data1 = serialize([name, id, nom, add1, add2])
        data1 = base64_encode(data1);
        # necessary for the transmission of accented characters
        # otherwise they are converted to \Uxxxx and I can't decode that
        data.set_text(data1);


    def drag_data_received_data2(self, widget, context, x, y, data, info, time) :


        return
        """
        model = widget.get_model();
        drop_info = widget.get_dest_row_at_pos(x, y);
        (dest_path, position) = drop_info;

        data1 = base64_decode(data.data);
        data2 = eval(data1);
        name = array_shift(data2);


        if name == widget.get_name() :
            # reorder
            if drop_info :

                dest_iter = model.get_iter(dest_path);
                src_selection = widget.get_selection();
                (src_model, src_iter) = src_selection.get_selected();


                if position == Gtk.TREE_VIEW_DROP_BEFORE :
                    src_model.move_before(src_iter,dest_iter);


                elif position in [Gtk.TREE_VIEW_DROP_AFTER,
                        Gtk.TREE_VIEW_DROP_INTO_OR_BEFORE,
                        Gtk.TREE_VIEW_DROP_INTO_OR_AFTER] :
                    src_model.move_after(src_iter,dest_iter);




        else :

            # copy
            ncol = model.get_n_columns();
            data2 = (len(data2) > ncol) ?  array_slice(data2,0,ncol) : array_pad(data2,ncol,"");


            if drop_info :
                switch (position)
                case gtk:
                    :TREE_VIEW_DROP_BEFORE :
                    model.insert(dest_path[0], data2) ;
                    break;

                case gtk:
                    :TREE_VIEW_DROP_AFTER :
                case gtk:
                    :TREE_VIEW_DROP_INTO_OR_BEFORE :
                case gtk:
                    :TREE_VIEW_DROP_INTO_OR_AFTER :
                    model.insert(dest_path[0] + 1, data2) ;
                    # dropped after the selected line
                    break;


            else :

                model.append(data2);



        """


    def help(self, object) :

        name = utils.get_extension(object.get_name());
        command = "start \"title\" \"doc/" + name + "\"";
        #Attention start takes a first parameter between quotes which is the title of the window
        exec(command);





    # ============================================================================================+= 1+
    #
    # C O L O N N E S
    #
    # ================================================================================================

    def ____________Colonnes____________() :
        pass
    def open_columns(self, widget) :


        self.maj_liste_col();
        self.montrer("s_columns",3);




    def maj_liste_col(self) :


        global  stores, mem, alias ;

        page = mem['result_page'];
        liste=self.arw['s_list2' + str(page)];
        listecol=self.arw['s_liste_colonnes'];
        store=stores['liste_cols'];
        store.clear();
        colonnes=liste.get_columns();
        titres = [];
        for z in colonnes :
            titres.append(z.get_title())

        for z in titres :
            titre = z
            if z != " " :
                if not v(self.colonnes_resultat,page) :
                    alert( "result page not yet configured (you must display at least one record)")
                    return False
                if not v(self.colonnes_resultat,page,z) :
                    if z in alias :         # If the name of the column is not that of the field
                        z = alias[z]
                    else :
                        alert ("Unknown column : " + z + ". Verify the configuration of the result list")
                        store.append(["???",False,0,True,True])
                        continue

                if not z in self.colonnes_resultat[page] :
                    print(z, " : pas trouvé")
                    continue
                data = self.colonnes_resultat[page][z];
                if data and len(data) > 2 :
                    if data[1] == "0":
                        data[1] = False
                    elif data[1] == "1" :
                        data[1] = True
                    #z1 = [data[0],bool(data[1]),int(data[2]),True,True]
                    z1 = [titre,bool(data[1]),int(data[2]),True,True]   # test : modified to display the name of the column instead of the field name
                    store.append(z1);
                    #titles2.append(z) what is it for?

    def toggle_cols(self, button,path) :

        global  stores, mem;

        page = mem['result_page'];
        liste=self.arw['s_list2' + str(page)];
        store=stores['liste_cols'];
        # listecol=self.arw['s_liste_colonnes'];
        iter1=store.get_iter(path);
        col=store.get_value(iter1,0);
        visible=store.get_value(iter1,1);
        # listecol.set_selectable(n,False);
        col2=liste.get_column(int(path));

        if visible==True :
            col2.set_visible(False);
            store.set(iter1,1,False);
            self.colonnes_resultat[page][col][1] = False;

        else :

            col2.set_visible(True);
            store.set(iter1,1,True);

            self.colonnes_resultat[page][col][1] = True;





    # ============================================================================================+= 1+
    #
    # T R I
    #
    # ================================================================================================
    """==============================================================================
    FONCTION   : tri_perso
    DESCRIPTION:  fonction inachevée et inutilisée qui devrait charger dans la fenêtre d
                    de tri les valeurs d'un tri personnalisé.
                    Idéalement devrait permettre aussi d'enregistrer un tri
                    sans avoir à passer par le configurateur
    PARAMETRES :
    RETOURNE :
    ==============================================================================
    """

    def _________Tri_perso______________() :
        pass

    def open_sort(self, widget) :

        self.maj_liste_col();
        self.montrer("s_tri",3);


    def tri_perso(self, trier = 1) :

        global result,  col_view, mem, tris_predefinis;


        for i in range(0, mysql_num_fields(result)) :

            nomchamp=mysql_field_name(result, i);
            listechamps.append(nomchamp)



        t1=list(tris_predefinis.keys())
        # could be used to dynamically name predefined sort buttons
        if trier == 1 :
            set_tris_predef();



        # self.arw['s_tri'].show_all();
        return True;



    def set_tris_predef(self, debug) :

        global tris_predefinis,  config;

        criteres = []


        # process the parameters

        i=0;
        for data in criteres :
            n1=strpos(data," ");
            if i > 2 :
                return;

            self.arw['s_descendant' + (i+1)].set_active(False);
            self.arw['s_numerique' + (i+1)].set_active(False);

            if n1==0 :
                self.arw['s_combo_tri_entry' + (i+1)].set_text(data);

            else :

                self.arw['s_combo_tri_entry' + (i+1)].set_text(substr(data,0,n1));
                switchs = substr(data,n1);
                if strpos(switchs,"d")!=0 :
                    self.arw['s_descendant' + (i+1)].set_active(True);

                if strpos(switchs,"n")!=0 :
                    self.arw['s_numerique' + (i+1)].set_active(True);

            i+= 1;


    def open_tools(self, widget) :

        if isinstance(widget, str) :
            tab = widget;
        else :
            tab = utils.get_extension(widget);
            tab = int(tab) - 1
        self.montrer("s_tools",3);
        mag.arw['s_notebook21'].set_current_page(tab);


    def import_csv_file(self, *params) :

        filepath_u = None
        records = csv.loadfile(filepath_u)
        self.records = records
        self.len_records = len(records)
        self.check_next_author("")


    # =========================================================
    # The following functions handle the display in the details area
    # ==========================================================#




    # edit function: opens the input window and loads the selected records into the input list,
    # or all the records if only one is selected
    def modifier(self, widget) :

        global  mem, affichage, config;

        ids = []
        page = mem['result_page'];
        clist = self.arw['s_list2'+ str(page)];
        store=clist.get_model();

        iters = iter_sel(clist);

        if len(iters) > 1 :
            # only load the selection
            for iter1 in iters :
                ids.append(store.get_value(iter1, 0))

            premier = 0;

        else :

            # load all, but display the selected record
            id_selection= store.get_value(iters[0], 0);
            # book_id of the selected row
            iters = array_iter(store);
            i=0;
            for iter1 in iters :
                ids.append(store.get_value(iter1, 0));
                # all the book_id of the list
                if ids[i] == id_selection :
                    index = i;

                i+= 1;

            premier = index;



        self.load_fiche(ids,premier);

        # open the right tab
        central_def = affichage[page]['central_def'];
        if 'edit_tab' in config['central'][central_def] :
            n = config['central'][central_def]['edit_tab'];
            self.arw['s_notebook4'].set_current_page(int(n) - 1);
        self.montrer('window4',1);





    # function modify2 : opens the input window and loads the selected records into the input list,
    # This function is intended to be called from the search lists, not from the result list
    # It must receive the relevant list as a parameter
    def modifier2(self, liste) :

        global  mem, affichage, treeview_data, config;

        clist = liste;
        store=clist.get_model();

        iters = iter_sel(clist);

        if len(iters) > 1 :
            # only load the selection
            for iter1 in iters :
                ids.append(store.get_value(iter1, 0))

            premier = 0;

        else :

            # load all, but display the selected record
            id_selection= store.get_value(iters[0], 0);
            # book_id of the selected row
            iters = array_iter(store);
            i=0;
            for iter1 in iters :
                ids[i]= store.get_value(iter1, 0);
                # all the book_id of the list
                if ids[i] == id_selection :
                    index = i;

                i+= 1;

            premier = index;





        # load the record and open the right tab
        nom_liste = liste.get_name();
        table_config = treeview_data[nom_liste]['table'];
        n = config['peripheral'][table_config]['edit_tab'];


        load_fiche(ids,premier,table_config);
        self.arw['s_notebook4'].set_current_page(n - 1);
        self.montrer('window4',1);


    # function modify3: Create a new record.
    # This function opens the input window and opens a new record.
    # To simplify, this function actually loads a form (the first one in the template),
    # so that the load_file function can set all the parameters
    # necessary for editing. Then the new_file function is started immediately.
    def modifier3(self, widget) :

        global  mem, affichage, config;

        page = mem['result_page'];
        clist = self.arw['s_list2'+ str(page)];
        store=clist.get_model();

        iter1 = store.get_iter_first()
        if iter1 :
            id1 = store.get_value(iter1, 0)
        else :                                      # aucune donnée dans la liste, donc "affichage" n'est pas initialisé. Il faut contourner le prooblème
            if len(config["central"]) == 1 :   # If there is only one central table defined, it can be chosen without risk
                central_def = list(config['central'].keys())[0]
                central_table = config['central'][central_def]['table']
                id_main = config['central'][central_def]["id_main"]
                req = "select %s from %s limit 1" % (id_main, central_table)
                cursor.execute(req)
                id1 = cursor.fetchone()[0]
                page = mem['result_page']
                affichage[page]['central_def'] = central_def

            else :
                return    # TODO : message to say that the central table cannot be chosen



        self.load_fiche([id1],0)
        self.nouv_fiche("")

        # open the right tab
        central_def = affichage[page]['central_def'];
        n = config['central'][central_def]['edit_tab'];
        self.arw['s_notebook4'].set_current_page(int(n) - 1);
        self.montrer('window4',1);

    def rafraichir(self, widget) :

        global mem, resultat;
        page = 'page' + str(mem['result_page']);

        req = resultat[page]['requete'];
        if req == "" :
            alert(_("There is no query recorded for this list."));

        else :

            self.chercher(req,0);

        self.montrer('window2');



    """==============================================================================
    FONCTION   : Supprimer_fiche
    DESCRIPTION:  Supprime une fiche et la copie dans la table des fiches supprimées
    PARAMETRES :
    RETOUR     :
    ==============================================================================
    """
    def supprimer_fiche(self, widget) :

        global  mem, affichage, config;

        page=mem['result_page'];
        central_table = affichage[page]['main_table'];
        main_field = affichage[page]['main_id_field'];


        clist2=self.arw['s_list2' + str(page)];


        sel=clist2.get_selection();
        if sel.count_selected_rows() > 1 :
            message(_("more than one line"));

        else :

            (model, arPaths) = sel.get_selected_rows();
            iter = model.get_iter(arPaths[0]);
            id = model.get_value(iter, 0);


            temp1 = _("Are you sure you want to delete the record %s")% id ;
            question = yes_no_dialog(temp1);
            if question == True :
                central_def = affichage[page]['central_def'];
                req = eval(php_string("delete from $central_table where $main_field= $id"))
                result = cursor.execute(req);

                for key in config['peripheral'] :
                    val = config['peripheral'][key]
                    gateway = val['gateway'];
                    if val['central_def'] == central_def and len(gateway) > 0 :
                        req = eval(php_string("delete from $gateway where $main_field = $id "))
                        result = cursor.execute(req)



                # ok=cursor.execute("insert into FichesSuppr(select * from central_table where main_field=id)");
                # ok=cursor.execute("update DeletedFiles set datesdeletion = now() where main_field =id");
                # result = cursor.execute("insert into central_table(main_field,notes) values(id,\"b\")");
                # recreate an empty form with note "b", so that the number is reused

                link.commit()
                self.rafraichir("");





    def ok_historique(self, widget) :

        global  mem, affichage, link, query;
        liste=self.arw['s_historique'];
        # source
        liste2 = self.arw['s_list2' + str(mem['result_page'])];
        # destination
        page = mem['result_page'];

        model=liste.get_model();
        # TODO
        arIter = iter_sel(liste);
        if len(arIter) == 0 :
            alert(_("there is no line selected"));

        else :

            row = model[arIter[0]];
            affichage[page] = eval(row[2])
            titre = row[0];
            mem['historique']="non";
            mem['nom_requete'] = titre;

            ajouter = None
            for line in arIter :
                row = model[line];
                requete = row[3];
                self.chercher(requete, 1, ajouter);
                # for the first one, add is None
                ajouter = 1;


        self.montrer('window2');
        self.arw['s_notebook2'].set_current_page(mem['result_page']);






    """==============================================================================
    FONCTION   :
    DESCRIPTION:
    PARAMETRES :
    RETOUR     :
    ==============================================================================
    """
    def save_position(self, window) :

        global  arWindows;
        global config, dialog;

        if widget_type(window) != "GtkWindow" :
            alert(_("Your button is misconfigured, \nyou must select a window as parameter."));
            return;

        name = Gtk.Buildable.get_name(window)

        (x, y) = window.get_position();
        (w, h) = window.get_size();
        v2(config, 'ini', 'position', name)
        config['ini']['position'][name]["x"] = x;
        config['ini']['position'][name]["y"] = y;
        config['ini']['position'][name]["h"] = h;
        config['ini']['position'][name]["w"] = w;

        save_settings();


    def save_panes_position(self, widget = "") :

        for key  in self.arHPaned :
            val = self.arHPaned[key ]

            position = val.get_position();
            v2(config['ini'], "Hpaned")
            config['ini']['Hpaned'][key] = position
            self.arw[key].set_position(position)
        save_settings()


    def db_save(self, widget ) :

        # TODO: set compression as an option

        chooser = Gtk.FileChooserDialog(title=_('Save database...'),
                action=Gtk.FILE_CHOOSER_ACTION_SAVE,
                buttons=(Gtk.STOCK_CANCEL,
                    Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_SAVE,
                    Gtk.ResponseType.ACCEPT))
        chooser.set_do_overwrite_confirmation(True)
        #chooser.set_current_folder(???)
        dirname_u,filename_u = os.path.split(db_file)
        (name_u,ext_u) = os.path.splitext(filename_u)

        date1 = datetime.date.today()
        today_u = unicode2(date1.isoformat())
        name_u = name_u + " " + today_u  + ext_u + ".zip"
        chooser.set_current_name(name_u)

        response = chooser.run()

        if response == Gtk.ResponseType.CANCEL:
            chooser.destroy()
            return

        elif response == Gtk.ResponseType.ACCEPT:
            filename = chooser.get_filename()
            filename_u = str(filename, "utf-8")
            chooser.destroy()

        if os.path.splitext(filename_u)[1] != ".zip" :
            filename_u += "zip"


        if db_file.lower().replace("\\", "/") == filename_u.lower().replace("\\", "/") :
            alert(_("You cannot overwrite your existing database.\nAborting"))
            return

        try :
            output = zipfile.ZipFile(filename_u, "w", zipfile.ZIP_DEFLATED)
            db_filename = os.path.split(db_file)[1]
            output.write(db_file, db_filename)
            output.close()

        except :
            utils.printExcept()




    def db_restore(self, widget, filename_u = None) :
        global config1

        if filename_u == None :
            chooser = Gtk.FileChooserDialog(title=_('_Open Database'),
                    action=Gtk.FILE_CHOOSER_ACTION_OPEN,
                    buttons=(Gtk.STOCK_CANCEL,
                        Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OPEN,
                        Gtk.ResponseType.OK))
            chooser.set_current_folder(configdir_u)
            chooser.set_show_hidden(True)  #Test : does not work. Why ??

            filter_all = Gtk.FileFilter()
            filter_all.set_name(_('All files'))
            filter_all.add_pattern('*')
            chooser.add_filter(filter_all)

            filter_ini = Gtk.FileFilter()
            filter_ini.set_name(_('SQLITE files'))
            filter_ini.add_pattern('*.sqlite')
            filter_ini.add_pattern('*.db3')
            filter_ini.add_pattern('*.sqlite.zip')
            chooser.add_filter(filter_ini)
            chooser.set_filter(filter_ini)

            response = chooser.run()
            if response == Gtk.ResponseType.OK:
                filename = chooser.get_filename()
                filename_u = str(filename,"utf-8")            # convert utf-8 to unicode for internal use

                if zipfile.is_zipfile(filename_u) :
                    print("====>", filename_u, " zipped")


            elif response == Gtk.ResponseType.CANCEL:
                print((_('Closed, no files selected')))
                chooser.destroy()
                return
            chooser.destroy()


    def create_backup(self, auto = None, *params) :


        (db_dir, db_name) = os.path.split(db_file)
        (name_u,ext) = os.path.splitext(db_name)
        date1 = datetime.date.today()
        today_u = unicode2(date1.isoformat())
        name_u = name_u + " " + today_u  + ".zip"

        backup_name_u = os.path.join(db_dir,"backup",name_u)
        if auto == True :
            if os.path.isfile(backup_name_u) :         # Automatic backup only once a day.
                return                                 # TODO : keep only a limited number of backups.
            if ("autobackup" in config["ini"]["database"]
                and config["ini"]["database"]["autobackup"] == 0) :     # Automatic backup only if configured
                return
            else:
                self.dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.INFO,Gtk.ButtonsType.CLOSE,
                               _("Automatic Backup running, please wait"))

                self.dialog.show_all()

                while Gtk.events_pending():
                    Gtk.main_iteration()


        if not os.path.isdir(os.path.join(db_dir,"backup")) :
            os.makedirs(os.path.join(db_dir,"backup"))

        try :
            output = zipfile.ZipFile(backup_name_u, "w", zipfile.ZIP_DEFLATED)
            db_filename = os.path.split(db_file)[1]

            files_list = glob.glob(os.path.join(configdir_u, "*"))     # add all config files
            files_list.append(db_file)
            for filename_u in files_list :
                if os.path.isfile(filename_u) :
                    output.write(filename_u, os.path.split(filename_u)[1])


            msg2 = output.namelist()
            output.close()

            if auto == None:
                msg = _("The backup of %s has been created successfully. \n It contains the following files :\n\n") % configname_u
                for name1 in msg2 :
                    msg += name1 + "\n"

                alert(msg)
            else :
                self.dialog.destroy()


        except :
            alert(_("There was a problem during the backup. \nSome files may have been saved nevertheless, \n Please, verify"))
            utils.printExcept()

        try:
            self.dialog.destroy()

        except :
            pass


    def side_panel(self, button) :

        global  config;

        name = Gtk.Buildable.get_name(button)
        gtkpaned = substr(name,strrpos(name,'@')+1);

        if button.get_active() == True :
            if self.arw[gtkpaned] :
                self.arw[gtkpaned].set_position(0);

        else :
            if self.arw[gtkpaned] :
                v2(config['ini'], 'Hpaned')
                if gtkpaned in config['ini']['Hpaned'] :
                    pos = config['ini']['Hpaned'][gtkpaned];
                    if pos > 2  :
                        self.arw[gtkpaned].set_position(pos);
                    else :
                        self.arw[gtkpaned].set_position(100);
                else :
                        self.arw[gtkpaned].set_position(100);






    def plein_ecran(self) :

        global mem

        if mem['ecran'] == "max" :

            self.arw['s_window'].fullscreen();
            mem['ecran'] = "full";

        else :

            self.arw['s_window'].unfullscreen();
            #self.arw['s_window'].maximize();


            mem['ecran'] = "max";




    def window_show(self, window) :

        if is_object(window) :
            window.show();

        else :

            self.arw[window.get_name()].show();


    def window_hide(self, window) :
        # TODO : it works but not very elegant.
        try :
            #if is_object(window) :
            window.hide();
        except :
            self.arw[window.get_name()].hide();



    def open_history(self, widget) :

        self.montrer("s_history",3)


    def open_about(self,widget) :           # TODO: does not work
        global  config;
        self.montrer("s_aboutdialog1",3);

    def montrer(self, widget, mode = 0, resize = 0) :
        # debug : resize était à 0. This does not work. It should do that redimensioning happens
        # only the first time, so that if you resize within a session
        # it is preserved. With 1, each time you close and reopen, the saved size is restored.
        # The easiest way would be to do this resize
        if isinstance(widget, str) :
            name = widget;
        else :
            name = utils.get_extension(widget);

        self.arw['s_tri'].hide();
        self.arw['s_columns'].hide();


        window = None
        tab = None
        if name.isdigit() :
            tab = int(name)

        elif name in ["window0", "window2"]  :
            tab = 2;
            window = "s_window"

        elif name in ['window4'] :
            tab = 3;
            window = "s_window"
        elif name in ['s_tri', 's_columns', 's_combine', 's_history', 's_window',
                        's_complex', 's_requetes', 's_options', 's_tools'] :
            window = name;


        if tab :
            tab = tab -1;
            if  tab >=0 :
                self.arw['s_notebook'].set_current_page(tab);


        if window :
            self.arw[window].present();


            win=self.arw[window].get_window()        # get the GdkWindow

## if resize == 1 :
## if 'position' in config['ini']:
## if window in config['ini']['position']:
## h = config['ini']['position'][window]["h"];
## w = config['ini']['position'][window]["w"];
## x = config['ini']['position'][window]["x"];
## y = config['ini']['position'][window]["y"];
##
## if win :
## win.move_resize(x, y, w, h);
## if mode == 3 :
## win.set_keep_above(True);


        """
        if plein_ecran==0 :
            #if mem['ecran']=="max" :
                win.maximize();

            #if mem['ecran']=="full" :
                win.fullscreen();


        # if full_screen==1 :
            win.maximize();

        # if full_screen==2:
            win.fullscreen();
        """



class utilities () :

    @staticmethod
    def get_extension(widget, separator = "@") :

        # extract the extension of the object name
        # if the extension has several parameters separated by , we return an array
        # otherwise return the extension as a string

        global config;

        if isinstance(widget, str) :
            name = widget;
        else :
            name = Gtk.Buildable.get_name(widget);

        extension = re.sub(".*" + separator, "" , name)


        if extension :
            arParams = extension.split(",")
            if len(arParams) == 1 :
                return extension;
            else :
                return arParams;
        else :
            return None

    @staticmethod
    def printExcept() :
        a,b,c = sys.exc_info()
        message_s = ""

        if a == None:
            return None
        result = traceback.format_exception(a,b,c)
        for d in result :
            print(d, end=' ')
            message_s += d
        return message_s


    @staticmethod
    def dict_or_OrdDict_to_formatted_str(OD, mode='dict', s="", indent=' '*4, level=0):
        def is_number(s):
            try:
                float(s)
                return True
            except ValueError:
                return False
        def fstr(s):
            return s if is_number(s) else '"%s"'%s
        if mode != 'dict':
            kv_tpl = '("%s", %s)'
            ST = 'OrderedDict([\n'; END = '])'
        else:
            kv_tpl = '"%s": %s'
            ST = '{\n'; END = '}'
        for i,k in enumerate(OD.keys()):
            if type(OD[k]) in [dict, OrderedDict]:
                level += 1
                s += (level-1)*indent+kv_tpl%(k,ST+utilities.dict_or_OrdDict_to_formatted_str(OD[k], mode=mode, indent=indent, level=level)+(level-1)*indent+END)
                level -= 1
            else:
                s += level*indent+kv_tpl%(k,fstr(OD[k]))
            if i!=len(OD)-1:
                s += ","
            s += "\n"
        return s



# def get_option : extracts the desired option from an options string :
def get_option(option,string) :

    string = string.replace(",", ";")
    temp = string.split(";")
    for data in temp :

        if data.strip() == option.strip() :

            return 1

        else :

            temp2 = data.split("=")
            if temp2[0].strip() == option.strip() :

                value = temp2[1]
                return value.strip()



        return None;
        # if option not found

def first_config() :

    global config, config_info, periph_tables, periph_tables2, order_field, modified_field, treeview_data;

    if len(config['ini']['database']['order_field'])>0 :
        order_field = config['ini']['database']['order_field']
    else :
        order_field = "s_order";

    if v(config, 'ini', 'database', 'modified_field') :
        modified_field = config['ini']['database']['modified_field']
    else :
        modified_field = "s_modified";



    # create the list of peripheral tables defined in config.php
    periph_tables = {}
    periph_tables2 = {}
    for key  in config['peripheral'] :
        val = config['peripheral'][key]

        #val['config_name'] = key;

        if 'gateway' in val :                  # relation n:n (with gateway)
            if len(val['gateway']) > 0 :
                val['table_type'] = "peripheral2";
                # get additional fields in the gateway table
                if val['table'] in config["gateway_data"] :
                    temp4 = []
                    for a in config["gateway_data"][val['table']]["cols"] :
                        fieldname = config["gateway_data"][val['table']]["cols"][a]["field"]
                        temp4.append(fieldname)

                    val["gateway_fields"] = temp4

        else :
            val['table_type'] = "peripheral1";      # relation 1:n (without gateway)


        if 'table' in val :
            periph_tables[val['table']] = val;
        if 'config_name' in val :
            periph_tables2[val['config_name']] = val        # TODO : problem if two peripheral definitions for the same table.
                                                            # This solution is not fully implemented but should work
        else :
            message = config_error('config_name', 'config.peripheral', key)
            alert(message)

    if config['words'] :
        for key  in config['words'] :
            val = config['words'][key ]

            val['config_name'] = key;
            val['table_type'] = "words";
            periph_tables[val['table']] = val;


    treeview_data = {}
    # create the list of tabs defined in config.py
    for key  in config['xtabs'] :
        val = config['xtabs'][key ]

        val['config_name'] = key;
        if 'treeview' in val :
            treeview_data[val['treeview']] = val;



    # create config_info

    config_info = {}
    config_info['central_tables'] = {}
    config_info['periph_tables'] = {}
    config_info['gateways'] = {}
    config_info['periph_def'] = {}
    config_info['words_tables'] = {}
    config_info['search_lists'] = {}
    config_info['details'] = {}
    config_info['result'] = {}

    # central tables
    if 'central' in config :

        for key in config['central'] :
            val = config['central'][key ]
            config_info['central_tables'][val['table']] = copy.deepcopy(val)

            # create references to details
            if 'details' in config['central'][key] :
                details = config['central'][key]['details']
                if len(details.strip()) > 0 :
                    details_list = details.split(",")           # details parameter may be a comma separated list
                    for value in details_list :
                        config_info['details'][value] = {}
                        config_info['details'][value]['central_def'] = key

            # create references to results
            if 'result' in config['central'][key] :
                result = config['central'][key]['result']
                if len(result.strip()) > 0 :
                    result_list = result.split(",")           # result parameter may be a comma separated list
                    for value in result_list :
                        config_info['result'][value] = {}
                        config_info['result'][value]['central_def'] = key





    if 'words' in config :
        for key  in config['words'] :
            val = config['words'][key ]

            # word tables that use this table
            central_def = val['central_def'];
            if central_def in config['central'] :
                table = config['central'][central_def]['table'];
                if not 'words' in config_info['central_tables'][table] :
                    config_info['central_tables'][table]['words'] = key + ",";
                else :
                    config_info['central_tables'][table]['words'] = key + ",";




    # peripheral tables and gateways
    for key  in config['peripheral'] :
        val = config['peripheral'][key ]
        if 'table' not in val :
            continue

        config_info['periph_tables'][val['table']] = val;
        if 'gateway' in val :

            v2(config_info, 'gateways',val['gateway'],'name')
            config_info['gateways'][val['gateway']]['name'] = val['gateway']

        if 'gateway_data' in config:

            for key in config['gateway_data'] :       # add info from gateway_data
                gd = config['gateway_data'][key]
                if 'gateway' in gd and 'gateway' in val :
                    if gd['gateway'] == val['gateway'] :

                        config_info['gateways'][val['gateway']]['data'] = gd['cols'];


    # peripheral definitions (merges peripheral and words tables)

    if config['peripheral'] :

        for key  in config['peripheral'] :
            val = config['peripheral'][key ]
            config_info['periph_def'][key] = val;

    if config['words'] :
        for key  in config['words'] :
            val = config['words'][key ]


            if key in config_info['periph_def'] :

                msg = _("The name %s is already used for a peripheral table, it cannot be used for a words table !") % key
                alert(msg);

            config_info['periph_def'][key] = val;





    # words tables
    if config['words'] :

        for key  in config['words'] :
            val = config['words'][key ]
            config_info['words_tables'][val['table']] = val;




    # search lists and combine
    for key  in config['xtabs'] :
        try :
            val = config['xtabs'][key ]

            config_info['search_lists'][val['treeview']] = val;
            config_info['search_lists'][val['treeview']]['name'] = key;
            table_def = val['table_def'];
            table = v(config_info,'periph_def',table_def,'table');
            config_info['search_lists'][val['treeview']]['peripheral_table'] = table;
            central_table_def = v(config_info,'periph_def',table_def,'central_def');
            central_table = v(config,'central',central_table_def,'table');
            config_info['search_lists'][val['treeview']]['central_table'] = central_table;

            if table in config_info['periph_tables'] :

                if 'search_lists' in config_info['periph_tables'][table] :
                    temp = config_info['periph_tables'][table]['search_lists']
                    try :
                        temp += "," + val['treeview'];
                    except :        # bad configuration
                        config_info['periph_tables'][table]['search_lists'] = val['treeview']
                    # TODO: check: should temp be reassigned?

                else :
                    config_info['periph_tables'][table]['search_lists'] = val['treeview']

        except :        # TODO: this should be done for all blocks above
            print("Error in configuration for search lists")






def config_defaults() :

    global config;

    if not "font" in config['ini']['lists'] :
        config['ini']['lists']["font"] = "sans";

    if not "font_size" in config['ini']['lists'] :
        config['ini']['lists']["font_size"] = 10;

    if not "line_height" in config['ini']['lists'] :
        config['ini']['lists']["line_height"] = 18;

    if not "type_delay" in config['ini']['lists'] :
        config['ini']['lists']["type_delay"] = 1000;

    if not "max_lines" in config['ini']['lists'] :
        config['ini']['lists']["max_lines"] = 300;

    if not "field_separator" in config['ini']['output'] :
        config['ini']['output']["field_separator"] = "|";

def verify_config() :
    for key in ["xtabs", "central", "peripheral","result", "details", "inversion", "popup", "gateway_data",
                "combobox", "fieldlist","words", "ini"]  :
        if not key in config :
            config[key] = {}
        if config[key] == None :
            config[key] = {}


def save_settings(widget = "") :

        global settings, config;

         # Backup configuration in JSON
        if os.path.exists(os.path.join(configdir_u, 'config.json')):
            shutil.copyfile(os.path.join(configdir_u, 'config.json'), os.path.join(configdir_u, 'config.json.bak'))

        # Backup configuration in config.py
        if os.path.exists(os.path.join(configdir_u, 'config.py')):
            shutil.copyfile(os.path.join(configdir_u, "config.py"), os.path.join(configdir_u, "config.bak"))

        pp = pprint.PrettyPrinter(indent = 4, width = 100)
        data1 = pp.pformat(config)
        f3 = open(os.path.join(configdir_u,"config.py"),"w")
        f3.write(data1)
        f3.close()

        with open(os.path.join(configdir_u, 'config.json'), 'w') as f:
            f.write(json.dumps(OrderedDict(config), indent=3, ))



def FormatPath (path,type = 0) :
    if type == 1 : path = path.replace(":","")
    path = path.replace("\\","/")
    path = path.replace("//","/")
    return(path)

def recordFilenames(label_s, dest_u) :
    pass

def unicode2(string) :
    if isinstance(string,str) :
        return string
    else :
        print("unicode2 has been used")
        try :
            return str(string,"utf_8")
        except :
            try :
# print string, "is written in cp1252"
                return str(string,"cp1252")
            except :
                return string       # Is this the good option ? Return False or an empty string?
                return "inconnu"

def print2(string, lineEnd = 0) :
    locmsg_s = time.strftime("%x, %X",time.localtime()) + " | "
    if isinstance(string,str) :
         print(string.encode("cp1252"))              # March 10th, 2012 - Averell
         locmsg_s += string.encode("cp1252")
    else :
        try :
            print(string)   # if we send utf8, we will get utf8 the screen.
            locmsg_s += string
        except :
            print("Non unicode string. Couldn't be printed")
            locmsg_s += "Non unicode string. Couldn't be printed"
    locmsg_s += "\r\n"
    ftrace = open("Trace.log","a")
    ftrace.write(locmsg_s)
    ftrace.close()

# Utilities




def implode(separator,mylist) :

    # separator.join(mylist) : We cannot use it , invalid if numbers in list
    temp = ""
    if len(mylist) > 0 :
        temp = str(mylist[0])
        for d in mylist[1:] :
            temp += separator + str(d)
    return temp

def explode(separator, data) :
    if data :
        return data.split(separator)
    else :
        return []


def isset(myObject) :
    if myObject == None :
        return False
    try:
        a = myObject
        return True
    except:
        return False

##def set_array(array, keys, value) :
## for key in keys :
## if array.has_key(key):
## array = array[key]
## else:
## array[key] = myDict()
## array = array[key]
## return True



def alert(message, dummy = 0) :
        message_parts = message.split("\n")
        message2 = ""
        for part in message_parts :
            if len(part) > 150 :
                for i in range(0, len(part), 150) :
                     message2 += part[i:i+150] + "\n"

            else :
                message2 += part[0:300] + "\n"

        dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.INFO,Gtk.ButtonsType.CLOSE,
                               message2)
        dialog.run()
        dialog.destroy()

def yes_no_dialog(message, dummy = 0) :
        dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.INFO,Gtk.ButtonsType.YES_NO,
                               message)
        answer = dialog.run()
        dialog.destroy()
        if answer == Gtk.ResponseType.YES :
            return True
        else :
            return False

def get_sel_row_data(treeview,row,col) :

    sel=treeview.get_selection();

    (model, arPaths) = sel.get_selected_rows();
    if isset(model) and len(arPaths) >= row and len(arPaths) > 0 :
        iter = model.get_iter(arPaths[row]);
        data = model.get_value(iter, col);
        return data;
    else :
        return None;





def get_field(result_row,table,field) :
    # sqlite
    field_index = db_structure[table][field]
    return result_row[field_index]


    #mysql
    return result_row[field]


def fetch_array(cursor, table = None) :
    # Returns an array of all the result, in the form obtained by the MySql function fetch_array
    # with numerical keys and field keys

    global db_structure, db_type



    if db_type == "mysql" :
        return cursor.fetchone()

    result_array = {}
    if table :      # sqlite
        row =cursor.fetchone()
        if not row :
            return None
        i = 0
        for a in row :
            result_array[i] = a         # numerical key
            i += 1
        for s in cursor.description :
            result_array[s[0]] = row[s[0]]

    return result_array


def BOM(file_f) :
        # If BOM present, skip the first three bytes
        isBOM_s = file_f.read(3)
        if isBOM_s == chr(239) + chr(187) + chr(191) :  # There is a BOM, skips it
            pass
        else :
            file_f.seek(0)                             # No BOM, come back to beginning of file


###########################################################################
# MAIN ####################################################################
###########################################################################

def main():

    # init
    usage_s = \
        "%prog [options]\n" + \
        "\tbackup filesystem"
    isExcept = False
    excMsg_s = ""
    global chars, config, myfunctions, mag, ml, alias
    global col_view,fonte1, fonte2;    #???
    global config_info, configdir_u, configname_u, config_defaults, config_dialog, con
    global db_structure, db_type, db_active
    global mem, resultat, affichage
    global arw, query, cr_editable, stores, modelsort, checkbox_list


    mem = {}
    chars = {}
    affichage = {}
    resultat = {}
    cr_editable = {}
    stores = {}
    modelsort = {}
    arw = {}
    query = {}
    checkbox_list = {}
    db_active = {}

    t1 = time.time()

    mem["elements_req"] = ""
    mem["update_query"] = 0


    global selector, utils

    # parse command line
    parser = OptionParser(usage = usage_s)
    parser.add_option(
            "-v",
            "--version",
            dest="version",
            action="store_true",
            default=False,
            help="display script version")

    parser.add_option(
            "-i",
            "--ini",
            dest="ini",
            help="specify ini/task file",
            metavar="ini")

    # get opt
    (option_v, arg_a) = parser.parse_args()

    try :

        # get the configuration
        configname_u = None
        if len(arg_a) > 0 :         # if the config is indicated on the command line

            if len(arg_a[0].strip()) > 0 :
                configname_u = unicode2(arg_a[0])

        if not configname_u :           # ask for config
                config_dialog = ask_for_config()
                configname_u = config_dialog.run()

        tmp_u = unicode2(os.path.abspath("./"))
        if os.name == "nt":
            configdir_u = os.path.join(tmp_u, "config", configname_u)
        else:
           configdir_u = "/usr/share/maggy/config/" + configname_u

        # load plugins

        import imp
        if os.path.isfile(os.path.join(configdir_u, "userfunctions.py")) :
            myfunctions = imp.load_source("standard.myfunctions", os.path.join(configdir_u, "userfunctions.py"))

        # load the configuration

        if os.path.exists(os.path.join('./config', configname_u, 'config.json')):
        # if False:
            # Load configuration via JSON
            with open(os.path.join('./config', configname_u, 'config.json'), 'r') as f:
                #config = json.load(f, cls=json_decoder.StringJSONDecoder)
                config = json.load(f,  object_pairs_hook=OrderedDict)
        else:
            f1 = open(os.path.join(configdir_u, "config.py"), "r")
            data = f1.read()
            f1.close()
            config = eval(data)

        v2(config,"ini","input")
        v2(config,"lists")
        v2(config,"ini",'output')
        try :
            x = config['ini']['output']['field_separator']  # Verify if config separator is defined.
        except :
            config['ini']['output']['field_separator'] = "|"  # else , default value
        mem["config"]="config.py"

        # change in the dictionary structure, from version 2
        # TODO : the field periph_tables is normally created by he program and should not be in the config ?

        if "version" in config :
            if int(config["version"]) < 2000 :
                for field in ["input", "output", "zoom1", "zoom2", "gui", "position", "Hpaned", "database", "lists"] :

                    if field in config :
                        config['ini'][field] = config[field]
                        del config[field]

                if 125 in config :
                    del config[125]

                config["version"] = 2000

                save_settings()

        """

        if (is_file(configdir_u . "colors.php")):
            include(configdir_u . "colors.php")
        require_once("extensions/rt_zoom.php");
        require_once("extensions/zoom_images.php");


        """


        # connexion à  la base de données
        db_utils = db_utilities()
        global link, cursor, db_structure, db_active_file
        # If a proper sqlite file is found, load it
        if 'database' in config['ini'] and 'sqlite' in config['ini']['database'] :  # If a filename is defined in the config
            db_file_sqlite = config['ini']['database']['sqlite']
            if db_file_sqlite.strip() == "" :           # sqlite db not set
                db_file_sqlite = os.path.join(configdir_u, configname_u + ".sqlite")
            else :
                if not os.path.isfile(db_file_sqlite) :
                    alert(_("Wrong file name in configuration for sqlite database :\n'%s'\nPlease correct." % db_file_sqlite))
                    os.exit(0)
        else :
            db_file_sqlite = os.path.join(configdir_u, configname_u + ".sqlite")

        db_file_sqlite2 = os.path.join(configdir_u, configname_u + ".db3")
        db_file_mdb = os.path.join(configdir_u, configname_u + ".mdb")
        db_file_accdb = os.path.join(configdir_u, configname_u + ".accdb")


        if os.path.isfile(db_file_sqlite) :
            db_type = "sqlite"
            db_file = db_file_sqlite
        elif os.path.isfile(db_file_sqlite2) :
            db_type = "sqlite"
            db_file = db_file_sqlite2
        elif os.path.isfile(db_file_mdb) :
            db_type = "mdb"
            db_file = db_file_mdb
        elif os.path.isfile(db_file_accdb) :
            db_type = "accdb"
            db_file = db_file_accdb
        else :
            db_file = None
            db_type = None

        db_active_file = db_file

        if db_type == "sqlite" :
            (link,cursor,db_structure, db_active_file) = db_utils.load_sqlite(db_file)
            db_active[1] = (link,cursor,db_structure, db_active_file)

## elif db_type == "accdb" :
##
## if not os.path.isfile(dbfile) :
## pypyodbc.win_create_mdb(dbfile)
## create_table = True
##
## connection_string = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + db_file
## #connection_string = 'Driver={Microsoft.ACE.OLEDB.12.0 (*.mdb, *.accdb)};DBQ=' + db_file
##
## link = pypyodbc.connect(connection_string)
## cursor = link.cursor()
## db_structure = {}
## TODO !!!!!!!!
## tables = ["tblArticle",
## "tblArticleCoAuthor",
## "tblAuthor",
## "tblBook",
## "tblBookCoAuthor",
## "tblCirculation",
## "tblCitation",
## "tblCity",
## "tblClass",
## "tblClassification",
## "tblCountry",
## "tblDivision",
## "tblKeyArticle",
## "tblKeyArticle Query",
## "tblKeyCitation",
## "tblKeyCitation Query",
## "tblKeyWord",
## "tblKeyWord Query",
## "tblLanguage",
## "tblPatron",
## "tblPeriodical",
## "tblPeriodical Query",
## "tblPrefix",
## "tblPublisher",
## "tblResponsibility",
## "tblRoom",
## "tblSection",
## "tblSize",
## "tblState",
## "tblSubject",
## "tblSuffix",
## "tblTheme",
## "tblTitle",
## "tblTopic",
## "zThemes2"]
##
##
## for table in tables :
## db_structure[table] = {}
## req = "select * from " + table
## try :
## cursor.execute(req)
## temp1 = cursor.description
##
## for line in temp1:
## db_structure[table][line[0]] = line[1]
## except:
## print "Could not find table ", table


        else :      # mySql
            hostLocale = config['ini']['database']['host'];
            userLocale = config['ini']['database']['user'];
            passLocale = config['ini']['database']['pass'];
            bddLocale = config['ini']['database']['database'];
            #host2 = config['ini']['database']['host2'];

            link = MySQLdb.connect(host=hostLocale,user=userLocale,passwd=passLocale, db=bddLocale, cursorclass=cursors.DictCursor);
            if (link == False):
                string = _("MySQL server not found.\nVerify it is started or check your configuration.\nContinue ? ");
                rep = yes_no_dialog(string, _("Server unreachable"));
                if (rep != -8):
                    die ;
                else:
                    mem['nodb'] = 1;


            cursor = link.cursor()
            link.query("set character set utf8");
            link.query("set names utf8");
            # Â£Â£ link.query("SET GLOBAL group_concat_max_len = 128000"); OperationalError: (1227, 'Access denied; you need the SUPER privilege for this operation')
            db_type = "mysql"
            db_structure = db_utils.mysql_db_structure(cursor)

            rep = link.select_db(bddLocale)
## if not rep:
## string = _("Database %s does not exist. Do you want to create it?") % bddLocale
## rep = yes_no_dialog(string , _("Database does not exist"));
## if (rep == -8):
## req = link.query("create database "+bddLocale+"");
## string = sprintf(_("The database %s was created but is still empty. \Do you want to load data from a file?"), bddLocale );
## rep = yes_no_dialog(string,_("Database empty"));
## if (rep == -8):
## db_restore();
## link.select_db(bddLocale);
## else:
## die(_("Problem with the database Verify your parameters in the Parameters tab of the Options dialog"));


        config_defaults();
        verify_config()
        first_config();

        #migration();

        """
        if mem['save_settings'] == 1 :
            mem['save_settings'] = 0
            save_settings();
        if (link):
            verify_database();
        """

        # initialization
        mem['historique']="";
        mem['detail_plein_ecran']=0;
        chars['index']=0;

        Gtk.rc_parse("couleurs.rc");

        utils = utilities()
        print ("strat Maggy")
        mag = Maggy()
        if not db_type == "accdb" :
            csv = Import_csv()

        # create automatic backup for sqlite
        if db_type == "sqlite" :
            gi.repository.GLib.idle_add(mag.create_backup, True )

        Gtk.main()

    except ScriptSg as instance :
        isExcept = True
        excMsg_s = "%s" % (instance)
        (excType, excValue, excTb) = sys.exc_info()
        tb_a = traceback.format_exception(excType, excValue, excTb)

    except ScriptIo as instance :
        isExcept = True
        excMsg_s = "%s" % (instance)
        (excType, excValue, excTb) = sys.exc_info()
        tb_a = traceback.format_exception(excType, excValue, excTb)

    except ScriptRt as instance :
        isExcept = True
        excMsg_s = "%s" % (instance)
        (excType, excValue, excTb) = sys.exc_info()
        tb_a = traceback.format_exception(excType, excValue, excTb)

    #Â£ except exceptions.SystemExit as instance:
    # sys.exit(instance)

    except :
        isExcept = True
        excMsg_s = "unexpected exception"
        (excType, excValue, excTb) = sys.exc_info()
        tb_a = traceback.format_exception(excType, excValue, excTb)

    # handle eventual exception
    if isExcept :
        # record exception

        print(("\nEXC: %s\n" % (excMsg_s)))
        for line_s in tb_a :
            print((line_s.strip()))
        print("\nERR: Exception reÃ§ue\n")

        dt = datetime.datetime.now()
        humanDate_s = dt.strftime("%a %x, %X ")
        l_msgerror = ""
        for line_s in tb_a :
            l_msgerror += line_s.strip()
            l_msgerror += "\n"
        print(l_msgerror)

        dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.ERROR,Gtk.ButtonsType.CLOSE,l_msgerror)

        dialog.run()
        dialog.destroy()
        sys.exit(1)

    else :
        sys.exit(0)


if __name__ == '__main__' :
    main()

# eof
