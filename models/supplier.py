from odoo import api, fields, models

class VendusSupplier(models.Model):
    _name = 'vendus.supplier'
    _description = 'Vendus Supplier'

    vendus_id = fields.Integer(string='Vendus ID', required=True)
    name = fields.Char(string='Name', required=True)
    contact_name = fields.Char(string='Contact Name')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    address = fields.Char(string='Address')
    city = fields.Char(string='City')
    postal_code = fields.Char(string='Postal Code')
    country = fields.Char(string='Country')

    @api.model
    def create_or_update_from_vendus(self, vendus_data):
        supplier = self.search([('vendus_id', '=', vendus_data['id'])])
        vals = {
            'vendus_id': vendus_data['id'],
            'name': vendus_data['name'],
            'contact_name': vendus_data.get('contact_name'),
            'email': vendus_data.get('email'),
            'phone': vendus_data.get('phone'),
            'address': vendus_data.get('address'),
            'city': vendus_data.get('city'),
            'postal_code': vendus_data.get('postal_code'),
            'country': vendus_data.get('country'),
        }
        if supplier:
            supplier.write(vals)
        else:
            supplier = self.create(vals)
        return supplier