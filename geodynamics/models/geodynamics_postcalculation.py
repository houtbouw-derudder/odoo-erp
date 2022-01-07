
from odoo import api, fields, models, _, tools

class GeodynamicsPostCalculationLine(models.Model):
    _name = 'geodynamics.postcalculation.line'
    _description = 'Geodynamics Postcalculation line'
    
    postcalculation_id = fields.Many2one('geodynamics.postcalculation', 'Postcalculation', required=True, ondelete='restrict', index=True)
    date = fields.Date(compute='_compute_date',store=True)
    employee_external_id = fields.Char(required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', compute='_compute_employee', store=True)
    task_external_id = fields.Char(required=True)
    task_id = fields.Many2one('projects.task', 'Task', compute='_compute_task', store=True)
    duration = fields.Float(default=0.0)
    km_home_work = fields.Float(default=0.0)
    km_driver = fields.Float(default=0.0)
    km_sigle_driver = fields.Float(default=0.0)
    km_passenger = fields.Float(default=0.0)

    @api.depends('postcalculation_id')
    def _compute_date(self):
        for record in self:
            record.date = record.postcalculation_id.date
    
    @api.depends('task_external_id')
    def _compute_task(self):
        for record in self:
            task_id_from_external = self.env.ref(record.task_external_id).id
            record.task_id = self.env['project.task'].search([task_id_from_external], limit=1)

    @api.depends('employee_external_id')
    def _compute_employee(self):
        for record in self:
            employee_id_from_external = self.env.ref(record.employee.external_id).id
            record.employee_id = self.env['hr.employee'].search([employee_id_from_external], limit=1)

    # datum = pc['Date'].split('T')[0]
    #     werknemer = pc['User']['Name']
    #     taak_id = pc['PostCalculation']['CostCenter']
    #     gewerkte_uren = round(pc['PostCalculation']['Duration'], 2)

    #     mobility = pc['PostCalculation']['Mobility']

    #     km_chauffeur = mobility['KmDriver']
    #     km_chauffeur_alleen = mobility['KmSingleDriver']
    #     km_passagier = mobility['KmPassenger']
    #     km_woon_werk = pc['TimeSheet']['Mobility']['KmHomeWork']


class GeodynamicsPostCalculation(models.Model):
    _name = 'geodynamics.postcalculation'
    _description = 'Geodynamics Postcalculation'
    _rec_name = 'date'

    date = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(selection=[('draft','Draft'),('validated','Validated')], default='draft')

    line_ids = fields.One2many('geodynamics.postcalculation.line', 'postcalculation_id', string="Postcalculation Lines")

    _sql_constraints = [
        ('date_unique', 'unique (date)', 'The date of the postcalculation must be unique !')
    ]

    def action_reload(self):
        pass

    def action_validate(self):
        pass
