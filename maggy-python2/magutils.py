
# coding: utf-8
# version 2.0.0.38  December 2015

import traceback, sys

# API  ################################################

def get_extension(widget, separator = None) :


    # extrait l'extension du nom de l'objet
    # si l'extension comporte plusieurs paramètres séparés par des , on retourne un array
    # sinon on retourne l'extension comme string

    global config

    if isinstance(widget, str) :

        name = widget
    else :
        name = widget.name

    if not isset(separator) :           # useless now
        separator = config['output']['field_separator']

    extension = substr(name,strrpos(name,'@')+1)
    arParams = explode(",",extension)
    if count(arParams) == 1 :

        return extension

    else :

        return arParams



def test_signal(object) :

    name = object.name
    alert('the object $name emitted a signal')


# GTK2-add ###################################################

def get_store_length(store) :
    # works only if all columns are str
    if len(store) > 0 :
        row = store[0]
        length = len(row)
    else :  # len(row) doesn't work if there is no row. Dirty workaround :
            # we try to insert a row  until it works
        for i in range(100) :
            test = (["a"] * i)
            try :
                store.append(test)
                length = len(test)
                store.clear()
                break
            except :
                pass

    return length



# retourne l'array des iter d'un store. Pourrait être fait plus simplement en python.
def array_iter(store) :

    if store == None :
        return
    iters = []
    i=0
    temp=store.get_iter_first()
    if temp :
        iters.append(temp)
        while True :
            temp = store.iter_next(iters[i])
            i+= 1
            if temp == None :
                break
            iters.append(temp)

    return iters


""" à effacer
def arIter(treeview) :

    sel=treeview.get_selection()
    (model, arPaths) = sel.get_selected_rows()
    if arPaths :

        for path in arPaths :  arIter.append( model.get_iter(path))

    return arIter
"""



def get_store_data(store,row,col) :


    if isinstance(store,gtkTreeView) :
        alert("tv")

    # non vérifié.
    if isinstance(store,gtkListStore) :
        alert("ls")



    arIters = array_iter(store)
    data = store.get_value(arIters[row],col)
    return data




def iter_sel(treeview, single = False) :


    #if not isinstance(treeview, gtk.Treeview):
    #    print "pas bon"
    #    return;
    iters = []

    sel=treeview.get_selection()
    if single == True :

        (model, iter) = sel.get_selected()
        return iter

    else :

        (model, arPaths) = sel.get_selected_rows()
        if arPaths :

            for path in arPaths :  iters.append( model.get_iter(path))

        return iters



# row = numéro de la ligne de la sélection et non de la ligne de la liste. 0 si on veut la première ligne.
def get_sel_row_data(treeview,row,col) :


    sel=treeview.get_selection()

    (model, arPaths) = sel.get_selected_rows()

    if model and arPaths :

        iter = model.get_iter(arPaths[row])
        data = model.get_value(iter, col)
        return data

    else :

        return None;





def get_text(widget, **kwargs) :
    # kwargs :  "col" : column number (used for treeview)
    #           "row" : row number (used for treeview)

    type_s = widget_type(widget);
    text = ""

    if type_s == "GtkLabel" :
        text = widget.get_label()
        # get_text() would get the text without the pango markup if any


    elif type_s == "GtkTextView" :

        buf = widget.get_buffer();
        (a,z) = buf.get_bounds();
        text = buf.get_text(a,z);


    elif type_s == "GtkEntry" :
        text = widget.get_text();


    elif type_s == "GtkComboBox" :
        model = widget.get_model();
        if widget.get_has_entry() :
            text = widget.child.get_text()
        else :
            iter1 = widget.get_active_iter();
            if iter1 :
                text = model.get_value(iter1, 0);



    elif type_s == "GtkComboBoxEntry" :
        text= widget.get_child().get_text();


    elif (type_s == "GtkCheckButton" or
        type_s == "GtkToggleButton" or
        type_s == "GtkRadioButton") :
        state = widget.get_active();
        if state == True :
            text = 1
        else :
            text = 0



    elif type_s == "GtkTreeView" :
        if "col" in kwargs :
            col = kwargs["col"]
        else :
            col = 0
        if "row" in kwargs :
            row = kwargs["row"]
        else :
            row = 0
        text = get_sel_row_data(widget,row, col)


    return text;


def set_text(widget, text) :

    type_s = widget_type(widget);
    if text == None :
        text = ""


    if type_s == "GtkTextView" :

        buf = widget.get_buffer();
        buf.set_text(str(text));


    elif (type_s == "GtkEntry" or
        type_s == "GtkLabel") :
        widget.set_text(str(text));


    elif type_s == "GtkComboBox" :
        model = widget.get_model();
        if model != None :
            iters = array_iter(model)
            i = 0
            for iter1 in iters :
                data = model.get_value(iter1,0)
                if text == data :
                    widget.set_active(i)
                i += 1
        else:
            print "no model for ComboBox %s" % widget.name


    elif type_s == "GtkComboBoxEntry" :
        entry = widget.get_child()
        if isinstance(text, int) :
            text = str(text)
        entry.set_text(text)


    elif type_s == "GtkRadioButton" :
        if text == "" :
            text = "0"
        i = int(text)
        widget.set_active(False)

    elif type_s == "GtkTreeView" :
        pass




def append(model,data,pad = "") :

    ncol = model.get_n_columns();
    if data == None :
        data = []
    if len(data) > ncol :

        data = data[0:ncol]
    else :
        data = array_pad(data,ncol,"");

    iter1 = model.append(data);
    return iter1



def array_pad(mylist, num, value) :
    temp = []
    for i in range(0,len(mylist)) :
        temp.append(mylist[i])

    for i in range(len(mylist),num) :
        temp.append(value)
    return temp



# si count n'est pas donné ou égal à 0, renvoie la totalité du texte.
# si count est donné, renvoie le nombre de caractères spécifiés à partir du curseur
# en avant si count est positif, en arrière s'il est négatif.

def textbuffer_text(buf, count = 0, action = "get") :



    (a,z) = buf.get_bounds()
    curseur=buf.get_insert()

    if count==0 :

        text = buf.get_text(a,z)

    else :

        iter1=buf.get_iter_at_mark(curseur)
        iter2=buf.get_iter_at_mark(curseur)
        iter2.forward_chars(count)
        if action == "get" :

            text = buf.get_text(iter2,iter1)

        if action == "delete" :

            text = buf.delete(iter2,iter1)



    return text




def insertion_tv(buffer,text,tag = "") :

    if tag == "" :

        buffer.insert_at_cursor(text)

    else :

        tags = explode(";",tag)
        x=buffer.get_end_iter()
        a = buffer.create_mark("a",x,True)
        buffer.insert_at_cursor(text)
        y=buffer.get_end_iter()
        a1 = buffer.get_iter_at_mark(a)
        for z in tags :

            buffer.apply_tag_by_name(z,a1,y)








def widget_type(widget) :

    try :
        z = widget.class_path()
        z =z.split(".")
        return z[-1]
    except :
        return




def widget_group_type(type,container,arWidgets) :

    for object in arWidgets :

        if widget_type(object) == type :

            z = object.path()
            if substr(z,strrpos(z,".")+1) == container : arObjects.append( object)


    return arObjects


def widget_group(container,arWidgets) :

    arObjects = []
    for key in arWidgets :
        widget = arWidgets[key]
        try :
            z = widget.path()
            if (z.find(container + ".") == 0 ) or(z.find("." + container + ".") > 0) :
                arObjects.append(widget)
        except :
##            a,b,c = sys.exc_info()
##            for d in traceback.format_exception(a,b,c) :
##                print d,
##            print "error for :", key, widget
            pass


    return arObjects



def strpos(string, needle) :
    x = string.find(needle)

class __________utilitaires________ :
    pass

def printn(message) :

    print message + "\n"



def timer(x) :

    global memtimer

    if x <> 'result' :

        memtimer[x] = getmicrotime()

    else :

        out =  "\n --- timer --- \n"
        for i in range(2, count(memtimer)) :

            time = memtimer[i] - memtimer[i-1]
            out +=("timer $i = $time\n")

        print out
        memtimer = []
        return out




def getmicrotime() :

    while(gtk.events_pending()) :


        gtk.main_iteration()

    (usec, sec) = explode(" ",microtime())
    return(usec + sec)


def list_properties(object) :

    ar = file("properties2.txt")
    for z in ar :

        prop = trim(z)

        if object.get_property(prop) :

            arProp[prop] = object.get_property(prop)




    keys = array_keys(arProp)
    print_r(keys)

    for key  in arProp :
        val = arProp[key ]

        print key + "=>" + val + "\n"



def on_enter(entry, button) :

    # handle Enter key
    button.clicked()
    # note 3


def execInBackground(path, exe, args = "", title = "---") :

    global conf

    if file_exists(path . exe) :

        present_dir = getcwd()
        chdir(path)
        if substr(php_uname(), 0, 7) == "Windows" :

            pclose(popen("start \"$title\" \"" + exe + "\" " + args, "r"))

        else :

            exec("./" + exe + " " + escapeshellarg(args) + " > /dev/null &")

        chdir(present_dir)



# Maggy utilities #######################################################



def mysql_dir() :

    global mem, arWidgets, config

    mysql_dir = config['database']['mysql']
    if is_file(mysql_dir +"\\bin\\mysql.exe") :

        program = mysql_dir +"\\bin\\mysql.exe"

    elif is_file(mysql_dir +"\\mysql.exe") :

        program = mysql_dir +"\\mysql.exe"

    else :

        msg = sprintf(_("The mysql.exe file cannot be found neither in %s \nnor in %s\\bin. \nPlease select the directory"), mysql_dir, mysql_dir)
        alert(msg)



        dialog = gtk.FileChooserDialog("File Save", None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, # note 2
        [gtk.STOCK_OK, gtk.RESPONSE_OK], None)
        dialog.show_all()
        if dialog.run() == gtk.RESPONSE_OK :

            file = dialog.get_filename()
            # get the input filename

        dialog.destroy()

        config['database']['mysql'] = file
        mem['save_settings'] = 1




def mysql_dir2() :

    global arWidgets
    dialog = gtk.FileChooserDialog("File Save", None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, # note 2
    [gtk.STOCK_OK, gtk.RESPONSE_OK], None)
    dialog.show_all()
    win=dialog.window
    # get the GdkWindow
    win.set_keep_above(True)
    if dialog.run() == gtk.RESPONSE_OK :

        file = dialog.get_filename()
        # get the input filename

    dialog.destroy()
    if len(file) > 0 :

        config['database']['mysql'] = file
        set_text(arWidgets['s_mysql_dir_entry'], file)



def sql_error(link, req = "") :


    message=mysql_error(link)
    ok=mysql_query("SHOW COUNT(*) WARNINGS")
    message2=limitLength(mysql_result(ok,0))
    if message :

        message = limitLength(message)
        if req !="" :

            message+= "\n"+ limitLength(req)

        alert(message)
        print "\n $message"


    if message2 > 0 :

        message2 = limitLength(message2)
        ok2 = mysql_query("SHOW WARNINGS")
        for i in range(0, mysql_num_rows(ok2)) :

            message2b = mysql_result(ok2,i,0) +  "  " + mysql_result(ok2,i,2)
            message2 += " warning(s) \n" + limitLength(message2b)

        if req !="" :

            message2+= "\n"+ limitLength(req)

        alert(message2)
        print "\n $message2  \n $req"



def limitLength(string) :


    param = 150
    l = (int) (len(string) / param)
    if l > 1 :

        for i in range(0, l) :

            out += mb_substr(string, param * i, param) + "\n"


    else :

        out = string

    return out

# ==========================================================
#               Sauvegarde / Restauration
# ==========================================================
def db_save() :

    global mem, arWidgets, config

    mysql_dir = config['database']['mysql']
    userLocale = config['database']['user']
    hostLocale = config["database"]['host']
    passLocale = config["database"]['pass']
    if len(passLocale) > 0 :

        password = "-p $passLocale "

    else :

        password = ""

    if is_file(mysql_dir +"\\bin\\mysqldump.exe") :

        program = mysql_dir +"\\bin\\mysqldump.exe"

    elif is_file(mysql_dir +"\\mysqldump.exe") :

        program = mysql_dir +"\\mysqldump.exe"

    else :

        msg = sprintf(_("The mysqldump.exe file cannot be found neither in %s \nnor in %s\\bin. \nPlease verify your configuration"), mysql_dir, mysql_dir)
        alert(msg)
        return


    dialog = gtk.FileChooserDialog("File Save", None, gtk.FILE_CHOOSER_ACTION_SAVE, # note 2
    [gtk.STOCK_OK, gtk.RESPONSE_OK], None)
    dialog.show_all()
    if dialog.run() == gtk.RESPONSE_OK :

        file = dialog.get_filename()
        # get the input filename

    dialog.destroy()

    database = config['database']['database']

    commande = "\"\""+ program + "\"  -h $hostLocale -u $userLocale $password $database > " + escapeshellarg(file)+"\""

    exec(commande)
    # impossible d'utiliser l'array de retour Ã  cause du fonctionnement de mysql dump
    #qui utilise dÃ©jÃ  >. Les messages sont retournÃ©s dans la fenÃªtre DOS et non dans le programme
    # il doit Ãªtre possible de les rÃ©cupÃ©rer, mais je ne sais pas comment faire
    size = filesize(file)
    alert(_("Size of the file created  : \n") . size)





def db_restore() :

    global mem, arWidgets, config

    mysql_dir  = config['database']['mysql']
    userLocale = config['database']['user']
    passLocale = config["database"]['pass']
    if len(passLocale) > 0 :

        password = "-p $passLocale "

    else :

        password = ""

    if is_file(mysql_dir +"\\bin\\mysql.exe") :

        program = mysql_dir +"\\bin\\mysql.exe"

    elif is_file(mysql_dir +"\\mysql.exe") :

        program = mysql_dir +"\\mysql.exe"

    else :

        msg = sprintf(_("The mysql.exe file cannot be found neither in %s \nnor in %s\\bin. \nPlease verify your configuration"), mysql_dir, mysql_dir)
        alert(msg)
        return


    dialog = gtk.FileChooserDialog("File Save", None, gtk.FILE_CHOOSER_ACTION_OPEN, # note 2
    [gtk.STOCK_OK, gtk.RESPONSE_OK], None)
    dialog.show_all()
    if dialog.run() == gtk.RESPONSE_OK :

        file = dialog.get_filename()
        # get the input filename

    dialog.destroy()

    database = config['database']['database']

    commande = "\"\""+ program + "\" -u $userLocale $password $database < " + escapeshellarg(file)+"\""
    print commande
    unset(output)
    exec(commande,output)
    message = implode(chr(10),output)
    # mÃªme remarque que pour db_save;
    #alert($message);



def save_config() :

    global mem, arWidgets, config

    dialog = gtk.FileChooserDialog("File Save", None, gtk.FILE_CHOOSER_ACTION_SAVE, # note 2
    [gtk.STOCK_OK, gtk.RESPONSE_OK], None)
    dialog.show_all()
    if dialog.run() == gtk.RESPONSE_OK :

        file = dialog.get_filename()
        # get the input filename

    dialog.destroy()

    set = fopen(file,"w")
    data = var_export(config,True)
    fputs(set,"<?php" + chr(10) + '$config = ')
    fputs(set,data)
    fputs(set,";" + chr(10) +"?>")
    fclose(set)





def restore_config() :

    global mem, arWidgets, config


    dialog = gtk.FileChooserDialog("File Save", None, gtk.FILE_CHOOSER_ACTION_OPEN, # note 2
    [gtk.STOCK_OK, gtk.RESPONSE_OK], None)
    dialog.show_all()
    if dialog.run() == gtk.RESPONSE_OK :

        file = dialog.get_filename()
        # get the input filename

    dialog.destroy()

##...         include file




def save_project_as() :

    global configdir

    reponse=prompt({"Name of your new project :" : ""})
    newdir = "config/" + reponse[0]
    mkdir(newdir)

    # read the present configuration directory
    files1 = scandir(configdir)
    files2 = glob(configdir)

    for val in files1 :

        copy(val, newdir + "/" + val)






def verify_database() :

    global link, config, central_table, periph_tables, order_field

    """
* vÃ©rifier que le champ ordre existe dans les tables pÃ©riphÃ©riques
N.B. : d'autres vÃ©rifications ont Ã©tÃ© transfÃ©rÃ©es ailleurs, dans invert_words, invert_words2 et maj_table_centrale

"""


    for key  in periph_tables :
        val = periph_tables[key ]

        gateway = val['gateway']
        if len(gateway) > 0 :

            # s'il y a une passerelle
            table = key

            result = mysql_query("DESCRIBE $gateway $order_field ")
            # vÃ©rification de l'existence du champ ordre
            if mysql_num_rows(result) == 0 :

                mysql_query("ALTER TABLE $gateway ADD COLUMN $order_field INTEGER")









def php_array_to_py(input_file, output_file) :


    f1 = open(input_file, "r")
    temp = f1.read(15)      # skip beginning
    data = f1.read()
    f1.close()


    data = data.replace("array (", "{")
    # TODO : ne pas faire ces remplacements à l'intérieur des quotes.
    data = data.replace("=>", ":")
    data = data.replace("NULL", "None")

    #find closing }
    level = 0
    inside = 0
    data2 = ""
    skip = 0
    for x in data :
        if skip == 1 :
            data2 += x
            skip = 0
            continue

        if x == "\\" :
            skip = 1
            data2 += x
            continue

        elif x == "'" :
            if inside == 0 :
                inside = 1
            else :
                inside = 0
            data2 += x
            continue

        if inside == 0 :
            if x == ")" :
                x = "}"

        if inside == 1 :
            if x == "\n" :
                x = " \\\n"

        data2 += x

    data2 = data2[0:-4]

    f2 = open(output_file, "w")
    f2.write(data2)
    f2.close()


