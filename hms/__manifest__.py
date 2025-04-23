{
    'name': 'Hospital Management',
    'version': '1.0',
    'category': '',
    'depends' : ['base'],
    'data' :[
    'security/ir.model.access.csv',
    'data/hms_patient_menu.xml',
    'views/hms_patient_views.xml',
    'views/hms_department_views.xml',
    'views/hms_doctor_views.xml',
    ],
    'installable': True,
    'application': True,
}