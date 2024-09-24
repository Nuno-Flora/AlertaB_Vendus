from typing import Optional, Dict
from odoo import api, fields, models


class VendusInvoice(models.Model):
    """
    Represents an invoice in Vendus.

    This model is used to store and manage invoices from Vendus in Odoo.

    The `create_or_update_from_vendus` method is used to create or update an
    invoice from the given data. If an invoice with the same Vendus ID already
    exists, it is updated. Otherwise, a new invoice is created.

    The `state` field is used to keep track of the invoice's state. The possible
    states are 'draft', 'posted', and 'paid'.

    The `_sql_constraints` list is used to define SQL constraints for the
    model. The only constraint is that the `vendus_id` must be unique.
    """
    _name = 'vendus.invoice'
    _description = 'Vendus Invoice'

    name: fields.Char = fields.Char(
        string='Invoice Number',
        required=True,
        help='The invoice number in Vendus.')
    vendus_id: fields.Char = fields.Char(
        string='Vendus ID',
        required=True,
        help='The ID of the invoice in Vendus.')
    odoo_invoice_id: fields.Many2one = fields.Many2one(
        'account.move',
        string='Odoo Invoice',
        help='The related invoice in Odoo.')
    date: fields.Date = fields.Date(
        string='Invoice Date',
        help='The date of the invoice in Vendus.')
    customer_id: fields.Many2one = fields.Many2one(
        'vendus.customer',
        string='Customer',
        help='The customer who made the purchase.')
    total_amount: fields.Float = fields.Float(
        string='Total Amount',
        help='The total amount of the invoice in Vendus.')
    state: fields.Selection = fields.Selection(
        [
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('paid', 'Paid'),
        ],
        string='Status',
        default='draft',
        help='The state of the invoice in Vendus.')

    _sql_constraints = [
        ('vendus_id_uniq', 'unique(vendus_id)', 'Vendus ID must be unique!')
    ]

    @api.model
    def create_or_update_from_vendus(self, vendus_data: Dict[str, str]) -> Optional['VendusInvoice']:
        """
        Create or update a vendus invoice from the given data.

        Args:
            vendus_data: The data from Vendus.

        Returns:
            The created or updated invoice, or None if no data was provided.
        """
        # Search for an invoice with the same Vendus ID
        vendus_invoice = self.search([('vendus_id', '=', vendus_data['id'])])

        if vendus_invoice:
            # If an invoice with the same Vendus ID already exists, update it
            vendus_invoice.write({
                'name': vendus_data['number'],
                'date': vendus_data['date'],
                'total_amount': vendus_data['total_amount'],
                'state': vendus_data['state'],
            })
        else:
            # If no invoice with the same Vendus ID exists, create a new one
            customer = self.env['vendus.customer'].search([('vendus_id', '=', vendus_data['customer_id'])])
            vendus_invoice = self.create({
                'name': vendus_data['number'],
                'vendus_id': vendus_data['id'],
                'date': vendus_data['date'],
                'customer_id': customer.id if customer else False,
                'total_amount': vendus_data['total_amount'],
                'state': vendus_data['state'],
            })

        return vendus_invoice