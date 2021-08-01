OrderedDict([
("affiche1", OrderedDict([
    ("name", "affiche1"),
    ("parameters", "?,Numero de depart, default=4000;"),
    ("central_def", "completex"),
    ("widths", "40,50,50,50,50,250,400,100,50,50"),
    ("details", "normal"),
    ("query", "select id_livre,section, num, format,  notes, g_personnes, titre, editeur, annee  from complete  [where id_livre >= {1} ] ")
])),
("chartreuses", OrderedDict([
    ("comment", ""),
    ("result", ""),
    ("names", ""),
    ("parameters", ""),
    ("query", "select * from chartreuses"),
    ("central_def", ""),
    ("widths", "40,40,250,400,100,50"),
    ("config", 0),
    ("name", "chartreuses"),
    ("details", "")
])),
("essai 1", OrderedDict([
    ("name", "essai 1"),
    ("parameters", "?,Numero de depart"),
    ("central_def", "completex"),
    ("widths", "100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100"),
    ("details", "normal"),
    ("query", "select id_livre, * from complete where notes like '$' ")
])),
("essai2", OrderedDict([
    ("query", "select id_langue, * from langues"),
    ("name", "essai2"),
    ("widths", "100,100,100,100,100")
])),
("recherche par cotes", OrderedDict([
    ("comment", ""),
    ("name", "recherche par cotes"),
    ("parameters", "combo_section;
entry_num;
combo_format;
combo_notes;
combo_localisation;"),
    ("central_def", "completex"),
    ("widths", "0,30,50,30,50,250,350,100,50,50,50"),
    ("details", "normal"),
    ("query", "select id_livre, section, num, format,  notes, g_personnes, titre,annee from complete 
where 1 = 1 
[and section like "{1}"] 
[and num = "{2}"]
[and format like "{3}"]
[and notes like "{4}"]
[and localisation like "{5}"]")
])),
("requete2", OrderedDict([
    ("central_def", "completex"),
    ("query", "select id_livre, notes, g_personnes, titre, editeur, date  from complete  where notes like "%EX%""),
    ("details", "normal"),
    ("name", "requete2"),
    ("widths", "40,40,250,400,100,50")
])),
("test2", OrderedDict([
    ("comment", ""),
    ("result", "complete_aut_ord"),
    ("name", "test2"),
    ("parameters", "40,50,50,50,50,250,400,100,50,50"),
    ("central_def", "completex"),
    ("widths", "40,40,40,40,40,40,40,40"),
    ("details", "normal"),
    ("query", "select id_livre, titre, editeur, annee from complete limit 1000"),
    ("config", 0),
    ("names", "")
])),
("toto", OrderedDict([
    ("comment", ""),
    ("result", "complete"),
    ("parameters", ""),
    ("widths", ""),
    ("central_def", "completex"),
    ("query", "select id_livre, g_personnes, titre, maison  from complete where format like "AC""),
    ("details", "normal"),
    ("config", 1),
    ("name", "toto"),
    ("names", "")
])),
("toutes les fiches", OrderedDict([
    ("comment", ""),
    ("result", "complete_aut_ord"),
    ("names", ""),
    ("parameters", ""),
    ("query", "select id_livre,section, num, format,  notes, auteur, titre, editeur, annee from complete limit 1000"),
    ("central_def", "completex"),
    ("widths", "40,50,50,50,50,250,400,100,50,50"),
    ("config", 0),
    ("name", "toutes les fiches"),
    ("details", "normal")
]))
])