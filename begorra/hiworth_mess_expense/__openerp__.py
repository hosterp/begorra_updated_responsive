{
    'name': 'Hiworth Mess and Expense',
    'description': 'Mess and Expense',
    'author': 'hiworth',
    'depends': [
                'base','hiworth_hr_attendance'
                ],
    'data': [
        'security/ir.model.access.csv',
        'data/mess_expense_sequence.xml',
        
        'report/mess_and_expense_report_views.xml',
        'wizard/mess_expense_report_wizard_views.xml',
        
        'views/hr_employee_views.xml',
        'views/mess_attendance_views.xml',
        'views/mess_expense_views.xml'
    ]
}