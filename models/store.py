from odoo import api, fields, models

class VendusStore(models.Model):
    _name = 'vendus.store'
    _description = 'Vendus Store'

    vendus_id = fields.Integer(string='Vendus ID', required=True)
    name = fields.Char(string='Name', required=True)
    type = fields.Selection([('store', 'Store'), ('warehouse', 'Warehouse')], string='Type')
    address = fields.Char(string='Address')
    city = fields.Char(string='City')
    postal_code = fields.Char(string='Postal Code')
    country = fields.Char(string='Country')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    status = fields.Selection([('on', 'Active'), ('off', 'Inactive')], string='Status')

    @api.model
    def create_or_update_from_vendus(self, vendus_data):
        store = self.search([('vendus_id', '=', vendus_data['id'])])
        vals = {
            'vendus_id': vendus_data['id'],
            'name': vendus_data['title'],
            'type': vendus_data['type'],
            'address': vendus_data['address'],
            'city': vendus_data['city'],
            'postal_code': vendus_data['postalcode'],
            'country': vendus_data['country'],
            'email': vendus_data['email'],
            'phone': vendus_data['phone'],
            'status': vendus_data['status'],
        }
        if store:
            store.write(vals)
        else:
            store = self.create(vals)
        return store