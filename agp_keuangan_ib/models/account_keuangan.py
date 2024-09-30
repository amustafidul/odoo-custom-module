from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class AccountKeuangan(models.Model):
    _name = "account.keuangan"
    _inherits = {'account.move': 'move_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']

    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry', readonly=True, ondelete='cascade',
        check_company=True)