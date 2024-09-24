import requests
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from typing import Dict, List, Optional

class VendusSync(models.AbstractModel):
    """Abstract model for Vendus synchronization."""

    _name = 'vendus.sync'
    _description = 'Vendus Synchronization'

    @api.model
    def _get_vendus_api_key(self) -> str:
        """Get the Vendus API key from the configuration parameters.

        The API key is used to authenticate requests to the Vendus API.
        """
        return self.env['ir.config_parameter'].sudo().get_param('vendus_integration.api_key')

    @api.model
    def _get_vendus_api_url(self) -> str:
        """Get the Vendus API URL from the configuration parameters.

        The API URL is used to construct the URL for requests to the Vendus API.
        """
        return self.env['ir.config_parameter'].sudo().get_param('vendus_integration.api_url', 'https://www.vendus.pt/ws/v1.1/')

    def _make_api_request(
        self,
        endpoint: str,
        method: str = 'GET',
        params: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Make a request to the Vendus API.

        Args:
            endpoint: The endpoint to make the request to.
            method: The HTTP method to use (GET, POST, PUT, DELETE). Defaults to GET.
            params: The URL parameters to pass.
            data: The JSON data to send in the request body.
            headers: The headers to send with the request.

        Returns:
            The JSON response from the API.

        Raises:
            UserError: If the API request fails.
        """
        api_key = self._get_vendus_api_key()
        api_url = self._get_vendus_api_url()

        if not api_key:
            raise UserError(_('Vendus API key is not configured.'))

        headers = headers or {}
        headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

        url = f"{api_url}{endpoint}"
        params = params or {}
        params['api_key'] = api_key

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                json=data
            )

            # Handle errors
            if response.status_code == 400:
                raise ValidationError(_('Bad Request: Could not parse request'))
            elif response.status_code == 401:
                raise UserError(_('Unauthorized: Authentication failed'))
            elif response.status_code == 403:
                raise UserError(_('Forbidden: Authenticated user does not have access'))
            elif response.status_code == 404:
                raise ValidationError(_('Not Found: Resource not found'))
            elif response.status_code == 415:
                raise ValidationError(_('Unsupported Media Type: Invalid content-type header'))
            elif response.status_code == 422:
                raise ValidationError(_('Unprocessable Entry: Validation error occurred'))
            elif response.status_code == 429:
                raise UserError(_('Too Many Requests: Request rejected due to rate limiting'))
            elif response.status_code >= 500:
                raise UserError(_('Internal Server Error: An unexpected error occurred'))

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise UserError(_(f'Error communicating with Vendus API: {str(e)}'))

    @api.model
    def sync_products(
        self,
        page: int = 1,
        per_page: int = 20,
        sort: Optional[str] = None,
    ) -> None:
        """Sync products from Vendus.

        Args:
            page: The page of results to retrieve. Defaults to 1.
            per_page: The number of results to retrieve per page. Defaults to 20.
            sort: The sort order. Defaults to None.
        """
        params = {
            'page': page,
            'per_page': per_page,
        }
        if sort:
            params['sort'] = sort

        products_data = self._make_api_request('products', params=params)
        for product_data in products_data.get('products', []):
            self.env['vendus.product'].create_or_update_from_vendus(product_data)

    @api.model
    def sync_customers(
        self,
        page: int = 1,
        per_page: int = 20,
        sort: Optional[str] = None,
    ) -> None:
        """Sync customers from Vendus.

        Args:
            page: The page of results to retrieve. Defaults to 1.
            per_page: The number of results to retrieve per page. Defaults to 20.
            sort: The sort order. Defaults to None.
        """
        params = {
            'page': page,
            'per_page': per_page,
        }
        if sort:
            params['sort'] = sort

        customers_data = self._make_api_request('customers', params=params)
        for customer_data in customers_data.get('customers', []):
            self.env['vendus.customer'].create_or_update_from_vendus(customer_data)

    @api.model
    def sync_documents(
        self,
        page: int = 1,
        per_page: int = 20,
        sort: Optional[str] = None,
    ) -> None:
        """Sync documents from Vendus.

        Args:
            page: The page of results to retrieve. Defaults to 1.
            per_page: The number of results to retrieve per page. Defaults to 20.
            sort: The sort order. Defaults to None.
        """
        params = {
            'page': page,
            'per_page': per_page,
        }
        if sort:
            params['sort'] = sort

        documents_data = self._make_api_request('documents', params=params)
        for document_data in documents_data.get('documents', []):
            self.env['vendus.document'].create_or_update_from_vendus(document_data)

    @api.model
    def sync_payment_methods(self) -> None:
        """Sync payment methods from Vendus."""
        payment_methods = self._make_api_request('documents/paymentmethods/')
        for payment_method in payment_methods:
            self.env['vendus.payment.method'].create_or_update_from_vendus(payment_method)

    @api.model
    def sync_document_types(self) -> None:
        """Sync document types from Vendus."""
        document_types = self._make_api_request('documents/types/')
        # Process and store document types

    @api.model
    def sync_stores(self) -> None:
        """Sync stores from Vendus."""
        stores_data = self._make_api_request('stores')
        for store_data in stores_data:
            self.env['vendus.store'].create_or_update_from_vendus(store_data)

    @api.model
    def sync_suppliers(self) -> None:
        """Sync suppliers from Vendus."""
        suppliers_data = self._make_api_request('suppliers')
        for supplier_data in suppliers_data:
            self.env['vendus.supplier'].create_or_update_from_vendus(supplier_data)

    @api.model
    def sync_rooms(self) -> None:
        """Sync rooms from Vendus."""
        rooms_data = self._make_api_request('rooms')
        for room_data in rooms_data:
            self.env['vendus.room'].create_or_update_from_vendus(room_data)

    @api.model
    def sync_tables(self) -> None:
        """Sync tables from Vendus."""
        tables_data = self._make_api_request('tables')
        for table_data in tables_data:
            self.env['vendus.table'].create_or_update_from_vendus(table_data)

    @api.model
    def sync_all(self) -> None:
        """Sync all Vendus data."""
        self.sync_products()
        self.sync_customers()
        self.sync_documents()
        self.sync_payment_methods()
        self.sync_document_types()
        self.sync_stores()
        self.sync_suppliers()
        self.sync_rooms()
        self.sync_tables()