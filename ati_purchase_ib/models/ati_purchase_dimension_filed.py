from odoo import models, fields, api, _

class PurchaseDimensionFiled(models.Model):
    _name = 'purchase.dimension.filed'
    _description = 'Purchase Dimension Filed'

    name = fields.Char(string='Project Name', required=True)
    mother_vessel_name = fields.Char(string='Mother Vessel Name', required=True)
    commenced_loading_port = fields.Many2one('commenced.loading.port', string='Commenced Loading Port', required=True)
    completed_discharge_port = fields.Many2one('completed.discharge.port', string='Completed Discharge Port', required=True)
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)