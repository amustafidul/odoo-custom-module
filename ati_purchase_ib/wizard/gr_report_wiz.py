from odoo import models, fields, api, _

class GrReport(models.TransientModel):
    _name = 'good.receipt.report'
    _description = 'Good Receipt Report'

    date_from = fields.Date(string='Date From', required=True, copy=False, readonly=False)
    date_to = fields.Date(string='Date To', required=True, copy=False, readonly=False)

    def print_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
            },
        }
        return self.env.ref('ati_purchase_ib.report_good_receipt').report_action(self, data=data)