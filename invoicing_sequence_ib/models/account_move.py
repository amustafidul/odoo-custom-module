from odoo import models, fields, api, _
from datetime import datetime

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        for rec in res:
            if rec.move_type == 'entry':
                seq_code = 'monthly.move.entry.sequence'
                seq = self.env['ir.sequence'].search([('code', '=', seq_code)], limit=1)
                next_number = '%s/%s/' % (rec.journal_id.code, self.env.user.code_branch) + seq.next_by_code(seq_code)
                next_number = next_number.split('/')
                if str(datetime.today().year) in next_number:
                    next_number[next_number.index(str(datetime.today().year))] = str(datetime.today().year)[-2:]
                    next_number = '/'.join(next_number)

                rec.name = next_number

        return res