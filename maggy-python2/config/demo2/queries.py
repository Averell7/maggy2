{'Portes': {'central_def': 'completex',
            'details': 'normal',
            'name': 'Portes',
            'query': 'select * from complete',
            'widths': '50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50'},
 'essai 1': {'central_def': 'completex',
             'details': 'normal',
             'name': 'essai 1',
             'parameters': '?,Numero de depart',
             'query': 'select id_livre, * from complete [where id_livre > {1}]',
             'widths': '100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100'},
 'essai2': {'central_def': 'completex',
            'comment': '',
            'config': 1,
            'details': '',
            'name': 'essai2',
            'parameters': '',
            'query': 'select id_langue, * from langues',
            'result': '',
            'widths': '100,100,100,100,100'},
 'recherche par cotes': {'central_def': 'completex',
                         'details': 'normal',
                         'name': 'recherche par cotes',
                         'parameters': 'combo_section',
                         'query': 'select * from complete where section like "%[{1}]%"',
                         'widths': '40,150,50,50,50,50,50,50'},
 'requete1': {'central_def': 'completex',
              'comment': '',
              'config': 1,
              'details': '',
              'name': 'requete1',
              'parameters': '?,Numero de depart;',
              'query': 'select id_livre, g_personnes, titre, editeur, date  from complete  [where id_livre > {1} ] ',
              'result': '',
              'widths': '40,250,400,100,50'},
 'test2': {'central_def': 'completex',
           'details': 'normal',
           'name': 'test2',
           'query': "select nom from personnes where nom like 'benoit%' order by nom",
           'widths': '250'}}