# -*- coding: utf-8 -*-
{
    'name': 'Hiworth Expense Book',
    'version': '1.0.0',
    'author': 'Hiworth Solutions Pvt Ltd',
    'category': 'Accounting',
    'website': 'http://www.hiworthsolutions.com',
    'depends': ['hiworth_accounting'],
    'data': [
         # 'security/accounting_security.xml',
         'report/expense_report.xml',
          'views/expense_book_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
