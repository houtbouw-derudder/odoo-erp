
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError


class GeodynamicsPostCalculationLine(models.Model):
    _name = 'geodynamics.postcalculation.line'
    _description = 'Geodynamics Postcalculation line'

    postcalculation_id = fields.Many2one(
        'geodynamics.postcalculation', 'Postcalculation', required=True, ondelete='cascade', index=True)
    date = fields.Date(compute='_compute_date', store=True)
    state = fields.Selection(related='postcalculation_id.state')
    employee_external_id = fields.Char(required=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee', compute='_compute_employee', store=True)
    task_external_id = fields.Char(required=True)
    task_id = fields.Many2one('project.task', 'Task',
                              compute='_compute_task', store=True)
    project_id = fields.Many2one(
        'project.project', 'Project', related="task_id.project_id", store=True)
    direct_work_time = fields.Float(default=0.0)
    indirect_work_time = fields.Float(default=0.0)
    indirect_travel_time = fields.Float(default=0.0)
    km_home_work = fields.Float(default=0.0)
    km_driver = fields.Float(default=0.0)
    km_single_driver = fields.Float(default=0.0)
    km_passenger = fields.Float(default=0.0)

    analytic_account_line_ids = fields.One2many(
        'account.analytic.line', 'postcalculation_line_id', string="Analytic Account Lines")

    @api.depends('postcalculation_id')
    def _compute_date(self):
        for record in self:
            record.date = record.postcalculation_id.date

    @api.depends('task_external_id')
    def _compute_task(self):
        for record in self:
            if record.task_external_id:
                try:
                    task_id_from_external = self.env.ref(
                        record.task_external_id).id
                    record.task_id = self.env['project.task'].search(
                        [('id', '=', task_id_from_external)], limit=1)
                except:
                    record.task_id = False
            else:
                record.task_id = False

    @api.depends('employee_external_id')
    def _compute_employee(self):
        for record in self:
            if record.employee_external_id:
                try:
                    employee_id_from_external = self.env.ref(
                        record.employee_external_id).id
                    record.employee_id = self.env['hr.employee'].search(
                        [('id', '=', employee_id_from_external)], limit=1)
                except:
                    record.employee_id = False
            else:
                record.employee_id = False

    def _compute_analytic_account_lines(self):
        for r in self:
            r.analytic_account_line_ids.unlink()
            analytic_account_line_vals = []
            analytic_account_line_vals.append({
                'task_id': r.task_id.id,
                'employee_id': r.employee_id.id,
                'date': r.date,
                'unit_amount': (r.direct_work_time + r.indirect_work_time),
                'name': _('Direct and indirect work time')
            })

            r.analytic_account_line_ids = self.env['account.analytic.line'].create(analytic_account_line_vals)


    def _reset(self):
        for r in self:
            r.analytic_account_line_ids.unlink()


class GeodynamicsPostCalculation(models.Model):
    _name = 'geodynamics.postcalculation'
    _description = 'Geodynamics Postcalculation'
    _rec_name = 'date'
    _inherit = ['mail.thread']

    date = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('validated', 'Validated')], default='draft')

    line_ids = fields.One2many('geodynamics.postcalculation.line',
                               'postcalculation_id', string="Postcalculation Lines")

    _sql_constraints = [
        ('date_unique', 'unique (date)',
         'The date of the postcalculation must be unique !')
    ]

    def _extract_postcalculation_line_data(self, data):
        return {
            'postcalculation_id': self.id,
            'employee_external_id': data['User']['Code'],
            'task_external_id': data['PostCalculation']['CostCenter'],
            'direct_work_time': data['PostCalculation']['Details']['DirectAssignedWorkTime'],
            'indirect_work_time': data['PostCalculation']['Details']['IndirectAssignedWorkTime'],
            'indirect_travel_time': data['PostCalculation']['Details']['IndirectAssignedMobilityBeforeTime'],
            'km_driver': data['PostCalculation']['Mobility']['KmDriver'],
            'km_single_driver': data['PostCalculation']['Mobility']['KmSingleDriver'],
            'km_passenger': data['PostCalculation']['Mobility']['KmPassenger'],
            'km_home_work': data['PostCalculation']['Mobility']['KmHomeWork']
        }

    def action_reload(self):
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(
                _("Reloading can only be done when state is 'Draft'."))

        self.line_ids.unlink()

        api = self.env['geodynamics.api']
        postcalculation_data = api.load_postcalculation(self.date)

        self.line_ids = self.env['geodynamics.postcalculation.line'].create(
            [self._extract_postcalculation_line_data(pc) for pc in postcalculation_data])

        self.message_post(body=_('<p>Data reload complete</p>'))

    def action_validate(self):
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(
                _("A Postcalculation must be in state draft to be validated."))

        for line in self.line_ids:
            if not line.task_id:
                raise UserError(_("At least one line has an unmapped task."))

            if not line.employee_id:
                raise UserError(
                    _("At least one line has an unmapped employee."))

        for line in self.line_ids:
            line._compute_analytic_account_lines()

        self.state = 'validated'
        self.message_post(body=_("<p>State: Draft -> Validated</p>"))

    def action_reset_to_draft(self):
        self.ensure_one()

        if self.state != 'validated':
            raise UserError(
                _("Reset can only be done when state is 'Validated'"))

        for line in self.line_ids:
            line._reset()

        self.state = 'draft'
        self.message_post(body=_("<p>State: Validated -> Draft</p>"))
