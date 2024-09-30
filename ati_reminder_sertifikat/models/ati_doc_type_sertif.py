from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import timedelta

class AtiDocTypeSertif(models.Model):
    _name = 'ati.doc.type.sertif'
    _description = 'ATI Document Type Sertifikat'

    name = fields.Char('Document Type')