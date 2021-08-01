# coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      dysmas
#
# Created:     16/06/2012
# Copyright:   (c) dysmas 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import sys, time
import traceback
import re

import _mysql
import MySQLdb
from MySQLdb import cursors

import sqlite3 as sqlite




def printExcept2(
          ) :
    a,b,c = sys.exc_info()
    for d in traceback.format_exception(a,b,c) :
        print d,
# ============================================================================

class SqliteUnicode :
    #
    def __init__(self) :
        self.collation = { u"a" : u"aàâä",
                           u"e" : u"eéèêë",
                           u"i" : u"iîï",
                           u"o" : u"oôö",
                           u"u" : u"uûü",
                           u"à" : u"aàâä",
                           u"è" : u"eéèêë",
                           u"ù" : u"uûü",
                           u"é" : u"eéèêë",
                           u"â" : u"aàâä",
                           u"ê" : u"eéèêë",
                           u"î" : u"iîï",
                           u"ô" : u"oôö",
                           u"û" : u"uûü",
                           u"ä" : u"aàâä",
                           u"ë" : u"eéèêë",
                           u"ï" : u"iîï",
                           u"ö" : u"oôö",
                           u"ü" : u"uûü",
                           u"c" : u"cç",
                           u"s" : u"sš"
                           }

        self.collation_ci = {}
        self.reg_exp = {}

        for a in self.collation :
            data = self.collation[a]
            self.collation_ci[a] = data + data.upper()

        # remove accents
        remove_accents1 = { u"a" : u"àáâãäåą",
                             "c" : u"çćč",
                             "d" : u"ð",
                             "e" : u"èéêëęε",
                             "i" : u"ìíîï",
                             "l" : u"ł",
                             "n" : u"ñńŋ",
                             "o" : u"òóôõöøő",
                             "r" : u"ř",
                             "s" : u"šśß",
                             "u" : u"ùúûüű",
                             "y" : u"ýÿ",
                             "z" : u"źżž",
                             u"ae" : u"æÆ",
                             u"oe" : u"œŒ"
                           }



        self.remove_accents = {}
        for key, value in remove_accents1.iteritems() :
            for letter in value :
                self.remove_accents[letter] = key

        # remove some other characters
        for letter in u"([<>…" :
            self.remove_accents[letter] = ""




        # regular expressions
        # We compile them to improve performance

        # These ones are used by collate
        self.re1 = re.compile(u"[àâä]")
        self.re2 = re.compile(u"[éèêë]")
        self.re3 = re.compile(u"[îï]")
        self.re4 = re.compile(u"[ôö]")
        self.re5 = re.compile(u"[ûü]")




    def replace_accents(self, string) :
    # used by like2 which too slow. Unused. 
    # This function will replace accentuated characters to allow a friendly like
    # e will find éèê etc. oe will find œ

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
            print "compile error", reg_string
        self.reg_exp[data] = comp_reg
        print reg_string.encode("utf8")
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
            print "echec de like : ", a, "/", b
            utils.printExcept()
            return False


    def like2(self, a, b) :
        # On a 80000 rows table :
        # original like takes 0.002s
        # this like takes 0.5 s (about 200x)
        # Unusable
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
            print "echec de like : ", a, "/", b
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

        string1 = unicode(string1,"utf_8")
        string2 = unicode(string2,"utf_8")
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

        compare = cmp(string1, string2)

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





def load_sqlite(db_file_s) :


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
    link.create_function("like", 2, extension.like)
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

    return (link, cursor)




cnx, cursor = load_sqlite("config/gb/gb.sqlite")

x1 = time.time()
req = "select mot from mots where mot like '%oeuvre%'"
result = cursor.execute(req)
x2 = time.time() - x1
a = cursor.fetchall()
for b in a :
    print b
print len(a)
print x2

contenu = u"essai pour la bibliothèque"

ex1 = re.findall(u"(?u) \w+",contenu);   # division en mots
print ex1
