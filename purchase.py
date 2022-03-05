from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class PurchaseReport(models.TransientModel):
    _name = 'purchase.order.report'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    
    @api.multi
    def print_purchase_report(self):
        purchases = self.env['purchase.order'].search(
            [ 
                ('date_order', '<=', self.end_date),
                ('date_order', '>=', self.start_date),
                ('state', '=', 'purchase'),
                ('invoice_status', '!=', 'no')
            ], 
            order="date_order asc")

        purchase_data = []
        for purchase in purchases:
            temp = []
            purchase_detail = []
            for orderline in purchase.order_line:
                detail = []
                detail.append(purchase.product_id.default_code)
                detail.append(purchase.product_id.name)
                detail.append(orderline.product_qty)
                detail.append(orderline.product_uom.name)
                detail.append(orderline.price_unit)
                detail.append(orderline.taxes_id.name)
                detail.append(purchase.amount_total)
                detail.append(orderline.price_subtotal)
                purchase_detail.append(detail)
            
            temp.append(purchase.name)
            temp.append(purchase.date_order)
            temp.append(purchase.picking_type_id.warehouse_id.name)
            temp.append(purchase.partner_id.display_name)
            temp.append(purchase.amount_total)
            temp.append(purchase_detail)
            
            purchase_data.append(temp)
            
        datas = {
            'ids': self.ids,
            'model': 'purchase.order.report',
            'form': purchase_data,
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env['report'].get_action(self,'po_report.purchase_report_temp', data=datas)
