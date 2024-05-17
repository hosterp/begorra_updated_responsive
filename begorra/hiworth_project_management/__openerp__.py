# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Hiworth Project Management',
    'version': '1.1',
    'website': 'https://www.odoo.com/page/project-management',
    'category': 'Project',
    'sequence': 10,
    'summary': 'Projects, Tasks',
    'depends': ['event','hiworth_construction'
    ],
    'description': """
..
    """,
    'data': [
    'security/project_security.xml',
    'views/project.xml',
    'security/res.country.state.csv',
    # 'views/external_signup.xml',
    'security/ir.model.access.csv',
       # 'views/web_login.xml',
       # 'views/auth_signup.xml',
       'security/ir.rule.csv',
       'views/sequence.xml',
       
       'views/index.xml',
       'views/messaging_prime.xml',
       # 'views/project_task.xml',
       'views/task_calendar.xml',
       'views/access_project.xml',
       # 'views/popup_notification.xml',
       'views/job_summary.xml',
       'views/customer_file_details.xml',
       'views/work_report.xml',
       'views/account_invoice.xml',
       # 'views/birthday_cron.xml',
       # 'edi/birthday_reminder_action_data.xml',
       # 'views/gallery.xml',
       # 'views/greetings.xml',
       
       # 'views/work_order_contractor.xml'
       # 'views/popup_notification.xml'
       # 'views/im_chat.xml'
       # 'views/website_templates.xml'
    ],
    
    # 'qweb': [
    #     'static/xml/popup_notification.xml',

    #     'static/src/xml/*.xml',
    #         ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
