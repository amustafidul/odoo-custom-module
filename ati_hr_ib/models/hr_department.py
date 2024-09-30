from odoo import models, fields, api, _

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    department_number = fields.Char(string='Department Number', required=False, copy=False, readonly=False)