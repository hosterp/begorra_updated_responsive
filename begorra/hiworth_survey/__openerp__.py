# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Survey Department",
    'depends': ['base', 'hiworth_construction', 'stock'],
    'installable': True,
    'auto_install': False,
    'category': "Tools",
    'version': "0.1",
	'demo': [],
    'description': """ """,
    'data': [
        "views/staff_details.xml",
        "views/planning_chart.xml",
        "views/dpr_status.xml",
        "views/instrument_status.xml",
        "views/meeting_minutes.xml",
        "views/pending_work_status.xml",
        "views/quantity_status.xml",
        "views/training_evaluation.xml",
        "views/work_status.xml",
        "security/ir.model.access.csv"
    ]
}