from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import timedelta

class ReminderSertifikat(models.Model):
    _name = 'ati.reminder.sertifikat'
    _description = 'Reminder Sertifikat'

    name = fields.Char(string='Name', default=lambda self: _('New'))
    document_type = fields.Selection([
        ('sertifikat', 'Sertifikat'),
    ], string='Document Type')
    document_type_id = fields.Many2one('ati.doc.type.sertif', string='Document Type')
    document_name = fields.Char(string='Document Name')
    document_number = fields.Char(string='Document Number', related='name')
    sertifikat_number = fields.Char(string='Nomor Sertifikat')
    department_id = fields.Many2one('hr.department', string='Department')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ], string='Status', default='draft')
    is_renewal = fields.Boolean(string='Is Renewal')
    is_renewal_draft = fields.Boolean(string='Is Renewal Draft')
    is_renewal_confirm = fields.Boolean(string='Is Renewal Confirm')
    attachment_files = fields.Binary(string='Upload Files')
    reminder_sertifikat_history_ids = fields.One2many('ati.reminder.sertifikat.history', 'reminder_sertifikat_id', string='Reminder Sertifikat History')

    def action_confirm(self):
        self.state = 'active'

    def action_when_expired(self):
        ati_reminder_sertifikat_obj = self.env['ati.reminder.sertifikat'].search([])
        if ati_reminder_sertifikat_obj:
            for rec in ati_reminder_sertifikat_obj:
                if rec.end_date:
                    if fields.Date.today() >= rec.end_date:
                        # send email notification
                        mail_obj = self.env['mail.mail']
                        body = """
                        Dear %s,<br>
                        <br>
                        Sertifikat anda sudah expired<br>
                        Berikut adalah link untuk melihat detail sertifikat anda:<br>
                        <a href="/web#id=%s&view_type=form&model=ati.reminder.sertifikat&action=0">%s</a><br>
                        <br>
                        Terima kasih.<br>
                        """
                        body = body % (rec.employee_id.name, rec.id, rec.name)
                        values = {
                            'subject': 'Sertifikat Expired',
                            'email_to': rec.employee_id.work_email,
                            'body_html': body,
                            'res_id': rec.id,
                            'model': 'ati.reminder.sertifikat',
                        }
                        mail_obj.create(values)
                        mail_obj.send()

                        rec.state = 'expired'

                        rec.is_renewal = True
                        rec.is_renewal_draft = True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'ati.reminder.sertifikat') or _("New")

        return super().create(vals_list)

    def action_renewal(self):
        self.ensure_one()
        self.is_renewal_draft = False
        self.is_renewal_confirm = True

        def prepare_renewal_history_data():
            return {
                'reminder_sertifikat_id': self.id,
                'name': self.name,
                'document_type_id': self.document_type_id.id,
                'document_number': self.document_number,
                'expiration_date': self.end_date,
                'renewal_date': fields.Date.today(),
                'new_start_date': False,
                'new_end_date': False,
                'state': 'draft',
            }

        self.env['ati.reminder.sertifikat.history'].create(
            prepare_renewal_history_data()
        )

        self.state = 'draft'

    def action_renewal_confirm(self):
        self.ensure_one()
        self.is_renewal = False
        self.is_renewal_draft = False
        self.is_renewal_confirm = False
        self.state = 'active'

        self.env['ati.reminder.sertifikat.history'].search([
            ('reminder_sertifikat_id', '=', self.id),
            ('state', '=', 'draft'),
        ]).write({
            'new_start_date': self.start_date,
            'new_end_date': self.end_date,
            'state': 'active',
        })

class ReminderSertifikatHistory(models.Model):
    _name = 'ati.reminder.sertifikat.history'
    _description = 'Reminder Sertifikat History'

    reminder_sertifikat_id = fields.Many2one('ati.reminder.sertifikat', string='Reminder Sertifikat')
    name = fields.Char(string='Name')
    document_type = fields.Selection([
        ('sertifikat', 'Sertifikat'),
    ], string='Document Type')
    document_type_id = fields.Many2one('ati.doc.type.sertif', string='Document Type')
    document_number = fields.Char(string='Document Number')
    expiration_date = fields.Date(string='Expiration Date')
    renewal_date = fields.Date(string='Renewal Date')
    new_start_date = fields.Date(string='New Start Date')
    new_end_date = fields.Date(string='New End Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ], string='Status')