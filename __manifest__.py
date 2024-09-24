{
    'name': 'AlertaB Vendus',
    'version': '17.0.1.1',
    'category': 'Accounting/Localizations',
    'summary': 'Integrate Vendus with Odoo for Portuguese localization',
    'description': """
        This module integrates Vendus with Odoo, tailored for Portuguese accounting requirements.
        It synchronizes products, customers, and documents between Vendus and Odoo.
    """,
    'author': 'Alertabreviado - Lda',
    'website': 'https://www.alertab.pt/',
    'depends': [
        'base',
        'account',
        'base_vat',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menus.xml',
        'views/document_views.xml',
        'views/customer_views.xml',
        'views/product_views.xml',
        'views/payment_method_views.xml',
        'views/store_views.xml',
        'views/supplier_views.xml',
        'views/room_views.xml',
        'views/table_views.xml',
        'views/sync_views.xml',
        'views/res_config_settings_views.xml',
        'views/dashboard_views.xml',
        'views/saft_import_wizard_views.xml',
        'data/account_tax_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}