from odoo import api, fields, models

class VendusTable(models.Model):
    _name = 'vendus.table'
    _description = 'Vendus Table'

    vendus_id = fields.Integer(string='Vendus ID', required=True)
    name = fields.Char(string='Name', required=True)
    capacity = fields.Integer(string='Capacity')
    status = fields.Selection([('on', 'Active'), ('off', 'Inactive')], string='Status')

    @api.model
    def create_or_update_from_vendus(self, vendus_data):
        table = self.search([('vendus_id', '=', vendus_data['id'])])
        vals = {
            'vendus_id': vendus_data['id'],
            'name': vendus_data['title'],
            'capacity': vendus_data.get('capacity'),
            'status': vendus_data['status'],
        }
        if table:
            table.write(vals)
        else:
            table = self.create(vals)
        return table