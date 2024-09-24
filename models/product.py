from odoo import api, fields, models
from odoo.addons.l10n_pt import models as l10n_pt_models

class VendusProduct(models.Model):
    _name = 'vendus.product'
    _description = 'Vendus Product'

    name = fields.Char(string='Name', required=True)
    vendus_id = fields.Integer(string='Vendus ID', required=True)
    odoo_product_id = fields.Many2one('product.product', string='Odoo Product')
    price = fields.Float(string='Price')
    sku = fields.Char(string='SKU')
    type = fields.Selection([
        ('product', 'Product'),
        ('service', 'Service')
    ], string='Type')
    unit = fields.Char(string='Unit')
    tax_id = fields.Many2one('account.tax', string='Tax')
    
    l10n_pt_saft_product_type = fields.Selection(
        selection=l10n_pt_models.get_saft_product_type_selection,
        string='SAF-T Product Type',
    )
    
    _sql_constraints = [
        ('vendus_id_uniq', 'unique(vendus_id)', 'Vendus ID must be unique!')
    ]

    @api.model
    def create_or_update_from_vendus(self, vendus_data):
        vendus_product = self.search([('vendus_id', '=', vendus_data['id'])])
        vals = {
            'name': vendus_data['title'],
            'vendus_id': vendus_data['id'],
            'price': vendus_data['price'],
            'sku': vendus_data['reference'],
            'type': 'product' if vendus_data['type'] == 'P' else 'service',
            'unit': vendus_data['unit'],
        }
        
        if vendus_product:
            vendus_product.write(vals)
        else:
            vendus_product = self.create(vals)
        
        return vendus_product