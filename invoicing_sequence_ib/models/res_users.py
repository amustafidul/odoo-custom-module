from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime

class ResUsers(models.Model):
    _inherit = 'res.users'

    code_branch = fields.Char('Code Branch', store=True)

    def write(self, vals_list):
        res = super().write(vals_list)
        vals_list['code_branch'] = vals_list.get('code_branch')
        return res