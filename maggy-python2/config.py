 {
  'database' : 
  {
    'central_table' : None,
    'main_field' : None,
    'modified_field' : 'datemodification',
    'host' : 'localhost',
    'user' : 'root',
    'pass' : '',
    'database' : 'alcool2',
    'order_field' : '',
    'deleted_records' : '',
    'mysql' : 'c:/prog3/gb/mysql test/bin/',
    'from' : None,
  },
  'input' : 
  {
    'container' : 'window4',
    'field_indicator' : '@',
    'separator' : '#',
  },
  'peripheral' : 
  {
    'requetes' : 
    {
      'cols' : '',
      'info' : None,
      'central_def' : '',
      'gateway' : '',
      'id_type' : 'id_requete',
      'main_field' : 'nom',
      'table' : 'requetes',
    },
    'lexique' : 
    {
      'cols' : '',
      'info' : None,
      'central_def' : '',
      'gateway' : '',
      'id_type' : 'id_lexique',
      'main_field' : 'sujet',
      'table' : 'lexique',
    },
    'recette' : 
    {
      'cols' : '',
      'info' : None,
      'central_def' : '',
      'gateway' : '',
      'id_type' : 'id_recette',
      'main_field' : 'coderecette',
      'table' : 'recette',
    },
    'fournisseur' : 
    {
      'cols' : '',
      'info' : None,
      'central_def' : '',
      'gateway' : '',
      'id_type' : 'NumFournisseur',
      'main_field' : 'NomFournisseur',
      'table' : 'fournisseur',
    },
    'commande' : 
    {
      'cols' : '',
      'info' : None,
      'central_def' : '',
      'gateway' : '',
      'id_type' : 'id_commande',
      'main_field' : 'NumCmde',
      'table' : 'commande',
    },
    'douanes' : 
    {
      'cols' : '',
      'info' : None,
      'central_def' : '',
      'gateway' : '',
      'id_type' : 'id_douanes',
      'main_field' : 'nom',
      'table' : 'douanes',
    },
    'liqueurs' : 
    {
      'cols' : '',
      'info' : None,
      'central_def' : 'def_inventaires',
      'gateway' : 'inventaire_liqueur',
      'id_type' : 'id_liqueur',
      'main_field' : 'CodeLiqueur',
      'table' : 'liqueurs',
    },
    'produits' : 
    {
      'cols' : '',
      'info' : None,
      'central_def' : 'def_inventaires',
      'gateway' : '',
      'id_type' : 'id_produit',
      'main_field' : 'produit',
      'table' : 'produits',
    },
    'foudresx' : 
    {
      'cols' : '',
      'info' : None,
      'central_def' : 'def_inventaires',
      'gateway' : 'inventaire_foudre',
      'id_type' : 'id_foudre',
      'main_field' : 'numfoudre',
      'table' : 'foudres',
    },
    'cavesx' : 
    {
      'cols' : None,
      'info' : None,
      'central_def' : 'def_inventaires',
      'gateway' : 'inventaire_cave',
      'id_type' : 'id_cave',
      'main_field' : 'cave',
      'table' : 'caves',
    },
    'moutures' : 
    {
      'cols' : '',
      'table' : 'mouturegene',
      'gateway' : '',
      'id_type' : 'id_mouture',
      'main_field' : 'CodeMouture',
    },
    'sacs' : 
    {
      'cols' : None,
      'info' : None,
      'central_def' : 'def_moutures',
      'gateway' : 'mouture_sac',
      'id_type' : 'id_sac',
      'main_field' : 'numsacmouture',
      'table' : 'sacmouture',
    },
    'menu' : 
    {
      'cols' : '',
      'table' : 'menu',
      'id_main' : '',
      'edit' : '',
      'edit tab' : '',
      'gateway' : '',
      'id_type' : 'id_menu',
      'main_field' : 'menu',
    },
    'plantesx' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : '',
          'width' : '150',
          'type' : '',
        },
        1 : 
        {
          'field' : 'NumSacPlante',
          'width' : '30',
          'type' : 'list',
          'title' : 'sac',
        },
        2 : 
        {
          'field' : 'NumLotPlante',
          'width' : '80',
          'type' : 'list',
          'title' : 'lot',
        },
        3 : 
        {
          'field' : 'Poids',
          'width' : '50',
          'type' : '',
          'title' : 'poids',
        },
      },
      'info' : None,
      'central_def' : 'def_moutures',
      'gateway' : 'mouture_plante',
      'id_type' : 'id_plante',
      'main_field' : 'CodePlante',
      'table' : 'plantes',
    },
    'en cours sac' : 
    {
      'cols' : '',
      'table' : 'encours_mouturesac',
      'id_main' : '',
      'edit' : '',
      'edit tab' : '',
      'gateway' : '',
      'id_type' : 'id_sac',
      'main_field' : 'numsacmouture',
    },
    'en cours recette' : 
    {
      'cols' : '',
      'table' : 'encours_recette',
      'id_main' : '',
      'edit' : '',
      'edit tab' : '',
      'gateway' : '',
      'id_type' : 'id_mouture',
      'main_field' : 'CodePlante',
    },
    'en cours plante' : 
    {
      'cols' : '',
      'table' : 'encours_moutureplante',
      'id_main' : '',
      'edit' : '',
      'edit tab' : '',
      'gateway' : '',
      'id_type' : 'id_plante',
      'main_field' : 'CodePlante',
    },
    'en cours mouture' : 
    {
      'cols' : '',
      'table' : 'encours_mouture',
      'id_main' : '',
      'edit' : '',
      'edit tab' : '',
      'gateway' : '',
      'id_type' : 'id_mouture',
      'main_field' : 'CodeMouture',
    },
    'alcool' : 
    {
      'cols' : '',
      'table' : 'alcool',
      'id_main' : '',
      'edit' : '',
      'edit tab' : '',
      'gateway' : '',
      'id_type' : 'id_alcool',
      'main_field' : 'CodeAlcool',
    },
    'sirop' : 
    {
      'cols' : '',
      'table' : 'sirop',
      'id_main' : '',
      'edit' : '',
      'edit tab' : '',
      'gateway' : '',
      'id_type' : 'id_sirop',
      'main_field' : 'CodeSirop',
    },
    's_predef_queries' : 
    {
      'cols' : None,
      'table' : 'requetes',
      'id_main' : '',
      'edit' : '',
      'edit tab' : '',
      'gateway' : '',
      'id_type' : 'id_requete',
      'main_field' : 'nom',
    },
  },
  'inversion' : None,
  'gateway_data' : 
  {
    'personnes' : ',200,,',
    'personnes1' : 
    {
      0 : 'fonction',
      1 : '100',
      2 : 'list',
      3 : '',
    },
    'personnes2' : 
    {
      0 : 'anonyme',
      1 : '50',
      2 : 'list',
      3 : '',
    },
  },
  'lists' : 
  {
    'max_lines' : '500',
    'font' : 'Arial',
    'font_size' : '9',
    'line_height' : '18',
    'type_delay' : '1000',
  },
  'periph_tables' : 
  {
    0 : 'plante',
    1 : 'requetes',
    2 : 'lexique',
    3 : 'recette',
    4 : 'fournisseur',
    5 : 'foudres',
    6 : 'mouturegene',
    7 : 'commande',
    8 : 'douanes',
    9 : 'sacmouture',
    10 : 'liqueurs',
    11 : 'produits',
    12 : 'caves',
  },
  'xtabs' : 
  {
    'menu' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'menu',
          'width' : '200',
          'title' : '',
          'detail' : '             <b>MENU</b>',
        },
        1 : 
        {
          'field' : 'choix',
          'width' : '',
          'title' : '',
          'detail' : 'menu_option',
        },
      },
      'check' : None,
      'treeview' : 'treeview_menu',
      'type' : 'tree',
      'entry' : '',
      'table_def' : 'menu',
      'result_def' : '',
      'details_def' : '',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'en cours mp' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'CodePlante',
          'width' : '100',
          'title' : 'Code Plante',
          'detail' : 'encours_codeplante',
        },
        1 : 
        {
          'field' : 'NumLotPlante',
          'width' : '100',
          'title' : 'Lot Plante',
          'detail' : 'encours_NumLotPlante',
        },
        2 : 
        {
          'field' : 'NumSacPlante',
          'width' : '100',
          'title' : 'Sac Plante',
          'detail' : 'encours_NumSacPlante',
        },
        3 : 
        {
          'field' : 'Poids',
          'width' : '100',
          'title' : 'Poids',
          'detail' : 'encours_poidsplante',
        },
      },
      'check' : None,
      'treeview' : 'mouture_droite',
      'type' : 'list',
      'entry' : '',
      'table_def' : 'en cours plante',
      'result_def' : '',
      'details_def' : '',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'en cours sac' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'numsacmouture',
          'width' : '150',
          'title' : 'Sac Mouture',
          'detail' : 'encours_numsac',
        },
        1 : 
        {
          'field' : 'poidssac',
          'width' : '100',
          'title' : 'Poids',
          'detail' : 'encours_poids-sac',
        },
      },
      'check' : None,
      'treeview' : 'encours_sac',
      'type' : 'list',
      'entry' : '',
      'table_def' : 'en cours sac',
      'result_def' : '',
      'details_def' : '',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'en cours r' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'CodePlante',
          'width' : '100',
          'title' : '',
          'detail' : '',
        },
      },
      'check' : None,
      'treeview' : 'mouture_gauche',
      'type' : 'list',
      'entry' : '',
      'table_def' : 'en cours recette',
      'result_def' : '',
      'details_def' : '',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'en cours m' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'CodeMouture',
          'width' : '150',
          'title' : 'Code Mouture',
          'detail' : 'encours_CodeMouture',
        },
        1 : 
        {
          'field' : 'id_mouture',
          'width' : '50',
          'title' : 'id',
          'detail' : '',
        },
        2 : 
        {
          'field' : 'CodeFabrication',
          'width' : '',
          'title' : '',
          'detail' : 'encours_CodeFabrication',
        },
        3 : 
        {
          'field' : 'DateLastModif',
          'width' : '',
          'title' : '',
          'detail' : 'encours_DateLastModif',
        },
        4 : 
        {
          'field' : 'DateCreation',
          'width' : '',
          'title' : '',
          'detail' : 'encours_DateCreation',
        },
        5 : 
        {
          'field' : 'Designation',
          'width' : '',
          'title' : '',
          'detail' : 'encours_Designation',
        },
        6 : 
        {
          'field' : 'Remarque',
          'width' : '',
          'title' : '',
          'detail' : 'encours_Remarque',
        },
      },
      'check' : None,
      'treeview' : 'encours_mouture',
      'type' : 'list',
      'entry' : '',
      'table_def' : 'en cours mouture',
      'result_def' : '',
      'details_def' : '',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'alcool' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'CodeAlcool',
          'width' : '100',
          'title' : '',
          'detail' : 'alcool_code',
        },
        1 : 
        {
          'field' : 'Designation',
          'width' : '200',
          'title' : '',
          'detail' : 'alcool_designation',
        },
        2 : 
        {
          'field' : 'Remarque',
          'width' : '',
          'title' : '',
          'detail' : 'alcool_remarque',
        },
      },
      'check' : None,
      'treeview' : 'liste_alcool',
      'type' : 'list',
      'entry' : 'tapez_alcools',
      'table_def' : 'alcool',
      'result_def' : '',
      'details_def' : '',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'sirop' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'CodeSirop',
          'width' : '150',
          'title' : '',
          'detail' : 'sirop_code',
        },
        1 : 
        {
          'field' : 'Designation',
          'width' : '200',
          'title' : '',
          'detail' : 'sirop_designation',
        },
        2 : 
        {
          'field' : 'Remarque',
          'width' : '',
          'title' : '',
          'detail' : 'sirop_remarque',
        },
      },
      'check' : None,
      'treeview' : 'liste_sirop',
      'type' : 'list',
      'entry' : 'tapez_sirops',
      'table_def' : 'sirop',
      'result_def' : '',
      'details_def' : '',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'predef_req27' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'id_requete',
        },
        1 : 
        {
          'field' : 'nom',
          'width' : '200',
          'title' : 'RequÃªte',
          'detail' : 's_nom4',
        },
        2 : 
        {
          'field' : 'requete',
          'width' : '400',
          'title' : 'Syntaxe SQL',
          'detail' : 's_requete4',
        },
        3 : 
        {
          'field' : 'largeurs',
          'detail' : 's_largeurs4',
        },
        4 : 
        {
          'field' : 'comment',
          'width' : '',
          'title' : '',
          'detail' : 's_comment4',
        },
        5 : 
        {
          'field' : 'parameters',
          'width' : '',
          'title' : '',
          'detail' : 's_parameters4',
        },
        6 : 
        {
          'field' : 'details',
          'width' : '',
          'title' : '',
          'detail' : 's_details4',
        },
      },
      'table_def' : 'requetes',
      'treeview' : 's_clist4',
      'type' : 'list',
      'entry' : 's_tapez4',
      'renvoi' : '',
      'couleur' : '',
    },
    'test1' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'id_inventaire',
          'width' : '100',
          'title' : '',
          'detail' : '',
        },
        1 : 
        {
          'field' : 'numfoudre',
          'width' : '100',
          'title' : '',
          'detail' : '',
        },
      },
      'treeview' : 'treeview_test',
      'type' : 'list',
      'entry' : '',
      'table_def' : 'produits',
      'result_def' : '',
      'details_def' : '',
      'couleur' : '',
      'complement' : '',
      'options' : 'n',
    },
    's_predef_queries' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'id_requete',
        },
        1 : 
        {
          'field' : 'nom',
          'width' : '200',
          'title' : 'Requête',
          'detail' : 's_nom4',
        },
        2 : 
        {
          'field' : 'requete',
          'width' : '400',
          'title' : 'Syntaxe SQL',
          'detail' : 's_requete4',
        },
        3 : 
        {
          'field' : 'largeurs',
          'detail' : 's_largeurs4',
        },
        4 : 
        {
          'field' : 'comment',
          'width' : '',
          'title' : '',
          'detail' : 's_comment4',
        },
        5 : 
        {
          'field' : 'parameters',
          'width' : '',
          'title' : '',
          'detail' : 's_parameters4',
        },
        6 : 
        {
          'field' : 'details',
          'width' : '',
          'title' : '',
          'detail' : 's_details4',
        },
      },
      'table_def' : 's_predef_queries',
      'treeview' : 's_clist4',
      'type' : 'list',
      'entry' : 's_tapez4',
      'renvoi' : '',
      'couleur' : '',
    },
    'plantes' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'CodePlante',
          'width' : '100',
          'title' : 'Code',
          'detail' : 'plante_code',
        },
        1 : 
        {
          'field' : 'Remarque',
          'width' : '200',
          'title' : 'Remarque',
          'detail' : 'plante_remarque',
        },
        2 : 
        {
          'field' : '#',
          'width' : '40',
          'title' : '',
          'detail' : '',
        },
      },
      'check' : None,
      'treeview' : 'liste_plantes',
      'type' : 'list',
      'entry' : 'tapez_plantes',
      'table_def' : 'plantesx',
      'result_def' : 'moutures',
      'details_def' : 'moutures',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'recettes' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'coderecette',
          'width' : '100',
          'title' : 'code',
          'detail' : 'recette_code',
        },
        1 : 
        {
          'field' : 'codeplante',
          'width' : '100',
          'title' : 'plante',
          'detail' : 'recette_code_plante',
        },
      },
      'check' : None,
      'treeview' : 'liste_recettes',
      'type' : 'list',
      'entry' : 'tapez_recettes',
      'table_def' : 'recette',
      'result_def' : '',
      'details_def' : '',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'moutures' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'CodeMouture',
          'width' : '100',
          'title' : '',
          'detail' : 'mouture_code',
        },
        1 : 
        {
          'field' : 'CodeFabrication',
          'width' : '100',
          'title' : '',
          'detail' : 'mouture_fabrication',
        },
        2 : 
        {
          'field' : 'Designation',
          'width' : '100',
          'title' : '',
          'detail' : 'mouture_designation',
        },
        3 : 
        {
          'field' : 'g_plantes',
          'width' : '',
          'title' : '',
          'detail' : 'mouture_plantes',
        },
        4 : 
        {
          'field' : 'Remarque',
          'width' : '',
          'title' : '',
          'detail' : 'mouture_remarque',
        },
        5 : 
        {
          'field' : '#',
          'width' : '50',
          'title' : '',
          'detail' : '',
        },
        6 : 
        {
          'field' : 'DateCreation',
          'width' : '',
          'title' : '',
          'detail' : 'mouture_creation',
        },
        7 : 
        {
          'field' : 'DateLastModif',
          'width' : '',
          'title' : '',
          'detail' : 'mouture_modif',
        },
      },
      'check' : None,
      'treeview' : 'liste_moutures',
      'type' : 'list',
      'entry' : 'tapez_mouture',
      'table_def' : 'moutures',
      'result_def' : '',
      'details_def' : '',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'sacs' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'numsacmouture',
          'width' : '170',
          'title' : 'Essai',
          'detail' : 'num_sac_mouture',
        },
        1 : 
        {
          'field' : '#',
          'width' : '30',
          'title' : 'Compte',
        },
        2 : 
        {
          'field' : 'poidssac',
          'width' : '',
          'title' : '',
          'detail' : 'sac_poids',
        },
      },
      'check' : None,
      'treeview' : 'liste_sacs',
      'type' : 'list',
      'entry' : 'tapez_sacs',
      'table_def' : 'sacs',
      'result_def' : 'moutures',
      'details_def' : 'moutures',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'produits' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'produit',
          'width' : '200',
          'title' : 'Code',
          'detail' : 'produit_code',
        },
        1 : 
        {
          'field' : '#',
          'width' : '40',
          'title' : '',
          'detail' : '',
        },
        2 : 
        {
          'field' : 'Designation',
          'width' : '200',
          'title' : 'Désignation',
          'detail' : 'produit_designation',
        },
      },
      'check' : None,
      'treeview' : 'liste_produits',
      'type' : 'list',
      'entry' : 'tapez_produits',
      'table_def' : 'produits',
      'result_def' : 'inventaire',
      'details_def' : 'inventaire',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'caves' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'cave',
          'width' : '200',
          'title' : 'Désignation',
          'detail' : 'cave_nom',
        },
        1 : 
        {
          'field' : '#',
          'width' : '40',
          'title' : '',
          'detail' : '',
        },
        2 : 
        {
          'field' : 'Remarque',
          'width' : '200',
          'title' : 'Remarque',
          'detail' : 'cave_remarque',
        },
      },
      'check' : None,
      'treeview' : 'liste_caves',
      'type' : 'list',
      'entry' : 'tapez_caves',
      'table_def' : 'cavesx',
      'result_def' : 'inventaire',
      'details_def' : 'inventaire',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'liqueurs' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'CodeLiqueur',
          'width' : '100',
          'title' : 'Code',
          'detail' : 'liqueur_code',
        },
        1 : 
        {
          'field' : '#',
          'width' : '50',
          'title' : '',
          'detail' : '',
        },
        2 : 
        {
          'field' : 'Designation',
          'width' : '100',
          'title' : 'Désignation',
          'detail' : 'liqueur_designation',
        },
      },
      'check' : None,
      'treeview' : 'liste_liqueurs',
      'type' : 'list',
      'entry' : 'tapez_liqueurs',
      'table_def' : 'liqueurs',
      'result_def' : 'inventaire',
      'details_def' : 'inventaire',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'foudres' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'numfoudre',
          'width' : '150',
          'title' : 'Code',
          'detail' : 'foudre_code',
        },
        1 : 
        {
          'field' : 'contenance',
          'width' : '100',
          'title' : 'Contenance',
          'detail' : 'foudre_contenance',
        },
        2 : 
        {
          'field' : 'cave',
          'width' : '150',
          'title' : 'Cave',
          'detail' : 'foudre_cave',
        },
        3 : 
        {
          'field' : '#',
          'width' : '40',
          'title' : '',
          'detail' : '',
        },
      },
      'check' : None,
      'treeview' : 'liste_foudres',
      'type' : 'list',
      'entry' : 'tapez_foudres',
      'table_def' : 'foudresx',
      'result_def' : 'inventaire',
      'details_def' : 'inventaire',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'douanes' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'nom',
          'width' : '150',
          'title' : 'Date',
          'detail' : '',
        },
        1 : 
        {
          'field' : 'datedeclaration',
          'width' : '150',
          'title' : 'Date',
          'detail' : 'douanes_date',
        },
        2 : 
        {
          'field' : 'stockdebprinc',
          'width' : '',
          'title' : '',
          'detail' : 'douanes_stockdebut1',
        },
        3 : 
        {
          'field' : 'entreeprinc',
          'width' : '',
          'title' : '',
          'detail' : 'douanes_entrees1',
        },
        4 : 
        {
          'field' : 'sortieprinc',
          'width' : '',
          'title' : '',
          'detail' : 'douanes_sorties1',
        },
        5 : 
        {
          'field' : 'stockfinsubd',
          'width' : '',
          'title' : '',
          'detail' : 'douanes_stockfin1',
        },
        6 : 
        {
          'field' : 'stockdebsubd',
          'width' : '',
          'title' : '',
          'detail' : 'douanes_stockdebut2',
        },
        7 : 
        {
          'field' : 'entreesubd',
          'width' : '',
          'title' : '',
          'detail' : 'douanes_entrees2',
        },
        8 : 
        {
          'field' : 'sortiesubd',
          'width' : '',
          'title' : '',
          'detail' : 'douanes_sorties2',
        },
        9 : 
        {
          'field' : 'stockfinsubd',
          'width' : '',
          'title' : '',
          'detail' : 'douanes_stockfin2',
        },
      },
      'check' : None,
      'treeview' : 'liste_douanes',
      'type' : 'list',
      'entry' : 'tapez_douanes',
      'table_def' : 'douanes',
      'result_def' : '',
      'details_def' : '',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'fournisseurs' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'NomFournisseur',
          'width' : '250',
          'title' : '',
          'detail' : 'fournisseur_nom',
        },
        1 : 
        {
          'field' : '#',
          'width' : '50',
          'title' : '',
          'detail' : '',
        },
        2 : 
        {
          'field' : 'Adresse',
          'width' : '',
          'title' : '',
          'detail' : 'fournisseur_adresse',
        },
        3 : 
        {
          'field' : 'CodePostal',
          'width' : '',
          'title' : '',
          'detail' : 'fournisseur_CP',
        },
        4 : 
        {
          'field' : 'Ville',
          'width' : '200',
          'title' : '',
          'detail' : 'fournisseur_ville',
        },
        5 : 
        {
          'field' : 'Contact',
          'width' : '',
          'title' : '',
          'detail' : 'fournisseur_contact',
        },
        6 : 
        {
          'field' : 'NumTelephone',
          'width' : '',
          'title' : '',
          'detail' : 'fournisseur_tel',
        },
        7 : 
        {
          'field' : 'NumFax',
          'width' : '',
          'title' : '',
          'detail' : 'fournisseur_fax',
        },
        8 : 
        {
          'field' : 'Email',
          'width' : '',
          'title' : '',
          'detail' : 'fournisseur_email',
        },
        9 : 
        {
          'field' : 'CodeNAF',
          'width' : '',
          'title' : '',
          'detail' : 'fournisseur_APE',
        },
        10 : 
        {
          'field' : 'Compte',
          'width' : '',
          'title' : '',
          'detail' : 'fournisseur_virement',
        },
        11 : 
        {
          'field' : 'CodeBanque',
          'width' : '',
          'title' : '',
          'detail' : 'fournisseur_banque',
        },
        12 : 
        {
          'field' : 'CodeGuichet',
          'width' : '',
          'title' : '',
          'detail' : 'fournisseur_guichet',
        },
        13 : 
        {
          'field' : 'NumCompteBanque',
          'width' : '',
          'title' : '',
          'detail' : 'fournisseur_compte',
        },
        14 : 
        {
          'field' : 'CleRIB',
          'width' : '',
          'title' : '',
          'detail' : 'fournisseur_RIB',
        },
        15 : 
        {
          'field' : 'Remarque',
          'width' : '',
          'title' : '',
          'detail' : 'fournisseur_remarque',
        },
      },
      'check' : None,
      'treeview' : 'liste_fournisseurs',
      'type' : 'list',
      'entry' : 'tapez_fournisseurs',
      'table_def' : 'fournisseur',
      'result_def' : '',
      'details_def' : '',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'commandes' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'NumCmde',
          'width' : '100',
          'title' : '',
          'detail' : '',
        },
        1 : 
        {
          'field' : 'CodePlante',
          'width' : '100',
          'title' : '',
          'detail' : '',
        },
      },
      'check' : None,
      'treeview' : 'liste_commandes',
      'type' : 'list',
      'entry' : 'tapez_commandes',
      'table_def' : 'commande',
      'result_def' : '',
      'details_def' : '',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
    'lexique' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'sujet',
          'width' : '150',
          'title' : 'Sujet',
          'detail' : 'lexique_sujet',
        },
        1 : 
        {
          'field' : 'theme',
          'width' : '150',
          'title' : '',
          'detail' : 'lexique_theme',
        },
        2 : 
        {
          'field' : 'annotation',
          'width' : '200',
          'title' : '',
          'detail' : 'lexique_annotation',
        },
        3 : 
        {
          'field' : 'date_annotation',
          'width' : '',
          'title' : '',
          'detail' : 'lexique_date_annotation',
        },
        4 : 
        {
          'field' : 'auteur',
          'width' : '',
          'title' : '',
          'detail' : 'lexique_auteur',
        },
      },
      'check' : None,
      'treeview' : 'liste_lexique',
      'type' : 'list',
      'entry' : 'tapez_lexique',
      'table_def' : 'lexique',
      'result_def' : '',
      'details_def' : '',
      'couleur' : '',
      'complement' : '',
      'options' : '',
    },
  },
  'fieldlist' : 
  {
    1 : 
    {
      'from' : '',
      'nom' : 'Code liqueur',
      'niveau' : '',
      'etoile' : 'CodeLiqueur',
      'centrale' : 'CodeLiqueur',
    },
    2 : 
    {
      'from' : '',
      'nom' : 'Volume',
      'niveau' : '',
      'etoile' : 'Vol',
      'centrale' : 'Vol',
    },
    3 : 
    {
      'from' : '',
      'nom' : 'Désignation',
      'niveau' : '',
      'etoile' : '',
      'centrale' : 'Designation',
    },
    4 : 
    {
      'from' : '',
      'nom' : 'Date Début',
      'niveau' : '',
      'etoile' : '',
      'centrale' : 'DateDebut',
    },
    6 : 
    {
      'from' : '',
      'nom' : 'Date fin',
      'niveau' : '',
      'etoile' : '',
      'centrale' : '',
    },
    5 : 
    {
      'from' : '',
      'nom' : 'Etat',
      'niveau' : '',
      'etoile' : 'Etat',
      'centrale' : 'Etat',
    },
  },
  'output' : 
  {
    'field_separator' : '|',
  },
  'zoom2' : 
  {
    'x' : 0,
    'y' : 512,
    'h' : 144,
    'w' : 1008,
  },
  'result' : 
  {
    'moutures' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'id_mouture',
          'width' : '40',
          'visible' : '',
          'alias' : '',
        },
        1 : 
        {
          'field' : 'CodeMouture',
          'width' : '100',
          'visible' : '1',
          'alias' : '',
        },
        2 : 
        {
          'field' : 'CodeFabrication',
          'width' : '100',
          'visible' : '1',
          'alias' : '',
        },
        3 : 
        {
          'field' : 'Designation',
          'width' : '100',
          'visible' : '1',
          'alias' : '',
        },
        4 : 
        {
          'field' : 'g_plantes',
          'width' : '100',
          'visible' : '1',
          'alias' : '',
        },
      },
      'sort' : 
      {
        0 : 
        {
          'name' : 'essai 1',
          'sort1' : 'CodeMouture',
          'sort2' : '',
          'sort3' : '',
        },
        1 : 
        {
          'name' : 'essai 2',
          'sort1' : 'CodeFabrication',
          'sort2' : '',
          'sort3' : '',
        },
        2 : 
        {
          'name' : 'essai 3',
          'sort1' : 'Designation',
          'sort2' : '',
          'sort3' : '',
        },
      },
      'from' : 'mouturegene',
    },
    'simple' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : '*',
          'width' : '40',
          'visible' : '1',
        },
        1 : 
        {
          0 : '',
          'width' : '40',
          'visible' : '1',
        },
        2 : 
        {
          0 : '',
          'width' : '40',
          'visible' : '1',
        },
        3 : 
        {
          0 : '',
          'width' : '200',
          'visible' : '1',
        },
      },
      'from' : 'mouturegene',
      'details tab' : '1',
    },
    'inventaire' : 
    {
      'cols' : 
      {
        0 : 
        {
          'field' : 'id_inventaire',
          'width' : '40',
          'visible' : '0',
          'alias' : '',
        },
        1 : 
        {
          'field' : 'numfoudre',
          'width' : '100',
          'visible' : '1',
          'alias' : '',
        },
        2 : 
        {
          'field' : 'contenance',
          'width' : '100',
          'visible' : '1',
          'alias' : '',
        },
        3 : 
        {
          'field' : 'produit',
          'width' : '100',
          'visible' : '1',
          'alias' : '',
        },
        4 : 
        {
          'field' : 'g_foudres',
          'width' : '100',
          'visible' : '1',
          'alias' : '',
        },
      },
      'from' : 'inventaire',
      'details tab' : '1',
      'sort' : 
      {
        0 : 
        {
          'name' : 'test 1',
          'sort1' : '',
          'sort2' : '',
          'sort3' : '',
        },
        1 : 
        {
          'name' : 'test 2',
          'sort1' : '',
          'sort2' : '',
          'sort3' : '',
        },
        2 : 
        {
          'name' : 'test 3',
          'sort1' : '',
          'sort2' : '',
          'sort3' : '',
        },
      },
    },
  },
  'zoom1' : 
  {
    'x' : -4,
    'y' : -4,
    'h' : 671,
    'w' : 1024,
  },
  125 : 11,
  'details' : 
  {
    'normal' : 
    {
      'zones' : 
      {
        0 : 
        {
          'code' : '[CodeLiqueur] \
',
          'widget' : 'detail_cote',
          'name' : 'cote',
        },
        1 : 
        {
          'code' : '[CodeMouture]',
          'widget' : 'detail_id',
          'name' : 'id',
        },
        2 : 
        {
          'code' : '[Designation]',
          'widget' : 'detail_auteur',
          'name' : 'auteur',
        },
        3 : 
        {
          'code' : '[DateDebut] / [DateFin]',
          'widget' : 'detail_titre',
          'name' : 'titre',
        },
        4 : 
        {
          'code' : '<b><span foreground="red">Alcool : </span></b>  [g_alcool, separator = -- ] \
<span foreground="red"><b>Sirop : </span></b>  [g_sirop, separator = -- ] \
',
          'widget' : 'detail_comp',
          'name' : 'plantes',
        },
        5 : 
        {
          'code' : '[Remarque]',
          'widget' : 'detail_autres',
          'name' : 'autres',
        },
        6 : 
        {
          'code' : '<b><span foreground="red">Moutures</b></span> :   [g_mouturegene, separator =  \
                    ]',
          'widget' : 'detail_themes',
          'name' : 'themes',
        },
      },
      'table' : '',
      'id_field' : '',
      'details tab' : '',
    },
    'inventaire' : 
    {
      'zones' : 
      {
        0 : 
        {
          'code' : 'Foudre : [numfoudre] \
             [contenance]',
          'widget' : 'detail_cote',
          'name' : 'cote',
        },
        1 : 
        {
          'code' : '[produit] \
[codeliqueur]',
          'widget' : 'detail_auteur',
          'name' : 'auteur',
        },
        2 : 
        {
          'code' : '[cave]',
          'widget' : 'detail_titre',
          'name' : 'titre',
        },
        3 : 
        {
          'code' : 'Alcool :  \
     [volalcoolp] \
     [volhl] \
     [volalcool20] \
     [volalcoolpur20]',
          'widget' : 'detail_themes',
          'name' : 'themes',
        },
        4 : 
        {
          'code' : '[dateinventaire]',
          'widget' : 'detail_comp',
          'name' : 'comp',
        },
      },
      'table' : 'inventaire',
      'id_field' : 'id_inventaire',
      'details tab' : '1',
    },
    'moutures' : 
    {
      'zones' : 
      {
        0 : 
        {
          'code' : '<span foreground="blue"><span size="16384" foreground="blue">[CodeMouture]</span> \
[CodeFabrication]</span>',
          'widget' : 'detail_test2',
          'name' : 'cote',
        },
        1 : 
        {
          'code' : '<span face="Times New Roman"><span size="16384" face="Times New Roman"><span foreground="red" size="16384" face="Times New Roman">Designation :</span> [Designation]</span></span>',
          'widget' : 'detail_auteur2',
          'name' : 'auteur',
        },
        2 : 
        {
          'code' : '[DateCreation]  /  [DateLastModif]',
          'widget' : 'detail_titre2',
          'name' : 'titre',
        },
        3 : 
        {
          'code' : '<span background="goldenrod1">Plantes : </span>[g_plantes]',
          'widget' : 'detail_themes2',
          'name' : 'themes',
        },
        4 : 
        {
          'code' : '<span background="dodger blue">Sacs mouture :</span>  [g_sacmouture]',
          'widget' : 'detail_comp2',
          'name' : 'comp',
        },
        5 : 
        {
          'code' : '[x,function =demo_affichage] \
',
          'widget' : 'detail_test2',
          'name' : 'test',
        },
      },
      'table' : 'mouturegene',
      'id_field' : 'id_mouture',
      'details tab' : '2',
    },
  },
  'popup' : None,
  'words' : None,
  'version' : 1100,
  'position' : 
  {
    'window0' : 
    {
      'x' : 0,
      'y' : 0,
      'h' : 602,
      'w' : 51,
    },
    's_window0' : 
    {
      'x' : -4,
      'y' : -4,
      'h' : 671,
      'w' : 1024,
    },
    'window1' : 
    {
      'x' : -4,
      'y' : -4,
      'h' : 671,
      'w' : 1024,
    },
    's_columns' : 
    {
      'x' : 154,
      'y' : 15,
      'h' : 582,
      'w' : 612,
    },
    'window4' : 
    {
      'x' : -4,
      'y' : -4,
      'h' : 671,
      'w' : 1024,
    },
    'window2' : 
    {
      'x' : -4,
      'y' : -4,
      'h' : 671,
      'w' : 1024,
    },
  },
  'print' : 
  {
    'inventaire rtf' : 
    {
      'code' : '\\trowd\\trgaph70\\cellx1500\\cellx3000\\cellx4500\\cellx6000\\cellx7500\\cellx9000 \
\\pard\\intbl \
[numfoudre]\\cell \
[contenance]\\cell \
[produit]\\cell \
[codeliqueur]\\cell \
[cave]\\cell \
[dateinventaire] \\cell \
\\pard\\intbl\\row\\pard \
',
      'before' : '{\\rtf1 ',
      'after' : '}',
      'extension' : 'rtf',
    },
    'inventaire html' : 
    {
      'code' : '<tr> \
    <td>[numfoudre]</td> \
    <td>[contenance]</td> \
    <td>[produit]</td> \
    <td>[codeliqueur]</td> \
    <td>[cave]</td> \
    <td>[dateinventaire]</td> \
  </tr>',
      'before' : '<html> \
<head> \
<title>Document sans-titre</title> \
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1"> \
</head> \
 \
<body bgcolor="#FFFFFF"> \
<table width="75%" border="1">',
      'after' : '</table> \
</body> \
</html>',
      'extension' : 'html',
    },
    'inventaire xls' : 
    {
      'code' : '\\trowd\\trgaph70\\cellx1500\\cellx3000\\cellx4500\\cellx6000\\cellx7500\\cellx9000 \
\\pard\\intbl \
[numfoudre]\\cell \
[contenance]\\cell \
[produit]\\cell \
[codeliqueur]\\cell \
[cave]\\cell \
[dateinventaire] \\cell \
\\pard\\intbl\\row\\pard \
',
      'before' : '{\\rtf1 ',
      'after' : '}',
      'extension' : 'xls',
    },
    'liste html' : 
    {
      'code' : '<tr> \
    <td>[0]</td> \
    <td>[1]</td> \
    <td>[2]</td> \
    <td>[3]</td> \
    <td>[4]</td> \
    <td>[5]</td> \
  </tr>',
      'before' : '<html> \
<head> \
<title>Document sans-titre</title> \
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1"> \
</head> \
 \
<body bgcolor="#FFFFFF"> \
<table width="75%" border="1">',
      'after' : '</table> \
</body> \
</html>',
      'extension' : 'html',
      'type' : 'liste',
    },
  },
  'combobox' : 
  {
    'charger_recette' : 
    {
      'query' : 'select distinct coderecette from recette',
      'combobox' : 'combo_recette',
      'load_on_start' : '1',
    },
    'inventaire produit' : 
    {
      'query' : 'select distinct produit, count(produit)  \
from inventaire  \
group by produit',
      'combobox' : 'combo-inv_produit',
      'entry' : '',
      'load_on_start' : '',
    },
    'inventaire liqueur' : 
    {
      'query' : 'select distinct codeliqueur \
from inventaire',
      'combobox' : 'combo-inv_liqueur',
      'entry' : '',
      'load_on_start' : '1',
    },
    'inventaire-foudre' : 
    {
      'query' : 'select distinct numfoudre  \
from inventaire',
      'combobox' : 'combo-inv_foudre',
      'entry' : '',
      'load_on_start' : '1',
    },
    'inventaire-cave' : 
    {
      'query' : 'select distinct cave  \
from inventaire',
      'combobox' : 'combo-inv_cave',
      'entry' : '',
      'load_on_start' : '1',
    },
    'inventaire-date' : 
    {
      'query' : 'select distinct dateinventaire  \
from inventaire',
      'combobox' : 'combo-inv_date',
      'entry' : '',
      'load_on_start' : '1',
    },
  },
  'central' : 
  {
    'def_inventaires' : 
    {
      'from' : '',
      'table' : 'inventaire',
      'id_main' : 'id_inventaire',
      'edit' : 'saisie_inventaire',
      'edit tab' : '3',
    },
    'def_moutures' : 
    {
      'from' : '',
      'table' : 'mouturegene',
      'id_main' : 'id_mouture',
      'edit' : 'saisie_mouture',
      'edit tab' : '2',
    },
    'def_liqueurs' : 
    {
      'from' : '',
      'table' : 'liqueurs',
      'id_main' : 'id_liqueur',
      'edit' : 'saisie_liqueur',
      'edit tab' : '1',
    },
  },
  'import' : 
  {
    'produits' : 
    {
      'central_def' : 'def_inventaires',
      'periph_def' : 'produits',
    },
  },
}