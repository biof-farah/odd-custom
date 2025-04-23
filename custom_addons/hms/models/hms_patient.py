from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo import exceptions
import re


class HmsPatient(models.Model):

    _name = 'hms.patient'
    _description = 'Hospital Patient'

    first_name = fields.Char(string="First Name", required =True)
    last_name = fields.Char(string="Last Name", required =True)
    birth_date = fields.Date(string="Birth Date")
    history = fields.Html(string="History")
    cr_ratio = fields.Float(string="CR Ratio")
    blood_type = fields.Selection([ 
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ], string="Blood Type")
    pcr = fields.Boolean(string="PCR")  
    image = fields.Binary(string="Image")
    address = fields.Text(string="Address")
    age = fields.Integer(string="Age", compute="_compute_age", store=True)    
    doctor_ids = fields.Many2many('hms.doctor', string="Doctor")
    department_id = fields.Many2one('hms.department', string="Department")
    email = fields.Char(string="Email", required=True)

    _sql_constraints = [
        ('unique_email', 'unique(email)', 'The email must be unique!')
    ]
    state = fields.Selection([
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious')
    ], string="State", default='undetermined')

    log_history_ids = fields.One2many(
        'hms.patient.history',
        'patient_id',
        string="Status Logs",
        readonly=True
    )
    history_visible = fields.Boolean(
        string="History Visible",
        store=True
    )
    department_capacity = fields.Integer(
        string="Capacity", 
        related='department_id.capacity', 
        readonly=True

    )
    department_available = fields.Boolean(
        String ="Opened",
        related='department_id.is_opened',
        readonly=True
    )

    @api.onchange('department_id')
    def _onchange_department_id(self):
        """Make Doctors field editable when a department is selected."""
        if self.department_id:
            self.doctor_ids = False  # Clear existing doctors
            return {'domain': {'doctor_ids': [('department_id', '=', self.department_id.id)]}}
        else:
            self.doctor_ids = False

    @api.constrains('department_id')
    def _check_department_available(self):
        for record in self:
            if not record.department_available:
                raise models.ValidationError("Department is closed, please choose another department")

    @api.constrains('pcr', 'cr_ratio')
    def _check_pcr_required(self):
        for record in self:
            if record.pcr and not record.cr_ratio:
                raise models.ValidationError("CR Ratio is required when PCR is checked")
            

    @api.constrains('age')
    def _onchange_age(self):
        if self.age > 30 and not self.pcr:
            raise models.ValidationError("for age over 30 -> CR Ratio is required when PCR is checked")

            

    @api.depends('age')
    def _computer_history_visible(self):
        for record in self:
            if record.age >= 50:
                record.history_visible = True
            else:
                record.history_visible = False

    @api.constrains('email')
    def _check_email_format(self):
        if not re.match('(\w+[.|\w])*@(\w+[.])*\w+', self.email):
            raise exceptions.ValidationError("Email not valid")
    
    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = fields.Date.today()
                birth_date = fields.Date.from_string(record.birth_date)
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                record.age = age
            else:
                record.age = 0
    def write(self, vals):

        if 'state' in vals:
            for record in self:

                if record.state != vals['state']:
                    self.env['hms.patient.history'].create({
                        'patient_id': record.id,
                        'date': datetime.now(),
                        'created_by': self.env.user.id,
                        'description': f"State changed from {record.state} to {vals['state']}"
                    })
        return super(HmsPatient, self).write(vals)

class HmsPatientHistory(models.Model):
    _name = 'hms.patient.history'
    _description = 'Hospital Patient History'
    _order = 'date desc' 

    patient_id = fields.Many2one(
        'hms.patient',
        string="Patient", 
        ondelete='cascade',
        required=True,
    )
    date = fields.Datetime(
        required=True,
    )
    created_by = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user,
        string="Changed By"
    )   
    description = fields.Text(string="Description")


