from typing import Dict, Optional
from odoo import api, fields, models

class VendusDocument(models.Model):
    """Vendus Document

    This model represents a document in Vendus, which can be an invoice, a receipt,
    a simplified invoice, a credit note, or a debit note. It contains the document
    number, the Vendus ID, the date, the customer, the total amount, the status, and
    the type. The status can be 'draft' or 'final', and the type can be 'FT' (invoice),
    'FR' (receipt), 'FS' (simplified invoice), 'NC' (credit note), or 'ND' (debit note).

    There is a unique constraint on the Vendus ID, so that we can't create two
    documents with the same Vendus ID.

    The create_or_update_from_vendus method creates or updates a document from the
    given data. If the document already exists, it updates it. If not, it creates it.
    The data must contain the document number, the Vendus ID, the date, the customer
    ID, the total amount, the status, and the type. The customer ID is used to find
    the corresponding customer in the vendus.customer model. If the customer is not
    found, the customer_id field is set to False.

    The method returns the created or updated document.
    """

    _name = 'vendus.document'

    name: fields.Char = fields.Char(string='Document Number', required=True)
    vendus_id: fields.Integer = fields.Integer(string='Vendus ID', required=True)
    odoo_invoice_id: fields.Many2one = fields.Many2one(
        'account.move', string='Odoo Invoice')
    date: fields.Date = fields.Date(string='Document Date')
    customer_id: fields.Many2one = fields.Many2one(
        'vendus.customer', string='Customer')
    total_amount: fields.Float = fields.Float(string='Total Amount')
    state: fields.Selection = fields.Selection([
        ('draft', 'Draft'),
        ('final', 'Final'),
        ('canceled', 'Canceled'),
    ], string='Status', default='draft')
    type: fields.Selection = fields.Selection([
        ('FT', 'Invoice'),
        ('FR', 'Receipt'),
        ('FS', 'Simplified Invoice'),
        ('NC', 'Credit Note'),
        ('ND', 'Debit Note'),
    ], string='Document Type')

    l10n_pt_atcud: fields.Char = fields.Char(string='ATCUD')
    l10n_pt_hash: fields.Char = fields.Char(string='Hash')
    
    _sql_constraints = [
        ('vendus_id_uniq', 'unique(vendus_id)', 'Vendus ID must be unique!')
    ]

    @api.model
    def create_or_update_from_vendus(self, vendus_data: Dict[str, str]) -> 'VendusDocument':
        """Create or update a vendus document from the given data.

        Args:
            vendus_data (Dict[str, str]): The data from Vendus.

        Returns:
            VendusDocument: The created or updated document.
        """
        # Find the document in the database
        vendus_document = self.search([('vendus_id', '=', vendus_data['id'])])

        # Find the customer in the database
        customer = self.env['vendus.customer'].search(
            [('vendus_id', '=', vendus_data['customer_id'])])
        
        # Create the values to write to the database
        vals = {
            'name': vendus_data['number'],
            'vendus_id': vendus_data['id'],
            'date': vendus_data['date'],
            'customer_id': customer.id if customer else False,
            'total_amount': vendus_data['total'],
            'state': 'final' if vendus_data['status'] == 'F' else 'draft',
            'type': vendus_data['type'],
        }
        
        # If the document already exists, update it
        if vendus_document:
            vendus_document.write(vals)
        # If not, create it
        else:
            vendus_document = self.create(vals)
        
        # Return the created or updated document
        return vendus_document