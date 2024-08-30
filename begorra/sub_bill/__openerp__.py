{
    'name': 'Sub Contractor Works',
    'version': '1.0',
    'depends': ['base', 'hiworth_construction', 'hiworth_project_management'],
    'data': [
            'security/ir.model.access.csv',
        'reports/advance_payment.xml',
            'views/sub_bill_order.xml',
            'views/work_order.xml',
        'views/partner_daily_statement_views.xml',


    ],
    'installable': True,
    'auto_install': False
}