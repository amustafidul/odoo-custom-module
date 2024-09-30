from odoo import _, api, fields, models
from odoo.exceptions import UserError

class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    def make_purchase_order(self):
        res = super().make_purchase_order()
        for rec in self:
            ctx = dict(rec._context or {})
            pr = rec.env['purchase.request'].browse(ctx.get('active_ids', []))
            for pr_obj in pr:
                for line in pr_obj.line_ids:
                    for po_line in line.purchase_lines:
                        po_line.currency_id = line.currency_id.id
                        po_line.product_uom = line.product_uom_id.id
                        po_line.price_unit = line.estimated_cost
                        for order_id in po_line.order_id:
                            purchase_order = rec.env['purchase.order'].browse(order_id.ids)
                            for po in purchase_order:
                                po.product_categ_ids = pr_obj.product_categ_ids.ids
                                po.department_id = pr_obj.department_id.id
                                if pr_obj.currency_id:
                                    po.currency_id = pr_obj.currency_id.id
                                else:
                                    raise UserError(_('Please set currency on PR Lines!'))
        return res

    @api.model
    def _prepare_purchase_order(self, picking_type, group_id, company, origin):
        res = super()._prepare_purchase_order(picking_type, group_id, company, origin)
        department_id = self.mapped('item_ids').mapped('line_id').mapped('request_id').mapped('department_id')
        if len(department_id) > 1 : department_id = department_id[:1]
        res.update(department_id=department_id.id)
        return res