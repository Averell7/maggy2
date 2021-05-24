#!/usr/bin/python
# coding: utf-8 -*-
# Version 2.0.0.48  - April 2016
# Version 2.0.0     - Averell - GTK GUI - May 17th, 2012
# Version 1.9.6     - Gaston - Sept 03th, 2011 - Cosmetic enhancements (title, background color)
# Version 1.9.5     - Revision 5 - Mar 03rd, 2012

###########################################################################
# VERSION #################################################################
###########################################################################

'''
problème possible : result lists : si un grand nombre de lignes, comme on utilise un dictionnaire,
l'ordre des colonnes sera-t-il conservé ? Et si non, show_result_details donnera un résultat faux
Solution : Avec Python 2.7, utliser OrderedDict

central/table/result fait double emploi avec result ???
Pas entièrement, on sélectionne les résultats utilisés par cette table

'''
import json
import subprocess
from collections import OrderedDict

"""
TODO :
Pour plusieurs champs (par exemple central tables, result), si on modifie à la main au lieu de sélectionner une valeur dans la liste, le changement n'est pas mémorisé.
Il manque le champ "complement" pour xtabs (search) (voir oraisons, sources)
quand on crée une config de table périphérique, les champs de base de gateway data (cols, gateway) ne sont pas créés,
ce qui provoque des erreurs.

Edit : Gateway data est construit avec cols = '' ce qui provoque une erreur dans treeview_add2


"""
###########################################################################
# SYSTEM LIBS #############################################################
###########################################################################

import copy
import exceptions
import glob
import gtk
import pprint
import re
from copy import deepcopy
from optparse import OptionParser

gtk.rc_parse("./gtkrc")

try:
    import _mysql
    import MySQLdb
    from MySQLdb import cursors
except:
    print("Mysql modules not installed.")

try:
    import pypyodbc  # for accdb tables
except:
    print ("pypyobdc not installed. accdb database not supported")

import sqlite3 as sqlite

import magutils

###########################################################################
# LOCALISATION ############################################################
###########################################################################
import elib_intl

elib_intl.install("archeotes", "share/locale")

###########################################################################
# APPLICATION LIBS ########################################################
###########################################################################


from magutils import *
from ScriptExcept import *
import datetime

#
Windows = "ntx"
osname = os.name

# python path
if osname == "nt":
    python_path = "c:/prog2/python27/python27.exe"
else:
    python_path = "python"


def explode(separator, data):
    return data.split(separator)


def unicode2(string):
    if isinstance(string, unicode):
        return string
    else:
        try:
            return unicode(string, "utf_8")
        except:
            try:
                #               print string, " est ecrit en cp1252"
                return unicode(string, "cp1252")
            except:
                return string  # Is this the good option ? Return False or an empty string ?
                return u"inconnu"


def v2(dictionary, *keys):  # verify is the keys exist (creates level if it does not exist)
    temp1 = dictionary
    keys_num = len(keys)
    for i in range(keys_num):
        if i == 0:
            if not keys[0] in dictionary:
                dictionary[keys[0]] = {}
        elif i == 1:
            if not keys[1] in dictionary[keys[0]]:
                dictionary[keys[0]][keys[1]] = {}
        elif i == 2:
            if not keys[2] in dictionary[keys[0]][keys[1]]:
                dictionary[keys[0]][keys[1]][keys[2]] = {}
        elif i == 3:
            if not keys[3] in dictionary[keys[0]][keys[1]][keys[2]]:
                dictionary[keys[0]][keys[1]][keys[2]][keys[3]] = {}
        elif i == 4:
            if not keys[4] in dictionary[keys[0]][keys[1]][keys[2]][keys[3]]:
                dictionary[keys[0]][keys[1]][keys[2]][keys[3]][keys[4]] = {}
        elif i == 5:
            if not keys[4] in dictionary[keys[0]][keys[1]][keys[2]][keys[3]][keys[4]]:
                dictionary[keys[0]][keys[1]][keys[2]][keys[3]][keys[4]][keys[5]] = {}


###########################################################################
# CLASSES #################################################################
###########################################################################

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
##        self[arg] = myDict()
##        return self[arg]

class SqliteUnicode:
    #
    def __init__(self):
        self.collation = {"e": u"eéèêë",
                          "a": u"aàâä",
                          "i": u"iîï",
                          "o": u"oôö",
                          "u": u"uûü"}

        self.collation_ci = {}
        self.reg_exp = {}

        for a in self.collation:
            data = self.collation[a]
            self.collation_ci[a] = data + data.upper()

    def convert_to_regex(self, data):
        if data in self.reg_exp:
            return self.reg_exp[data]
        reg_string = "(?i)"
        for c in data:
            if c == "%":
                reg_string += ".*"
            elif c in self.collation_ci:
                reg_string += "[" + self.collation_ci[c] + "]"
            else:
                reg_string += c
        comp_reg = re.compile(reg_string)
        self.reg_exp[data] = comp_reg
        return comp_reg

    def like(self, a, b):
        # On a 80000 rows table :
        # original like takes 0.032s
        # this like takes 0.25 s (about 8x)
        data = self.convert_to_regex(a)
        if b == None or a == None:
            return False
        if data.match(b):
            return True
        else:
            return False

    def regexp(self, a, b):
        if b == None:
            return False
        if re.match(a, b):
            return True
        else:
            return False

    def collate(self, string1, string2):
        # print string1, string2
        return cmp(string1.lower(), string2.lower())


class db_utilities:

    def __init__(self):
        pass

    # connexion à  la base de données
    # If a proper sqlite file is found, load it

    def load_sqlite(self, db_file_s):

        # db_active_file = os.path.split(db_file_s)[1]
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
        link.create_function("like", 2, extension.like)
        link.create_function("concat_ws", -1, extension.concat_ws)
        link.create_function("clean_commas", 1, extension.clean_commas)
        link.create_function("date2year", 1, extension.date2year)
        link.create_function("date2ymd", 1, extension.date2ymd)

        # retrieve structure
        db_structure = {}

        """SELECT name FROM sqlite_master
        WHERE type  IN (?,?)
        AND name NOT LIKE ?
        UNION ALL SELECT name FROM sqlite_temp_master
        WHERE type IN (?,?)
        ORDER BY 1','table','view','sqlite_%','table','view') ;
        """

        req = "select name from sqlite_master where type in ('table')"
        cursor.execute(req)
        result = cursor.fetchall()
        for a in result:
            for b in a:
                db_structure[b] = {}
                req = "PRAGMA table_info (" + b + ")"
                cursor.execute(req)
                for s in cursor:
                    db_structure[b][s[0]] = s[1]
                    db_structure[b][s[1]] = s[0]

        return (link, cursor, db_structure, db_active_file)

    def mysql_db_structure(self, cursor):

        table_def = {}
        index_def = {}
        constraint_def = {}
        errors_count = 0

        # Extract mysql structure
        # Extract tables list
        cursor.execute("show tables")

        tables = []
        for row in cursor:
            key = row.keys()[0]
            name = row[key]
            try:
                cursor.execute("show columns from " + name)  # Test the validity of the table name.
                # We have seen a database with a table named "1" which was impossible to handle with sql commands
                tables.append(name)
            except:
                print ("WARNING : Unable to handle table " + name + "\nCheck if there is no problem with it.")

        for name in tables:

            table_def[name] = {}
            index_def[name] = {}

            # extract columns
            cursor.execute("show columns from " + name)
            columns = cursor.fetchall()
            for col in columns:
                keys = col.keys()
                colname = col['Field']
                table_def[name][colname] = {}
                table_def[name][colname]['type'] = col['Type']
                table_def[name][colname]['null'] = col['Null']
                table_def[name][colname]['primary'] = col['Key']
                table_def[name][colname]['default'] = col['Default']
                table_def[name][colname]['autoinc'] = col['Extra']

        return (table_def)

    def db_compare(self, *params):

        chooser = gtk.FileChooserDialog(title=_('_Open Configuration'),
                                        action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL,
                                                 gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_OPEN,
                                                 gtk.RESPONSE_OK))
        chooser.set_current_folder(configdir_u)
        chooser.set_show_hidden(True)  # Test : does not work. Why ??

        filter_all = gtk.FileFilter()
        filter_all.set_name(_('All files'))
        filter_all.add_pattern('*')
        chooser.add_filter(filter_all)

        filter_ini = gtk.FileFilter()
        filter_ini.set_name(_('sqlite files'))
        filter_ini.add_pattern('*.sqlite')
        filter_ini.add_pattern('*.db3')
        chooser.add_filter(filter_ini)
        chooser.set_filter(filter_ini)

        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            filename_u = unicode(filename, "utf-8")  # convert utf-8 to unicode for internal use

        elif response == gtk.RESPONSE_CANCEL:
            print(_('Closed, no files selected'))
            chooser.destroy()
            return
        chooser.destroy()

        new_records_a = []
        (link2, cursor2, db_structure2, db_active_file2) = self.load_sqlite(filename_u)

        # create columns list

        cursor.execute("select * from complete")
        row = cursor.fetchone()
        list_cols = row.keys()

        info = self.arw['s_info10']
        buffer1 = info.get_buffer()
        buffer1.set_text("")

        treeview = mag.arw["s_compare_tree"]
        model1 = treeview.get_model()

        cursor.execute("select * from complete")
        # cursor2.execute("select * from complete")
        i = 0

        for row in cursor:
            id1 = row["id_livre"]
            i += 1

            cursor2.execute("select * from complete where id_livre = %s" % id1)
            row2 = cursor2.fetchone()

            if row2:

                for field in list_cols:
                    # print field
                    # print row[field]
                    if field in row2.keys():
                        # print row2[field]
                        if row[field] != row2[field]:
                            model1.append([str(id1), field, row[field], row2[field]])

            else:
                new_records_a.append(id1)  # new records in base1

        # new records
        insertion_tv(buffer1, "\n terminé\n")
        insertion_tv(buffer1, str(i) + "records")
        temp = "\n\n NEW RECORDS :  "

        for rec in new_records_a:
            temp += str(rec) + " ,  "
        insertion_tv(buffer1, temp)

        # deleted records
        deleted_a = []
        cursor2.execute("select * from complete")
        for row2 in cursor2:
            id2 = row2["id_livre"]
            cursor.execute("select * from complete where id_livre = %s" % id2)
            row = cursor.fetchone()

            if not row:
                deleted_a.append(id2)

        temp = "\n\n DELETED RECORDS :  "
        for rec in deleted_a:
            temp += str(rec) + " ,  "
        insertion_tv(buffer1, temp)

    def is_field(self, cursor, table, field, coltype=None):

        if not table in db_structure:
            alert("Table " + table + " does not exist !")
            return False
        found = False
        if db_type == "sqlite":
            req = "PRAGMA table_info(" + table + ")"
            cursor.execute(req)
            found = False
            for row in cursor:
                if row[1] == field:
                    found = True


        elif db_type == "mysql":

            cursor.execute("DESCRIBE " + table + " " + field)
            result = cursor.fetchall()
            if len(result) > 0:
                found = True


        elif db_type == "accdb":
            cursor.execute("select * from " + table)
            data1 = cursor.description
            for line in data1:
                if line[0] == field.lower():
                    found = True

        if not found:
            if db_type == "accdb" and coltype.lower() == "text":
                coltype = "MEMO"
            # insertion_tv(buffer1, "g_" + table + " not present, we should create it")
            print table + "." + field + " not present, we should create it"
            req = "ALTER TABLE $table ADD COLUMN $field $coltype"
            req1 = eval(php_string(req))
            cursor.execute(req1)
            link.commit()

        return found


class ask_for_config:
    def __init__(self):
        # dialog = gtk.Dialog(title=None, parent=None, flags=0, buttons=None)
        self.dialog = gtk.Dialog(title='Configuration choice', parent=None, flags=gtk.DIALOG_MODAL,
                                 buttons=("OK", 1, "Cancel", 0))
        self.combo = gtk.combo_box_new_text()
        temp = glob.glob("config/*")

        for val in temp:
            if os.path.isdir(val):
                dir_name = val[7:]
                if dir_name[0:1] != "#":
                    self.combo.append_text(dir_name)
        self.combo.set_active(0)
        self.dialog.vbox.pack_start(self.combo)
        self.dialog.show_all()

    def run(self):
        result = self.dialog.run()
        reponse = self.combo.get_active_text()
        self.dialog.destroy()
        return reponse


class ask_for_input:
    def __init__(self):
        # dialog = gtk.Dialog(title=None, parent=None, flags=0, buttons=None)
        self.dialog = gtk.Dialog(title='Configuration choice', parent=None, flags=gtk.DIALOG_MODAL,
                                 buttons=("OK", 1, "Cancel", 0))
        self.entry = gtk.Entry()

        self.dialog.vbox.pack_start(self.entry)
        self.dialog.show_all()

    def run(self):
        result = self.dialog.run()
        reponse = self.entry.get_text()
        self.dialog.destroy()
        return reponse


class general_chooser_dialog:

    def __init__(self, data):
        # dialog = gtk.Dialog(title=None, parent=None, flags=0, buttons=None)
        self.dialog = gtk.Dialog(title='Configuration choice', parent=None, flags=gtk.DIALOG_MODAL,
                                 buttons=("OK", 1, "Cancel", 0))
        self.combo = gtk.combo_box_new_text()

        for val in data:
            self.combo.append_text(str(val))
        self.combo.set_active(0)
        self.dialog.vbox.pack_start(self.combo)
        self.dialog.show_all()

    def run(self):
        result = self.dialog.run()
        reponse = self.combo.get_active_text()
        self.dialog.destroy()
        return reponse


class utilities:
    def get_extension(self, widget, separator="@"):

        # extrait l'extension du nom de l'objet
        # si l'extension comporte plusieurs paramètres séparés par des , on retourne un array
        # sinon on retourne l'extension comme string

        global config

        if isinstance(widget, str):
            name = widget
        else:
            name = gtk.Buildable.get_name(widget)

        extension = re.sub(".*" + separator, "", name)

        if extension:
            arParams = extension.split(",")
            if len(arParams) == 1:
                return extension
            else:
                return arParams
        else:
            return None

    def entry_update(self, widget, *params):
        category_s, field_s = widget.name.split("@")
        response = magutils.get_text(widget)

        if category_s in ["central", "peripheral"]:
            configuration = self.database_structure_active[1]
            self.config[category_s][configuration][field_s] = response
            self.load_database_tree()

        elif category_s == "xtabs":
            configuration = self.search_active
            self.config["xtabs"][configuration][field_s] = response

        elif category_s == "inversion":
            configuration = self.inversion_active
            self.config["inversion"][configuration][field_s] = response

        elif category_s == "combobox":
            configuration = self.combobox_active
            self.config["combobox"][configuration][field_s] = response

        elif category_s == "details":
            configuration = self.details_active
            self.config["details"][configuration][field_s] = response

        elif category_s == "result":
            configuration = self.result_active
            self.config["result"][configuration][field_s] = response

        elif category_s == "popup":
            configuration = self.popup_active
            self.config["popup"][configuration][field_s] = response

    def populate_combo(self, combo, data):
        # adds a model to a combo and populates it
        # data must be a list
        model1 = gtk.ListStore(str)
        combo.set_model(model1)
        for item in data:
            model1.append([item])

        case = gtk.CellRendererText()
        combo.pack_start(case, True)
        combo.add_attribute(case, 'text', 0)
        combo.set_active(0)


class Treeview_handle:
    def __init__(self):
        pass

    def treeview_add(self, treeview):
        # adds a row to the treeview; used for first level

        dialog = ask_for_input()
        name = dialog.run()

        if treeview.name == "search_lists":
            self.config["xtabs"][name] = {}
        elif treeview.name == "result_lists":
            self.config["result"][name] = {}
        elif treeview.name == "inversion_treeview":
            self.config["inversion"][name] = {}
        elif treeview.name == "combobox_treeview":
            self.config["combobox"][name] = {}
        elif treeview.name == "details_list":
            self.config["details"][name] = {}
        elif treeview.name == "popup_list":
            self.config["popup"][name] = {}
        elif treeview.name == "gateway_data":
            self.config["gateway_data"][name] = {}

        model = treeview.get_model()
        iter1 = model.insert(1000)
        model.set_value(iter1, 0, name)

    def treeview2_select(self, treeview):

        try:
            if treeview.name == "treeview6":
                name = self.search_active
                use_config = self.config["xtabs"][name]

            elif treeview.name == "treeview5":
                name = self.result_active
                use_config = self.config["result"][name]

            elif treeview.name == "treeview7":  # Sort
                name = self.result_active
                use_config = self.config["result"][name]

            elif treeview.name == "gateway_details":  # Sort
                name = self.gateway_active
                use_config = self.config["gateway_data"][name]

            return use_config
        except:
            alert(_("no configuration selected"))

    def treeview_add2(self, treeview):
        # adds a row to the treeview; used for second level

        use_config = self.treeview2_select(treeview)
        # get the higher number
        index = 0
        for key in use_config["cols"]:
            if key > index:
                index = key
        index += 1
        use_config["cols"][index] = {}

        model = treeview.get_model()
        iter1 = model.insert(1000)

    def treeview_delete(self, treeview):
        sel = treeview.get_selection()
        model, iter1 = sel.get_selected()
        name = model.get_value(iter1, 0)
        if treeview.name == "search_lists":
            del self.config["xtabs"][name]
            model.remove(iter1)
        elif treeview.name == "result_lists":
            del self.config["result"][name]
            model.remove(iter1)
        elif treeview.name == "inversion_treeview":
            del self.config["inversion"][name]
            model.remove(iter1)
        elif treeview.name == "combobox_treeview":
            del self.config["combobox"][name]
            model.remove(iter1)
        elif treeview.name == "details_list":
            del self.config["details"][name]
            model.remove(iter1)
        elif treeview.name == "popup_list":
            del self.config["popup"][name]
            model.remove(iter1)
        elif treeview.name == "gateway_data":
            del self.config["gateway_data"][name]
            model.remove(iter1)

    def treeview_delete2(self, treeview):

        use_config = self.treeview2_select(treeview)

        sel = treeview.get_selection()
        model, arpaths = sel.get_selected_rows()
        active_row = arpaths[0][0]
        model, iter1 = sel.get_selected()

        if treeview.name == "search_lists":
            name = self.search_active
            del self.config["xtabs"][name]['cols'][active_row]
            model.remove(iter1)
        elif treeview.name == "treeview5":
            name = self.result_active
            del self.config["result"][name]['cols'][active_row]
            model.remove(iter1)
        elif treeview.name == "gateway_details":
            name = self.gateway_active
            del self.config["gateway_data"][name]['cols'][active_row]
            model.remove(iter1)
        else:
            alert(treeview.name + " not found in code; call programmer")

        self.treeview_renum(treeview)

    def treeview_renum(self, treeview):
        use_config = self.treeview2_select(treeview)
        keys = use_config['cols'].keys()
        keys.sort()
        new_dict = {}
        i = 0
        for key in keys:
            new_dict[i] = use_config['cols'][key]
            i += 1

        use_config['cols'] = new_dict
        keys = use_config['cols'].keys()
        print keys

    def treeview_down(self, treeview):
        self.treeview_up(treeview, down=1)

    def treeview_up(self, treeview, down=0):

        use_config = self.treeview2_select(treeview)
        sel = treeview.get_selection()
        model, arpaths = sel.get_selected_rows()
        # get the number of the line
        line_num = arpaths[0][0]
        if down == 1:
            newline_num = line_num + 1
        else:
            newline_num = line_num - 1

        # we want to go up one line, this means swapping row x and x - 1

        temp = {}
        temp = use_config['cols'][int(line_num)]
        use_config['cols'][int(line_num)] = use_config['cols'][int(newline_num)]
        use_config['cols'][int(newline_num)] = temp
        # redisplay list
        self.model5.clear()
        coldef = use_config["cols"]
        for s in coldef:
            data1 = []
            for field in ['field', 'title', 'width', 'visible', 'options']:
                if field in coldef[s]:
                    data1.append(coldef[s][field])
                else:
                    data1.append("")
            self.model5.append(data1)
            sel.select_path(newline_num)


class Restore(utilities, Treeview_handle):

    # parameters :

    def __init__(self):

        global table_def, link, cursor
        app = self

        self.program_dir = os.path.abspath('.').replace('\\', '/')

        self.widgets = gtk.Builder()
        self.widgets.add_from_file('./data/config_explorer.glade')
        arWidgets = self.widgets.get_objects()
        self.arw = {}
        for z in arWidgets:
            try:
                name = gtk.Buildable.get_name(z)
                self.arw[name] = z
                z.set_name(name)
            except:
                pass

        self.widgets.connect_signals(self)

        # Advanced - Treeview for db structure tab
        cell_renderer = gtk.CellRendererText()
        self.model2 = gtk.TreeStore(str, str)
        view2 = self.arw['treeview2']
        # view2.set_size_request(400, 620);
        view2.append_column(gtk.TreeViewColumn('Folders / Files', cell_renderer, text=0))
        view2.append_column(gtk.TreeViewColumn('Folders / Files', cell_renderer, text=1))
        view2.set_model(self.model2)

        # treeview3 - presently unused
        self.model3 = gtk.TreeStore(str, str)
        view3 = self.arw['treeview3']
        # view3.set_size_request(400, 620);
        view3.append_column(gtk.TreeViewColumn('Folders / Files', cell_renderer, text=0))
        view3.append_column(gtk.TreeViewColumn('Folders / Files', cell_renderer, text=1))
        view3.set_model(self.model3)

        # Advanced search
        self.model4 = gtk.ListStore(str, str, str, str)
        view4 = self.arw['treeview4']
        cr = {}
        for j in range(0, 5):
            cr[j] = gtk.CellRendererText()
            cr[j].connect("edited", self.edit_list_search, j,
                          "treeview4")  # cette procÃ©dure permet au cell-renderer de renvoyer le numÃ©ro de la colonne
            cr[j].connect("editing-started", self.edit_treeview_started, j, "treeview4")
            cr[j].set_property('editable', True)

        view4.append_column(gtk.TreeViewColumn('niveau', cr[0], text=0))
        view4.append_column(gtk.TreeViewColumn('nom', cr[1], text=1))
        view4.append_column(gtk.TreeViewColumn('etoile', cr[2], text=2))
        view4.append_column(gtk.TreeViewColumn('centrale', cr[3], text=3))
        # view4.append_column(gtk.TreeViewColumn('visible', cr[4], text=4));
        # view4.append_column(gtk.TreeViewColumn('options', cr[5], text=5));
        view4.set_model(self.model4)

        # result lists details
        self.model5 = gtk.ListStore(str, str, str, str, str)
        view5 = self.arw['treeview5']
        cr = {}
        for j in range(0, 7):
            cr[j] = gtk.CellRendererText()
            cr[j].connect("edited", self.edit_list,
                          j)  # cette procÃ©dure permet au cell-renderer de renvoyer le numÃ©ro de la colonne
            cr[j].connect("editing-started", self.edit_treeview_started, j, "treeview5")
            cr[j].set_property('editable', True)

        view5.append_column(gtk.TreeViewColumn('field', cr[0], text=0))
        view5.append_column(gtk.TreeViewColumn('title', cr[1], text=1))
        view5.append_column(gtk.TreeViewColumn('width', cr[2], text=2))
        view5.append_column(gtk.TreeViewColumn('visible', cr[3], text=3))
        view5.append_column(gtk.TreeViewColumn('options', cr[4], text=4))
        view5.set_model(self.model5)

        # search lists details
        self.model6 = gtk.ListStore(str, str, str, str, str, str)
        view6 = self.arw['treeview6']
        cr = {}
        for j in range(0, 7):
            cr[j] = gtk.CellRendererText()
            cr[j].connect("edited", self.edit_list_search, j,
                          "treeview6")  # cette procÃ©dure permet au cell-renderer de renvoyer le numÃ©ro de la colonne
            cr[j].connect("editing-started", self.edit_treeview_started, j, "treeview6")
            cr[j].set_property('editable', True)
        # view3.set_size_request(400, 620);
        view6.append_column(gtk.TreeViewColumn('field', cr[0], text=0))
        view6.append_column(gtk.TreeViewColumn('title', cr[1], text=1))
        view6.append_column(gtk.TreeViewColumn('width', cr[2], text=2))
        view6.append_column(gtk.TreeViewColumn('detail', cr[3], text=3))
        view6.append_column(gtk.TreeViewColumn('options', cr[4], text=4))
        view6.append_column(gtk.TreeViewColumn('-', cr[5], text=5))
        view6.set_model(self.model6)

        # treeview for checkboxes
        self.model7 = gtk.ListStore(str, str, str, str, str, str)
        view7 = self.arw['treeview7']
        cr = {}
        for j in range(0, 6):
            cr[j] = gtk.CellRendererText()
            cr[j].connect("edited", self.edit_list_search, j,
                          "treeview7")  # cette procÃ©dure permet au cell-renderer de renvoyer le numÃ©ro de la colonne
            cr[j].connect("editing-started", self.edit_treeview_started, j, "treeview7")
            cr[j].set_property('editable', True)
        view7.append_column(gtk.TreeViewColumn('name', cr[0], text=0))
        view7.append_column(gtk.TreeViewColumn('sort1', cr[1], text=1))
        view7.append_column(gtk.TreeViewColumn('sort2', cr[2], text=2))
        view7.append_column(gtk.TreeViewColumn('sort3', cr[3], text=3))
        view7.append_column(gtk.TreeViewColumn('-', cr[4], text=4))
        view7.append_column(gtk.TreeViewColumn('-', cr[5], text=5))
        view7.set_model(self.model7)

        # treeview for gateway details
        self.gateway_details_model = gtk.ListStore(str, str, str, str, str, str)
        view = self.arw['gateway_details']
        cr = {}
        for j in range(0, 6):
            cr[j] = gtk.CellRendererText()
            cr[j].connect("edited", self.edit_list_search, j,
                          "gateway_details")  # cette procÃ©dure permet au cell-renderer de renvoyer le numÃ©ro de la colonne
            cr[j].connect("editing-started", self.edit_treeview_started, j, "gateway_details")
            cr[j].set_property('editable', True)
        view.append_column(gtk.TreeViewColumn(_('field'), cr[0], text=0))
        view.append_column(gtk.TreeViewColumn(_('title'), cr[1], text=1))
        view.append_column(gtk.TreeViewColumn(_('width'), cr[2], text=2))
        view.append_column(gtk.TreeViewColumn(_('type'), cr[3], text=3))
        view.append_column(gtk.TreeViewColumn('-', cr[4], text=4))
        view.append_column(gtk.TreeViewColumn('-', cr[5], text=5))
        view.set_model(self.gateway_details_model)

        # treeview for configuration selection (displays a list of possible choices)
        self.model8 = gtk.ListStore(str)
        view8 = self.arw['treeview8']
        # view3.set_size_request(400, 620);
        view8.append_column(gtk.TreeViewColumn(_('Selector'), cell_renderer, text=0))
        view8.set_model(self.model8)

        ##        colmenu = gtk.TreeViewColumn('Details', cell_renderer, text=0)
        ##        colmenu.set_resizable(True)
        ##        self.arw['details_list'].append_column(colmenu)

        # treeview for search lists
        self.search_model = gtk.ListStore(str)
        self.arw['search_lists'].set_model(self.search_model)
        cell_renderer = gtk.CellRendererText()
        colmenu = gtk.TreeViewColumn('Search', cell_renderer, text=0)
        colmenu.set_resizable(True)
        self.arw['search_lists'].append_column(colmenu)

        # treeview for inversion
        self.inversion_model = gtk.ListStore(str)
        view9 = self.arw['inversion_treeview']
        view9.append_column(gtk.TreeViewColumn(_('Selector'), cell_renderer, text=0))
        view9.set_model(self.inversion_model)

        # treeview for combobox
        self.combobox_model = gtk.ListStore(str)
        view10 = self.arw['combobox_treeview']
        view10.append_column(gtk.TreeViewColumn(_('Selector'), cell_renderer, text=0))
        view10.set_model(self.combobox_model)

        # treeview for details
        self.details_model = gtk.ListStore(str)
        view11 = self.arw['details_list']
        view11.append_column(gtk.TreeViewColumn(_('Details'), cell_renderer, text=0))
        view11.set_model(self.details_model)

        # treeview for popups
        self.popup_model = gtk.ListStore(str)
        view12 = self.arw['popup_list']
        view12.append_column(gtk.TreeViewColumn(_('Popups'), cell_renderer, text=0))
        view12.set_model(self.popup_model)

        # treeview for gateway_data
        self.edit_model = gtk.ListStore(str)
        view13 = self.arw['gateway_data']
        view13.append_column(gtk.TreeViewColumn(_('Edit'), cell_renderer, text=0))
        view13.set_model(self.edit_model)

        self.model_dbdetails = gtk.TreeStore(str, str)
        ##        view_dd = self.arw['database_details']
        ##        #view3.set_size_request(400, 620);
        ##        cr_editable = gtk.CellRendererText();
        ##        cr_editable.connect("edited", self.edit_db_struct);
        ##        cr_editable.set_property('editable', True);
        ##        view_dd.append_column(gtk.TreeViewColumn('Folders / Files', cell_renderer, text=0));
        ##        view_dd.append_column(gtk.TreeViewColumn('Folders / Files', cr_editable, text=1));
        ##        view_dd.set_model(self.model_dbdetails);

        config_store = gtk.TreeStore(str, str, int, str)  # display, color, level, central config name
        self.arw['database_tree'].set_model(config_store)
        colmenu = gtk.TreeViewColumn('Database', cell_renderer, markup=0, foreground=1)
        colmenu.set_resizable(True)
        self.arw['database_tree'].append_column(colmenu)

        if os.path.exists(os.path.join('./config', configname_u, 'config.json')):
            # Load configuration via JSON
            with open(os.path.join('./config', configname_u, 'config.json'), 'r') as f:
                self.load_ini(json_data=json.load(f))
        else:
            # Load configuration via python file
            myinifile = os.path.join("./config", configname_u, "config.py")
            if not os.path.isfile(myinifile):
                alert("config.ini file not found. New file created")
                f1 = open(myinifile, "w")
                f1.close()
            self.load_ini(myinifile)
        self.load_glade_objects(os.path.join("./config", configname_u, configname_u + ".glade"))

        # Configuration de l'interface

        # choix des couleurs
        model1 = gtk.ListStore(str, str, str, str)
        treeview = self.arw['colors_list']
        treeview.set_model(model1)

        cell_renderer = gtk.CellRendererText()
        colnew = gtk.TreeViewColumn("", cell_renderer, text=0)
        colnew.set_fixed_width(200)
        colnew.set_resizable(True)
        treeview.append_column(colnew)

        ##        if colors :
        ##
        ##            for key  in colors :
        ##                data = colors[key ]
        ##                append(model1,[key,data));

        ##        self.arw['save_colors_button'].connect("clicked","save_colors1");
        ##        self.arw['colors_list'].connect("cursor_changed","show_selected_colors");
        ##        self.arw['f_color_button'].connect("color-set","colors_selection","f");
        ##        self.arw['b_color_button'].connect("color-set","colors_selection","b");

        # choix de la langue
        files = glob.glob("locale/*")
        combo = self.arw['language_combo']
        model = gtk.ListStore(str)
        combo.set_model(model)
        for i in range(0, len(files)):

            filex = substr(files[i], 7)
            model.append([filex])
            if filex == config['gui']['language']:
                combo.set_active(i)

        combo.pack_start(cell_renderer)
        combo.set_attributes(cell_renderer, text=0)

        ##        # treeview de gauche
        ##        treeview2 = self.arw['config_periph'];
        ##        treeview2.set_model(gtk.ListStore(str,str,str));
        ##        renderer = gtk.CellRendererText();
        ##        column = gtk.TreeViewColumn('Title', renderer, text=0);
        ##        treeview2.append_column(column);
        ##        treeview2.append_column(gtk.TreeViewColumn('Title', renderer, text=2));
        ##        treeview2.connect('row-activated', self.load_data2);
        ##        treeview2.connect('cursor-changed', self.load_data2);
        ##        treeview2.set_reorderable(True);
        ##        treeview2.get_model().connect_after('rows-reordered', "reorder_list");
        ##        # ne fonctionne pas dans php-gtk2 2.0

        """
        # champs de saisie de la partie gauche
        for z in range(2,10) :

            self.arw['config_data' + str(z)].connect('changed',update_data2);

        temp = self.arw['config_data1'].get_buffer();
        temp.connect_simple('changed',"update_data2");

        # champs de saisie de droite
        for z in ['2', '3', '4', '5') :

            self.arw['config_dataB' . z].connect_simple('changed',"update_data_cols", "B");

        temp = self.arw['config_dataB1'].get_buffer();
        temp.connect_simple('changed',"update_data_cols", "B");

        # champs de saisie de la troisiÃ¨me liste
        for z in ['2', '3', '4') :

            self.arw['config_dataC' . z].connect_simple('changed',"update_data_cols", "C");

        temp = self.arw['config_dataC1'].get_buffer();
        temp.connect_simple('changed',"update_data_cols", "C");
        """

        ##        # Liste des colonnes
        ##        treeview3 = self.arw['config_cols'];
        ##        treeview3.set_model(gtk.ListStore(str,str,str));
        ##        renderer3 = gtk.CellRendererText();
        ##        column3 = gtk.TreeViewColumn(_('Columns'), renderer3, text=0);
        ##        treeview3.append_column(column3);
        ##        treeview3.append_column(gtk.TreeViewColumn('Title', renderer, text=2));
        ####        treeview3.connect('row-activated', 'load_data_cols',"B");
        ####        treeview3.connect('cursor-changed', 'load_data_cols',"B");
        ##        treeview3.set_reorderable(True);
        ####        treeview3.get_model().connect_after('rows-reordered', "reorder_list_cols");
        ##        # ne fonctionne pas dans php-gtk2 2.0
        ##
        ##        # TroisiÃ¨me liste
        ##        treeview4 = self.arw['config_comp'];
        ##        treeview4.set_model(gtk.ListStore(str,str,str));
        ##        renderer4 = gtk.CellRendererText();
        ##        column4 = gtk.TreeViewColumn(_('Columns'), renderer4, text=0);
        ##        treeview4.append_column(column4);
        ##        treeview4.append_column(gtk.TreeViewColumn('Title', renderer, text=2));
        ####        treeview4.connect('row-activated', 'load_data_cols',"C");
        ####        treeview4.connect('cursor-changed', 'load_data_cols',"C");

        # onglet paramÃ¨tres

        try:
            (link, cursor) = self.connect()
        except:
            (link, cursor) = (None, None)  # TODO : message d'erreur mais erreur non forcément fatale
        if db_type == "sqlite":
            table_def = sqlite_db_structure()
        elif db_type == "mysql":
            table_def = db_utils.mysql_db_structure(cursor)
        elif db_type == "accdb":
            table_def = access_db_structure()

        self.populate_tree(table_def, self.model2)

        window1 = self.arw["window1"]
        window1.show()
        # window1.set_title("Restore ARCHEOTES  [ 2.0 - RC6 ]")
        window1.connect("destroy", lambda w: gtk.main_quit())
        self.arw["quit_program"].connect("destroy", lambda w: gtk.main_quit())

        # view.expand_all()

    def connect(self):

        # connexion à  la base de données
        global db_type
        # If a proper sqlite file is found, load it
        db_file_sqlite = os.path.join(configdir_u, configname_u + ".sqlite")
        db_file_sqlite2 = os.path.join(configdir_u, configname_u + ".db3")
        db_file_mdb = os.path.join(configdir_u, configname_u + ".mdb")
        db_file_accdb = os.path.join(configdir_u, configname_u + ".accdb")

        if os.path.isfile(db_file_sqlite) or os.path.isfile(db_file_sqlite2):
            db_type = "sqlite"
            db_file = db_file_sqlite
        elif os.path.isfile(db_file_mdb):
            db_type = "mdb"
            db_file = db_file_mdb
        elif os.path.isfile(db_file_accdb):
            db_type = "accdb"
            db_file = db_file_accdb
        else:
            db_file = None
            db_type = None

        if db_type == "sqlite":
            link = sqlite.connect(db_file)
            # optimize performances
            # cnx.isolation_level = "DEFERRED"
            link.row_factory = sqlite.Row
            cursor = link.cursor()
            extension = SqliteUnicode()
            link.create_collation("test", extension.collate)
            link.create_function("regexp", 2, extension.regexp)
            link.create_function("like", 2, extension.like)


        elif db_type == "accdb":

            ##        if not os.path.isfile(db_file) :
            ##            pypyodbc.win_create_mdb(db_file)

            connection_string = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + db_file
            link = pypyodbc.connect(connection_string)
            cursor = link.cursor()

        else:
            host = self.config["ini"]["database"]["host"]
            user = self.config["ini"]["database"]["user"]
            password = self.config["ini"]["database"]["pass"]
            bdd = self.config["ini"]["database"]["database"]

            link = MySQLdb.connect(host=host, user=user, passwd=password, db=bdd, cursorclass=cursors.DictCursor)
            cursor = link.cursor()
            link.query("set character set utf8")
            link.query("set names utf8")

            db_type = "mysql"

            cursor.execute("set character set utf8")
            cursor.execute("set names utf8")

        return (link, cursor)

    def load_ini(self, file_s=None, json_data=None):
        data = ''
        if file_s:
            f1 = open(file_s, "r")
            data = f1.read()
            f1.close()

        if not json_data and len(data) == 0:
            self.config = {"xtabs": {},
                           "central": {},
                           "peripheral": {},
                           "result": {},
                           "details": {},
                           "combobox": {},
                           "ini": {},
                           "words": {},
                           "import": {},
                           "fieldlist": {},
                           "inversion": {},
                           "popup": {},
                           "gateway_data": {},
                           "edit_lists": {}}
        elif json_data:
            self.config = json_data
        else:
            self.config = eval(data)

        # Verify that all necessary fields are present
        for key in ["xtabs", "central", "peripheral", "result", "details", "inversion", "popup", "gateway_data",
                    "combobox", "fieldlist", "edit_lists", "words", "ini"]:
            if not key in self.config:
                self.config[key] = {}
            if self.config[key] == None:
                self.config[key] = {}

        # changes in the dictionary structure, from version 2
        # TODO : the field periph_tables is normally created by he program and should not be in the config ?
        for field in ["input", "output", "zoom1", "zoom2", "gui", "position", "Hpaned", "database", "lists"]:

            if field in self.config:
                v2(self.config, "ini")
                self.config['ini'][field] = self.config[field]
                del self.config[field]

        if 125 in self.config:
            del self.config[125]

        if "version" in self.config:
            if self.config['version'] < int(2002):
                # change fieldlist format
                try:
                    if 'fieldlist' in self.config:
                        temp_fieldlist = deepcopy(self.config['fieldlist'])
                        del self.config['fieldlist']
                        central_tables = self.config['central'].keys()
                        self.config['central'][central_tables[0]]['cols'] = temp_fieldlist
                        if "$d_from" in temp_fieldlist:
                            if 'from' in temp_fieldlist['$d_from']:
                                self.config['central'][central_tables[0]]['from'] = temp_fieldlist['$d_from']['from']
                            del temp_fieldlist['$d_from']


                except:
                    pass  # not critical

        self.config["version"] = 2001

    def array_settings(self):

        arSettings = [("database", "mysql", ""),
                      ("database", "host", ""),
                      ("database", "user", ""),
                      ("database", "pass", ""),
                      ("database", "database", ""),
                      ("database", "order_field", ""),
                      ("database", "autobackup", ""),

                      ("database", "sqlite", ""),

                      ("lists", "font", "Arial"),
                      ("lists", "font_size", "10"),
                      ("lists", "line_height", "18"),
                      ("lists", "type_delay", "1000"),
                      ("lists", "max_lines", "150"),

                      ("output", "field_separator", " ;"),

                      ## ("gui", "language", ""),
                      ("gui", "start_tab", ""),
                      ]

        return arSettings

    def load_settings(self, widget=""):
        # charge les données dans la fenêtre de paramétrage
        global config, arWidgets

        # chargement des champs de la zone "database"
        arSettings = self.array_settings()
        for (section, element, default) in arSettings:
            if not section in self.config['ini']:
                self.config['ini'][section] = {}
            if not element in self.config['ini'][section]:
                self.config['ini'][section][element] = default
            field_s = section + "@" + element
            set_text(self.arw[field_s], self.config['ini'][section][element])

    ##        if file_exists(config['database']['mysql']);
    ##            set_text(arWidgets['mysql_dir_entry'], config['database']['mysql']);

    def save_settings(self, widget=""):
        # Saves the full config dictionary
        global configdir_u, settings, config

        # Backup configuration in JSON
        if os.path.exists(os.path.join(configdir_u, 'config.json')):
            with open(os.path.join(configdir_u, 'config.json'), 'r') as f:
                json_data = json.load(f)

            if json_data:
                with open(os.path.join(configdir_u, 'config.json.bak'), 'w') as f:
                    f.write(json.dumps(OrderedDict(json_data), indent=3))

        # crÃ©ation d'un backup.
        # procÃ©dure un peu lourde mais qui Ã©vite l'enfer des " pour les commandes shell
        f1 = open(os.path.join(configdir_u, "config.py"), "r")
        backup = f1.read()
        f1.close()

        f2 = open(os.path.join(configdir_u, "config.bak"), "w")
        f2.write(backup)
        f2.close()

        pp = pprint.PrettyPrinter(indent=4, width=100)
        out = pp.pformat(self.config)
        # out = readable_repr(self.config)

        f3 = open(os.path.join(configdir_u, "config.py"), "w")
        f3.write(out)
        f3.close()

        with open(os.path.join(configdir_u, 'config.json'), 'w') as f:
            f.write(json.dumps(OrderedDict(self.config), indent=3))

    def update_settings(self, widget):

        global config, arWidgets
        arSettings = self.array_settings()

        for (section, element, default) in arSettings:
            field_s = section + "@" + element
            if not field_s in self.arw:
                print field_s, " not found"
                continue

            v2(self.config['ini'], section)
            self.config['ini'][section][element] = get_text(self.arw[field_s])

        # TODO  self.config['database']['mysql'] = get_text(self.arw['mysql_dir_entry']);

        self.save_settings()

    def load_glade_objects(self, glade_file):
        # creates arrays of the objects names

        self.widgets2 = gtk.Builder()
        try:
            self.widgets2.add_from_file(glade_file)
            arWidgets2 = self.widgets2.get_objects()
        except:
            print "Glade file could not be loaded by gtk.Builder"
        arWidgets2 = {}
        self.ar_treeview = {}
        self.ar_entry = {}
        self.ar_textview = {}
        self.ar_check = {}
        self.ar_comboboxentry = {}
        self.arw2 = {}
        for z in arWidgets2:
            try:
                name = gtk.Buildable.get_name(z)
                z.set_name(name)
                self.arw2[name] = z
                if magutils.widget_type(z) == "GtkTreeView":
                    self.ar_treeview[name] = z
                elif magutils.widget_type(z) == "GtkTextView":
                    self.ar_textview[name] = z
                if magutils.widget_type(z) == "GtkEntry":
                    self.ar_entry[name] = z
                if magutils.widget_type(z) == "GtkheckButton":
                    self.ar_entry[name] = z
                if magutils.widget_type(z) == "GtkComboBoxEntry":
                    self.ar_comboboxentry[name] = z

            except:
                pass

    def populate_combo(self, combo, data):
        # adds a model to a combo and populates it
        # data must be a list
        model1 = gtk.ListStore(str)
        combo.set_model(model1)
        for item in data:
            model1.append([item])

        case = gtk.CellRendererText()
        combo.pack_start(case, True)
        combo.add_attribute(case, 'text', 0)
        combo.set_active(0)

    def select_sqlite_file(self, widget=None):
        # launched by the Filechooserbutton for the sqlite file
        filename = self.arw["sqlitefilechooser"].get_filename()
        self.arw["database@sqlite"].set_text(filename)
        if not 'database' in self.config['ini']:
            self.config['ini']['database'] = {}
        self.config['ini']['database']['sqlite'] = filename
        self.updated = True

    def show_database_details(self, widget):
        # show details when a line of the daabase structure is selected

        db_tree = self.arw["database_tree"]
        sel = db_tree.get_selection()
        model, iter1 = sel.get_selected()

        key2 = model.get_value(iter1, 2)  # level
        key3 = model.get_value(iter1, 3)  # configuration name

        if key2 == 1:  # level 1, central table
            temparray = self.config["central"][key3]
            self.arw["frame_periph"].hide()
            self.arw["frame_central"].show()
        elif key2 == 3:  # level 3 peripheral table
            temparray = self.config["peripheral"][key3]
            self.arw["frame_periph"].show()
            self.arw["frame_central"].hide()
        elif key2 == 2:
            temparray = self.config["peripheral"][key3]
            self.arw["frame_periph"].show()
            self.arw["frame_central"].hide()

        self.database_structure_active = [key2, key3]  # used by the function "general_chooser_answer"

        level = key2
        # clear text

        for widget in ["central@table",
                       "central@id_main",
                       "central@result",
                       "central@details",
                       "central@edit",
                       "central@edit_tab",
                       "central@from",

                       "peripheral@config_name",
                       "peripheral@table",
                       "peripheral@id_type",
                       "peripheral@main_field",
                       "peripheral@gateway",
                       "peripheral@linked_field",
                       "peripheral@central_def"]:
            magutils.set_text(self.arw[widget], "")

        if level == 1:  # central table
            for field in [
                "table",
                "id_main",
                "result",
                "details",
                "edit",
                "edit_tab",
                "from"
            ]:
                if key3 in self.config["central"]:
                    if field in self.config["central"][key3]:
                        magutils.set_text(self.arw["central@" + field], self.config["central"][key3][field])

        elif level > 1:  # peripheral table
            for field in ["config_name", "table", "id_type",
                          "main_field", "gateway", "linked_field", "central_def"]:
                try:
                    self.arw["peripheral@" + field].set_text(self.config["peripheral"][key3][field])
                except:
                    pass

    def show_inversion_details(self, widget):
        # show details when a line of the inversion list is selected

        db_tree = self.arw["inversion_treeview"]
        sel = db_tree.get_selection()
        model, iter1 = sel.get_selected()

        key = model.get_value(iter1, 0)  # configuration name

        self.inversion_active = key  # used by the function "general_chooser_answer"

        for widget in ["inversion@table_def",
                       "inversion@invert_field",
                       "inversion@central_field",
                       "inversion@content",
                       "inversion@condition"]:
            self.arw[widget].set_text("")

        for field in ["table_def",
                      "invert_field",
                      "central_field",
                      "content",
                      "condition",
                      ]:
            if key in self.config["inversion"]:
                if field in self.config["inversion"][key]:
                    self.arw["inversion@" + field].set_text(self.config["inversion"][key][field])

    def show_combobox_details(self, widget):
        # show details when a line of the combobox list is selected

        db_tree = self.arw["combobox_treeview"]
        sel = db_tree.get_selection()
        model, iter1 = sel.get_selected()
        if not iter1:
            return

        key = model.get_value(iter1, 0)  # configuration name

        self.combobox_active = key  # used by the function "general_chooser_answer"

        group = "combobox"
        fields = ["combobox", "group", "query"]

        for field_s in fields:
            self.arw[group + "@" + field_s].set_text("")

            if key in self.config[group]:
                if field_s in self.config[group][key]:
                    text_s = self.config[group][key][field_s]
                    if not isinstance(text_s, str):  # migration security
                        text_s = ""
                    self.arw[group + "@" + field_s].set_text(text_s)

    def show_popup_details(self, widget):
        # show details when a line of the popup list is selected

        db_tree = self.arw["popup_list"]
        sel = db_tree.get_selection()
        model, iter1 = sel.get_selected()

        key = model.get_value(iter1, 0)  # configuration name

        self.popup_active = key  # used by the function "general_chooser_answer"

        group = "popup"
        fields = ["table_def", "type", "code", "condition", "query"]

        for field_s in fields:
            magutils.set_text(self.arw[group + "@" + field_s], "")

            if key in self.config[group]:
                if field_s in self.config[group][key]:
                    text_s = self.config[group][key][field_s]
                    if not isinstance(text_s, str):  # migration security
                        text_s = ""
                    magutils.set_text(self.arw[group + "@" + field_s], text_s)

    def show_result_details(self, widget):

        sel = widget.get_selection()
        model, iter1 = sel.get_selected()
        key = model.get_value(iter1, 0)  # configuration name
        self.result_active = key  # used by the function "general_chooser_answer"
        self.model5.clear()

        # find name
        name = model.get_value(iter1, 0)
        self.result_active = name
        v2(self.config["result"][name], "cols")
        coldef = self.config["result"][name]["cols"]
        for s in coldef:
            data1 = []
            for field in ['field', 'title', 'width', 'visible', 'options']:
                if field in coldef[s]:
                    data1.append(coldef[s][field])
                else:
                    data1.append("")
            self.model5.append(data1)

        # from
        if "from" in self.config["result"][name]:
            magutils.set_text(self.arw["result@from"], self.config["result"][name]["from"])

        # sort treeview
        self.model7.clear()

        v2(self.config["result"][name], "sort")
        coldef = self.config["result"][name]["sort"]
        try:
            for s in coldef:
                data1 = []
                for field in ['name', 'sort1', 'sort2', 'sort3', '', '']:
                    if field in coldef[s]:
                        data1.append(coldef[s][field])
                    else:
                        data1.append("")
                self.model7.append(data1)
        except:
            pass

    def show_details_details(self, widget):
        # show details when a line of the details list is selected

        db_tree = self.arw["details_list"]
        sel = db_tree.get_selection()
        model, iter1 = sel.get_selected()

        key = model.get_value(iter1, 0)  # configuration name

        self.details_active = key  # used by the function "general_chooser_answer"

        group = "details"
        fields = ["central_def", "container", "details_tab"]

        for field_s in fields:
            self.arw[group + "@" + field_s].set_text("")

            if key in self.config[group]:
                if field_s in self.config[group][key]:
                    text_s = self.config[group][key][field_s]
                    if not isinstance(text_s, str):  # migration security
                        try:
                            text_s = str(text_s)
                        except:
                            text_s = ""
                    self.arw[group + "@" + field_s].set_text(text_s)

    def show_search_details(self, widget):

        sel = widget.get_selection()
        model, iter1 = sel.get_selected()
        name = model.get_value(iter1, 0)
        self.search_active = name  # memorize the name, it will be used by update_field and treeview_add
        for field in ["table_def", "result_def", "details_def",
                      "treeview", "entry", "type", "options"]:
            if not field in self.config["xtabs"][name]:
                self.config["xtabs"][name][field] = ""
            self.arw["xtabs@" + field].set_text(self.config["xtabs"][name][field])

        self.model6.clear()
        v2(self.config["xtabs"][name], "cols")
        coldef = self.config["xtabs"][name]["cols"]
        for s in coldef:
            data1 = []
            for field in ['field', 'title', 'width', 'detail', 'options', '']:
                if field in coldef[s]:
                    data1.append(coldef[s][field])
                else:
                    data1.append("")
            self.model6.append(data1)

    def show_gateway_data_details(self, widget):

        sel = widget.get_selection()
        model, iter1 = sel.get_selected()
        name = model.get_value(iter1, 0)
        if not iter1:
            return
        self.gateway_active = name  # memorize the name, it will be used by update_field and treeview_add
        for field in ["width"]:
            if not field in self.config["gateway_data"][name]:
                self.config["gateway_data"][name][field] = ""
            self.arw["gateway_data@" + field].set_text(str(self.config["gateway_data"][name][field]))

        self.gateway_details_model.clear()
        v2(self.config["gateway_data"][name], "cols")
        coldef = self.config["gateway_data"][name]["cols"]
        for s in coldef:
            data1 = []
            for field in ['field', 'title', 'width', 'type', '', '']:
                if field in coldef[s]:
                    data1.append(coldef[s][field])
                else:
                    data1.append("")
            self.gateway_details_model.append(data1)

    def edit_list(self, cr, path, texte, col):

        """ appelée par les cell_renderer de treeview5 (result lists)

    """

        sheet = self.arw['treeview5']
        store = sheet.get_model()
        (path2, colonne) = sheet.get_cursor()
        champ = colonne.get_title()

        iter1 = store.get_iter(path)
        id = store.get_value(iter1, 0)

        # mise à jour de la liste affichée et de la configuration
        if col != "":
            store.set(iter1, col, texte)

            name = get_sel_row_data(self.arw['result_lists'], 0, 0)
            v2(self.config["result"][name]["cols"], int(path))
            self.config["result"][name]["cols"][int(path)][champ] = texte

        else:

            alert(sprintf(_("Editing the field %s is not allowed."), champ))

    ##    def edit_list_adv(self, cr,path,texte,col) :
    ##
    ##        #appelée par les cell_renderer de treeview4 (advanced search)
    ##
    ##        sheet=self.arw['treeview4']
    ##        store = sheet.get_model();
    ##        (path2,colonne) = sheet.get_cursor();
    ##        champ=colonne.get_title();
    ##
    ##
    ##        iter1=store.get_iter(path);
    ##        id = store.get_value(iter1,0);
    ##
    ##        # mise à jour de la liste affichée et de la configuration
    ##        if col != "" :
    ##            store.set(iter1, col, texte);
    ##            self.config["fieldlist"][int(path) + 1][champ] = texte   # +1 car cette liste commence à 1 et non à 0
    ##
    ##        else :
    ##
    ##            alert(sprintf(_("Editing the field %s is not allowed."), champ));

    def edit_list_search(self, cr, row, texte, col, treeview):

        # appelée par les cell_renderer de treeview6 (search lists)
        sheet = self.arw[treeview]
        store = sheet.get_model()
        (path2, colonne) = sheet.get_cursor()
        champ = colonne.get_title()

        iter1 = store.get_iter(row)
        id = store.get_value(iter1, 0)

        # mise à jour de la liste affichée et de la configuration
        if col != "":
            store.set(iter1, col, texte)
            # self.config["fieldlist"]
            if treeview == "treeview6":
                name = get_sel_row_data(self.arw['search_lists'], 0, 0)
                v2(self.config["xtabs"][name]["cols"], int(row))
                self.config["xtabs"][name]["cols"][int(row)][
                    champ] = texte  # +1 car cette liste commence à 1 et non à 0
            elif treeview == "treeview5":
                name = get_sel_row_data(self.arw['result_lists'], 0, 0)
                v2(self.config["result"][name]["cols"], int(row))
                self.config["result"][name]["cols"][int(row)][
                    champ] = texte  # +1 car cette liste commence à 1 et non à 0
            elif treeview == "gateway_details":
                name = get_sel_row_data(self.arw['gateway_data'], 0, 0)
                v2(self.config["gateway_data"][name]["cols"], int(row))
                self.config["gateway_data"][name]["cols"][int(row)][
                    champ] = texte  # +1 car cette liste commence à 1 et non à 0


        else:

            alert(sprintf(_("Editing the field %s is not allowed."), champ))

    def edit_list_gateway(self, cr, row, texte, col, treeview):

        # appelée par les cell_renderer de gateway_details
        sheet = self.arw[treeview]
        store = sheet.get_model()
        (path2, colonne) = sheet.get_cursor()
        champ = colonne.get_title()

        iter1 = store.get_iter(row)
        id = store.get_value(iter1, 0)

        # mise à jour de la liste affichée et de la configuration
        if col != "":
            store.set(iter1, col, texte)
            # self.config["fieldlist"]
            if treeview == "treeview6":
                name = get_sel_row_data(self.arw['search_lists'], 0, 0)
                v2(self.config["xtabs"][name]["cols"], int(row))
                self.config["xtabs"][name]["cols"][int(row)][
                    champ] = texte  # +1 car cette liste commence à 1 et non à 0
            elif treeview == "treeview5":
                name = get_sel_row_data(self.arw['result_lists'], 0, 0)
                v2(self.config["result"][name]["cols"], int(row))
                self.config["result"][name]["cols"][int(row)][
                    champ] = texte  # +1 car cette liste commence à 1 et non à 0


        else:

            alert(sprintf(_("Editing the field %s is not allowed."), champ))

    def edit_treeview_started(self, cr, entry, row, col, treeview):

        self.search_edit_cell = [row, col, treeview]

        if treeview == "treeview6":  # Search lists
            data = []
            conf = self.arw["xtabs@table_def"].get_text()
            if conf in self.config['peripheral']:
                table = self.config["peripheral"][conf]["table"]
            elif conf in self.config["words"]:
                table = self.config["words"][conf]["table"]
            else:
                # Error in config. Clear the chooser
                self.general_chooser(self.arw["treeview5"], data=data)

            if col == 0:
                data = table_def[table].keys()
            elif col == 3:
                data = self.ar_entry.keys() + self.ar_textview.keys()

            self.general_chooser(self.arw["treeview6"], data=data)

        elif treeview == "treeview5":  # Result lists
            conf = get_text(self.arw["result_lists"])
            data = []
            if "from" in self.config["result"][conf]:
                from_s = self.config["result"][conf]["from"]
                table = from_s.split()[0]  # normally the first word of the from clause is the important table
                if col == 0:
                    data = table_def[table].keys()
                if col == 2:
                    data = table_def[table].keys()
            if col == 3:
                data = self.ar_entry.keys() + self.ar_textview.keys()

            self.general_chooser(self.arw["treeview5"], data=data)

    def ___________Advanced_Tab___________():
        pass

    def populate_tree(self, folder, model):
        # This function displays a dictionary in a Treeview. It may be used to display
        # a directory tree, but non only
        dir_list = []
        i = 0
        dir_list.append([folder, 0])  # // stores the directory list as queue
        nodes = {}
        nodes[0] = None
        model.clear()

        while (len(dir_list) > 0):
            dir = dir_list.pop(0)  # // get the first entry in queue
            # //echo "folder = $dir\n";
            for key in dir[0]:
                val = dir[0][key]

                i += 1
                if isinstance(val, dict):  # // is it a dictionary?
                    dir_list.append([val, i])  # // yes, queue it in the dir list
                    nodes[i] = model.append(nodes[dir[1]], [key, ""])
                else:
                    nodes[i] = model.append(nodes[dir[1]], [key, val])

    def find_string(self, *args):
        string_s = self.arw["find_entry"].get_text().strip()
        message = find_in_dict(self.config, string_s)
        buf1 = self.arw['find_TV'].get_buffer()
        buf1.set_text(message)

    def general_chooser(self, widget, event=None, data=None):

        self.chooser_widget_source = widget

        if data == None:

            # liste des tables de la base de données
            if widget.name in ["peripheral@table",
                               "central@table",
                               "peripheral@gateway",
                               ]:
                data = table_def.keys()

            # champs d'une table
            elif widget.name in ["central@id_main"]:
                table_s = self.arw["central@table"].get_text()
                data = table_def[table_s].keys()

            elif widget.name in ["peripheral@linked_field"]:
                central_config_s = self.arw["peripheral@central_def"].get_text()
                table_s = self.config['central'][central_config_s]['table']
                data = table_def[table_s].keys()

            elif widget.name in ["inversion@invert_field", "inversion@content", "inversion@condition"]:
                table_config_s = self.arw["inversion@table_def"].get_text()
                table_s = self.config['peripheral'][table_config_s]['table']
                data = table_def[table_s].keys()

            elif widget.name in ["inversion@central_field"]:
                table_config_s = self.arw["inversion@table_def"].get_text()
                central_def_s = self.config['peripheral'][table_config_s]['central_def']
                table_s = self.config['central'][central_def_s]['table']
                data = table_def[table_s].keys()

            elif widget.name in ["peripheral@id_type", "peripheral@main_field"]:
                table_s = self.arw["peripheral@table"].get_text()
                data = table_def[table_s].keys()

            # result definitions
            elif widget.name in ["central@result", "xtabs@result_def"]:
                data = self.config["result"].keys()

            # details definitions
            elif widget.name in ["central@details", "xtabs@details_def"]:
                data = self.config["details"].keys()

            # central tables definitions
            elif widget.name in ["peripheral@central_def", "details@central_def"]:
                data = self.config["central"].keys()

            # peripheral and words table definitions
            elif widget.name in ["xtabs@table_def"]:
                data = self.config["peripheral"].keys()
                data += self.config["words"].keys()

            # peripheral table definitions
            elif widget.name in ["inversion@table_def"]:
                data = self.config["peripheral"].keys()

            # central and peripheral table definitions
            elif widget.name in ["popup@table_def"]:
                data = self.config["peripheral"].keys()
                data += self.config["central"].keys()

            elif widget.name == "xtabs@type":
                data = ["list", "tree"]

            elif widget.name == "popup@type":
                data = ["text", "photo"]  # TODO

            elif widget.name in ["xtabs@treeview"]:
                data = self.ar_treeview.keys()

            elif widget.name in ["xtabs@entry"]:
                data = self.ar_entry.keys()

            elif widget.name in ["combobox@combobox"]:
                data = self.ar_comboboxentry.keys()


            elif widget.name in ["details@container"]:  # list of containers of the tabs of s_notebook3
                y = self.arw2["s_notebook3"].children()
                data = []
                for a in y:
                    data.append(a.name)

            elif widget.name in ["central@edit"]:  # list of containers of the tabs of s_notebook3
                y = self.arw2["s_notebook4"].children()
                data = []
                for a in y:
                    data.append(a.name)

        model = self.arw["treeview8"].get_model()
        model.clear()

        if data != None:
            data.sort()
            model.append([""])
            for line in data:
                model.append([line])

    def general_chooser_answer(self, *params):

        widget = self.chooser_widget_source
        widget_type = magutils.widget_type(widget)

        if widget_type == "GtkEntry":
            response = get_sel_row_data(self.arw["treeview8"], 0, 0)
            widget.set_text(response)

            temp1 = widget.name.split("@")
            category_s = temp1[0]
            field_s = temp1[1]

            if category_s in ["central", "peripheral"]:
                configuration = self.database_structure_active[1]
                self.config[category_s][configuration][field_s] = response
                self.load_database_tree()

            elif category_s == "xtabs":
                configuration = self.search_active
                self.config["xtabs"][configuration][field_s] = response

            elif category_s == "inversion":
                configuration = self.inversion_active
                self.config["inversion"][configuration][field_s] = response

            elif category_s == "combobox":
                configuration = self.combobox_active
                self.config["combobox"][configuration][field_s] = response

            elif category_s == "details":
                configuration = self.details_active
                self.config["details"][configuration][field_s] = response

            elif category_s == "popup":
                configuration = self.popup_active
                self.config["popup"][configuration][field_s] = response


        elif widget_type == "GtkTreeView":
            if widget.name == "treeview6":  # Search lists
                (row, col, treeview) = self.search_edit_cell
                response = get_sel_row_data(self.arw["treeview8"], 0, 0)
                self.edit_list_search("", row, response, col, treeview)

            elif widget.name == "treeview5":  # Result lists
                (row, col, treeview) = self.search_edit_cell
                response = get_sel_row_data(self.arw["treeview8"], 0, 0)
                self.edit_list_search("", row, response, col, treeview)

    def add_central_def(self, widget):

        dialog = ask_for_input()
        text = dialog.run()

        self.config["central"][text] = {}
        self.config["central"][text]["table"] = "---"
        self.config["central"][text]["id_main"] = "---"
        self.load_database_tree()

    def add_periph_def(self, widget):

        dialog = ask_for_input()
        text = dialog.run()

        self.config["peripheral"][text] = {}
        self.config["peripheral"][text]["config_name"] = text
        self.config["peripheral"][text]["id_type"] = "---"
        self.config["peripheral"][text]["table"] = "---"
        data = self.config["central"].keys()
        dialog = general_chooser_dialog(data)
        response = dialog.run()
        self.config["peripheral"][text]["central_def"] = response

        self.load_database_tree()

    def delete_line(self, *params):
        return
        sel = treeview.get_selection()
        model, iter1 = sel.get_selected()
        name = model.get_value(iter1, 0)
        if treeview.name == "search_lists":
            del self.config["xtabs"][name]
        elif treeview.name == "result_lists":
            del self.config["result"][name]
        elif treeview.name == "inversion_treeview":
            del self.config["inversion"][name]
        elif treeview.name == "combobox_treeview":
            del self.config["combobox"][name]
        elif treeview.name == "details_list":
            del self.config["details"][name]
        model.remove(iter1)

    def edit_db_struct(self, *params):
        return

    ##    def load_config_menu(self) :
    ##
    ##
    ##        global arWidgets;
    ##        #Titles
    ##        config_menu_titles = [_("Database"), _("Advanced Database Settings"),
    ##        _("Search Lists"), _("Result Lists"), _("Edit")]
    ##
    ##
    ##        config_menu = {1 : [["central",    _("Central tables")],
    ##        ["peripheral", _("Peripheral tables")],
    ##        ["words",      _("words tables")]],
    ##        2 : [["inversion", _("Inversions")],
    ##        ["import", _("Importations")]],
    ##        3 : [["xtabs", _("Search lists")],
    ##        ["combobox",  _("Combobox data")],
    ##        ["fieldlist", _("Fields lists")]],
    ##        4 : [["result", _("Result lists")],
    ##        ["details", _("Record details")],
    ##        ["popup",  _("Popup data")]],
    ##        5 : [["gateway_data",_("Gateway data")],
    ##        ["edit_lists",   _("Edit lists")]]};
    ##
    ##        config_store = gtk.TreeStore(str,str,str);
    ##        self.arw['config_menu'].set_model(config_store);
    ##        cell_renderer = gtk.CellRendererText();
    ##        colmenu = gtk.TreeViewColumn('Menu', cell_renderer, markup=0);
    ##        colmenu.set_resizable(True);
    ##        self.arw['config_menu'].append_column(colmenu);
    ##
    ##        i = 1;
    ##        node = {}
    ##        for val in config_menu_titles :
    ##
    ##            node[i] = config_store.append(None, [val,"title",""]);
    ##            i+= 1;
    ##
    ##
    ##        for key  in config_menu :
    ##            val = config_menu[key ]
    ##
    ##            for data in val :
    ##
    ##                config_store.append(node[key], [data[1],data[0],""]);
    ##
    ##
    ##        self.arw['config_menu'].expand_all();

    def load_search_list(self):

        keys = self.config["xtabs"].keys()
        keys.sort()
        for val in keys:
            self.search_model.append([val])

    def load_gateway_data_list(self):

        keys = self.config["gateway_data"].keys()
        keys.sort()
        for val in keys:
            self.edit_model.append([val])

    def load_combobox_list(self):

        keys = self.config["combobox"].keys()
        keys.sort()
        for val in keys:
            self.combobox_model.append([val])

    def load_popup_list(self):

        keys = self.config["popup"].keys()
        keys.sort()
        for val in keys:
            self.popup_model.append([val])

    def load_database_tree(self):

        global arWidgets
        # Titles

        config_store = self.arw['database_tree'].get_model()
        config_store.clear()
        keys = self.config["central"].keys()
        keys.sort()
        tempdict = {}

        for val in keys:
            ##            try :
            # Create first level (list of central tables definitions)
            data = val
            central_table = self.config["central"][val]["table"]
            central_id = self.config["central"][val]["id_main"]
            data = val + " [<b>" + central_table + "</b> / " + central_id + "]"
            node = config_store.append(None, [data, "red", 1, val])

            # Create second and third level (gateways and peripheral tables)
            keys2 = self.config["peripheral"].keys()
            keys2.sort()
            for val2 in keys2:
                if val2 in self.config["peripheral"]:
                    if "central_def" in self.config["peripheral"][val2]:
                        if self.config["peripheral"][val2]["central_def"] == val:
                            periph_id = self.config["peripheral"][val2]["id_type"]
                            table = "<b>" + self.config["peripheral"][val2]["table"] + "</b> [" + periph_id + "]"
                            if "gateway" in self.config["peripheral"][val2]:
                                gateway = self.config["peripheral"][val2][
                                    "gateway"]  # + " [" + central_id + " / " + periph_id + "]"
                            else:
                                gateway = ""
                            if gateway.strip() == "":
                                node2 = config_store.append(node, [table, "blue", 3, val2])
                            else:
                                node2 = config_store.append(node, [gateway, "green", 2, val2])
                                node3 = config_store.append(node2, [table, "blue", 3, val2])
                    else:
                        print "We don't find 'central_def' in peripheral/%s definition" % val2
                else:
                    print "We don't find %s in the peripheral tables definition" % val2

            # Create second level (Words tables)
            keys3 = self.config["words"].keys()
            keys3.sort()
            for val3 in keys3:
                if self.config["words"][val3]["central_def"] == val:
                    # periph_id = self.config["words"][val3]["id_type"]
                    table = "<b>" + self.config["words"][val3]["table"] + "</b>"
                    # gateway = self.config["words"][val3]["gateway"] # + " [" + central_id + " / " + periph_id + "]"
                    node2 = config_store.append(node, [table, "orange", 1, ""])
        ##            except:
        ##                    print "We got a problem ..."

        self.arw['database_tree'].expand_all()

    def load_inversion_list(self):

        global arWidgets
        # Titles

        keys = self.config["inversion"].keys()
        keys.sort()
        for val in keys:
            self.inversion_model.append([val])

    def load_result_list(self):

        global arWidgets
        # Titles

        config_store = gtk.ListStore(str)
        self.arw['result_lists'].set_model(config_store)
        cell_renderer = gtk.CellRendererText()
        colmenu = gtk.TreeViewColumn('Result', cell_renderer, text=0)
        colmenu.set_resizable(True)
        self.arw['result_lists'].append_column(colmenu)

        keys = self.config["result"].keys()
        keys.sort()
        for val in keys:
            config_store.append([val])

    ##            node2 = config_store.append(node,[_(u"columns"),"",""])
    ##            node3 = config_store.append(node,[_(u"sort"),"",""])
    ##            # Load data for columns
    ##            cols = self.config["result"][val]["cols"]
    ##            if cols :
    ##                for val2 in cols :
    ##                        if cols[val2] :
    ##                            try :
    ##                                data = cols[val2]["field"]
    ##                                node4 = config_store.append(node2,[data,"",""])
    ##                            except :
    ##                                "error 27"
    ##            # Load data for sort
    ##            sort = self.config["result"][val]["sort"]
    ##            if sort :
    ##                for val2 in sort :
    ##                    if val2 :
    ##                        if sort[val2] :
    ##                            data = sort[val2]["name"]
    ##                            node4 = config_store.append(node3,[data,"",""])

    def load_details(self):

        global arWidgets
        # Titles

        keys = self.config["details"].keys()
        keys.sort()
        for val in keys:
            node = self.details_model.append([val])

    def load_advanced_details(self):

        try:
            firstdb = self.config["central"].keys()[0]
            coldef = self.config["central"][firstdb]['cols']
            for s in coldef:
                data1 = []
                for field in ['niveau', 'nom', 'etoile', 'centrale']:
                    if field in coldef[s]:
                        data1.append(coldef[s][field])
                    else:
                        data1.append("")
                self.model4.append(data1)
        except:
            pass  # configuration may not be sufficient yet

    def execute_menu_config(self, treeview):
        sel = treeview.get_selection()
        (model, iter) = sel.get_selected()
        option = model.get_value(iter, 1)
        self.load_settings2(option)

    def first_config(self, widget=None):

        config = self.config

        if len(config['ini']['database']['order_field']) > 0:
            order_field = config['ini']['database']['order_field']
        else:
            order_field = "s_order"

        try:
            modified_field = config['ini']['database']['modified_field']
        except:
            modified_field = "s_modified"

        # crÃ©er la liste des tables pÃ©riphÃ©riques dÃ©finies dans config.php
        periph_tables = {}
        periph_tables2 = {}
        for key in config['peripheral']:
            val = config['peripheral'][key]

            val['config_name'] = key

            if 'gateway' in val:  # relation n:n (with gateway)
                if len(val['gateway']) > 0:
                    val['table_type'] = "peripheral2"
                    # get additional fields in the gateway table
                    if val['table'] in config["gateway_data"]:
                        temp4 = []
                        for a in config["gateway_data"][val['table']]["cols"]:
                            fieldname = config["gateway_data"][val['table']]["cols"][a]["field"]
                            temp4.append(fieldname)

                        val["gateway_fields"] = temp4

            else:
                val['table_type'] = "peripheral1"  # relation 1:n (without gateway)

            if val.has_key('table'):
                periph_tables[val['table']] = val
            periph_tables2[
                key] = val  # TODO : problem if two peripheral definitions for the same table. Dirty workaround. This should be studied

        if config['words']:
            for key in config['words']:
                val = config['words'][key]

                val['config_name'] = key
                val['table_type'] = "words"
                periph_tables[val['table']] = val

        treeview_data = {}
        # crÃ©er la liste des onglets dÃ©finis dans config.py
        for key in config['xtabs']:
            val = config['xtabs'][key]

            val['config_name'] = key
            if 'treeview' in val:
                treeview_data[val['treeview']] = val

        # crÃ©ation de config_info

        config_info = {}
        config_info['central_tables'] = {}
        config_info['periph_tables'] = {}
        config_info['gateways'] = {}
        config_info['periph_def'] = {}
        config_info['words_tables'] = {}
        config_info['search_lists'] = {}
        # central tables
        if 'central' in config:

            for key in config['central']:
                val = config['central'][key]
                config_info['central_tables'][val['table']] = copy.deepcopy(val)

        if 'details' in config:
            for key in config['details']:
                val = config['details'][key]
                # configuration details qui utilisent cette table
                central_def = val['central_def']
                if central_def != "":
                    if central_def in config['central']:
                        table = config['central'][central_def]['table']

                        v2(config_info, 'central_tables', table)
                        try:
                            config_info['central_tables'][table]['details'] += "," + key
                        except:
                            config_info['central_tables'][table]['details'] = key  # if 'details' does not exist, create

        if config[
            'result']:  # TODO il y a ici un chargement en double : c'était déjà chargé par config_info['central_tables'][val['table']] = copy.deepcopy(val)
            # voir ce qui doit être conservé.
            for key in config['result']:
                val = config['result'][key]

                # configuration "result" qui utilisent cette table
                if "from" in val:
                    _from = val['from']
                    temp = _from.split(" ")
                    table = temp[0]

                    if table in config_info['central_tables']:
                        try:
                            config_info['central_tables'][table]['result'] += "," + key
                        except:
                            config_info['central_tables'][table]['result'] = key  # if 'result' does not exist, create

        if config['words']:
            for key in config['words']:
                val = config['words'][key]

                # tables de mots qui utilisent cette table
                central_def = val['central_def']
                if central_def in config['central']:
                    table = config['central'][central_def]['table']
                    if not 'words' in config_info['central_tables'][table]:
                        config_info['central_tables'][table]['words'] = key + ","
                    else:
                        config_info['central_tables'][table]['words'] = key + ","

        # peripheral tables and gateways
        for key in config['peripheral']:
            val = config['peripheral'][key]
            if not val.has_key('table'):
                continue

            config_info['periph_tables'][val['table']] = val
            if val.has_key('gateway'):
                v2(config_info, 'gateways', val['gateway'], 'name')
                config_info['gateways'][val['gateway']]['name'] = val['gateway']

            if 'gateway_data' in config:

                for key in config['gateway_data']:  # ajouter les infos extraites de gateway_data
                    gd = config['gateway_data'][key]
                    if 'gateway' in gd and 'gateway' in val:
                        if gd['gateway'] == val['gateway']:
                            config_info['gateways'][val['gateway']]['data'] = gd['cols']

        # peripheral definitions (merges peripheral and words tables)

        if config['peripheral']:

            for key in config['peripheral']:
                val = config['peripheral'][key]
                config_info['periph_def'][key] = val

        if config['words']:
            for key in config['words']:
                val = config['words'][key]

                if config_info['periph_def'].has_key(key):
                    msg = _(
                        "The name %s is already used for a peripheral table, it cannot be used for a words table !") % key
                    alert(msg)

                config_info['periph_def'][key] = val

        # words tables
        if config['words']:

            for key in config['words']:
                val = config['words'][key]
                config_info['words_tables'][val['table']] = val

        # Search lists and combine
        for key in config['xtabs']:
            try:
                val = config['xtabs'][key]

                config_info['search_lists'][val['treeview']] = val
                config_info['search_lists'][val['treeview']]['name'] = key
                table_def = val['table_def']
                table = v(config_info, 'periph_def', table_def, 'table')
                config_info['search_lists'][val['treeview']]['peripheral_table'] = table
                central_table_def = v(config_info, 'periph_def', table_def, 'central_def')
                central_table = v(config, 'central', central_table_def, 'table')
                config_info['search_lists'][val['treeview']]['central_table'] = central_table

                if config_info['periph_tables'].has_key(table):

                    if 'search_lists' in config_info['periph_tables'][table]:
                        temp = config_info['periph_tables'][table]['search_lists']
                        try:
                            temp += "," + val['treeview']
                        except:  # bad configuration
                            config_info['periph_tables'][table]['search_lists'] = val['treeview']
                        # TODO : vérifier : faut-il réassigner temp ?

                    else:
                        config_info['periph_tables'][table]['search_lists'] = val['treeview']

            except:  # TODO : this should be done for all blocks above
                print "Error in configuration for search lists"

    def check_config(self, widget=None):

        # central tables

        for c_table in config['central']:
            # details
            details = c_table['details']
            if not details in config['details']:
                alert("error for details in central table")

    def advance_tab_switch_page(self, widget, page, page_num):
        """Handler for Advance tag switching"""
        if page_num == 0:
            # If the config page is loaded, load json-edit program
            json_path = os.path.join('./config', configname_u, 'config.json')
            if not os.path.exists(json_path):
                # Create the json file
                with open(json_path, 'w') as f:
                    f.write(json.dumps(OrderedDict(self.config), indent=3))

            json_edit = os.path.join(os.path.dirname(__file__), 'json-edit.py')
            subprocess.call(
                [python_path, json_edit, json_path],
            )

    def advance_config_editor_clicked(self, widget):             
        # load json-edit program
        json_path = os.path.join('./config', configname_u, 'config.json')
        if not os.path.exists(json_path):
            # Create the json file
            with open(json_path, 'w') as f:
                f.write(json.dumps(OrderedDict(self.config), indent=3))

        json_edit = os.path.join(os.path.dirname(__file__), 'json-edit.py')
        subprocess.call(
            [python_path, json_edit, json_path],
        )



    def hide_options(self):
        self.arw['options'].hide()
        self.arw['window1'].hide()
        gtk.main_quit()



def readable_repr(data0):
    """
    placeholders prevent strings and comments from being processed
    (?s)/\*.*?\*/|//[^\n]*|#[^\n]*|([\"'])[^\\\\]*?(\\\\.[^\\\\]*?)*?\\1
    In details :
        (?s) : multiline search
        ([\"'])[^\\\\]*?(\\\\.[^\\\\]*?)*?\\1 : search strings "..." and '...'
    """

    data1 = repr(data0)
    out = ""
    level = -1
    tab = 4
    i = 0
    patterns = []
    placeholders = []

    for match in re.finditer("(?s)([\"'])[^\\\\]*?(\\\\.[^\\\\]*?)*?\\1", data1):
        data2 = match.group(0)

        placeholder_s = "'[placeholder" + str(i) + "]'"
        placeholders.append(placeholder_s)
        patterns.append(data2)
        i += 1

    for i in range(0, len(placeholders)):
        pattern_s = patterns[i]
        placeholder_s = placeholders[i]
        search_s = re.escape(pattern_s)
        data1 = re.sub(search_s, placeholder_s, data1, 1)

    for a in data1:
        if a == "{":
            level += 1
            out += "\n" + (" " * (level * tab)) + "{"

        elif a == "}":
            level -= 1
            out += "}\n" + (" " * (level * tab))

        else:
            out += a

    out = re.sub("\n(\s*),", ",\n\g<1>", out)

    for i in range(0, len(placeholders)):
        pattern_s = patterns[i]
        placeholder_s = placeholders[i]
        out = out.replace(placeholder_s, pattern_s)

    return out


def sqlite_db_structure():
    table_def = {}
    global cursor

    req = "PRAGMA table_info(candidats)"

    """SELECT name FROM sqlite_master
    WHERE type  IN (?,?)
    AND name NOT LIKE ?
    UNION ALL SELECT name FROM sqlite_temp_master
    WHERE type IN (?,?)
    ORDER BY 1','table','view','sqlite_%','table','view') ;
    """

    req = "select name from sqlite_master where type in ('table')"
    cursor.execute(req)
    result = cursor.fetchall()
    for a in result:
        for b in a:
            table_def[b] = {}
            req = "PRAGMA table_info (" + b + ")"
            cursor.execute(req)
            for s in cursor:
                table_def[b][s[1]] = s[2]

    ##                for a in s :
    ##                    print a,
    ##                print

    # get links
    links_table = {}
    # list of fields
    for table in table_def:
        for field in table_def[table]:
            if not field in links_table:
                links_table[field] = {}
            links_table[field][table] = ""

    # possible links
    ##    for key in links_table :
    ##        if len(links_table[key].keys()) > 1 :
    ##            print "tables", links_table[key].keys(), "may have a link on", key

    return table_def


def access_db_structure():
    table_def = {}
    tables = ["tblArticle",
              "tblArticleCoAuthor",
              "tblAuthor",
              "tblBook",
              "tblBookCoAuthor",
              "tblCirculation",
              "tblCitation",
              "tblCity",
              "tblClass",
              "tblClassification",
              "tblCountry",
              "tblDivision",
              "tblKeyArticle",
              "tblKeyArticle Query",
              "tblKeyCitation",
              "tblKeyCitation Query",
              "tblKeyWord",
              "tblKeyWord Query",
              "tblLanguage",
              "tblPatron",
              "tblPeriodical",
              "tblPeriodical Query",
              "tblPrefix",
              "tblPublisher",
              "tblResponsibility",
              "tblRoom",
              "tblSection",
              "tblSize",
              "tblState",
              "tblSubject",
              "tblSuffix",
              "tblTheme",
              "tblTitle",
              "tblTopic",
              "zThemes2",
              "tblWords"]

    for table in tables:
        table_def[table] = {}
        req = "select * from " + table
        cursor.execute(req)
        temp1 = cursor.description

        for line in temp1:
            table_def[table][line[0]] = line[1]

    return table_def


def find_in_dict(dictionary, string_s):
    stack = [dictionary]
    levels = ["/"]
    message = ""
    while True:
        if len(stack) == 0:
            break
        dico = stack.pop()
        level = levels.pop()
        for key in dico:
            if isinstance(dico[key], dict):
                stack.append(dico[key])
                levels.append(level + str(key) + "/")
            else:
                element = dico[key]
                if isinstance(element, str):
                    if element.find(string_s) >= 0:
                        message += str(level) + str(key) + "/" + str(element) + "\n"

            if isinstance(key, str):
                if key.find(string_s) >= 0:
                    message += str(level) + key + "/\n"

    return message


def show_options():
    global arWidgets
    montrer("s_options", 3)


def alert(message, type=0):
    dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE,
                               message)
    dialog.run()
    dialog.destroy()


def yes_no_dialog(message, type=0):
    dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO,
                               message)
    answer = dialog.run()
    dialog.destroy()
    if answer == gtk.RESPONSE_YES:
        return True
    else:
        return False


# ==========================================================
# Les fonctions suivantes gÃ¨rent le paramÃ©trage du programme
# ==========================================================


def migration():
    global config, configdir_u
    if config['version'] < 300:

        for key in config['xtabs']:
            val = config['xtabs'][key]

            unset(config['xtabs'][key]['load_on_start'])

            temp = config['xtabs'][key]['table']
            unset(config['xtabs'][key]['table'])
            if isset(temp):
                config['xtabs'][key]['table_def'] = temp

            temp = config['xtabs'][key]['display']
            unset(config['xtabs'][key]['display'])
            if isset(temp):
                config['xtabs'][key]['result_def'] = temp

            temp = config['xtabs'][key]['details']
            unset(config['xtabs'][key]['details'])
            if isset(temp):
                config['xtabs'][key]['details_def'] = temp

        temp = config['display']
        if isset(temp):
            unset(config['display'])
            config['result'] = temp
            unset(temp)

        config['version'] = 300

    if config['version'] < 310:

        for key in config['peripheral']:
            val = config['peripheral'][key]

            config['peripheral'][key]['table'] = config['peripheral'][key]['peripheral']
            unset(config['peripheral'][key]['peripheral'])

        config['version'] = 310

    if config['version'] < 1000:

        # Print config is now taken from files. Write files from existing configurations
        for key in config['print']:
            val = config['print'][key]

            outfile = configdir_u + "backup/" + key + "." + val['extension']
            if not is_dir(configdir_u + "backup/"):
                mkdir(configdir_u + "backup/")

            f1 = fopen(outfile, "w")
            fwrite(f1, val['before'])
            fwrite(f1, val['code'])
            fwrite(f1, val['after'])
            fclose(f1)

        # Support for 1:n relations added : previously this support was bad.
        # Transform tables which were marked as 1:n relations in independant tables to prevent corruption of configuration
        for key in config['peripheral']:
            val = config['peripheral'][key]

            gateway = val['gateway']
            if len(gateway) > 0:
                val['central_def'] = ""

        config['version'] = 1100
        save_settings()


"""

def migration2() :

    # migrations qui ne peuvent Ãªtre Ã©xÃ©cutÃ©es qu'aprÃ¨s buildDialog
    global config, arWidgets, configdir_u;

    # RequÃªtes prÃ©enregistrÃ©es
    if config['version'] < 809 :


        query = "select *	from requetes";
        result = mysql_query(query);
        sql_error(link, query);
        model = self.arw['clist4'].get_model();
        model.clear();

        data = True
        while data :
            data = mysql_fetch_assoc(result)

            # changements de noms
            change = ["nom" 		: "name",
            "requete" 	: "query",
            "largeurs" : "widths",
            "comment"	: "comment",
            "parameters" : "parameters",
            "details" 	: "details",
            "central_def" : "central_def");
            for key  in change :
 val = change[key ]

                data2[val] = data[key];


            append(model,data2);
            # array
            name = data2["name"];
            queries[name] = data2;




        # enregistrer sur fichier

        set = fopen(configdir_u . "queries.php","w");
        data = var_export(queries,True);
        fputs(set,"" . chr(10) . 'queries = ');
        fputs(set,data);
        fputs(set,";" . chr(10) ."");
        fclose(set);

        # recharger
        predef_query_load();


        config['version'] = 809;
        save_settings();

        alert("You can delete the table 'requetes', it is no longer used by the system.
Prerecorded queries are now found in the file queries.php in your configuration directory");




"""


def add_data2():
    global config, mem, arWidgets
    reponse = prompt({"Nom Ã  ajouter Ã  la liste :": ""})
    config[mem['config_periph']][reponse[0]] = ""
    load_settings2()
    # model = arWidgets['config_periph'].get_model();
    # append(model,[reponse[0]));


def duplicate_data2():
    global config, mem, arWidgets

    liste = arWidgets['config_periph']
    name = get_sel_row_data(liste, 0, 0)
    row = get_sel_row_data(liste, 0, 1)
    data = unserialize(row)
    config[mem['config_periph']][name + "2"] = data
    load_settings2()


def delete_data2():
    global arWidgets, config, mem

    liste = arWidgets['config_periph']
    element = mem['config_name']
    section = mem['config_periph']
    x = iter_sel(liste, True)
    if isset(x) == false:

        alert(_("Nothing selected."))

    else:

        #  store = liste.get_model();
        #  store.remove(x);
        unset(config[section][element])
        load_settings2()

    reorder_list()


def rename_data2():
    global arWidgets, config, mem

    liste = arWidgets['config_periph']
    element = mem['config_name']
    section = mem['config_periph']
    x = iter_sel(liste, True)
    if isset(x) == false:

        alert(_("Nothing selected."))

    else:

        name = get_sel_row_data(liste, 0, 0)
        reponse = prompt({"Nouveau nom :": name})
        store = liste.get_model()
        store.set(x, 0, reponse[0])
        temp = config[section][name]
        unset(config[section][name])
        config[section][reponse[0]] = temp

    load_settings2()


"""
def update_data2() :

    # FenÃªtre des paramÃ¨tres : met Ã  jour les donnÃ©es de la liste des tables pÃ©riphÃ©riques quand un champ de saisie est modifiÃ©
    global arWidgets, config, mem;

    if mem['update'] == 0 :

        return;

    # on dÃ©sactive la fonction pendant le chargement des listes
    sel=arWidgets['config_periph'].get_selection();
    list(model, arPaths) = sel.get_selected_rows();
    iter = model.get_iter(arPaths[0]);
    #element = get_sel_row_data(arWidgets['config_periph'],0,0);
    series = mem['config_series'];
    series3 = mem['config_series3'];
    element = mem['config_name'];
    section = mem['config_periph'];


    # si la configuration utilise la 2eme liste

    if section in ["peripheral","result","xtabs","details"] :


        if series :

            cols = config[section][element][series];
            out[series] = cols;

        if series3 :

            cols = config[section][element][series3];
            out[series3] = cols;


        keys = mem['config_keys1'];

        for (i = 0; i < count(keys); i+= 1)

            j = i + 1;
            out[keys[i]] = get_text(arWidgets['config_data'.j]);


        model.set(iter,1,serialize(out));
        config[section][element] = out;


def load_data_cols(liste, code) :

    # FenÃªtre des paramÃ¨tres : affiche les donnÃ©es de la liste des colonnes dans les champs de saisie
    global arWidgets, config, mem;

    mem['update']=0;
    col = get_sel_row_data(liste,0,1);
    arData = unserialize(col);
    mem['config_col'] = get_sel_row_data(liste,0,0);


    if code == "B" :

        keys = mem['config_keys2'];

    # voir la fonction load_settings2
    if code == "C" :

        keys = mem['config_keys3'];


    for z in [0,1,2,3,4) :

        j = z + 1;

        if isset(keys[z]) :


            set_text(arWidgets['config_data'.code.j],arData[keys[z]]);
            #arWidgets['config_data_labelB'.j].set_text(keys2[z]);

        else :

            # effacement des champs inutilisÃ©s
            set_text(arWidgets['config_data'.code.j],"");
            #arWidgets['config_data_labelB'.j].set_text("");





    mem['update'] = 1;


def add_data_cols() :

    global config, mem, arWidgets;


    reorder_list_cols();

    section = mem['config_periph'];
    element = mem['config_name'];
    series = mem['config_series'];

    config[section][element][series][] = "";
    num = count(config[section][element][series]);

    model = arWidgets['config_cols'].get_model();
    append(model,[num - 1));



def duplicate_data_cols() :

    global config, mem, arWidgets;

    liste = arWidgets['config_cols'];
    row = get_sel_row_data(liste,0,1);
    data = unserialize(row);

    reorder_list_cols();

    section = mem['config_periph'];
    element = mem['config_name'];
    series = mem['config_series'];

    config[section][element][series][] = data;
    num = count(config[section][element][series]);

    #model = arWidgets['config_cols'].get_model();
    #append(model,[num - 1));
    load_data2();




def delete_data_cols() :

    global arWidgets, config, mem;

    liste = arWidgets['config_cols'];
    element = mem['config_name'];
    section = mem['config_periph'];
    series = mem['config_series'];
    col = mem['config_col'];

    x=iter_sel(liste,True);
    if isset(x) == false :

        alert(_("Nothing selected."));

    else :

        store = liste.get_model();
        store.remove(x);
        unset(config[section][element][series][col]);

    reorder_list_cols();

def update_data_cols(code) :

    # FenÃªtre des paramÃ¨tres : met Ã  jour les donnÃ©es de la liste de gauche quand un champ de saisie est modifiÃ©

    global arWidgets, config, mem;
    if mem['update'] == 0 :

        return;


    if code == "B" :

        keys = mem['config_keys2'];
        sel=arWidgets['config_cols'].get_selection();
        series = mem['config_series'];


    if code == "C" :

        keys = mem['config_keys3'];
        sel=arWidgets['config_comp'].get_selection();
        series = mem['config_series3'];



    for (i = 0; i < count(keys); i+= 1)

        j = i + 1;
        out[keys[i]] = get_text(arWidgets['config_data'.code.j]);






    list(model, arPaths) = sel.get_selected_rows();
    iter = model.get_iter(arPaths[0]);
    model.set(iter,1,serialize(out));
    section = mem['config_periph'];
    name = mem['config_name'];
    col = mem['config_col'];
    config[section][name][series][col] = out;






def add_data_comp() :

    global config, mem, arWidgets;


    reorder_list_cols();

    section = mem['config_periph'];
    element = mem['config_name'];
    series = mem['config_series3'];

    config[section][element][series][] = "";
    num = count(config[section][element][series]);

    model = arWidgets['config_comp'].get_model();
    append(model,[num - 1));


def delete_data_comp() :

    global arWidgets, config, mem;

    liste = arWidgets['config_comp'];
    element = mem['config_name'];
    section = mem['config_periph'];
    series = mem['config_series3'];
    col = mem['config_col'];

    x=iter_sel(liste,True);
    if isset(x) == false :

        alert(_("Nothing selected."));

    else :

        store = liste.get_model();
        store.remove(x);
        unset(config[section][element][series][col]);

    reorder_list_comp();






def reorder_list() :

    global mem, config, arWidgets;

    if mem['update'] == 0 :

        return;

    # on dÃ©sactive la fonction pendant le chargement des listes

    section = mem['config_periph'];
    model = arWidgets['config_periph'].get_model();

    for row in model :

        key = row[0];
        temp[key] = config[section][key];


    config[section] = temp;


def reorder_list_cols() :

    global mem, config, arWidgets;

    if mem['update'] == 0 :

        return;

    # on dÃ©sactive la fonction pendant le chargement des listes

    series = mem['config_series'];
    element = mem['config_name'];
    section = mem['config_periph'];
    model = arWidgets['config_cols'].get_model();

    for row in model :

        key = row[0];
        temp[] = config[section][element][series][key];


    config[section][element][series] = temp;
    load_data2();


def reorder_list_comp() :

    global mem, config, arWidgets;

    if mem['update'] == 0 :

        return;

    # on dÃ©sactive la fonction pendant le chargement des listes

    series = mem['config_series3'];
    element = mem['config_name'];
    section = mem['config_periph'];
    model = arWidgets['config_comp'].get_model();

    for row in model :

        key = row[0];
        temp[] = config[section][element][series][key];


    config[section][element][series] = temp;
    load_data2();

"""

"""



# ================================= Predefined queries  ==============================


def predef_query_detail(selection) :

    # Affichage dans le cadre de droite
    global arWidgets, mem;
    mem['update_query'] = 0;

    selection = arWidgets['clist4'].get_selection();
    list(model, arPaths) = selection.get_selected_rows();
    if isset(arPaths) :

        effacer = 0;
        iter = model.get_iter(arPaths[0]);
        # premiÃ¨re ligne sÃ©lectionnÃ©e

    else :

        effacer = 1;
        iter = None;

    # s'il n'y a pas de sÃ©lection, on efface


    fields = ["name", "query", "widths", "comment", "parameters", "details", "central_def");


    for (i = 0; i < 7; i+= 1)

        if effacer == 1 :

            texte ="";

        else :

            texte=model.get_value(iter, i);

        widget = arWidgets["s_". fields[i] . "4"];
        set_text(widget,texte);


    mem['query_name'] = model.get_value(iter, 0);
    mem['update_query'] = 1;


def predef_query_build() :

    global arWidgets;

    treeview = arWidgets['clist4'];
    treeview.set_model(gtk.ListStore(str,str,str,str,str,str,str,str));
    renderer = gtk.CellRendererText();
    column = gtk.TreeViewColumn('Title', renderer, 'text', 0);
    treeview.append_column(column);
    treeview.append_column(gtk.TreeViewColumn('Title', renderer, 'text', 1));
    treeview.connect('row-activated', 'predef_query_detail');
    treeview.connect('cursor-changed', 'predef_query_detail');
    treeview.set_reorderable(True);

    # mise Ã  jour

    for key  in [0 : "name", 5 : "details", 6 : "central_def") :
name = [0 : "name", 5 : "details", 6 : "central_def")[key ]

        arWidgets["s_" . name . "4"].connect("changed", "predef_query_update", key, name);


    for key  in [1 : "query", 2 : "widths", 3 : "comment", 4 : "parameters") :
name = [1 : "query", 2 : "widths", 3 : "comment", 4 : "parameters")[key ]

        buffer = arWidgets["s_" . name . "4"].get_buffer();
        buffer.connect("changed", "predef_query_update", key, name);




def predef_query_load() :

    global arWidgets, link, queries, configdir_u;

    include(configdir_u . "queries.php");
    model = arWidgets['clist4'].get_model();
    model.clear();

    fields = ["name", "query", "widths", "comment", "parameters", "details", "central_def");
    if queries) foreach(queries as data :

        unset(data2);
        for name in fields :

            data2[] = data[name];

        append(model,data2);




def predef_query_save() :

    global queries, configdir;

    set = fopen(configdir . "queries.php","w");
    data = var_export(queries,True);
    fputs(set,"" . chr(10) . 'queries = ');
    fputs(set,data);
    fputs(set,";" . chr(10) ."");
    fclose(set);



def predef_query_new() :

    global queries, arWidgets;

    model = arWidgets['clist4'].get_model();
    name = _("New query");
    append(model,array(name));






def predef_query_delete() :

    global arWidgets, queries;

    sel = arWidgets['clist4'].get_selection();
    list(model, arPaths) = sel.get_selected_rows();
    n3=count(arPaths);

    if n3==0 :

        alert(_("No line selected. Aborting."));
        return;

    else :
    if n3>1 :

        alert(_("More than one line selected. Aborting."));
        return;

    else :

        iter = model.get_iter(arPaths[0]);
        # valeur premiÃ¨re ligne
        name = model.get_value(iter,0);
        unset(queries[name]);
        model.remove(iter);




def predef_query_update(widget,col, name) :

    global arWidgets, link, queries, configdir, mem;

    if mem['update_query'] == 0 :

        return;

    sel = arWidgets['clist4'].get_selection();
    list(model, arPaths) = sel.get_selected_rows();
    n3=count(arPaths);

    if n3==0 :

        alert(_("No line selected. Aborting."));
        return;

    elif n3>1 :

        alert(_("More than one line selected. Aborting."));
        return;

    else :

        iter = model.get_iter(arPaths[0]);

    # valeur premiÃ¨re ligne

    switch (name)


    case "name" :

        text = get_text(arWidgets["s_name4"]);
        queries[text] = queries[mem['query_name']];
        queries[text]['name'] = text;
        unset(queries[mem['query_name']]);
        model.set(iter,col,text);
        mem['query_name'] = text;

        break;

        default :

        line_name = get_text(arWidgets["s_name4"]);
        text = get_text(arWidgets["s_" . name . "4"]);
        queries[line_name][name] = text;
        model.set(iter,col,text);






def colors_selection(button,action) :

    global arWidgets, colors;

    colors_list = arWidgets['colors_list'];
    option = get_sel_row_data(colors_list,0,0);
    color = button.get_color();
    r=color.red;
    g=color.green;
    b=color.blue;

    r= (r/65535)*255;
    g= (g/65535)*255;
    b= (b/65535)*255;

    rgb = sprintf("#%02x%02x%02x", r, g, b);

    colors[option][action] = rgb;





def save_colors1() :

    globalconfigdir, colors;

    backup = file_get_contents(configdir . "colors.php");
    #crÃ©ation d'un backup.
    file1 = fopen(configdir . "colors.bak","w");
    # procÃ©dure un peu lourde mais qui Ã©vite l'enfer des " pour les commandes shell
    fputs(file1,backup);
    fclose(file1);


    set = fopen(configdir . "colors.php","w");
    data = var_export(colors,True);
    fputs(set,"" . chr(10) . 'colors = ');
    fputs(set,data);
    fputs(set,";" . chr(10) ."");
    fclose(set);


def save_colors0() :

    global configdir, colors;

    backup = file_get_contents(configdir . "colors.php");
    #crÃ©ation d'un backup.
    file1 = fopen(configdir . "colors.bak","w");
    # procÃ©dure un peu lourde mais qui Ã©vite l'enfer des " pour les commandes shell
    fputs(file1,backup);
    fclose(file1);

    source = save_colors(colors);

    set = fopen(configdir . "colors.php","w");
    data = var_export(source,True);
    fputs(set,"" . chr(10) . 'colors = ');
    fputs(set,data);
    fputs(set,";" . chr(10) ."");
    fclose(set);


def save_colors(source) :

    # note 6


    for &data in source :

        if is_array(data) :

            save_colors(&data);

        else :

            if is_object(data) :

                red = data.red;
                green = data.green;
                blue = data.blue;

                data = "red,green,blue";



    return source;





def get_colors(source) :

    # note 6
    global configdir;


    for &data in source :

        if is_array(data) :

            get_colors(&data);

        else :

            if is_string(data) :

                rgb = (explode(",",data));
                data = new GdkColor(rgb[0],  rgb[1], rgb[2]);



    return source;



def color_new() :

    global colors, arWidgets;
    r = prompt(array("nom ?" : "x"));
    colors[r[0]] = array();

    model = arWidgets['colors_list'].get_model();
    append(model,r);




def color_delete() :

    global colors, arWidgets;

    list = arWidgets['colors_list'];
    iter = iter_sel(list,True);
    model = list.get_model();
    option = get_sel_row_data(list,0,0);
    model.remove(iter);
    unset(colors[option]);


def show_selected_colors(list) :

    global arWidgets, colors;

    option = get_sel_row_data(list,0,0);
    color = colors[option]['f'];
    if color :

        arWidgets['f_color_button'].set_color(GdkColor::parse(color));

    color = colors[option]['b'];
    if color :

        arWidgets['b_color_button'].set_color(GdkColor::parse(color));







"""

###########################################################################
# MAIN ####################################################################
###########################################################################

global selector, utils, table_def, configdir_u, mem, db_type
global db_utils

mem = {}
db_type = ""
table_def = {}
configdir_u = ""

if __name__ == '__main__':

    # init
    usage_s = \
        "%prog [options]\n" + \
        "\tbackup filesystem"
    isExcept = False
    excMsg_s = ""

    # parse command line
    parser = OptionParser(usage=usage_s)
    parser.add_option(
        "-v",
        "--version",
        dest="version",
        action="store_true",
        default=False,
        help="display script version")

    parser.add_option(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="activate process traces")
    parser.add_option(
        "-n",
        "--simulation",
        dest="simulation",
        action="store_true",
        default=False,
        help="simulation, no action performed")
    parser.add_option(
        "-i",
        "--ini",
        dest="ini",
        help="specify ini/task file",
        metavar="ini")

    # get opt
    (option_v, arg_a) = parser.parse_args()

    try:

        # Get the configuration
        configname_u = None
        if len(arg_a) > 0:  # if the config is indicated on the command line
            print "x", arg_a[0], "x"

            if len(arg_a[0].strip()) > 0:
                configname_u = unicode2(arg_a[0])

        if not configname_u:  # ask for config
            config_dialog = ask_for_config()
            configname_s = config_dialog.run()
            configname_u = unicode2(configname_s)

        # init

        tmp_u = unicode2(os.path.abspath("./"))
        configdir_u = os.path.join(tmp_u, u"config", configname_u)

        db_utils = db_utilities()
        selector = Restore()
        utils = utilities()

        # selector.load_config_menu()
        selector.load_settings()
        selector.load_search_list()
        selector.load_combobox_list()
        selector.load_database_tree()
        selector.load_inversion_list()
        selector.load_result_list()
        selector.load_details()
        try:
            selector.load_popup_list()
        except:
            print "Error loading popup list"
        selector.load_gateway_data_list()
        selector.load_advanced_details()
        gtk.main()

    except ScriptSg, instance:
        isExcept = True
        excMsg_s = "%s" % (instance)
        (excType, excValue, excTb) = sys.exc_info()
        tb_a = traceback.format_exception(excType, excValue, excTb)

    except ScriptIo, instance:
        isExcept = True
        excMsg_s = "%s" % (instance)
        (excType, excValue, excTb) = sys.exc_info()
        tb_a = traceback.format_exception(excType, excValue, excTb)

    except ScriptRt, instance:
        isExcept = True
        excMsg_s = "%s" % (instance)
        (excType, excValue, excTb) = sys.exc_info()
        tb_a = traceback.format_exception(excType, excValue, excTb)

    except exceptions.SystemExit, instance:
        sys.exit(instance)

    except:
        isExcept = True
        excMsg_s = "unexpected exception"
        (excType, excValue, excTb) = sys.exc_info()
        tb_a = traceback.format_exception(excType, excValue, excTb)

    # handle eventual exception
    if isExcept:
        # record exception

        print("\nEXC: %s\n" % (excMsg_s))
        for line_s in tb_a:
            print(line_s.strip())
        print("\nERR: Exception reÃ§ue\n")

        dt = datetime.datetime.now()
        humanDate_s = dt.strftime("%a %x, %X ")
        l_msgerror = ""
        for line_s in tb_a:
            l_msgerror += line_s.strip()
            l_msgerror += "\n"
        print l_msgerror

        dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, l_msgerror)
        dialog.run()
        dialog.destroy()
        sys.exit(1)

    else:
        sys.exit(0)

# eof
