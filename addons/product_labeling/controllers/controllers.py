# -*- coding: utf-8 -*-
# from odoo import http


# class ProductLabeling(http.Controller):
#     @http.route('/product_labeling/product_labeling', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_labeling/product_labeling/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_labeling.listing', {
#             'root': '/product_labeling/product_labeling',
#             'objects': http.request.env['product_labeling.product_labeling'].search([]),
#         })

#     @http.route('/product_labeling/product_labeling/objects/<model("product_labeling.product_labeling"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_labeling.object', {
#             'object': obj
#         })

