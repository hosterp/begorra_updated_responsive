
{
    'name': 'Expense Module',
    'version': '1.0',
    'category': 'Expense',
    'sequence': 21,
    'description': """ Expense  """,
    'depends': ['hiworth_construction'],
    'data': [
         'security/ir.model.access.csv',
         'data/mou_sequence.xml',
         'views/expense_views.xml',
         'views/mou_views.xml',
         'views/fleet_vehicle_views.xml'


    ],

    'qweb': [
                
            ],

    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
