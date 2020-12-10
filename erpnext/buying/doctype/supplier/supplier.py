# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe import msgprint, _
from frappe.model.naming import set_name_by_naming_series
from frappe.contacts.address_and_contact import load_address_and_contact, delete_contact_and_address
from erpnext.utilities.transaction_base import TransactionBase
from erpnext.accounts.party import validate_party_accounts, get_dashboard_info, get_timeline_data # keep this


class Supplier(TransactionBase):
	def get_feed(self):
		return self.supplier_name

	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)
		self.load_dashboard_info()

	def before_save(self):
		if not self.on_hold:
			self.hold_type = ''
			self.release_date = ''
		elif self.on_hold and not self.hold_type:
			self.hold_type = 'All'

	def load_dashboard_info(self):
		info = get_dashboard_info(self.doctype, self.name)
		self.set_onload('dashboard_info', info)

	def autoname(self):
		supp_master_name = frappe.defaults.get_global_default('supp_master_name')
		if supp_master_name == 'Supplier Name':
			self.name = self.supplier_name
		else:
			set_name_by_naming_series(self)
	def on_update(self):
		if not self.naming_series:
			self.naming_series = ''
	def validate_supplier_code(self):
		data = self.supplier_code
		check_if_exst  = frappe.db.sql("SELECT name FROM `tabSupplier` WHERE supplier_code = '%s' "%self.supplier_code)
		if check_if_exst :
			self.supplier_code = data +'-'+ str(self.supplier_name)+'-'+'1'
	def validate(self):
		self.coding_supp()
			
		if frappe.defaults.get_global_default('supp_master_name') == 'Naming Series':
			if not self.naming_series:
				msgprint(_("Series is mandatory"), raise_exception=1)

		validate_party_accounts(self)
	def coding_supp(self):
		if not self.supplier_code and self.supplier_group:
			code_naming = frappe.db.get_single_value('Buying Settings' ,'auto_create_supplier_codes' ) 
			count_supplier = frappe.db.sql("SELECT  count(name) FROM `tabSupplier` ")
			if code_naming and not self.supplier_code:
				check_type = frappe.db.get_single_value('Buying Settings' ,'selet_namig_code_type' ) 
				if check_type == 'Manual Add':
					add_type= frappe.db.get_single_value('Buying Settings' ,'serializer' ) 
					self.supplier_code = 'SUPP' + "-"+str(add_type) +'-'+ str(int(count_supplier[0][0])+1)
				if check_type == 'Add By Group Code':
					group = frappe.get_doc('Supplier Group',self.supplier_group)
					code = group.group_code
					if code :
						self.supplier_code = 'SUPP' + "-"+str(code) +'-'+str(int(count_supplier[0][0])+1)
					else :
						self.supplier_code = 'SUPP' + "-"+str(int(count_supplier[0][0])+1)
			self.validate_supplier_code()
		return self.supplier_code
	def on_trash(self):
		delete_contact_and_address('Supplier', self.name)

	def after_rename(self, olddn, newdn, merge=False):
		if frappe.defaults.get_global_default('supp_master_name') == 'Supplier Name':
			frappe.db.set(self, "supplier_name", newdn)


	def check_coding_status(self):
		return (frappe.db.get_single_value('Buying Settings' ,'auto_create_supplier_codes' ) )