from odoo import api, fields, models
from datetime import date, datetime, timedelta
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class PurchaseReport(models.TransientModel):
    _name = 'purchase.order.report'

    date = fields.Date('Tanggal', required=True, default=datetime.today())
    is_purchase_paid = fields.Boolean(string="Tagihan Terbayar")
    is_waiting_shipment = fields.Boolean(string="Pesanan Belum Diterima")
    
    @api.multi
    def print_purchase_report(self):
        purchase_references = []
        #####################################################################
        if self.is_purchase_paid and self.is_waiting_shipment :
            purchases = self.env['purchase.order'].search(
                [ 
                    ('date_order', '<=', self.date),
                    ('state', '=', 'purchase'),
                    ('invoice_status', '=', 'invoiced')
                ], 
                order="date_order asc")
            origins = list(map(lambda x: x.name, purchases))

            stock_pickings = self.env['stock.picking'].search(
                [
                    ('origin', 'in', origins),
                    ('state', 'not in', ['done', 'cancel'] ),
                ],
            )
            origins1 = list(map(lambda x: x.origin, stock_pickings))
            states = list(map(lambda x: x.state, stock_pickings))
            purchase_references = origins1
            # return False

        elif (not self.is_purchase_paid) and self.is_waiting_shipment :
            purchases = self.env['purchase.order'].search(
                [ 
                    ('date_order', '<=', self.date),
                    ('state', '=', 'purchase'),
                    ('invoice_status', '=', 'to invoice')
                ], 
                order="date_order asc")
            origins = list(map(lambda x: x.name, purchases))

            stock_pickings = self.env['stock.picking'].search(
                [
                    ('origin', 'in', origins),
                    ('state', 'not in', ['done', 'cancel'] ),
                ],
            )
            origins1 = list(map(lambda x: x.origin, stock_pickings))
            states = list(map(lambda x: x.state, stock_pickings))
            purchase_references = origins1

        elif self.is_purchase_paid and (not self.is_waiting_shipment) :
            purchases = self.env['purchase.order'].search(
                [ 
                    ('date_order', '<=', self.date),
                    ('state', '=', 'purchase'),
                    ('invoice_status', '=', 'invoiced')
                ], 
                order="date_order asc")
            origins = list(map(lambda x: x.name, purchases))

            stock_pickings = self.env['stock.picking'].search(
                [
                    ('origin', 'in', origins),
                    ('state', 'in', ['done'] ),
                ],
            )
            origins1 = list(map(lambda x: x.origin, stock_pickings))
            states = list(map(lambda x: x.state, stock_pickings))
            purchase_references = origins1

        elif (not self.is_purchase_paid) and (not self.is_waiting_shipment) :
            purchases = self.env['purchase.order'].search(
                [ 
                    ('date_order', '<=', self.date),
                    ('state', '=', 'purchase'),
                    ('invoice_status', '=', 'to invoice')
                ], 
                order="date_order asc")
            origins = list(map(lambda x: x.name, purchases))

            stock_pickings = self.env['stock.picking'].search(
                [
                    ('origin', 'in', origins),
                    ('state', 'in', ['done'] ),
                ],
            )
            origins1 = list(map(lambda x: x.origin, stock_pickings))
            states = list(map(lambda x: x.state, stock_pickings))
            purchase_references = origins1

        #####################################################################
        purchases = self.env['purchase.order'].search(
                [ 
                    ('name', 'in', purchase_references)
                ],  
            )
        purchase_data = []
        for purchase in purchases:
            temp = []
            purchase_detail = []
            # bills = self.env['account.invoice'].search(
            #     [
            #         ('origin', '=', purchase.name),
            #         ('state', '!=', 'paid')
            #     ]
            # )
            # if len(bills) == 0:
            for orderline in purchase.order_line:
                # if orderline.product_id.categ_id.name == "Expenses":
                if orderline.product_id.type == "service":
                    continue
                
                detail = []

                detail.append(orderline.product_id.name)    #0 nama produk
                detail.append(orderline.product_qty)        #1 jumlah order
                detail.append(orderline.product_uom.name)   #2 uom
                detail.append(orderline.price_unit)         #3 unit price
                detail.append(orderline.price_subtotal)     #4 total harga

                qty_done = 0
                stock_packs = self.env['stock.pack.operation'].search(
                    [
                        ('picking_id.origin', '=', purchase.name),
                        ('product_id.id', '=', orderline.product_id.id),
                        ('state', 'in', ['assigned', 'done']),
                        ('picking_id.picking_type_code', '=', 'incoming'),
                    ]
                    # ,limit=1
                )
                for stock_pack in stock_packs:
                    qty_done += stock_pack.qty_done
                
                qty_await = 0 if orderline.product_qty-qty_done <= 0 else orderline.product_qty-qty_done 
                qty_done = orderline.product_qty if orderline.price_unit == 0 else qty_done

                detail.append(qty_done)                     #5 jumlah diterima
                detail.append(qty_await)                    #6 jumlah belum qty
                
                if qty_await == 0 and self.is_waiting_shipment:
                    continue
                purchase_detail.append(detail)
            
            if len(purchase_detail) == 0:
                continue

            temp.append(purchase.name)          #0
            temp.append(purchase.date_order)    #1
            temp.append(purchase.picking_type_id.warehouse_id.name) #2
            temp.append(purchase.partner_id.display_name) #3
            temp.append(purchase.amount_total) #4
            if purchase.invoice_status == "to invoice":
                temp.append("Belum Terbayar") #5
            else:
                temp.append("Terbayar") #5
            temp.append(purchase.date_planned) #6
            temp.append(purchase_detail) #7
            
            purchase_data.append(temp)
            
        datas = {
            'ids': self.ids,
            'model': 'purchase.order.report',
            'form': purchase_data,
            'date': self.date,
            'is_waiting': self.is_waiting_shipment,
        }
        return self.env['report'].get_action(self,'po_report.purchase_report_temp', data=datas)
        

    @api.multi
    def print_purchase_report_1(self):
        _logger.warning("print_purchase_report")
        _logger.warning(self.date)
        if self.is_purchase_paid:
            purchases = self.env['purchase.order'].search(
                [ 
                    ('date_order', '>=', "2021-12-12"),
                    ('date_order', '<=', self.date),
                    ('state', '=', 'purchase'),
                    ('invoice_status', '=', 'invoiced')
                ], 
                order="date_order asc")
        else:
            purchases = self.env['purchase.order'].search(
                [ 
                    ('date_order', '>=', "2021-12-12"),
                    ('date_order', '<=', self.date),
                    ('state', '=', 'purchase'),
                    ('invoice_status', '!=', 'invoiced')
                ], 
                order="date_order asc")

        purchase_data = []
        for purchase in purchases:
            temp = []
            purchase_detail = []
            bills = self.env['account.invoice'].search(
                [
                    ('origin', '=', purchase.name),
                    ('state', '!=', 'paid')
                ]
            )
            if len(bills) == 0:
                for orderline in purchase.order_line:
                    # if orderline.product_id.categ_id.name == "Expenses":
                    if orderline.product_id.type == "service":
                        continue
                    
                    detail = []

                    detail.append(orderline.product_id.name)    #0 nama produk
                    detail.append(orderline.product_qty)        #1 jumlah order
                    detail.append(orderline.product_uom.name)   #2 uom
                    detail.append(orderline.price_unit)         #3 unit price
                    detail.append(orderline.price_subtotal)     #4 total harga

                    qty_done = 0
                    stock_packs = self.env['stock.pack.operation'].search(
                        [
                            ('picking_id.origin', '=', purchase.name),
                            ('product_id.id', '=', orderline.product_id.id),
                            ('state', 'in', ['assigned', 'done']),
                            ('picking_id.picking_type_code', '=', 'incoming'),
                        ]
                    )
                    for stock_pack in stock_packs:
                        qty_done += stock_pack.qty_done
                    
                    qty_await = 0 if orderline.product_qty-qty_done <= 0 else orderline.product_qty-qty_done 
                    qty_done = orderline.product_qty if orderline.price_unit == 0 else qty_done

                    detail.append(qty_done)                     #5 jumlah diterima
                    detail.append(qty_await)                    #6 jumlah belum qty
                    
                    if qty_await == 0 and self.is_waiting_shipment:
                        continue
                    purchase_detail.append(detail)
                
                if len(purchase_detail) == 0:
                    continue

                temp.append(purchase.name)          #0
                temp.append(purchase.date_order)    #1
                temp.append(purchase.picking_type_id.warehouse_id.name) #2
                temp.append(purchase.partner_id.display_name) #3
                temp.append(purchase.amount_total) #4
                if purchase.invoice_status == "to invoice":
                    temp.append("Belum Terbayar") #5
                else:
                    temp.append("Terbayar") #5
                temp.append(purchase.date_planned) #6
                temp.append(purchase_detail) #7
                
                purchase_data.append(temp)
            
        datas = {
            'ids': self.ids,
            'model': 'purchase.order.report',
            'form': purchase_data,
            'date': self.date,
            'is_waiting': self.is_waiting_shipment,
        }
        return self.env['report'].get_action(self,'po_report.purchase_report_temp', data=datas)
