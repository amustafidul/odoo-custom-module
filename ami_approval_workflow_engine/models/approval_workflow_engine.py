from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

from pkg_resources import require


class ApprovalWorkflow(models.Model):
    _name = 'approval.workflow'
    _description = 'Approval Workflow'

    name = fields.Char(string='Workflow Name', required=True)
    res_model = fields.Many2one('ir.model', string='Model', ondelete='cascade', required=True)
    line_ids = fields.One2many('approval.workflow.line', 'workflow_id', string='Approval Lines')
    approval_type = fields.Selection([
        ('nominal', 'Rentang Nominal'),
        ('non_nominal', 'Non Nominal')
    ], string="Jenis Approval", required=True, default='non_nominal')
    status = fields.Char(string='Approval Statuses', required=True,
                         help="Input up to 3 statuses separated by commas. Only A-Z and spaces are allowed.")
    synced = fields.Boolean(string='Synced to Model', default=False)
    is_nominal = fields.Boolean('is Nominal?', compute='_compute_is_nominal')

    @api.depends('approval_type')
    def _compute_is_nominal(self):
        for rec in self:
            if rec.approval_type == 'nominal':
                rec.is_nominal = True
            else:
                rec.is_nominal = False

    @api.constrains('status')
    def _check_status(self):
        for record in self:
            if record.status:
                # Pisahkan status berdasarkan koma
                status_list = [status.strip() for status in record.status.split(',')]

                # Cek jika lebih dari 3 status
                if len(status_list) > 3:
                    raise ValidationError(_("You can only input up to 3 statuses separated by commas."))

                # Validasi karakter hanya boleh huruf A-Z dan spasi
                for status in status_list:
                    if not re.match(r'^[A-Za-z ]+$', status):
                        raise ValidationError(_("Status can only contain letters A-Z and spaces: '%s'" % status))

    def sync_to_model(self):
        # Step 1: Get the target model object and model ID
        model_obj = self.env[self.res_model.model].sudo()
        model_record = self.env['ir.model'].sudo().search([('model', '=', model_obj._name)], limit=1)
        if not model_record:
            raise ValueError(f"Model {model_obj._name} not found in ir.model")

        # Step 2: Create dynamic model line (e.g., x_hr_employee_line)
        line_model_name = f'x_{model_obj._name.replace(".", "_")}_line'
        line_model_description = f'{model_obj._description} Line'

        # Check if the dynamic line model already exists
        line_model_record = self.env['ir.model'].sudo().search([('model', '=', line_model_name)], limit=1)
        if not line_model_record:
            # Create the dynamic model
            line_model_record = self.env['ir.model'].sudo().create({
                'name': line_model_description,
                'model': line_model_name
            })

            # Create Many2one field in the line model pointing to the target model
            if not self.env['ir.model.fields'].sudo().search(
                    [('model', '=', line_model_name), ('name', '=', f'x_{model_obj._name.replace(".", "_")}_id')],
                    limit=1):
                self.env['ir.model.fields'].sudo().create({
                    'model_id': line_model_record.id,
                    'name': f'x_{model_obj._name.replace(".", "_")}_id',  # Field pointing to target model
                    'field_description': f'{model_obj._description} Reference',
                    'ttype': 'many2one',
                    'relation': model_obj._name,  # Relation to target model (e.g., hr.employee)
                    'state': 'manual',
                })

            # Create other fields (sequence, approver_id) in the line model
            if not self.env['ir.model.fields'].sudo().search(
                    [('model', '=', line_model_name), ('name', '=', 'x_sequence')], limit=1):
                self.env['ir.model.fields'].sudo().create({
                    'model_id': line_model_record.id,
                    'name': 'x_sequence',
                    'field_description': 'Approval Sequence',
                    'ttype': 'integer',
                    'state': 'manual',
                })
            if not self.env['ir.model.fields'].sudo().search(
                    [('model', '=', line_model_name), ('name', '=', 'x_approver_id')], limit=1):
                self.env['ir.model.fields'].sudo().create({
                    'model_id': line_model_record.id,
                    'name': 'x_approver_id',
                    'field_description': 'Approver',
                    'ttype': 'many2one',
                    'relation': 'res.users',
                    'state': 'manual',
                })

        # Step 3: Add conditional fields for 'nominal' approval type
        if self.approval_type == 'nominal':
            # Create x_min_nominal and x_max_nominal fields only if approval type is 'nominal'
            if not self.env['ir.model.fields'].sudo().search(
                    [('model', '=', line_model_name), ('name', '=', 'x_min_nominal')], limit=1):
                self.env['ir.model.fields'].sudo().create({
                    'model_id': line_model_record.id,
                    'name': 'x_min_nominal',
                    'field_description': 'Minimum Nominal',
                    'ttype': 'float',
                    'state': 'manual',
                })
            if not self.env['ir.model.fields'].sudo().search(
                    [('model', '=', line_model_name), ('name', '=', 'x_max_nominal')], limit=1):
                self.env['ir.model.fields'].sudo().create({
                    'model_id': line_model_record.id,
                    'name': 'x_max_nominal',
                    'field_description': 'Maximum Nominal',
                    'ttype': 'float',
                    'state': 'manual',
                })

        # Step 4: Add One2many field to the target model
        if not self.env['ir.model.fields'].sudo().search(
                [('model', '=', model_obj._name), ('name', '=', f'x_{line_model_name}_ids')], limit=1):
            self.env['ir.model.fields'].sudo().create({
                'model_id': model_record.id,
                'name': f'x_{line_model_name}_ids',  # One2many field in target model
                'field_description': f'{line_model_description}',
                'ttype': 'one2many',
                'relation': line_model_name,
                'relation_field': f'x_{model_obj._name.replace(".", "_")}_id',  # Link to target model field
                'state': 'manual',
            })

        # Step 5: Use custom status from workflow field
        status_selection = []
        if self.status:
            status_list = [status.strip() for status in self.status.split(',')]
            status_selection = [(status, status.capitalize()) for status in status_list]

        # Check if x_approval_status field already exists, if not create it
        if not self.env['ir.model.fields'].sudo().search(
                [('model', '=', model_obj._name), ('name', '=', 'x_approval_status')], limit=1):
            self.env['ir.model.fields'].sudo().create({
                'model_id': model_record.id,
                'name': 'x_approval_status',  # Status field in target model
                'field_description': 'Approval Status',
                'ttype': 'selection',
                'selection': status_selection,
                'state': 'manual',
            })

        # Step 6: Reload registry and cache to ensure fields are recognized
        self.env.registry.setup_models(self.env.cr)

        # Step 7: Define the tree view for the dynamic line model
        tree_view_arch = f"""
            <tree>
                <field name="x_sequence"/>
                <field name="x_approver_id"/>
        """
        if self.approval_type == 'nominal':
            tree_view_arch += """
                <field name="x_min_nominal"/>
                <field name="x_max_nominal"/>
            """
        tree_view_arch += "</tree>"

        # Check if the tree view for the line model exists, and if not, create it
        line_view = self.env['ir.ui.view'].sudo().search(
            [('model', '=', line_model_name), ('name', '=', f'{line_model_name}.tree')], limit=1)

        if not line_view:
            self.env['ir.ui.view'].sudo().create({
                'name': f'{line_model_name}.tree',
                'type': 'tree',
                'model': line_model_name,
                'arch_base': tree_view_arch
            })

        # Step 8: Add a new notebook page to the form view of the target model
        form_view = self.env['ir.ui.view'].sudo().search([
            ('model', '=', model_obj._name),
            ('type', '=', 'form')
        ], limit=1)

        if form_view:
            # Inherit the form view and add a notebook page for Approval Workflow
            self.env['ir.ui.view'].sudo().create({
                'name': f'{model_obj._name}.approval.workflow.form.inherit',
                'type': 'form',
                'model': model_obj._name,
                'inherit_id': form_view.id,
                'arch_base': f"""
                    <xpath expr="//notebook" position="inside">
                        <page string="Approval Workflow">
                            <field name="x_{line_model_name}_ids" mode="tree" context="{{'default_x_{model_obj._name.replace('.', '_')}_id': id}}">
                                <tree create="false" delete="false">
                                    <field name="x_sequence"/>
                                    <field name="x_approver_id"/>
                                    {'<field name="x_min_nominal"/><field name="x_max_nominal"/>' if self.approval_type == 'nominal' else ''}
                                </tree>
                            </field>
                        </page>
                    </xpath>
                """
            })

        if form_view:
            self.env['ir.ui.view'].sudo().create({
                'name': f'{model_obj._name}.approval.statusbar.form.inherit',
                'type': 'form',
                'model': model_obj._name,
                'inherit_id': form_view.id,
                'arch_base': f"""
                        <xpath expr="//header" position="inside">
                            <field name="x_approval_status" widget="statusbar"/>
                        </xpath>
                    """
            })

        # Step 9: Get all records from the target model (without limit)
        records = model_obj.sudo().search([])

        if not records:
            raise ValueError(f"No records found in model {model_obj._name}")

        # Step 10: Iterate over all records and add approval lines from line_ids
        for record in records:
            # Clear old data in One2many field
            if record[f'x_{line_model_name}_ids']:
                record.sudo().write({f'x_{line_model_name}_ids': [(5, 0, 0)]})

            # Get line_ids from the approval workflow
            approval_lines = [(0, 0, {
                'x_sequence': line.sequence,
                'x_approver_id': line.approver_id.id,
                f'x_{model_obj._name.replace(".", "_")}_id': record.id,  # Link to target model
                'x_min_nominal': line.min_nominal if self.approval_type == 'nominal' else False,
                'x_max_nominal': line.max_nominal if self.approval_type == 'nominal' else False
            }) for line in self.line_ids]

            first_status = self.status.split(',')[0].strip()

            # Write the One2many field to the target model
            record.sudo().write({'x_approval_status': first_status, f'x_{line_model_name}_ids': approval_lines})

        # Step 11: Set synced to True
        self.sudo().synced = True

        # Step 12: Add access rights dynamically for the line model
        self.env['ir.model.access'].sudo().create({
            'name': f'Access {line_model_name}',
            'model_id': line_model_record.id,
            'group_id': self.env.ref('base.group_user').id,  # Grant access to regular users
            'perm_read': True,
            'perm_write': True,
            'perm_create': True,
            'perm_unlink': True,
        })


    def remove_sync(self):
        model_obj = self.env[self.res_model.model].sudo()

        # Step 1: Direct SQL query to remove the dynamically added fields from the database table
        table_name = model_obj._table

        # SQL queries to remove columns directly
        self.env.cr.execute(f'ALTER TABLE {table_name} DROP COLUMN IF EXISTS approval_sequence CASCADE;')
        self.env.cr.execute(f'ALTER TABLE {table_name} DROP COLUMN IF EXISTS approval_approver_id CASCADE;')
        self.env.cr.execute(f'ALTER TABLE {table_name} DROP COLUMN IF EXISTS approval_workflow_line_ids CASCADE;')
        self.env.cr.execute(
            f'ALTER TABLE {table_name} DROP COLUMN IF EXISTS x_approval_status CASCADE;')  # Remove approval status

        # If the approval type is 'nominal', also remove the min_nominal and max_nominal fields
        if self.approval_type == 'nominal':
            self.env.cr.execute(f'ALTER TABLE {table_name} DROP COLUMN IF EXISTS x_min_nominal CASCADE;')
            self.env.cr.execute(f'ALTER TABLE {table_name} DROP COLUMN IF EXISTS x_max_nominal CASCADE;')

        # Step 2: Remove any views that reference these fields
        views_to_delete = self.env['ir.ui.view'].sudo().search([
            ('model', '=', model_obj._name),
            ('name', 'ilike', f'{model_obj._name}.approval.workflow%')
        ])
        views_to_delete.unlink()

        # Remove the view that added the statusbar for the approval status
        status_view_to_delete = self.env['ir.ui.view'].sudo().search([
            ('model', '=', model_obj._name),
            ('name', '=', f'{model_obj._name}.approval.statusbar.form.inherit')
        ])
        if status_view_to_delete:
            status_view_to_delete.unlink()

        # Step 3: Remove the x_approval_status field from ir.model.fields
        field_to_delete = self.env['ir.model.fields'].sudo().search([
            ('model', '=', model_obj._name),
            ('name', '=', 'x_approval_status')
        ])
        if field_to_delete:
            field_to_delete.unlink()

        # If the approval type is 'nominal', also remove the x_min_nominal and x_max_nominal fields from ir.model.fields
        if self.approval_type == 'nominal':
            min_nominal_field = self.env['ir.model.fields'].sudo().search([
                ('model', '=', model_obj._name),
                ('name', '=', 'x_min_nominal')
            ])
            if min_nominal_field:
                min_nominal_field.unlink()

            max_nominal_field = self.env['ir.model.fields'].sudo().search([
                ('model', '=', model_obj._name),
                ('name', '=', 'x_max_nominal')
            ])
            if max_nominal_field:
                max_nominal_field.unlink()

        # Step 4: Clear caches related to the model and view
        self.clear_caches()
        self.env['ir.ui.view'].sudo().clear_caches()

        # Step 5: Reload the registry completely to ensure all cache is refreshed
        self.env.registry.setup_models(self.env.cr)

        # Step 6: Reload the model to ensure the model is reloaded after field removal
        model_obj._setup_fields()

        # Finally, set synced to False to indicate the sync has been removed
        self.sudo().synced = False


class ApprovalWorkflowLine(models.Model):
    _name = 'approval.workflow.line'
    _description = 'Approval Workflow Line'

    workflow_id = fields.Many2one('approval.workflow', string='Workflow', required=True)
    sequence = fields.Integer(string='Sequence', required=True)
    approver_id = fields.Many2one('res.users', string='Approver', required=True)
    min_nominal = fields.Float(string='Nominal Minimum')
    max_nominal = fields.Float(string='Nominal Maksimum')
    x_approval_sequence = fields.Integer(string='Approval Sequence')
    x_approval_approver_id = fields.Many2one('res.users', string='Approver')
    is_nominal = fields.Boolean(string='Is Nominal Approval', compute='_compute_is_nominal')

    _sql_constraints = [
        ('unique_sequence', 'unique(workflow_id, sequence)', 'The sequence must be unique per workflow!')
    ]

    @api.onchange('workflow_id')
    def _onchange_workflow_type(self):
        if self.workflow_id.approval_type == 'nominal':
            # Jika jenis approval adalah nominal, tampilkan field rentang nominal
            self.min_nominal = 0
            self.max_nominal = 0
        else:
            # Jika bukan nominal, sembunyikan field rentang nominal
            self.min_nominal = False
            self.max_nominal = False

    @api.depends('workflow_id.is_nominal')
    def _compute_is_nominal(self):
        for line in self:
            line.is_nominal = line.workflow_id.is_nominal