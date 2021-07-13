#!/usr/bin/python
# coding: utf-8 -*-

# TODO : rendre générique configdir_u dans la classe UserFunctions


###########################################################################
# VERSION #################################################################
###########################################################################
"""
maggy version = "2.0.0.41"
default version : 2.0
"""
###########################################################################
# SYSTEM LIBS #############################################################
###########################################################################

import sqlite3 as sqlite
import gtk
import os, sys, subprocess
import re
import magutils
from magutils import *

###########################################################################
# APPLICATION LIBS ########################################################
###########################################################################



###########################################################################
# CLASSES #################################################################
###########################################################################

class UserFunctions :

    

    def __init__(self, mag, arw, link, cursor, config, mem) :
        configdir_u = "d:/Mes Documents/en cours/maggy1.1/config"
        self.mag = mag
        self.arw = arw
        self.link = link
        self.cursor = cursor
        self.config = config
        self.mem = mem

            
    def alert(self, message, trou = None, normal = None) :
        dialog = gtk.MessageDialog(None,0,gtk.MESSAGE_INFO,gtk.BUTTONS_CLOSE,
                               message)
        dialog.set_markup(message)
        dialog.run()
        dialog.destroy()




    def after_load(self, id_fiche, table_config, saisieActive, saisieFlipActive) :
        # launched after the load of a record in the edit window is finished   
        return

    def after_update(self, id_livre, set1, mem):
        # launched after the saveprocessus of a record
        return
        
    def after_details(self, id_livre):
        return
        
    """
    user can create other functions which will receive as parameter a list of records.
    They are launched by th ecode : 
    call_user_func(function_name, list_of_records. Probably not really usable yet. 
    """



# ==================================================================================

def main() :
    import os
    global configdir_u, link, cursor
    

        

if __name__ == '__main__':
    main()