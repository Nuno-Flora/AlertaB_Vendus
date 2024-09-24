from typing import Optional
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class VendusCustomer(models.Model):
    _name = 'vendus.customer'
    _description = 'Vendus Customer'

    name: fields.Char = fields.Char(string='Name', required=True, index=True)
    vendus_id: fields.Integer = fields.Integer(string='Vendus ID', required=True, index=True)
    odoo_partner_id: fields.Many2one = fields.Many2one('res.partner', string='Odoo Partner', index=True)
    email: fields.Char = fields.Char(string='Email')
    phone: fields.Char = fields.Char(string='Phone')
    vat: fields.Char = fields.Char(string='VAT')
    address: fields.Char = fields.Char(string='Address')
    city: fields.Char = fields.Char(string='City')
    postal_code: fields.Char = fields.Char(string='Postal Code')
    country_id: fields.Many2one = fields.Many2one('res.country', string='Country')
    
    l10n_pt_vat: fields.Char = fields.Char(string='Portuguese VAT')
    
    _sql_constraints = [
        ('vendus_id_uniq', 'unique(vendus_id)', 'Vendus ID must be unique!')
    ]

    @api.model
    def create_or_update_from_vendus(self, vendus_data: dict) -> Optional['VendusCustomer']:
        """Create or update a customer from Vendus data

        Args:
            vendus_data (dict): The data from Vendus.

        Returns:
            Optional[VendusCustomer]: The created or updated customer, or None if no data was provided.
        """
        if not vendus_data:
            return None
        customer = self.env['vendus.customer'].sudo().with_context(active_test=False).search([
            ('vendus_id', '=', vendus_data['id'])
        ], limit=1)
        values = {
            'name': vendus_data['name'],
            'email': vendus_data.get('email'),
            'phone': vendus_data.get('phone'),
            'vat': vendus_data.get('vat'),
            'address': vendus_data.get('address'),
            'city': vendus_data.get('city'),
            'postal_code': vendus_data.get('postal_code'),
        }
        if customer:
            customer.sudo().write(values)
        else:
            customer = self.env['vendus.customer'].sudo().create(values)
        return customer
