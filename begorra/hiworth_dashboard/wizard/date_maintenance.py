from openerp import fields, models, api
from datetime import datetime,timedelta
from openerp.osv import osv
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from dateutil.relativedelta import relativedelta
from dateutil import tz


class MaintenanceReport(models.TransientModel):
    _name = 'maintanance.report'

    @api.onchange('own_vehicle')
    def onchange_own_vehicle(self):
        for rec in self:
            rec.rent_vehicle = False
            rec.rent_machinery_owner = False
            rec.rent_vehicle_id = False

    @api.onchange('rent_vehicle')
    def onchange_rent_vehicle(self):
        for rec in self:
            rec.own_vehicle = False
            rec.vehicle_id = False

    @api.onchange('rent_machinery_owner')
    def onchange_rent_vehicle_owner_id(self):
        for rec in self:
            vehicle = self.env['fleet.vehicle'].search([('vehicle_under', '=', rec.rent_machinery_owner.id)])
        return {'domain': {'rent_vehicle_id': [('id', 'in', vehicle.ids)]}}

    from_date = fields.Date('Date')
    to_date = fields.Date('To Date')
    own_vehicle = fields.Boolean("Own Vehicle")
    rent_vehicle = fields.Boolean("Rent Vehicle")
    vehicle_id = fields.Many2one('fleet.vehicle',"Vehicle/Machinery",domain="['|','|',('machinery','=',True),('other','=',True),('vehicle_ok','=',True)]")
    rent_machinery_owner = fields.Many2one('res.partner',"Rent Machinery/Vehicle Owner",domain="[('is_rent_mach_owner','=',True)]")
    rent_vehicle_id = fields.Many2one('fleet.vehicle',"Rent Vehicle/Machinery",domain="['|','|',('rent_vehicle','=',True),('rent_other','=',True),('is_rent_mach','=',True)]")

    tyre_id = fields.Many2one('vehicle.tyre',"Tyre")



    @api.multi
    def generate_xls_report(self):

        # return self.env["report"].get_action(self, report_name='equipment_utilisation_report.xlsx')
        if self._context.get('monthly_report',False):
            return self.env["report"].get_action(self, report_name='equipment_monthly_report.xlsx')
        if self._context.get('daily_utilisation',False):
            return self.env["report"].get_action(self, report_name='equipment_utilisation_report.xlsx')
        if self._context.get('breakdown_report',False):
            return self.env["report"].get_action(self, report_name='equipment_breakdown_report.xlsx')
        if self._context.get('preventive_maintenance',False):
            return self.env["report"].get_action(self, report_name='equipment_preventive_report.xlsx')
        if self._context.get('daily_maintenance',False):
            return self.env["report"].get_action(self, report_name='equipment_daily_report.xlsx')
        if self._context.get('tyre_repairs',False):
            return self.env["report"].get_action(self, report_name='equipment_tyre_repairs_report.xlsx')
        if self._context.get('fuel_details',False):
            return self.env["report"].get_action(self, report_name='equipment_fuel_details_report.xlsx')


class BillReportXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, invoices):
        worksheet = workbook.add_worksheet("Equiment Utilisation")
        # raise UserError(str(invoices.invoice_no.id))

        boldc = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'font': 'height 10'})
        heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
        bold = workbook.add_format({'bold': True})
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        right = workbook.add_format({'align': 'right'})
        regular = workbook.add_format({'align': 'center', 'bold': False, 'size': 8})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_color': '#000000',
        })
        format_hidden = workbook.add_format({
            'hidden': True
        })
        align_format = workbook.add_format({
            'align': 'right',
        })
        row = 6
        col = 1
        new_row = row

        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('D:S', 13)

        worksheet.merge_range('A1:Q1', 'BEGORRA INFRASTRUCTURE & DEVELOPERS PVT LTD', boldc)
        worksheet.merge_range('A2:Q2',
                              'DATE : From %s To %s' % (
                                  datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                                  (datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%d-%m-%Y"))),
                              boldc)
        worksheet.merge_range('A3:Q3', 'Equipment utilisation in terms of working hrs/kms', boldc)
        worksheet.write('A5', 'Sl.NO', regular)
        worksheet.write('B5', 'Date', regular)
        worksheet.write('C5', 'Type of Equipment', regular)
        worksheet.write('D5', 'Fleet No', regular)
        worksheet.write('E5', 'Plant & Equipment', regular)
        worksheet.write('F5', 'Location', regular)
        worksheet.write('G5', 'Starting KM', regular)
        worksheet.write('H5', 'Ending KM', regular)
        worksheet.write('I5', 'Running KM', regular)
        worksheet.write('J5', 'Fuel', regular)
        worksheet.write('K5', 'Mileage', regular)
        worksheet.write('L5', 'EXPENSE ON FUEL', regular)
        worksheet.write('M5', 'EXPENSE ON SPARE', regular)
        worksheet.write('N5', 'EXPENSE ON LUB', regular)
        worksheet.write('O5', 'EXPENSE ON TYRES', regular)
        worksheet.write('P5', 'EXPENSE ON BATTERY', regular)

        # worksheet.merge_range('A4:O5','',regular)
        worksheet.write('Q5', 'Remarks', regular)

        count = 1
        for rec in invoices:
            date_from = datetime.strptime(invoices.from_date, "%Y-%m-%d")
            to_date = datetime.strptime(invoices.to_date, "%Y-%m-%d")

            count = 1
            count = 1
            if not rec.vehicle_id:
                vehicle_categ = self.env['vehicle.category.type'].search([], order='priority asc')
            else:
                vehicle_categ = rec.vehicle_id.vehicle_categ_id
            for categ in vehicle_categ:
                if not rec.vehicle_id:
                    vehicle_list = self.env['fleet.vehicle'].search([('vehicle_categ_id', '=', categ.id)])

                    for daily in vehicle_list:
                        domain = []
                        domain2 = []
                        if rec.from_date:
                            domain.append(('date', '>=', date_from))
                            domain2.append(('date', '>=', date_from))
                        if rec.to_date:
                            domain.append(('date', '<=', to_date))
                            domain2.append(('date', '<=', to_date))
                        domain2.append(('vehicle_id', '=', daily.id))
                        domain.append(('vehicle_no', '=', daily.id))
                        start_km = self.env['driver.daily.statement'].search(
                            [('date', '>=', date_from), ('date', '<=', to_date), ('vehicle_no', '=', daily.id),
                             ('start_km', '!=', 0)], order='date asc', limit=1)
                        close_km = self.env['driver.daily.statement'].search(
                            [('date', '>=', date_from), ('date', '<=', to_date), ('vehicle_no', '=', daily.id),
                             ('actual_close_km', '!=', 0)], order='date desc', limit=1)
                        daily_statement = self.env['driver.daily.statement'].search(domain, order='date asc', limit=1)
                        daily_statement_des = self.env['driver.daily.statement'].search(domain, order='date desc',
                                                                                        limit=1)

                        expense_spares = 0
                        expense_lub = 0
                        expense_tyre = 0
                        expense_battery = 0
                        expense_fuel = 0
                        if daily_statement_des:
                            worksheet.write('A%s' % (new_row), count, regular)
                            worksheet.write('B%s' % (new_row), daily_statement_des.date, regular)
                            worksheet.write('C%s' % (new_row), daily.vehicle_categ_id.name, regular)
                            worksheet.write('D%s' % (new_row), daily.fleet_no, regular)
                            worksheet.write('E%s' % (new_row), daily.name, regular)
                            worksheet.write('F%s' % (new_row), daily_statement_des.project_id.location_id.name, regular)

                            worksheet.write('G%s' % (new_row), start_km.start_km, regular)
                            worksheet.write('H%s' % (new_row), close_km.actual_close_km, regular)
                            worksheet.write('I%s' % (new_row),
                                            close_km.actual_close_km - start_km.start_km,
                                            regular)
                            fuel = 0
                            mileage = 0

                            date_from = datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%Y-%m-%d 00:00:00")
                            from_zone = tz.gettz('UTC')
                            to_zone = tz.gettz('Asia/Kolkata')
                            # from_zone = tz.tzutc()
                            # to_zone = tz.tzlocal()
                            utc = datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')
                            utc = utc.replace(tzinfo=to_zone)
                            central = utc.astimezone(from_zone)

                            # date_today = utcc.replace(tzinfo=from_zone)
                            date_from = datetime.strptime(central.strftime("%Y-%m-%d %H:%M:%S"),
                                                          '%Y-%m-%d %H:%M:%S').strftime(
                                "%Y-%m-%d %H:%M:%S")
                            date_to = datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%Y-%m-%d 23:59:59")
                            from_zone = tz.gettz('UTC')
                            to_zone = tz.gettz('Asia/Kolkata')
                            # from_zone = tz.tzutc()
                            # to_zone = tz.tzlocal()
                            utc = datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')
                            utc = utc.replace(tzinfo=to_zone)
                            central = utc.astimezone(from_zone)

                            # date_today = utcc.replace(tzinfo=from_zone)
                            date_to = datetime.strptime(central.strftime("%Y-%m-%d %H:%M:%S"),
                                                        '%Y-%m-%d %H:%M:%S').strftime(
                                "%Y-%m-%d %H:%M:%S")

                            diesel_entry_desc = self.env['diesel.pump.line'].search(domain2, order='date desc', limit=1)
                            diesel_entry_asc = self.env['diesel.pump.line'].search(domain2, order='date asc', limit=1)

                            material_issue = self.env['material.issue.slip'].search(
                                [('date', '<=', date_to), ('date', '>=', date_from), ('vehicle_id', '=', daily.id)])
                            for material in material_issue:
                                for expense_line in material.material_issue_slip_lines_ids:
                                    if expense_line.item_id.categ_id.vehicle_type == 'fuel':
                                        fuel += expense_line.req_qty
                                        expense_fuel += expense_line.amount

                            worksheet.write('J%s' % (new_row), fuel, regular)
                            if fuel == 0:
                                mileage = 0
                            else:
                                if daily.machinery:
                                    if (close_km.actual_close_km - start_km.start_km) == 0:
                                        mileage = 0
                                    else:
                                        mileage = fuel / (close_km.actual_close_km - start_km.start_km)
                                else:
                                    mileage = (close_km.actual_close_km - start_km.start_km) / fuel

                            worksheet.write('K%s' % (new_row), round(mileage, 2), regular)
                            expense_spare = self.env['material.issue.slip'].search(
                                [('date', '>=', date_from), ('date', '<=', date_to), ('vehicle_id', '=', daily.id)])
                            for expense in expense_spare:
                                for expense_line in expense.material_issue_slip_lines_ids:
                                    if expense_line.item_id.categ_id.vehicle_type == 'spare':
                                        expense_spares += expense_line.amount
                                    if expense_line.item_id.categ_id.vehicle_type == 'lub':
                                        expense_lub += expense_line.amount
                                    if expense_line.item_id.categ_id.vehicle_type == 'tyre':
                                        expense_tyre += expense_line.amount
                                    if expense_line.item_id.categ_id.vehicle_type == 'battery':
                                        expense_battery += expense_line.amount
                            remark = ''
                            worksheet.write('L%s' % (new_row), expense_fuel, regular)
                            worksheet.write('M%s' % (new_row), expense_spares, regular)
                            worksheet.write('N%s' % (new_row), expense_lub, regular)
                            worksheet.write('O%s' % (new_row), expense_tyre, regular)
                            worksheet.write('P%s' % (new_row), expense_battery, regular)
                            worksheet.write('Q%s' % (new_row), remark, regular)

                            count += 1
                            new_row += 1
                else:
                    vehicle_list = rec.vehicle_id
                    for daily in vehicle_list:
                        date_from = datetime.strptime(rec.from_date, '%Y-%m-%d')
                        to_date = datetime.strptime(rec.to_date, '%Y-%m-%d')
                        date_diff = to_date - date_from
                        close_km_prev = 0
                        for rangeg in range(date_diff.days + 1):
                            domain = []
                            domain2 = []
                            expense_spares = 0
                            expense_lub = 0
                            expense_tyre = 0
                            expense_battery = 0
                            expense_fuel = 0
                            fuel = 0
                            mileage = 0
                            if date_from:
                                domain.append(('date', '=', date_from))
                                domain2.append(('date', '=', date_from))

                            domain2.append(('vehicle_id', '=', daily.id))
                            domain.append(('vehicle_no', '=', daily.id))
                            daily_statement_des = self.env['driver.daily.statement'].search(domain, order='date asc')

                            worksheet.write('A%s' % (new_row), count, regular)
                            worksheet.write('B%s' % (new_row), date_from.strftime("%d-%m-%Y"), regular)
                            worksheet.write('C%s' % (new_row), daily.vehicle_categ_id.name, regular)
                            worksheet.write('D%s' % (new_row), daily.fleet_no, regular)
                            worksheet.write('E%s' % (new_row), daily.name, regular)

                            running_km = 0
                            for statement in daily_statement_des:
                                worksheet.write('F%s' % (new_row), statement.project_id.location_id.name, regular)

                                worksheet.write('G%s' % (new_row), statement.start_km, regular)
                                worksheet.write('H%s' % (new_row), statement.actual_close_km, regular)
                                worksheet.write('I%s' % (new_row),
                                                round((statement.actual_close_km - statement.start_km),2),
                                                regular)
                                running_km += statement.actual_close_km - statement.start_km
                                close_km_prev = statement.actual_close_km
                            if not daily_statement_des:
                                worksheet.write('G%s' % (new_row), close_km_prev, regular)
                                worksheet.write('H%s' % (new_row), close_km_prev, regular)
                                worksheet.write('I%s' % (new_row),
                                                close_km_prev - close_km_prev,
                                                regular)

                            fuel_date_from = date_from.strftime("%Y-%m-%d 00:00:00")

                            fuel_date_to = date_from.strftime("%Y-%m-%d 23:59:59")
                            material_issue = self.env['material.issue.slip'].search(
                                [('date', '<=', fuel_date_to), ('date', '>=', fuel_date_from),
                                 ('vehicle_id', '=', daily.id)])

                            for material in material_issue:
                                for expense_line in material.material_issue_slip_lines_ids:
                                    if expense_line.item_id.categ_id.vehicle_type == 'fuel':
                                        fuel += expense_line.req_qty
                                        expense_fuel += expense_line.amount
                                    if expense_line.item_id.categ_id.vehicle_type == 'spare':
                                        expense_spares += expense_line.amount
                                    if expense_line.item_id.categ_id.vehicle_type == 'lub':
                                        expense_lub += expense_line.amount
                                    if expense_line.item_id.categ_id.vehicle_type == 'tyre':
                                        expense_tyre += expense_line.amount
                                    if expense_line.item_id.categ_id.vehicle_type == 'battery':
                                        expense_battery += expense_line.amount
                            remark = ''
                            if daily.machinery:
                                if running_km == 0:
                                    mileage = 0
                                else:
                                    mileage = fuel / running_km
                            else:
                                mileage = running_km / fuel
                            worksheet.write('J%s' % (new_row), fuel, regular)
                            worksheet.write('K%s' % (new_row), round(mileage,2), regular)
                            worksheet.write('L%s' % (new_row), expense_fuel, regular)
                            worksheet.write('M%s' % (new_row), expense_spares, regular)
                            worksheet.write('N%s' % (new_row), expense_lub, regular)
                            worksheet.write('O%s' % (new_row), expense_tyre, regular)
                            worksheet.write('P%s' % (new_row), expense_battery, regular)
                            worksheet.write('Q%s' % (new_row), remark, regular)
                            count += 1
                            new_row += 1
                            from_date = date_from + timedelta(days=1)
                            date_from = from_date

        worksheet = workbook.add_worksheet("Equiment Breakdown Report")
        # raise UserError(str(invoices.invoice_no.id))

        boldc = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'font': 'height 10'})
        heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
        bold = workbook.add_format({'bold': True})
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        right = workbook.add_format({'align': 'right'})
        regular = workbook.add_format({'align': 'center', 'bold': False, 'size': 8})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_color': '#000000',
        })
        format_hidden = workbook.add_format({
            'hidden': True
        })
        align_format = workbook.add_format({
            'align': 'right',
        })
        row = 6
        col = 1
        new_row = row

        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('D:S', 13)

        worksheet.merge_range('A1:J1', 'BEGORRA INFRASTRUCTURE & DEVELOPERS PVT LTD', boldc)
        worksheet.merge_range('A2:J2',
                              'DATE : From %s To %s' % (
                              datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                              (datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%d-%m-%Y"))),
                              boldc)
        worksheet.merge_range('A3:J3', 'Equipment Breakdown Report', boldc)
        worksheet.merge_range('A4:A5', 'Sl.NO', regular)
        worksheet.merge_range('B4:B5', 'Date of Breakdown', regular)
        worksheet.merge_range('C4:C5', 'Machinery Details', regular)
        worksheet.merge_range('D4:D5', 'Model & Serial No', regular)
        worksheet.merge_range('E4:E5', 'Location', regular)
        worksheet.write('F5', 'Breakdown Details', regular)
        worksheet.write('G5', 'Action Taken', regular)
        worksheet.write('H5', 'Date of Rectification', regular)
        worksheet.write('I5', 'Target Date of Completion', regular)
        worksheet.write('J5', 'Remarks', regular)

        count = 1
        for rec in invoices:
            date_from = datetime.strptime(invoices.from_date, "%Y-%m-%d")
            to_from = datetime.strptime(invoices.to_date, "%Y-%m-%d")
    
            count = 1


            if not rec.vehicle_id:
                vehicle_categ = self.env['vehicle.category.type'].search([], order='priority asc')
            else:
                vehicle_categ = rec.vehicle_id.vehicle_categ_id
            for categ in vehicle_categ:
                if not rec.vehicle_id:
                    vehicle_list = self.env['fleet.vehicle'].search([('vehicle_categ_id', '=', categ.id)])
                else:
                    vehicle_list = rec.vehicle_id

                for daily in vehicle_list:
                    domain = []
                    if rec.from_date:
                        domain.append(('date_com', '>=', date_from))
                        domain.append(('r_b_bool', '=', True))
                    if rec.to_date:
                        domain.append(('date_com', '<=', to_from))
                    domain.append(('vehicle_id','=',daily.id))
                    daily_statement = self.env['fleet.vehicle.log.services'].search(domain)

                    for daily in daily_statement:
                        worksheet.write('A%s' % (new_row), count, regular)
                        worksheet.write('B%s' % (new_row), daily.date_com, regular)
                        worksheet.write('C%s' % (new_row), daily.vehicle_id.vehicle_categ_id.name, regular)
                        worksheet.write('D%s' % (new_row), daily.vehicle_id.name, regular)
                        worksheet.write('E%s' % (new_row), daily.project_id.location_id.name, regular)

                        worksheet.write('F%s' % (new_row), daily.nature_breakdown, regular)
                        worksheet.write('G%s' % (new_row), daily.works_done, regular)
                        worksheet.write('H%s' % (new_row), daily.date_of_rectification, regular)
                        worksheet.write('I%s' % (new_row), daily.target_date_completion, regular)
                        worksheet.write('J%s' % (new_row), daily.notes, regular)

                        count += 1
                        new_row += 1

        worksheet = workbook.add_worksheet("Equiment Preventive ")
        # raise UserError(str(invoices.invoice_no.id))

        boldc = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'font': 'height 10'})
        heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
        bold = workbook.add_format({'bold': True})
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        right = workbook.add_format({'align': 'right'})
        regular = workbook.add_format({'align': 'center', 'bold': False, 'size': 8})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_color': '#000000',
        })
        format_hidden = workbook.add_format({
            'hidden': True
        })
        align_format = workbook.add_format({
            'align': 'right',
        })
        row = 6
        col = 1
        new_row = row

        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('D:S', 13)

        worksheet.merge_range('A1:J1', 'BEGORRA INFRASTRUCTURE & DEVELOPERS PVT LTD', boldc)
        worksheet.merge_range('A2:J2',
                              'DATE : From %s To %s' % (
                              datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                              (datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%d-%m-%Y"))),
                              boldc)
        worksheet.merge_range('A3:J3', 'Equiment Preventive Maintenance', boldc)
        worksheet.write('A5', 'Sl.NO', regular)

        worksheet.write('B5', 'Type of Equipment/Vehicle', regular)
        worksheet.write('C5', 'Fleet No', regular)

        worksheet.write('D5', 'Reg No:', regular)
        worksheet.write('E5', 'Date', regular)
        worksheet.write('F5', 'Last Service KM/HRS', regular)
        worksheet.write('G5', 'Service Period', regular)
        worksheet.write('H5', 'Current Reading', regular)

        worksheet.write('I5', 'Next Service SMR', regular)
        worksheet.write('J5', 'Remarks', regular)

        count = 1
        for rec in invoices:
            date_from = datetime.strptime(invoices.from_date, "%Y-%m-%d")
            to_from = datetime.strptime(invoices.to_date, "%Y-%m-%d")
    
            count = 1
    

            if not rec.vehicle_id:
                vehicle_categ = self.env['vehicle.category.type'].search([], order='priority asc')
            else:
                vehicle_categ = rec.vehicle_id.vehicle_categ_id
            for categ in vehicle_categ:
                if not rec.vehicle_id:
                    vehicle_list = self.env['fleet.vehicle'].search([('vehicle_categ_id', '=', categ.id)])
                else:
                    vehicle_list = rec.vehicle_id


                for veh in vehicle_list:
                    domain = []

                    if rec.to_date:
                        domain.append(('date', '<=', rec.to_date))
                    domain.append(('vehicle_id', '=', veh.id))
                    daily_statement = self.env['vehicle.preventive.maintenance.line'].search(domain, order='date desc', limit=1)
                    for daily in daily_statement:
                        worksheet.write('A%s' % (new_row), count, regular)
                        worksheet.write('B%s' % (new_row), veh.vehicle_categ_id.name, regular)
                        worksheet.write('C%s' % (new_row), veh.brand_id.name, regular)
                        worksheet.write('D%s' % (new_row), veh.name, regular)

                        worksheet.write('E%s' % (new_row), daily.date, regular)
                        worksheet.write('F%s' % (new_row), daily.last_service_km, regular)
                        worksheet.write('G%s' % (new_row), daily.service_period, regular)
                        daily_statement = self.env['driver.daily.statement'].search(
                            [('date', '<=', rec.to_date), ('vehicle_no', '=', veh.id)], limit=1,
                            order='date desc')
                        worksheet.write('H%s' % (new_row), daily_statement.actual_close_km, regular)

                        worksheet.write('I%s' % (new_row), daily.next_service_km, regular)
                        worksheet.write('J%s' % (new_row), daily.remarks, regular)
                        count += 1
                        new_row += 1
        


        worksheet = workbook.add_worksheet("Equipment Daily Maintanance")
        # raise UserError(str(invoices.invoice_no.id))

        boldc = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'font': 'height 10'})
        heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
        bold = workbook.add_format({'bold': True})
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        right = workbook.add_format({'align': 'right'})
        regular = workbook.add_format({'align': 'center', 'bold': False, 'size': 8})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_color': '#000000',
        })
        format_hidden = workbook.add_format({
            'hidden': True
        })
        align_format = workbook.add_format({
            'align': 'right',
        })
        row = 6
        col = 1
        new_row = row

        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('D:S', 13)

        worksheet.merge_range('A1:H1', 'BEGORRA INFRASTRUCTURE & DEVELOPERS PVT LTD', boldc)
        worksheet.merge_range('A2:H2',
                              'DATE : From %s To %s' % (
                              datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                              (datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%d-%m-%Y"))),
                              boldc)
        worksheet.merge_range('A3:H3', 'Equipment Daily Maintenance attended ', boldc)
        worksheet.merge_range('A4:A5', 'Sl.NO', regular)
        worksheet.merge_range('B4:B5', 'Date', regular)
        worksheet.merge_range('C4:C5', 'Machine Name', regular)

        worksheet.write('D5', 'Machine No', regular)
        worksheet.write('E5', 'Mechanic', regular)
        worksheet.write('F5', 'Work Description', regular)
        worksheet.write('G5', 'Material Used', regular)
        worksheet.write('H5', 'Remarks', regular)

        count = 1
        for rec in invoices:
            date_from = datetime.strptime(invoices.from_date, "%Y-%m-%d")
            date_to = datetime.strptime(invoices.to_date, "%Y-%m-%d")

            count = 1
            if not rec.vehicle_id:
                vehicle_categ = self.env['vehicle.category.type'].search([], order='priority asc')
            else:
                vehicle_categ = rec.vehicle_id.vehicle_categ_id
            for categ in vehicle_categ:
                if not rec.vehicle_id:
                    vehicle_list = self.env['fleet.vehicle'].search([('vehicle_categ_id', '=', categ.id)])
                else:
                    vehicle_list = rec.vehicle_id

                for veh in vehicle_list:
                    domain = []
                    domain.append(('daily_maint_bool', '=', True))

                    domain.append(('vehicle_id', '=', veh.id))
                    if rec.from_date:
                        domain.append(('date_com', '>=', date_from))
                    if rec.to_date:
                        domain.append(('date_com', '<=', date_to))
                    daily_statement = self.env['fleet.vehicle.log.services'].search(domain, order='date_com asc')

                    for daily in daily_statement:
                        worksheet.write('A%s' % (new_row), count, regular)
                        worksheet.write('B%s' % (new_row), daily.date_com, regular)
                        worksheet.write('C%s' % (new_row), daily.vehicle_id.vehicle_categ_id.name, regular)
                        worksheet.write('D%s' % (new_row), daily.vehicle_id.name, regular)
                        mec_name = ''
                        for mec in daily.mechanic_id:
                            mec_name += mec.name + ','
                        worksheet.write('E%s' % (new_row), mec_name, regular)
                        material_used = ''
                        for mate in daily.cost_ids:
                            material_used += mate.particular_id and mate.particular_id.name or ' ' + ','
                        worksheet.write('F%s' % (new_row),daily.notes , regular)
                        worksheet.write('G%s' % (new_row),material_used , regular)

                        count += 1
                        new_row += 1

        worksheet = workbook.add_worksheet("Equipment Tyres ")
        # raise UserError(str(invoices.invoice_no.id))

        boldc = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'font': 'height 10'})
        heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
        bold = workbook.add_format({'bold': True})
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        right = workbook.add_format({'align': 'right'})
        regular = workbook.add_format({'align': 'center', 'bold': False, 'size': 8})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_color': '#000000',
        })
        format_hidden = workbook.add_format({
            'hidden': True
        })
        align_format = workbook.add_format({
            'align': 'right',
        })
        row = 6
        col = 1
        new_row = row

        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('D:S', 13)

        worksheet.merge_range('A1:L1', 'BEGORRA INFRASTRUCTURE & DEVELOPERS PVT LTD', boldc)
        worksheet.merge_range('A2:L2',
                              'DATE : From %s To %s' % (
                              datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                              (datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%d-%m-%Y"))),
                              boldc)
        worksheet.merge_range('A3:L3', 'Equipment Tyres & Repairs/Replacement/Puncture', boldc)
        worksheet.merge_range('A4:A5', 'Sl.NO', regular)
        worksheet.merge_range('B4:B5', 'Machine Name', regular)
        worksheet.merge_range('C4:C5', 'Machine No', regular)

        worksheet.write('D5', 'Tyre No', regular)
        worksheet.write('E5', 'Tyre Fitting Date', regular)
        worksheet.write('F5', 'Fitting KM', regular)
        worksheet.write('G5', 'Tyre Removing Date', regular)
        worksheet.write('H5', 'Removing KM', regular)
        worksheet.write('I5', 'Current KM', regular)
        worksheet.write('J5', 'Mileage(KM)', regular)
        worksheet.write('K5', 'Cum Mileage(KM)', regular)
        worksheet.write('L5', 'Remarks', regular)

        count = 1
        for rec in invoices:
            date_from = datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%Y-%m-%d 00:00:00")
            date_to = datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%Y-%m-%d 23:59:59")


            count = 1

            vehicle_categ = self.env['vehicle.category.type'].search([], order='priority asc')

            for categ in vehicle_categ:
                vehicle_list = self.env['fleet.vehicle'].search([('vehicle_categ_id', '=', categ.id)])
                for vehicle in vehicle_list:
                    domain = []
                    if rec.from_date:
                        domain.append('|')
                        domain.append(('removed_date', '=', False))
                    if rec.to_date:
                        domain.append(('removed_date', '<=', rec.to_date))

                    if rec.tyre_id:
                        domain.append(('tyre_id', '=', rec.tyre_id.id))
                    else:
                        domain.append(('vehicle_id', '=', vehicle.id))
                    daily_statement = self.env['retreading.tyre.line'].search(domain, limit=1, order='id desc')

                    for daily in daily_statement:
                        worksheet.write('A%s' % (new_row), count, regular)
                        worksheet.write('B%s' % (new_row), daily.vehicle_id.vehicle_categ_id.name, regular)
                        worksheet.write('C%s' % (new_row), daily.vehicle_id.name, regular)

                        worksheet.write('D%s' % (new_row), daily.tyre_id.name, regular)
                        worksheet.write('E%s' % (new_row), daily.fitting_date, regular)
                        worksheet.write('F%s' % (new_row), daily.fitting_km, regular)
                        worksheet.write('G%s' % (new_row), daily.removed_date, regular)
                        worksheet.write('H%s' % (new_row), daily.removing_km, regular)
                        daily_statement = self.env['driver.daily.statement'].search(
                            [('date', '<=', rec.to_date), ('vehicle_no', '=', daily.vehicle_id.id)], limit=1, order='date desc')
                        worksheet.write('I%s' % (new_row), daily_statement.actual_close_km, regular)
                        if daily.removing_km != 0:
                            mileage = daily.removing_km - daily.fitting_km
                            cum_km = daily.cum_km
                        else:
                            mileage = daily_statement.actual_close_km - daily.fitting_km
                            cum_km = (daily.cum_km + daily.fitting_km) + mileage
                        worksheet.write('J%s' % (new_row), mileage, regular)
                        worksheet.write('K%s' % (new_row), cum_km, regular)
                        worksheet.write('L%s' % (new_row), '', regular)

                        count += 1
                        new_row += 1

        worksheet = workbook.add_worksheet("Bill")
        # raise UserError(str(invoices.invoice_no.id))
        # print 'ddddddddddddddddddddddddd',self
        # print 'iiiiiiiiiiiiiiiiiiiiiiiiii',invoices

        boldc = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'font': 'height 10'})
        heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
        bold = workbook.add_format({'bold': True, 'align': 'center', 'size': 8})
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        right = workbook.add_format({'align': 'right'})
        regular = workbook.add_format({'align': 'center', 'bold': False, 'size': 8})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_color': '#000000',
        })
        format_hidden = workbook.add_format({
            'hidden': True
        })
        align_format = workbook.add_format({
            'align': 'right',
        })
        row = 6
        col = 1
        new_row = row

        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:S', 13)

        worksheet.merge_range('A1:L1', 'BEGORRA INFRASTRUCTURE & DEVELOPERS PVT LTD', boldc)
        worksheet.merge_range('A2:L2', 'All Project', boldc)
        worksheet.merge_range('A2:L2',
                              'DATE : From %s To %s' % (
                              datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                              (datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%d-%m-%Y"))),
                              boldc)
        worksheet.merge_range('A4:A5', 'Sl.NO', regular)
        worksheet.merge_range('B4:B5', 'Type of Vehicle', regular)
        worksheet.merge_range('C4:C5', 'Vehicle No', regular)
        worksheet.merge_range('D4:D5', 'Fuel Type', regular)
        worksheet.merge_range('E4:E5', 'Unit of Measure', regular)
        worksheet.merge_range('F4:F5', 'Fuel Tanker', regular)
        worksheet.merge_range('G4:G5', 'Today Receipt', regular)
        worksheet.merge_range('H4:H5', datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%d-%m-%Y"), regular)
        worksheet.merge_range('I4:I5', 'Pre Reading', regular)
        worksheet.merge_range('J4:J5', 'Current Reading', regular)
        worksheet.merge_range('K4:K5', 'Running KM', regular)
        worksheet.write('L5', "Mileage (KM)", regular)
        # worksheet.write('E5', "Closing KM", regular)
        # worksheet.write('F5', "Running KM", regular)
        # worksheet.write('G5', "Fuel Issue", regular)
        # worksheet.write('H5', "Consumption", regular)
        count = 1
        for rec in invoices:
            total_consumption = 0
            total_fuel = 0
            total_receipt = 0
            vehicle_list = self.env['fleet.vehicle'].search([
                ('rent_vehicle', '=', False),
                ('is_rent_mach', '=', False)])

            if rec.vehicle_id:
                vehicle_list = rec.vehicle_id

            for vehicle in vehicle_list:

                diesel_entry = self.env['diesel.pump.line'].search(
                    [('vehicle_id', '=', vehicle.id), ('date', '=', invoices.from_date)])

                if len(diesel_entry) != 0:
                    worksheet.write('A%s' % (new_row), count, regular)
                    worksheet.write('B%s' % (new_row), vehicle.vehicle_categ_id.name, regular)
                    worksheet.write('C%s' % (new_row), vehicle.license_plate, regular)

                    worksheet.write('E%s' % (new_row), "Litre", regular)
                    receipt_qty = 0
                    for diesel in diesel_entry:
                        if diesel.diesel_mode == 'pump':
                            receipt_qty += diesel.litre
                            total_receipt += diesel.litre
                    total = 0
                    milege = 0
                    for diesel in diesel_entry:
                        worksheet.write('D%s' % (new_row), diesel.fuel_product_id.name, regular)
                        worksheet.write('F%s' % (new_row), diesel.diesel_tanker.name, regular)
                        total += diesel.total_diesel
                        milege += diesel.mileage
                    worksheet.write('G%s' % (new_row), receipt_qty, regular)
                    if vehicle.tanker_bool == False and total == 0 and total_receipt != 0:

                        worksheet.write('H%s' % (new_row), receipt_qty, regular)
                    else:

                        worksheet.write('H%s' % (new_row), total, regular)
                    date_today = datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime(
                        "%Y-%m-%d 00:00:00")

                    diesel_entry_date_desc = self.env['diesel.pump.line'].search(
                        [('vehicle_id', '=', vehicle.id), ('date', '=', invoices.from_date)], order='id desc',
                        limit=1)

                    diesel_entry_date_asc = self.env['diesel.pump.line'].search(
                        [('vehicle_id', '=', vehicle.id), ('date', '=', invoices.from_date)], order='id asc',
                        limit=1)

                    total_fuel += total

                    worksheet.write('I%s' % (new_row), diesel_entry_date_desc.start_km, regular)
                    worksheet.write('J%s' % (new_row), diesel_entry_date_asc.close_km, regular)
                    worksheet.write('K%s' % (new_row), diesel_entry_date_asc.close_km - diesel_entry_date_desc.start_km,
                                    regular)
                    worksheet.write('L%s' % (new_row), milege, regular)
                    # worksheet.write('H%s' % (new_row), daily_statement.consumption_rate, regular)

                    new_row += 1
                    count += 1
            # worksheet.write('H%s' % (new_row), total_consumption, regular)
            worksheet.write('G%s' % (new_row), total_receipt, regular)
            worksheet.write('H%s' % (new_row), total_fuel, regular)
            new_row += 3
            vehicle_tank = self.env['fleet.vehicle'].search([('tanker_bool', '=', True)])
            for tanker in vehicle_tank:
                tanker_stock = sum(self.env['stock.history'].search(
                    [('date', '<', rec.from_date), ('location_id', '=', tanker.location_id.id)]).mapped('quantity'))

                worksheet.merge_range('A%s:F%s' % (new_row, new_row), "Diesel Tanker Opening Stock %s" % (tanker.name),
                                      bold)
                worksheet.write('G%s' % (new_row), tanker_stock, bold)
                new_row += 1

            for tanker in vehicle_tank:
                diesel_issued = sum(self.env['diesel.pump.line'].search(
                    [('date', '=', rec.from_date), ('diesel_tanker', '=', tanker.id),
                     ('fuel_product_id', '=', 'DIESEL FUEL')]).mapped('total_diesel'))

                worksheet.merge_range('A%s:F%s' % (new_row, new_row), "Diesel Tanker Issued %s" % (tanker.name), bold)
                worksheet.write('G%s' % (new_row), diesel_issued, bold)
                new_row += 1

            for tanker in vehicle_tank:
                tanker_stock = sum(self.env['stock.history'].search(
                    [('date', '<', rec.from_date), ('location_id', '=', tanker.location_id.id)]).mapped('quantity'))

                diesel_issued = sum(self.env['diesel.pump.line'].search(
                    [('date', '=', rec.from_date), ('diesel_tanker', '=', tanker.id),
                     ('fuel_product_id', '=', 'DIESEL FUEL')]).mapped('total_diesel'))

                diesel_entry = sum(self.env['diesel.pump.line'].search(
                    [('vehicle_id', '=', tanker.id), ('date', '=', rec.from_date)]).mapped('litre'))

                used = 0.0
                used += tanker_stock + diesel_entry - diesel_issued

                worksheet.merge_range('A%s:F%s' % (new_row, new_row), "Diesel Tanker Closing Stock %s" % (tanker.name),
                                      bold)
                worksheet.write('G%s' % (new_row), used, bold)
                new_row += 1

            vehicle_pump = self.env['res.partner'].search([('is_fuel_station', '=', True)])

            total_pump = 0

            worksheet.merge_range('C%s:D%s' % (new_row, new_row), "Diesel Receipt from Pump", bold)
            new_row += 1

            for pump in vehicle_pump:
                diesel_issued = sum(self.env['diesel.pump.line'].search(
                    [('date', '=', rec.from_date), ('diesel_pump', '=', pump.id),
                     ('fuel_product_id', '=', 4873)]).mapped('litre'))

                if diesel_issued:
                    worksheet.merge_range('C%s:D%s' % (new_row, new_row), "Pump :  %s  " % (pump.name), regular)
                    worksheet.write('E%s' % (new_row), diesel_issued, regular)
                    total_pump += diesel_issued
                    new_row += 1

            worksheet.merge_range('C%s:D%s' % (new_row, new_row), "Petrol Receipt from Pump", bold)
            new_row += 1

            for pump in vehicle_pump:
                diesel_issued = sum(self.env['diesel.pump.line'].search(
                    [('date', '=', rec.from_date), ('diesel_pump', '=', pump.id),
                     ('fuel_product_id', '=', 4874)]).mapped('litre'))

                if diesel_issued:
                    worksheet.merge_range('C%s:D%s' % (new_row, new_row), "Pump : %s " % (pump.name), regular)
                    worksheet.write('E%s' % (new_row), diesel_issued, regular)
                    total_pump += diesel_issued
                    new_row += 1

            worksheet.write('E%s' % (new_row), total_pump, regular)
            # worksheet.write('R%s' % (new_row), driver.remark, regular)

BillReportXlsx('report.equipment_monthly_report.xlsx', 'maintanance.report')

class BillReportXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, invoices):
        worksheet = workbook.add_worksheet("Equiment Utilisation")
        # raise UserError(str(invoices.invoice_no.id))

        boldc = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'font': 'height 10'})
        heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
        bold = workbook.add_format({'bold': True})
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        right = workbook.add_format({'align': 'right'})
        regular = workbook.add_format({'align': 'center', 'bold': False, 'size': 8})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_color': '#000000',
        })
        format_hidden = workbook.add_format({
            'hidden': True
        })
        align_format = workbook.add_format({
            'align': 'right',
        })
        row = 6
        col = 1
        new_row = row

        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('D:S', 13)

        worksheet.merge_range('A1:Q1', 'BEGORRA INFRASTRUCTURE & DEVELOPERS PVT LTD', boldc)
        worksheet.merge_range('A2:Q2',
                              'DATE : From %s To %s' % (
                              datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                              (datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%d-%m-%Y"))),
                              boldc)
        worksheet.merge_range('A3:Q3', 'Equipment utilisation in terms of working hrs/kms', boldc)
        worksheet.write('A5', 'Sl.NO', regular)
        worksheet.write('B5', 'Date', regular)
        worksheet.write('C5', 'Type of Equipment', regular)
        worksheet.write('D5', 'Fleet No', regular)
        worksheet.write('E5', 'Plant & Equipment', regular)
        worksheet.write('F5', 'Location', regular)
        worksheet.write('G5', 'Starting KM', regular)
        worksheet.write('H5', 'Ending KM', regular)
        worksheet.write('I5', 'Running KM', regular)
        worksheet.write('J5', 'Fuel', regular)
        worksheet.write('K5', 'Mileage', regular)
        worksheet.write('L5', 'EXPENSE ON FUEL', regular)
        worksheet.write('M5', 'EXPENSE ON SPARE', regular)
        worksheet.write('N5', 'EXPENSE ON LUB', regular)
        worksheet.write('O5', 'EXPENSE ON TYRES', regular)
        worksheet.write('P5', 'EXPENSE ON BATTERY', regular)

        # worksheet.merge_range('A4:O5','',regular)
        worksheet.write('Q5', 'Remarks', regular)

        count = 1
        for rec in invoices:
            date_from = datetime.strptime(invoices.from_date, "%Y-%m-%d")
            to_date = datetime.strptime(invoices.to_date, "%Y-%m-%d")

            count = 1
            count = 1
            if not rec.vehicle_id:
                vehicle_categ = self.env['vehicle.category.type'].search([], order='priority asc')
            else:
                vehicle_categ = rec.vehicle_id.vehicle_categ_id
            for categ in vehicle_categ:
                if not rec.vehicle_id:
                    vehicle_list = self.env['fleet.vehicle'].search([('vehicle_categ_id', '=', categ.id)])


                    for daily in vehicle_list:
                        domain = []
                        domain2 = []
                        if rec.from_date:
                            domain.append(('date', '>=', date_from))
                            domain2.append(('date', '>=', date_from))
                        if rec.to_date:
                            domain.append(('date', '<=', to_date))
                            domain2.append(('date', '<=', to_date))
                        domain2.append(('vehicle_id', '=', daily.id))
                        domain.append(('vehicle_no', '=', daily.id))
                        start_km = self.env['driver.daily.statement'].search([('date', '>=', date_from),('date', '<=', to_date),('vehicle_no', '=', daily.id),('start_km','!=',0)], order='date asc', limit=1)
                        close_km =  self.env['driver.daily.statement'].search([('date', '>=', date_from),('date', '<=', to_date),('vehicle_no', '=', daily.id),('actual_close_km','!=',0)], order='date desc', limit=1)
                        daily_statement = self.env['driver.daily.statement'].search(domain, order='date asc', limit=1)
                        daily_statement_des = self.env['driver.daily.statement'].search(domain, order='date desc', limit=1)

                        expense_spares = 0
                        expense_lub = 0
                        expense_tyre = 0
                        expense_battery = 0
                        expense_fuel = 0
                        if daily_statement_des:
                            worksheet.write('A%s' % (new_row), count, regular)
                            worksheet.write('B%s' % (new_row), daily_statement_des.date, regular)
                            worksheet.write('C%s' % (new_row), daily.vehicle_categ_id.name, regular)
                            worksheet.write('D%s' % (new_row), daily.fleet_no, regular)
                            worksheet.write('E%s' % (new_row), daily.name, regular)
                            worksheet.write('F%s' % (new_row), daily_statement_des.project_id.location_id.name, regular)

                            worksheet.write('G%s' % (new_row), start_km.start_km, regular)
                            worksheet.write('H%s' % (new_row), close_km.actual_close_km, regular)
                            worksheet.write('I%s' % (new_row),
                                            close_km.actual_close_km - start_km.start_km,
                                            regular)
                            fuel = 0
                            mileage = 0

                            date_from = datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%Y-%m-%d 00:00:00")
                            from_zone = tz.gettz('UTC')
                            to_zone = tz.gettz('Asia/Kolkata')
                            # from_zone = tz.tzutc()
                            # to_zone = tz.tzlocal()
                            utc = datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')
                            utc = utc.replace(tzinfo=to_zone)
                            central = utc.astimezone(from_zone)

                            # date_today = utcc.replace(tzinfo=from_zone)
                            date_from = datetime.strptime(central.strftime("%Y-%m-%d %H:%M:%S"),
                                                          '%Y-%m-%d %H:%M:%S').strftime(
                                "%Y-%m-%d %H:%M:%S")
                            date_to = datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%Y-%m-%d 23:59:59")
                            from_zone = tz.gettz('UTC')
                            to_zone = tz.gettz('Asia/Kolkata')
                            # from_zone = tz.tzutc()
                            # to_zone = tz.tzlocal()
                            utc = datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')
                            utc = utc.replace(tzinfo=to_zone)
                            central = utc.astimezone(from_zone)

                            # date_today = utcc.replace(tzinfo=from_zone)
                            date_to = datetime.strptime(central.strftime("%Y-%m-%d %H:%M:%S"),
                                                        '%Y-%m-%d %H:%M:%S').strftime(
                                "%Y-%m-%d %H:%M:%S")

                            diesel_entry_desc = self.env['diesel.pump.line'].search(domain2, order='date desc', limit=1)
                            diesel_entry_asc = self.env['diesel.pump.line'].search(domain2, order='date asc', limit=1)

                            material_issue = self.env['material.issue.slip'].search(
                                [('date', '<=', date_to), ('date', '>=', date_from), ('vehicle_id', '=', daily.id)])
                            for material in material_issue:
                                for expense_line in material.material_issue_slip_lines_ids:
                                    if expense_line.item_id.categ_id.vehicle_type == 'fuel':
                                        fuel += expense_line.req_qty
                                        expense_fuel += expense_line.amount

                            worksheet.write('J%s' % (new_row), fuel, regular)
                            if fuel == 0:
                                mileage = 0
                            else:
                                if daily.machinery:
                                    if (close_km.actual_close_km - start_km.start_km) == 0:
                                        mileage = 0
                                    else:
                                        mileage = fuel / (close_km.actual_close_km - start_km.start_km)
                                else:
                                    mileage = (close_km.actual_close_km - start_km.start_km) / fuel


                            worksheet.write('K%s' % (new_row), round(mileage,2), regular)
                            expense_spare = self.env['material.issue.slip'].search(
                                [('date', '>=', date_from), ('date', '<=', date_to), ('vehicle_id', '=', daily.id)])
                            for expense in expense_spare:
                                for expense_line in expense.material_issue_slip_lines_ids:
                                    if expense_line.item_id.categ_id.vehicle_type == 'spare':
                                        expense_spares += expense_line.amount
                                    if expense_line.item_id.categ_id.vehicle_type == 'lub':
                                        expense_lub += expense_line.amount
                                    if expense_line.item_id.categ_id.vehicle_type == 'tyre':
                                        expense_tyre += expense_line.amount
                                    if expense_line.item_id.categ_id.vehicle_type == 'battery':
                                        expense_battery += expense_line.amount
                            remark = ''
                            worksheet.write('L%s' % (new_row), expense_fuel, regular)
                            worksheet.write('M%s' % (new_row), expense_spares, regular)
                            worksheet.write('N%s' % (new_row), expense_lub, regular)
                            worksheet.write('O%s' % (new_row), expense_tyre, regular)
                            worksheet.write('P%s' % (new_row), expense_battery, regular)
                            worksheet.write('Q%s' % (new_row), remark, regular)

                            count += 1
                            new_row += 1
                else:
                    vehicle_list = rec.vehicle_id
                    for daily in vehicle_list:
                        date_from = datetime.strptime(rec.from_date, '%Y-%m-%d')
                        to_date = datetime.strptime(rec.to_date, '%Y-%m-%d')
                        date_diff = to_date - date_from
                        close_km_prev = 0
                        for rangeg in range(date_diff.days + 1):
                            domain = []
                            domain2 = []
                            expense_spares = 0
                            expense_lub = 0
                            expense_tyre = 0
                            expense_battery = 0
                            expense_fuel = 0
                            fuel = 0
                            mileage = 0
                            if date_from:
                                domain.append(('date', '=', date_from))
                                domain2.append(('date', '=', date_from))

                            domain2.append(('vehicle_id', '=', daily.id))
                            domain.append(('vehicle_no', '=', daily.id))
                            daily_statement_des = self.env['driver.daily.statement'].search(domain, order='date asc')

                            worksheet.write('A%s' % (new_row), count, regular)
                            worksheet.write('B%s' % (new_row), date_from.strftime("%d-%m-%Y"), regular)
                            worksheet.write('C%s' % (new_row), daily.vehicle_categ_id.name, regular)
                            worksheet.write('D%s' % (new_row), daily.fleet_no, regular)
                            worksheet.write('E%s' % (new_row), daily.name, regular)
                            running_km = 0
                            for statement in daily_statement_des:
                                worksheet.write('F%s' % (new_row), statement.project_id.location_id.name, regular)

                                worksheet.write('G%s' % (new_row), statement.start_km, regular)
                                worksheet.write('H%s' % (new_row), statement.actual_close_km, regular)
                                worksheet.write('I%s' % (new_row),
                                                round((statement.actual_close_km - statement.start_km),2),
                                                regular)
                                running_km += statement.actual_close_km - statement.start_km
                                close_km_prev = statement.actual_close_km
                            if not daily_statement_des:
                                worksheet.write('G%s' % (new_row), close_km_prev, regular)
                                worksheet.write('H%s' % (new_row), close_km_prev, regular)
                                worksheet.write('I%s' % (new_row),
                                                close_km_prev - close_km_prev,
                                                regular)

                            fuel_date_from = date_from.strftime("%Y-%m-%d 00:00:00")

                            fuel_date_to = date_from.strftime("%Y-%m-%d 23:59:59")
                            material_issue = self.env['material.issue.slip'].search(
                                [('date', '<=', fuel_date_to), ('date', '>=', fuel_date_from), ('vehicle_id', '=', daily.id)])

                            for material in material_issue:
                                for expense_line in material.material_issue_slip_lines_ids:
                                    if expense_line.item_id.categ_id.vehicle_type == 'fuel':
                                        fuel += expense_line.req_qty
                                        expense_fuel += expense_line.amount
                                    if expense_line.item_id.categ_id.vehicle_type == 'spare':
                                        expense_spares += expense_line.amount
                                    if expense_line.item_id.categ_id.vehicle_type == 'lub':
                                        expense_lub += expense_line.amount
                                    if expense_line.item_id.categ_id.vehicle_type == 'tyre':
                                        expense_tyre += expense_line.amount
                                    if expense_line.item_id.categ_id.vehicle_type == 'battery':
                                        expense_battery += expense_line.amount
                            remark = ''
                            if daily.machinery:
                                if running_km == 0:
                                    mileage = 0
                                else:
                                    mileage = fuel / running_km
                            else:
                                mileage = running_km / fuel
                            worksheet.write('J%s' % (new_row), fuel, regular)
                            worksheet.write('K%s' % (new_row), round(mileage,2), regular)
                            worksheet.write('L%s' % (new_row), expense_fuel, regular)
                            worksheet.write('M%s' % (new_row), expense_spares, regular)
                            worksheet.write('N%s' % (new_row), expense_lub, regular)
                            worksheet.write('O%s' % (new_row), expense_tyre, regular)
                            worksheet.write('P%s' % (new_row), expense_battery, regular)
                            worksheet.write('Q%s' % (new_row), remark, regular)
                            count += 1
                            new_row += 1
                            from_date = date_from + timedelta(days=1)
                            date_from = from_date



BillReportXlsx('report.equipment_utilisation_report.xlsx', 'maintanance.report')


class BillReportXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, invoices):
        worksheet = workbook.add_worksheet("Equiment Breakdown Report")
        # raise UserError(str(invoices.invoice_no.id))

        boldc = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'font': 'height 10'})
        heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
        bold = workbook.add_format({'bold': True})
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        right = workbook.add_format({'align': 'right'})
        regular = workbook.add_format({'align': 'center', 'bold': False, 'size': 8})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_color': '#000000',
        })
        format_hidden = workbook.add_format({
            'hidden': True
        })
        align_format = workbook.add_format({
            'align': 'right',
        })
        row = 6
        col = 1
        new_row = row

        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('D:S', 13)

        worksheet.merge_range('A1:J1', 'BEGORRA INFRASTRUCTURE & DEVELOPERS PVT LTD', boldc)
        worksheet.merge_range('A2:J2',
                              'DATE : From %s To %s' % (
                              datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                              (datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%d-%m-%Y"))),
                              boldc)
        worksheet.merge_range('A3:J3', 'Equipment Breakdown Report', boldc)
        worksheet.merge_range('A4:A5', 'Sl.NO', regular)
        worksheet.merge_range('B4:B5', 'Date of Breakdown', regular)
        worksheet.merge_range('C4:C5', 'Machinery Details', regular)
        worksheet.merge_range('D4:D5', 'Model & Serial No', regular)
        worksheet.merge_range('E4:E5', 'Location', regular)
        worksheet.write('F5', 'Breakdown Details', regular)
        worksheet.write('G5', 'Action Taken', regular)
        worksheet.write('H5', 'Date of Rectification', regular)
        worksheet.write('I5', 'Target Date of Completion', regular)
        worksheet.write('J5', 'Remarks', regular)

        count = 1
        for rec in invoices:
            date_from = datetime.strptime(invoices.from_date, "%Y-%m-%d")
            to_from = datetime.strptime(invoices.to_date, "%Y-%m-%d")

            count = 1
            domain = []
            if rec.from_date:
                domain.append('|')
                domain.append(('target_date_completion', '=', False))
                domain.append(('date_com', '<=', date_from))
                domain.append(('target_date_completion', '>=', to_from))
                domain.append(('r_b_bool', '=', True))

            if rec.vehicle_id:
                domain.append(('vehicle_id', '=', rec.vehicle_id.id))

            daily_statement = self.env['fleet.vehicle.log.services'].search(domain)

            for daily in daily_statement:
                worksheet.write('A%s' % (new_row), count, regular)
                worksheet.write('B%s' % (new_row), daily.date_com, regular)
                worksheet.write('C%s' % (new_row), daily.vehicle_id.vehicle_categ_id.name, regular)
                worksheet.write('D%s' % (new_row), daily.vehicle_id.name, regular)
                worksheet.write('E%s' % (new_row), daily.project_id.location_id.name, regular)

                worksheet.write('F%s' % (new_row), daily.nature_breakdown, regular)
                worksheet.write('G%s' % (new_row), daily.works_done, regular)
                worksheet.write('H%s' % (new_row), daily.date_of_rectification, regular)
                worksheet.write('I%s' % (new_row), daily.target_date_completion, regular)
                worksheet.write('J%s' % (new_row), daily.notes, regular)

                count += 1
                new_row += 1

BillReportXlsx('report.equipment_breakdown_report.xlsx', 'maintanance.report')


class BillReportXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, invoices):
        worksheet = workbook.add_worksheet("Equiment Preventive ")
        # raise UserError(str(invoices.invoice_no.id))

        boldc = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'font': 'height 10'})
        heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
        bold = workbook.add_format({'bold': True})
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        right = workbook.add_format({'align': 'right'})
        regular = workbook.add_format({'align': 'center', 'bold': False, 'size': 8})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_color': '#000000',
        })
        format_hidden = workbook.add_format({
            'hidden': True
        })
        align_format = workbook.add_format({
            'align': 'right',
        })
        row = 6
        col = 1
        new_row = row

        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('D:S', 13)

        worksheet.merge_range('A1:J1', 'BEGORRA INFRASTRUCTURE & DEVELOPERS PVT LTD', boldc)
        worksheet.merge_range('A2:J2',
                              'DATE : From %s To %s' % (
                              datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                              (datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%d-%m-%Y"))),
                              boldc)
        worksheet.merge_range('A3:J3', 'Equiment Preventive Maintenance', boldc)
        worksheet.merge_range('A4:A5', 'Sl.NO', regular)

        worksheet.merge_range('B4:B5', 'Type of Equipment/Vehicle', regular)
        worksheet.merge_range('C4:C5', 'Fleet No', regular)

        worksheet.write('D5', 'Reg No:', regular)
        worksheet.write('E5', 'Date', regular)
        worksheet.write('F5', 'Last Service KM/HRS', regular)
        worksheet.write('G5', 'Service Period', regular)
        worksheet.write('H5', 'Current Reading', regular)
        worksheet.write('I5', 'Next Service KM/HRS', regular)
        worksheet.write('J5', 'Remarks', regular)

        count = 1
        for rec in invoices:
            date_from = datetime.strptime(invoices.from_date, "%Y-%m-%d")
            to_from = datetime.strptime(invoices.to_date, "%Y-%m-%d")

            count = 1

            if rec.vehicle_id:
                vehicle = rec.vehicle_id
            else:
                vehicle = self.env['fleet.vehicle'].search([])

            for veh in vehicle:
                domain = []

                if rec.to_date:
                    domain.append(('date', '<=', rec.to_date))
                domain.append(('vehicle_id', '=', veh.id))
                daily_statement = self.env['vehicle.preventive.maintenance.line'].search(domain, order='date desc',
                                                                                         limit=1)
                for daily in daily_statement:
                    worksheet.write('A%s' % (new_row), count, regular)
                    worksheet.write('B%s' % (new_row), veh.vehicle_categ_id.name, regular)
                    worksheet.write('C%s' % (new_row), veh.brand_id.name, regular)
                    worksheet.write('D%s' % (new_row), veh.name, regular)

                    worksheet.write('E%s' % (new_row), daily.date, regular)
                    worksheet.write('F%s' % (new_row), daily.last_service_km, regular)
                    worksheet.write('G%s' % (new_row), daily.service_period, regular)
                    daily_statement = self.env['driver.daily.statement'].search(
                        [('date', '<=', rec.to_date), ('vehicle_no', '=', veh.id)], limit=1,
                        order='date desc')
                    worksheet.write('H%s' % (new_row), daily_statement.actual_close_km, regular)

                    worksheet.write('I%s' % (new_row), daily.next_service_km, regular)
                    worksheet.write('J%s' % (new_row), daily.remarks, regular)
                    count += 1
                    new_row += 1
BillReportXlsx('report.equipment_preventive_report.xlsx', 'maintanance.report')


class BillReportXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, invoices):
        worksheet = workbook.add_worksheet("Equipment Daily Maintanance")
        # raise UserError(str(invoices.invoice_no.id))

        boldc = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'font': 'height 10'})
        heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
        bold = workbook.add_format({'bold': True})
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        right = workbook.add_format({'align': 'right'})
        regular = workbook.add_format({'align': 'center', 'bold': False, 'size': 8})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_color': '#000000',
        })
        format_hidden = workbook.add_format({
            'hidden': True
        })
        align_format = workbook.add_format({
            'align': 'right',
        })
        row = 6
        col = 1
        new_row = row

        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('D:S', 13)

        worksheet.merge_range('A1:H1', 'BEGORRA INFRASTRUCTURE & DEVELOPERS PVT LTD', boldc)
        worksheet.merge_range('A2:H2',
                              'DATE : From %s To %s' % (
                              datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                              (datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%d-%m-%Y"))),
                              boldc)
        worksheet.merge_range('A3:H3', 'Equipment Daily Maintenance attended ', boldc)
        worksheet.merge_range('A4:A5', 'Sl.NO', regular)
        worksheet.merge_range('B4:B5', 'Date', regular)
        worksheet.merge_range('C4:C5', 'Machine Name', regular)

        worksheet.write('D5', 'Machine No', regular)
        worksheet.write('E5', 'Mechanic', regular)
        worksheet.write('F5', 'Work Description', regular)
        worksheet.write('G5', 'Material Used', regular)
        worksheet.write('H5', 'Remarks', regular)

        count = 1
        for rec in invoices:
            date_from = datetime.strptime(invoices.from_date, "%Y-%m-%d")
            date_to = datetime.strptime(invoices.to_date, "%Y-%m-%d")
            domain = []
            domain.append(('daily_maint_bool', '=', True))
            if rec.vehicle_id:
                domain.append(('vehicle_id', '=', rec.vehicle_id.id))
            if rec.from_date:
                domain.append(('date_com', '>=', date_from))
            if rec.to_date:
                domain.append(('date_com', '<=', date_to))
            count = 1

            daily_statement = self.env['fleet.vehicle.log.services'].search(domain, order='date_com asc')

            for daily in daily_statement:
                worksheet.write('A%s' % (new_row), count, regular)
                worksheet.write('B%s' % (new_row), daily.date_com, regular)
                worksheet.write('C%s' % (new_row), daily.vehicle_id.vehicle_categ_id.name, regular)
                worksheet.write('D%s' % (new_row), daily.vehicle_id.name, regular)
                mec_name = ''
                for mec in daily.mechanic_id:
                    mec_name += mec.name + ','
                worksheet.write('E%s' % (new_row), mec_name, regular)
                material_used = ''
                for mate in daily.cost_ids:
                    material_used += mate.particular_id and mate.particular_id.name or ' ' + ','
                worksheet.write('F%s' % (new_row), material_used, regular)
                worksheet.write('G%s' % (new_row), daily.notes, regular)

                count += 1
                new_row += 1
BillReportXlsx('report.equipment_daily_report.xlsx', 'maintanance.report')


class BillReportXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, invoices):
        worksheet = workbook.add_worksheet("Equipment Tyres ")
        # raise UserError(str(invoices.invoice_no.id))

        boldc = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'font': 'height 10'})
        heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
        bold = workbook.add_format({'bold': True})
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        right = workbook.add_format({'align': 'right'})
        regular = workbook.add_format({'align': 'center', 'bold': False, 'size': 8})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_color': '#000000',
        })
        format_hidden = workbook.add_format({
            'hidden': True
        })
        align_format = workbook.add_format({
            'align': 'right',
        })
        row = 6
        col = 1
        new_row = row

        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('D:S', 13)

        worksheet.merge_range('A1:L1', 'BEGORRA INFRASTRUCTURE & DEVELOPERS PVT LTD', boldc)
        worksheet.merge_range('A2:L2',
                              'DATE : From %s To %s' % (
                                  datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                                  (datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%d-%m-%Y"))),
                              boldc)
        worksheet.merge_range('A3:L3', 'Equipment Tyres & Repairs/Replacement/Puncture', boldc)
        worksheet.merge_range('A4:A5', 'Sl.NO', regular)
        worksheet.merge_range('B4:B5', 'Machine Name', regular)
        worksheet.merge_range('C4:C5', 'Machine No', regular)

        worksheet.write('D5', 'Tyre No', regular)
        worksheet.write('E5', 'Tyre Fitting Date', regular)
        worksheet.write('F5', 'Fitting KM', regular)
        worksheet.write('G5', 'Tyre Removing Date', regular)
        worksheet.write('H5', 'Removing KM', regular)
        worksheet.write('I5', 'Current KM', regular)
        worksheet.write('J5', 'Mileage(KM)', regular)
        worksheet.write('K5', 'Cum Mileage(KM)', regular)
        worksheet.write('L5', 'Remarks', regular)

        count = 1
        for rec in invoices:
            date_from = datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%Y-%m-%d 00:00:00")
            date_to = datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%Y-%m-%d 23:59:59")

            count = 1

            vehicle_categ = self.env['vehicle.category.type'].search([], order='priority asc')

            for categ in vehicle_categ:
                vehicle_list = self.env['fleet.vehicle'].search([('vehicle_categ_id', '=', categ.id)])
                for vehicle in vehicle_list:
                    domain = []
                    if rec.from_date:
                        domain.append('|')
                        domain.append(('removed_date', '=', False))
                    if rec.to_date:
                        domain.append(('removed_date', '<=', rec.to_date))

                    if rec.tyre_id:
                        domain.append(('tyre_id', '=', rec.tyre_id.id))
                    else:
                        domain.append(('vehicle_id', '=', vehicle.id))
                    daily_statement = self.env['retreading.tyre.line'].search(domain, limit=1, order='id desc')

                    for daily in daily_statement:
                        worksheet.write('A%s' % (new_row), count, regular)
                        worksheet.write('B%s' % (new_row), daily.vehicle_id.vehicle_categ_id.name, regular)
                        worksheet.write('C%s' % (new_row), daily.vehicle_id.name, regular)

                        worksheet.write('D%s' % (new_row), daily.tyre_id.name, regular)
                        worksheet.write('E%s' % (new_row), daily.fitting_date, regular)
                        worksheet.write('F%s' % (new_row), daily.fitting_km, regular)
                        worksheet.write('G%s' % (new_row), daily.removed_date, regular)
                        worksheet.write('H%s' % (new_row), daily.removing_km, regular)
                        daily_statement = self.env['driver.daily.statement'].search(
                            [('date', '<=', rec.to_date), ('vehicle_no', '=', daily.vehicle_id.id)], limit=1,
                            order='date desc')
                        worksheet.write('I%s' % (new_row), daily_statement.actual_close_km, regular)
                        if daily.removing_km != 0:
                            mileage = daily.removing_km - daily.fitting_km
                            cum_km = daily.cum_km
                        else:
                            mileage = daily_statement.actual_close_km - daily.fitting_km
                            cum_km = (daily.cum_km + daily.fitting_km) + mileage
                        worksheet.write('J%s' % (new_row), mileage, regular)
                        worksheet.write('K%s' % (new_row), cum_km, regular)
                        worksheet.write('L%s' % (new_row), '', regular)

                        count += 1
                        new_row += 1
BillReportXlsx('report.equipment_tyre_repairs_report.xlsx', 'maintanance.report')



class BillReportXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, invoices):
        worksheet = workbook.add_worksheet("Bill")
        # raise UserError(str(invoices.invoice_no.id))
        # print 'ddddddddddddddddddddddddd',self
        # print 'iiiiiiiiiiiiiiiiiiiiiiiiii',invoices

        boldc = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'font': 'height 10'})
        heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
        bold = workbook.add_format({'bold': True, 'align': 'center', 'size': 8})
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        right = workbook.add_format({'align': 'right'})
        regular = workbook.add_format({'align': 'center', 'bold': False, 'size': 8})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_color': '#000000',
        })
        format_hidden = workbook.add_format({
            'hidden': True
        })
        align_format = workbook.add_format({
            'align': 'right',
        })
        row = 6
        col = 1
        new_row = row

        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:S', 13)

        worksheet.merge_range('A1:L1', 'BEGORRA INFRASTRUCTURE & DEVELOPERS PVT LTD', boldc)
        worksheet.merge_range('A2:L2', 'All Project', boldc)
        worksheet.merge_range('A2:L2',
                              'DATE : From %s To %s' % (
                              datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                              (datetime.strptime(invoices.to_date, "%Y-%m-%d").strftime("%d-%m-%Y"))),
                              boldc)
        worksheet.merge_range('A4:A5', 'Sl.NO', regular)
        worksheet.merge_range('B4:B5', 'Type of Vehicle', regular)
        worksheet.merge_range('C4:C5', 'Vehicle No', regular)
        worksheet.merge_range('D4:D5', 'Fuel Type', regular)
        worksheet.merge_range('E4:E5', 'Unit of Measure', regular)
        worksheet.merge_range('F4:F5', 'Fuel Tanker', regular)
        worksheet.merge_range('G4:G5', 'Today Receipt', regular)
        worksheet.merge_range('H4:H5', datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime("%d-%m-%Y"), regular)
        worksheet.merge_range('I4:I5', 'Pre Reading', regular)
        worksheet.merge_range('J4:J5', 'Current Reading', regular)
        worksheet.merge_range('K4:K5', 'Running KM', regular)
        worksheet.write('L5', "Mileage (KM)", regular)
        # worksheet.write('E5', "Closing KM", regular)
        # worksheet.write('F5', "Running KM", regular)
        # worksheet.write('G5', "Fuel Issue", regular)
        # worksheet.write('H5', "Consumption", regular)
        count = 1
        for rec in invoices:
            total_consumption = 0
            total_fuel = 0
            total_receipt = 0
            vehicle_list = self.env['fleet.vehicle'].search([
                ('rent_vehicle', '=', False),
                ('is_rent_mach', '=', False)])

            if rec.vehicle_id:
                vehicle_list = rec.vehicle_id

            for vehicle in vehicle_list:

                diesel_entry = self.env['diesel.pump.line'].search(
                    [('vehicle_id', '=', vehicle.id), ('date', '=', invoices.from_date)])

                if len(diesel_entry) != 0:
                    worksheet.write('A%s' % (new_row), count, regular)
                    worksheet.write('B%s' % (new_row), vehicle.vehicle_categ_id.name, regular)
                    worksheet.write('C%s' % (new_row), vehicle.license_plate, regular)

                    worksheet.write('E%s' % (new_row), "Litre", regular)
                    receipt_qty = 0
                    for diesel in diesel_entry:
                        if diesel.diesel_mode == 'pump':
                            receipt_qty += diesel.litre
                            total_receipt += diesel.litre
                    total = 0
                    milege = 0
                    for diesel in diesel_entry:
                        worksheet.write('D%s' % (new_row), diesel.fuel_product_id.name, regular)
                        worksheet.write('F%s' % (new_row), diesel.diesel_tanker.name, regular)
                        total += diesel.total_diesel
                        milege += diesel.mileage
                    worksheet.write('G%s' % (new_row), receipt_qty, regular)
                    if vehicle.tanker_bool == False and total == 0 and total_receipt != 0:

                        worksheet.write('H%s' % (new_row), receipt_qty, regular)
                    else:

                        worksheet.write('H%s' % (new_row), total, regular)
                    date_today = datetime.strptime(invoices.from_date, "%Y-%m-%d").strftime(
                        "%Y-%m-%d 00:00:00")

                    diesel_entry_date_desc = self.env['diesel.pump.line'].search(
                        [('vehicle_id', '=', vehicle.id), ('date', '=', invoices.from_date)], order='id desc',
                        limit=1)

                    diesel_entry_date_asc = self.env['diesel.pump.line'].search(
                        [('vehicle_id', '=', vehicle.id), ('date', '=', invoices.from_date)], order='id asc',
                        limit=1)

                    total_fuel += total

                    worksheet.write('I%s' % (new_row), diesel_entry_date_desc.start_km, regular)
                    worksheet.write('J%s' % (new_row), diesel_entry_date_asc.close_km, regular)
                    worksheet.write('K%s' % (new_row), diesel_entry_date_asc.close_km - diesel_entry_date_desc.start_km,
                                    regular)
                    worksheet.write('L%s' % (new_row), milege, regular)
                    # worksheet.write('H%s' % (new_row), daily_statement.consumption_rate, regular)

                    new_row += 1
                    count += 1
            # worksheet.write('H%s' % (new_row), total_consumption, regular)
            worksheet.write('G%s' % (new_row), total_receipt, regular)
            worksheet.write('H%s' % (new_row), total_fuel, regular)
            new_row += 3
            vehicle_tank = self.env['fleet.vehicle'].search([('tanker_bool', '=', True)])
            for tanker in vehicle_tank:
                tanker_stock = sum(self.env['stock.history'].search(
                    [('date', '<', rec.from_date), ('location_id', '=', tanker.location_id.id)]).mapped('quantity'))

                worksheet.merge_range('A%s:F%s' % (new_row, new_row), "Diesel Tanker Opening Stock %s" % (tanker.name),
                                      bold)
                worksheet.write('G%s' % (new_row), tanker_stock, bold)
                new_row += 1

            for tanker in vehicle_tank:
                diesel_issued = sum(self.env['diesel.pump.line'].search(
                    [('date', '=', rec.from_date), ('diesel_tanker', '=', tanker.id),
                     ('fuel_product_id', '=', 'DIESEL FUEL')]).mapped('total_diesel'))

                worksheet.merge_range('A%s:F%s' % (new_row, new_row), "Diesel Tanker Issued %s" % (tanker.name), bold)
                worksheet.write('G%s' % (new_row), diesel_issued, bold)
                new_row += 1

            for tanker in vehicle_tank:
                tanker_stock = sum(self.env['stock.history'].search(
                    [('date', '<', rec.from_date), ('location_id', '=', tanker.location_id.id)]).mapped('quantity'))

                diesel_issued = sum(self.env['diesel.pump.line'].search(
                    [('date', '=', rec.from_date), ('diesel_tanker', '=', tanker.id),
                     ('fuel_product_id', '=', 'DIESEL FUEL')]).mapped('total_diesel'))

                diesel_entry = sum(self.env['diesel.pump.line'].search(
                    [('vehicle_id', '=', tanker.id), ('date', '=', rec.from_date)]).mapped('litre'))

                used = 0.0
                used += tanker_stock + diesel_entry - diesel_issued

                worksheet.merge_range('A%s:F%s' % (new_row, new_row), "Diesel Tanker Closing Stock %s" % (tanker.name),
                                      bold)
                worksheet.write('G%s' % (new_row), used, bold)
                new_row += 1

            vehicle_pump = self.env['res.partner'].search([('is_fuel_station', '=', True)])

            total_pump = 0

            worksheet.merge_range('C%s:D%s' % (new_row, new_row), "Diesel Receipt from Pump", bold)
            new_row += 1

            for pump in vehicle_pump:
                diesel_issued = sum(self.env['diesel.pump.line'].search(
                    [('date', '=', rec.from_date), ('diesel_pump', '=', pump.id),
                     ('fuel_product_id', '=', 4873)]).mapped('litre'))

                if diesel_issued:
                    worksheet.merge_range('C%s:D%s' % (new_row, new_row), "Pump :  %s  " % (pump.name), regular)
                    worksheet.write('E%s' % (new_row), diesel_issued, regular)
                    total_pump += diesel_issued
                    new_row += 1

            worksheet.merge_range('C%s:D%s' % (new_row, new_row), "Petrol Receipt from Pump", bold)
            new_row += 1

            for pump in vehicle_pump:
                diesel_issued = sum(self.env['diesel.pump.line'].search(
                    [('date', '=', rec.from_date), ('diesel_pump', '=', pump.id),
                     ('fuel_product_id', '=', 4874)]).mapped('litre'))

                if diesel_issued:
                    worksheet.merge_range('C%s:D%s' % (new_row, new_row), "Pump : %s " % (pump.name), regular)
                    worksheet.write('E%s' % (new_row), diesel_issued, regular)
                    total_pump += diesel_issued
                    new_row += 1

            worksheet.write('E%s' % (new_row), total_pump, regular)
                # worksheet.write('R%s' % (new_row), driver.remark, regular)


BillReportXlsx('report.equipment_fuel_details_report.xlsx', 'maintanance.report')






