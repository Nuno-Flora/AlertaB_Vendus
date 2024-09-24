from typing import Optional

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """Configuration settings for the Vendus integration.

    This model is used to store and manage the configuration settings for the
    Vendus integration. The settings are stored in the ir.config_parameter table
    and are accessed using the config_parameter attribute of the Char field.

    The api_key and api_url fields are used to store the API key and URL of the
    Vendus API. The default value of the api_url field is the production URL of
    the Vendus API, but it can be overridden by setting the
    vendus_integration.api_url parameter in the configuration file.

    The _get_api_key and _get_api_url methods are used to retrieve the values of
    the api_key and api_url fields from the configuration, and the _set_api_key
    and _set_api_url methods are used to set the values of the api_key and api_url
    fields in the configuration.

    The compute and inverse attributes of the api_key and api_url fields are used
    to automatically call the _get_api_key and _get_api_url methods when the
    fields are accessed, and to automatically call the _set_api_key and _set_api_url
    methods when the fields are modified.

    The default value of the api_key field is None, which means that the
    configuration will not be stored in the database until the user saves the
    configuration for the first time.

    The default value of the api_url field is the production URL of the Vendus API,
    which is 'https://www.vendus.pt/ws/'. This means that if the user does not
    specify a value for the api_url field, the production URL will be used by
    default.
    """

    _inherit = 'res.config.settings'

    @api.model
    def _get_api_key(self) -> Optional[str]:
        """Get the Vendus API key from the configuration.

        This method retrieves the value of the api_key field from the
        configuration.

        Returns:
            str: The API key stored in the configuration.
        """
        return self.env['ir.config_parameter'].sudo().get_param(
            'vendus_integration.api_key')

    @api.model
    def _set_api_key(self, value: str) -> None:
        """Set the Vendus API key in the configuration.

        This method sets the value of the api_key field in the configuration.

        Args:
            value (str): The API key to be stored in the configuration.
        """
        self.env['ir.config_parameter'].sudo().set_param(
            'vendus_integration.api_key', value)

    @api.model
    def _get_api_url(self) -> str:
        """Get the Vendus API URL from the configuration.

        This method retrieves the value of the api_url field from the
        configuration.

        Returns:
            str: The API URL stored in the configuration.
        """
        return self.env['ir.config_parameter'].sudo().get_param(
            'vendus_integration.api_url', 'https://www.vendus.pt/ws/')

    @api.model
    def _set_api_url(self, value: str) -> None:
        """Set the Vendus API URL in the configuration.

        This method sets the value of the api_url field in the configuration.

        Args:
            value (str): The API URL to be stored in the configuration.
        """
        self.env['ir.config_parameter'].sudo().set_param(
            'vendus_integration.api_url', value)

    vendus_api_key: Optional[str] = fields.Char(
        string="Vendus API Key",
        config_parameter='vendus_integration.api_key',
        compute='_get_api_key',
        inverse='_set_api_key',
        default=None,
    )
    vendus_api_url: str = fields.Char(
        string="Vendus API URL",
        config_parameter='vendus_integration.api_url',
        default='https://www.vendus.pt/ws/',
        compute='_get_api_url',
        inverse='_set_api_url',
    )
