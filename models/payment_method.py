from typing import Optional, Dict
from odoo import api, fields, models


class VendusPaymentMethod(models.Model):
    """
    Represents a payment method in Vendus.

    Attributes:
        vendus_id (int): The ID of the payment method in Vendus.
        name (str): The name of the payment method.
        change (bool): Whether the payment method allows change.
        type (str): The official type of the payment method.
        status (str): The status of the payment method.
        order (int): The display order of the payment method.
    """
    _name = 'vendus.payment.method'
    _description = 'Vendus Payment Method'

    vendus_id: int = fields.Integer(
        string='Vendus ID',
        required=True,
        help='The unique identifier of the payment method in Vendus.')
    name: str = fields.Char(
        string='Name',
        required=True,
        help='The name of the payment method.')
    change: bool = fields.Boolean(
        string='Allows Change',
        help='Whether the payment method allows change.')
    type: str = fields.Char(
        string='Official Type',
        help='The official type of the payment method.')
    status: str = fields.Selection(
        [('on', 'Active'), ('off', 'Inactive')],
        string='Status',
        help='The status of the payment method.')
    order: int = fields.Integer(
        string='Display Order',
        help='The display order of the payment method.')

    @api.model
    def create_or_update_from_vendus(self, vendus_data: Dict[str, str]) -> Optional['VendusPaymentMethod']:
        """
        Creates or updates a payment method from the given Vendus data.

        Args:
            vendus_data (Dict[str, str]): The data from Vendus.

        Returns:
            Optional[VendusPaymentMethod]: The created or updated payment method, or None if no data was provided.
        """
        # Find the payment method in the database based on the ID from Vendus
        payment_method = self.search([('vendus_id', '=', vendus_data['id'])])

        # Create the values to write to the database
        vals = {
            'vendus_id': vendus_data['id'],  # The ID of the payment method in Vendus
            'name': vendus_data['title'],  # The name of the payment method
            'change': vendus_data['change'] == '1',  # Whether the payment method allows change
            'type': vendus_data['type'],  # The official type of the payment method
            'status': vendus_data['status'],  # The status of the payment method
            'order': vendus_data['order'],  # The display order of the payment method
        }

        # If the payment method already exists, update it
        if payment_method:
            payment_method.write(vals)
        # If not, create it
        else:
            payment_method = self.create(vals)

        # Return the created or updated payment method
        return payment_method
