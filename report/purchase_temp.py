from odoo import api, models


class ReportPurchaseWise(models.AbstractModel):
    _name = 'report.po_report.purchase_report_temp'

    @api.model
    def render_html(self, docids, data=None):
        docargs =  {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'data': data['form'],
            'date': data['date'],
            'is_waiting': data['is_waiting'],
        }
        print "===================docargs",docargs
        return self.env['report'].render('po_report.purchase_report_temp', docargs)
