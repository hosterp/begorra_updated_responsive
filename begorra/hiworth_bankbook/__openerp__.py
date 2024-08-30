# -*- coding: utf-8 -*-
{
    'name': 'Hiworth Bank Book',
    'version': '1.0.0',
    'author': 'Hiworth Solutions Pvt Ltd',
    'category': 'Accounting',
    'website': 'http://www.hiworthsolutions.com',
    'depends': ['hiworth_accounting'],
    'data': [
        # 'security/accounting_security.xml',
        # 'security/ir.model.access.csv',
        'views/bank_book_view.xml',
        'report/bankbook_report.xml'
    ],
    'installable': True,
    'auto_install': False,
}
