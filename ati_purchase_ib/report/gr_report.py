from odoo import models, fields, api, _
from datetime import datetime, timedelta

class GrReport(models.AbstractModel):
    _name = 'report.ati_purchase_ib.report_good_receipt'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Good Receipt Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        docs = self.env['purchase.order'].search([
            ('date_order','>=',date_from),
            ('date_order','<=',date_to),
        ])
        return {
            'doc_ids': docs.ids,
            'doc_model': 'purchase.order',
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
        }

    def generate_xlsx_report(self, workbook, data, lines):
        report_value = self._get_report_values(lines, data)

        sheet = workbook.add_worksheet('Good Receipt Report')
        sheet.set_column('A:A', 14)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 20)
        sheet.set_column('L:L', 20)
        sheet.set_column('M:M', 20)
        sheet.set_column('N:N', 20)
        sheet.set_column('O:O', 20)
        sheet.set_column('P:P', 20)
        sheet.set_column('Q:Q', 20)
        sheet.set_column('R:R', 20)
        sheet.set_column('S:S', 20)
        sheet.set_column('T:T', 20)
        sheet.set_column('U:U', 20)
        sheet.set_column('V:V', 20)
        sheet.set_column('W:W', 20)
        sheet.set_column('X:X', 20)
        sheet.set_column('Y:Y', 20)
        sheet.set_column('Z:Z', 20)
        sheet.set_column('AA:AA', 20)
        sheet.set_column('AB:AB', 20)
        sheet.set_column('AC:AC', 20)
        sheet.set_column('AD:AD', 20)
        sheet.set_column('AE:AE', 20)
        sheet.set_column('AF:AF', 20)
        sheet.set_column('AG:AG', 20)
        sheet.set_column('AH:AH', 20)
        sheet.set_column('AI:AI', 20)
        sheet.set_column('AJ:AJ', 20)
        sheet.set_column('AK:AK', 20)
        sheet.set_column('AL:AL', 20)
        sheet.set_column('AM:AM', 20)
        sheet.set_column('AN:AN', 20)

        sheet.write(0, 0, 'Date From:')
        sheet.write(1, 0, 'Date To:')
        sheet.write(0, 1, report_value.get('date_from'))
        sheet.write(1, 1, report_value.get('date_to'))

        # header column
        sheet.write(3, 0, 'PO Number')
        sheet.write(3, 1, 'Vendor')
        sheet.write(3, 2, 'Order Date')
        sheet.write(3, 3, 'Schedule Date')
        sheet.write(3, 4, 'PO Qty')
        sheet.write(3, 5, 'Unit Price')
        sheet.write(3, 6, 'Subtotal')
        sheet.write(3, 7, 'Received Qty')
        sheet.write(3, 8, 'Received Date')

        row = 4
        for doc in report_value.get('docs'):
            sheet.write(row, 0, doc.name)
            sheet.write(row, 1, doc.partner_id.name)
            sheet.write(row, 2, doc.date_order.strftime(
                        '%d/%m/%Y %H:%M:%S'))
            sheet.write(row, 3, doc.date_planned.strftime(
                        '%d/%m/%Y %H:%M:%S') if doc.date_planned else '-')
            for line in doc.order_line:
                sheet.write(row, 4, line.product_qty)
                sheet.write(row, 5, line.price_unit)
                sheet.write(row, 6, line.price_subtotal)
                for move in line.move_ids:
                    sheet.write(row, 7, move.quantity_done)
                    sheet.write(row, 8, move.picking_id.date_done.strftime(
                        '%d/%m/%Y %H:%M:%S') if move.picking_id.date_done else '-')

            row += 1

