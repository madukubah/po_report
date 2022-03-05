{
    'name': 'Purchase Report',
    'category': 'purchase',
    'version': '0.1',
    'summary': 'This module provides Purchase Report.',
    'description': '''This module provides Purchase Report.'''
                   ,
    'depends': ['base', 'purchase'],
    'data': [
        'views/po_report_view.xml',
        'report/purchase_report.xml',
        'report/purchase_temp.xml'
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': False,
}
