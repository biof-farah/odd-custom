from odoo import models, fields

class HmsDepartment(models.Model):
    _name = 'hms.department'
    _description = 'Hospital Department'

    name = fields.Char(string="Department Name", required=True)
    description = fields.Text(string="Description")
    is_opened = fields.Boolean(default=True, required=True)
    capacity = fields.Integer(string="Capacity")
    patient_ids = fields.One2many('hms.patient', 'department_id', string = 'Patients in department')
    doctor_ids = fields.One2many('hms.doctor', 'department_id')

