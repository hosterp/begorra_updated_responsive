
{
    'name': 'Hiworth Dashboard',
    'version': '1.0',
    'category': 'Project',
    'sequence': 21,
    'description': """ Project Cost Estimation """,
    'depends': ['hiworth_construction','hr'],
    'data': [
                'security/dashboard_security.xml',
                'security/ir.model.access.csv',

                'wizard/date_maintenace_views.xml',
                'views/hr_dashboard_views.xml',
                'views/stock_dashboard_views.xml',
                'views/fleet_dashboard_views.xml'

    ],

    'qweb': [
                'static/src/xml/stock_dashboard_views.xml',
            ],

    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
