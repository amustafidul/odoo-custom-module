from odoo import models, fields, api, _
import datetime
import roman
import json

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    department_id = fields.Many2one('hr.department', string='Department', required=False, copy=False, readonly=False)
    product_categ_ids = fields.Many2many('product.category', string='Product Category', required=True, copy=False, readonly=False)
    purchase_dimension_filed_ids = fields.One2many('purchase.dimension.filed', 'purchase_id', string='Purchase Dimension Filed',
                                               copy=False, readonly=False)

    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        # Ensures default picking type and currency are taken from the right company.
        self_comp = self.with_company(company_id)
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))

            # Dapatkan bulan saat ini
            bulan_sekarang = datetime.datetime.now().month
            # Dapatkan tahun saat ini
            tahun_sekarang = datetime.datetime.now().year
            # Konversi bulan ke bentuk romawi
            romawi_bulan = roman.toRoman(bulan_sekarang)
            sequence_seq = self_comp.env['ir.sequence'].next_by_code('purchase.order.custom', sequence_date=seq_date) or '/'
            sequence_seq = sequence_seq.replace("/PO/ARK", "/PO/ARK/%s/%s/%s"
                                                % (self.env['hr.department'].search([('id', '=', vals.get('department_id'))], limit=1).name,
                                                   romawi_bulan, tahun_sekarang))
            vals['name'] = sequence_seq
        res = super(PurchaseOrder, self).create(vals)
        return res

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)

        for order in self:
            if 'department_id' in vals:
                # Dapatkan bulan saat ini
                bulan_sekarang = datetime.datetime.now().month
                # Dapatkan tahun saat ini
                tahun_sekarang = datetime.datetime.now().year
                # Konversi bulan ke bentuk romawi
                romawi_bulan = roman.toRoman(bulan_sekarang)

                # Split string name
                name_parts = order.name.split('/')

                prev_romawi = name_parts[-2]
                prev_tahun = name_parts[-1]

                # Cari indeks tempat "ARK" terletak
                ark_index = name_parts.index("ARK")

                # Sisipkan department_id setelah "ARK"
                name_parts.insert(ark_index + 1, str(
                    self.env['hr.department'].search([('id', '=', vals.get('department_id'))], limit=1).name))

                # Hapus bagian di belakang department_id
                del name_parts[ark_index + 2:]

                # Tambahkan romawi_bulan dan tahun_sekarang
                name_parts.extend([prev_romawi, str(prev_tahun)])

                # Gabungkan kembali string
                new_name = '/'.join(name_parts)

                # Update 'name'
                order.write({'name': new_name})

        return res

    def action_create_invoice(self):
        res = super(PurchaseOrder, self).action_create_invoice()

        purchase = self.env['purchase.order'].browse(self.ids)

        # Set untuk menyimpan referensi ke dimension_filed yang sudah diproses
        processed_dimensions = set()

        for po_obj in purchase:
            for po_line_obj in po_obj.order_line:
                for inv_line in po_line_obj.invoice_lines:
                    inv_line.write({
                        # 'business_name': po_line_obj.business_name,
                        'business_type_id': po_line_obj.business_type_id.id,
                        'account_vessel_id': po_line_obj.account_vessel_id.id,
                        'analytic_distribution': po_line_obj.analytic_distribution,
                        'account_project_id': po_line_obj.account_project_id.id,
                        'mother_vessel_name': po_line_obj.mother_vessel_name,
                        'commenced_loading_port': po_line_obj.commenced_loading_port.id,
                        'completed_discharge_port': po_line_obj.completed_discharge_port.id,
                    })
                for dimension_filed in po_obj.purchase_dimension_filed_ids:
                    # Cek apakah dimension_filed sudah diproses
                    if dimension_filed.id not in processed_dimensions:
                        for move_id in inv_line.move_id:
                            pass

                        # Tandai bahwa dimension_filed sudah diproses
                        processed_dimensions.add(dimension_filed.id)

            for bill in po_obj.invoice_ids:
                bill.department_id = po_obj.department_id.id
                bill.prod_categ_id = po_obj.product_categ_ids.ids
        return res

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    department_id = fields.Many2one('hr.department', string='Department', required=True, copy=False, readonly=False)

    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        # Ensures default picking type and currency are taken from the right company.
        self_comp = self.with_company(company_id)
        if vals.get('name', 'New') == 'New':
            # Dapatkan bulan saat ini
            bulan_sekarang = datetime.datetime.now().month
            # Dapatkan tahun saat ini
            tahun_sekarang = datetime.datetime.now().year
            # Konversi bulan ke bentuk romawi
            romawi_bulan = roman.toRoman(bulan_sekarang)
            sequence_seq = self_comp.env['ir.sequence'].next_by_code('purchase.request.custom') or '/'
            sequence_seq = sequence_seq.replace("/PR/ARK", "/PR/ARK/%s/%s/%s"
                                                % (
                                                self.env['hr.department'].search([('id', '=', vals.get('department_id'))],
                                                                                 limit=1).name,
                                                romawi_bulan, tahun_sekarang))
            vals['name'] = sequence_seq
        res = super(PurchaseRequest, self).create(vals)
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    business_name = fields.Char(string='Business Name')
    business_type_id = fields.Many2one('account.vessel.type', string='Business Name', required=False, copy=False,
                                       readonly=False)
    vessel_name = fields.Char(string='Vessel Name')
    account_vessel_id = fields.Many2one('account.vessel', string='Vessel Name')
    project_name = fields.Char(string='Project Name', required=False, copy=False, readonly=False)
    account_project_id = fields.Many2one('account.project', string='Project Name')
    mother_vessel_name = fields.Char(string='Mother Vessel Name', required=False, copy=False, readonly=False)
    commenced_loading_port = fields.Many2one('commenced.loading.port', string='Commenced Loading Port', required=False,
                                             copy=False, readonly=False)
    completed_discharge_port = fields.Many2one('completed.discharge.port', string='Completed Discharge Port',
                                               required=False, copy=False, readonly=False)
    product_categ_ids = fields.Many2many('product.category', string='Product Category', related='order_id.product_categ_ids')