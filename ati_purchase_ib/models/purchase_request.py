from odoo import models, fields, api, _

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    product_categ_ids = fields.Many2many('product.category', string='Product Category')
    currency_id = fields.Many2one(related='line_ids.currency_id', string='Currency')

class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    product_categ_ids = fields.Many2many(related='request_id.product_categ_ids', string='Product Category')
