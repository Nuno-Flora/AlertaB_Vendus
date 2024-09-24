from odoo import api, fields, models, _
from odoo.exceptions import UserError
import base64
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict, Any

class SaftImportWizard(models.TransientModel):
    """
    This is a wizard to import SAF-T files into Odoo.

    It will allow the user to upload a SAF-T file and then import the data from the file
    into Odoo. The wizard will handle the import process, including parsing the XML file,
    preparing the data, and then importing it into Odoo.
    """
    _name = 'account.saft.import.wizard'
    _description = 'SAF-T Import Wizard'

    company_id: models.Many2one = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    attachment_id: Optional[bytes] = fields.Binary(string='SAF-T File', required=True)
    attachment_name: Optional[str] = fields.Char(string='File Name')

    def _get_account_types(self) -> Dict[str, str]:
        if self.company_id.country_code != 'PT':
            return super()._get_account_types()
        return {
            '101': 'asset_fixed',
            '102': 'asset_current',
            '201': 'liability_non_current',
            '202': 'liability_current',
            '301': 'equity',
            '401': 'income',
            '501': 'expense',
        }
    def _get_cleaned_namespace(self, tree: ET.ElementTree) -> Dict[str, str]:
        """
        Clean up namespace for easier parsing

        This method is used to clean up the namespace of the SAF-T XML file to make it easier
        to parse. It removes any unnecessary namespaces and replaces them with the 'saft'
        namespace.
        """
        print("Getting cleaned namespace")
        nsmap = {k: v for k, v in tree.nsmap.items() if k}
        if None in tree.nsmap:
            nsmap['saft'] = tree.nsmap[None]
        return nsmap

    def _prepare_account_data(self, tree: ET.ElementTree) -> ET.ElementTree:
        """
        Adjust for Portuguese SAF-T

        This method is used to adjust the XML data for Portuguese SAF-T. It replaces the
        'GeneralLedgerAccounts' node with 'StandardAccountID' to make it easier to parse.
        """
        if self.company_id.country_code == 'PT':
            nsmap = self._get_cleaned_namespace(tree)
            account_id_nodes = tree.findall('.//saft:GeneralLedgerAccounts', nsmap)
            for account_id_node in account_id_nodes:
                account_id_node.tag = account_id_node.tag.replace('GeneralLedgerAccounts', 'StandardAccountID')

        return tree

    def _prepare_partner_data(self, tree: ET.ElementTree) -> ET.ElementTree:
        """
        Handle partner-specific data in Portuguese SAF-T

        This method is used to handle partner-specific data in Portuguese SAF-T. It removes
        any nodes with the 'CustomerID' node that have 'N/A' as their value.
        """
        if self.company_id.country_code == 'PT':
            nsmap = self._get_cleaned_namespace(tree)
            partner_id_nodes = tree.findall('.//saft:CustomerID', nsmap)
            for partner_id_node in partner_id_nodes:
                if partner_id_node.text == 'N/A':
                    partner_id_node.getparent().remove(partner_id_node)

        return tree

    def _prepare_move_data(self, journal_tree: ET.ElementTree, default_currency: str, journal_id_saft: str, journal_id: int, map_accounts: Dict[str, int], map_taxes: Dict[str, int], map_currencies: Dict[str, int], map_partners: Dict[str, int]) -> Dict[str, Any]:
        """
        Adjust journal move data for Portuguese SAF-T

        This method is used to adjust the journal move data for Portuguese SAF-T. It takes
        the journal tree, default currency, journal ID from the SAF-T file, journal ID from
        Odoo, and the mappings for accounts, taxes, currencies, and partners as arguments.

        It should return a dictionary with the following keys:
        - journal_id: The ID of the journal in Odoo
        - date: The date of the move
        - ref: The reference of the move
        - line_ids: A list of move lines

        The method should be implemented to extract the necessary data from the SAF-T file
        and prepare the move data accordingly.
        """
        if self.company_id.country_code == 'PT':
            nsmap = self._get_cleaned_namespace(journal_tree)
            journal_tree = journal_tree.find('.//saft:Journal', nsmap)

        # Extract the date and reference from the SAF-T file
        date = journal_tree.find('saft:Date', nsmap).text
        ref = journal_tree.find('saft:Reference', nsmap).text

        # Extract the move lines from the SAF-T file
        move_lines: List[Dict[str, Any]] = []
        for journal_entry in journal_tree.findall('saft:JournalEntry', nsmap):
            debit_account_id = map_accounts[journal_entry.find('saft:DebitAccount', nsmap).text]
            credit_account_id = map_accounts[journal_entry.find('saft:CreditAccount', nsmap).text]
            debit_amount = float(journal_entry.find('saft:DebitAmount', nsmap).text)
            credit_amount = float(journal_entry.find('saft:CreditAmount', nsmap).text)
            currency_id = map_currencies[journal_entry.find('saft:Currency', nsmap).text]
            partner_id = map_partners[journal_entry.find('saft:CustomerID', nsmap).text]
            move_lines.append((0, 0, {
                'account_id': debit_account_id,
                'partner_id': partner_id,
                'debit': debit_amount,
                'credit': credit_amount,
                'currency_id': currency_id,
            }))

        print("Preparing move data")
        return {
            'journal_id': journal_id,
            'date': date,
            'ref': ref,
            'line_ids': move_lines,
        }

    def import_file(self) -> Dict[str, str]:
        """
        Import the SAF-T file

        This method is used to import the SAF-T file into Odoo. It takes the SAF-T file as
        input and then processes it to extract the necessary data to import into Odoo.

        The method should return a dictionary with the following keys:
        - type: The type of the action to perform after the import (e.g. 'ir.actions.act_window_close')
        """
        self.ensure_one()
        if not self.attachment_id:
            raise UserError(_("Please upload a SAF-T file."))

        try:
            saft_file: bytes = base64.b64decode(self.attachment_id)
            tree: ET.ElementTree = ET.fromstring(saft_file)
        except Exception as e:
            raise UserError(_("Invalid file format. Please upload a valid SAF-T XML file."))

        # Process the SAF-T file
        tree = self._prepare_account_data(tree)
        tree = self._prepare_partner_data(tree)

        # Import accounts
        account_types: Dict[str, str] = self._get_account_types()
        map_accounts: Dict[str, int] = {}
        for account in tree.findall('.//saft:StandardAccountID', self._get_cleaned_namespace(tree)):
            account_id = int(account.text)
            account_type = account_types[account_type]
            account_odoo_id = self.env['account.account'].create({
                'name': account_id,
                'code': account_id,
                'user_type_id': self.env.ref('account.data_account_type_' + account_type).id,
                'company_id': self.company_id.id,
            }).id
            map_accounts[account_id] = account_odoo_id

        # Import partners
        map_partners: Dict[str, int] = {}
        for partner in tree.findall('.//saft:Partner', self._get_cleaned_namespace(tree)):
            partner_id = partner.find('saft:CustomerID', self._get_cleaned_namespace(tree)).text
            partner_odoo_id = self.env['res.partner'].create({
                'name': partner_id,
                'company_id': self.company_id.id,
            }).id
            map_partners[partner_id] = partner_odoo_id

        # Import moves
        journals = self.env['account.journal'].search([('company_id', '=', self.company_id.id)])
        map_journals: Dict[str, int] = {}
        for journal in journals:
            journal_id = journal.code
            journal_id_saft = journal.name
            map_journals[journal_id_saft] = journal.id
        for journal in tree.findall('.//saft:Journal', self._get_cleaned_namespace(tree)):
            journal_id_saft = journal.find('saft:JournalID', self._get_cleaned_namespace(tree)).text
            journal_id = map_journals[journal_id_saft]
            move_data = self._prepare_move_data(journal, self.company_id.currency_id.name, journal_id_saft, journal_id, map_accounts, {}, {}, map_partners)
            self.env['account.move'].create(move_data)

        print("Importing move data")
        return {'type': 'ir.actions.act_window_close'}