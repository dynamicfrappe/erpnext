# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.controllers.selling_controller import SellingController
from frappe.utils import cint, flt, add_months, today, date_diff, getdate, add_days, cstr, nowdate
from erpnext.accounts.utils import get_account_currency
from erpnext.accounts.party import get_party_account, get_due_date
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request
from erpnext.accounts.doctype.loyalty_program.loyalty_program import validate_loyalty_points
from erpnext.stock.doctype.serial_no.serial_no import get_pos_reserved_serial_nos, get_serial_nos
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice, get_bank_cash_account, update_multi_mode_option
import time
from six import iteritems

class POSInvoice(SalesInvoice):
	def __init__(self, *args, **kwargs):
		super(POSInvoice, self).__init__(*args, **kwargs)



	#create return adjustment 
	def update_values_for_return(self):

		if  self.is_return:
			self.paid_amount             = self.rounded_total or self.grand_total 
			self.payments[0].base_amount = self.rounded_total or self.grand_total 
			self.payments[0].amount = self.rounded_total or self.grand_total

			return "done"


	def get_pos_profile_wahrehouse(self):
		pos_profile = frappe.get_doc("POS Profile" , self.pos_profile)
		if pos_profile.warehouse : 
			whare_house = pos_profile.warehouse
			for i in self.items :
				i.warehouse = whare_house
		if not self.payments[0].mode_of_payment :
				self.payments[0].mode_of_payment= pos_profile.payments[0].mode_of_payment
	def validate(self):
		self.get_pos_profile_wahrehouse()
		if self.is_pos and self.is_return :
			self.update_values_for_return()
		if not cint(self.is_pos):
			frappe.throw(_("POS Invoice should have {} field checked.").format(frappe.bold("Include Payment")))
		if not self.debit_to:
			self.debit_to = get_party_account("Customer", self.customer, self.company)
			self.party_account_currency = frappe.db.get_value("Account", self.debit_to, "account_currency", cache=True)
			if not self.debit_to:
				frappe.msgprint("Debit to is mandatory")
		try:
			if self.is_return:
				self.payments[0].amount=self.rounded_total
				self.paid_amount =self.rounded_total
		except:
			pass

		# run on validate method of selling controller
		super(SalesInvoice, self).validate()
		self.validate_auto_set_posting_time()
		self.validate_mode_of_payment()
		self.validate_uom_is_integer("stock_uom", "stock_qty")
		self.validate_uom_is_integer("uom", "qty")
		self.validate_debit_to_acc()
		self.validate_write_off_account()
		self.validate_change_amount()
		self.validate_change_account()
		self.validate_item_cost_centers()
		self.validate_serialised_or_batched_item()
		self.validate_stock_availablility()
		self.validate_return_items_qty()
		self.validate_non_stock_items()
		self.set_status()
		self.set_account_for_mode_of_payment()
		self.validate_pos()
		self.validate_payment_amount()
		self.validate_loyalty_transaction()
		self.validate_paid()
		



	def on_submit(self):
		# create the loyalty point ledger entry if the customer is enrolled in any loyalty program
		if self.is_return:
			frappe.db.sql("""update `tabPOS Invoice` set returned=1 where name='{}'""".format(self.return_against))
			frappe.db.commit()
		if self.loyalty_program:
			self.make_loyalty_point_entry()
		elif self.is_return and self.return_against and self.loyalty_program:
			against_psi_doc = frappe.get_doc("POS Invoice", self.return_against)
			against_psi_doc.delete_loyalty_point_entry()
			against_psi_doc.make_loyalty_point_entry()
		if self.redeem_loyalty_points and self.loyalty_points:
			self.apply_loyalty_points()
		self.check_phone_payments()
		self.set_status(update=True)

		if not self.validate_serialised_or_batched_item():
			return frappe.throw("error please check item batched or serial number")
		try:

			if(self.updatestock==1):
				frappe.db.sql("""update `tabPOS Invoice` set update_stock=0 where name='{}'""".format(self.name))
				frappe.db.commit()
				self.update_stock_ledger()
		except:
			pass


	def on_cancel(self):
		# run on cancel method of selling controller
		super(SalesInvoice, self).on_cancel()
		if self.loyalty_program:
			self.delete_loyalty_point_entry()
		elif self.is_return and self.return_against and self.loyalty_program:
			against_psi_doc = frappe.get_doc("POS Invoice", self.return_against)
			against_psi_doc.delete_loyalty_point_entry()
			against_psi_doc.make_loyalty_point_entry()
	def validate_paid(self):
		grand_total = flt(self.rounded_total) or flt(self.grand_total)
		# if grand_total-(abs(self.rounded_total-self.grand_total)) > flt(self.paid_amount):
		# # 	frappe.throw("Paid amount must be equal total amount")
		# if grand_total  != self.paid_amount :
		# 	frappe.throw("Erro Paid Amount ")
	def check_phone_payments(self):
		for pay in self.payments:
			if pay.type == "Phone" and pay.amount >= 0:
				paid_amt = frappe.db.get_value("Payment Request",
					filters=dict(
						reference_doctype="POS Invoice", reference_name=self.name,
						mode_of_payment=pay.mode_of_payment, status="Paid"),
					fieldname="grand_total")

				if pay.amount != paid_amt:
					return frappe.throw(_("Payment related to {0} is not completed").format(pay.mode_of_payment))

	def validate_stock_availablility(self):
		if self.is_return:
			return

		allow_negative_stock = frappe.db.get_value('Stock Settings', None, 'allow_negative_stock')
		error_msg = []
		for d in self.get('items'):
			msg = ""
			if d.serial_no:
				filters = { "item_code": d.item_code, "warehouse": d.warehouse }
				if d.batch_no:
					filters["batch_no"] = d.batch_no
				reserved_serial_nos = get_pos_reserved_serial_nos(filters)
				serial_nos = get_serial_nos(d.serial_no)
				invalid_serial_nos = [s for s in serial_nos if s in reserved_serial_nos]

				bold_invalid_serial_nos = frappe.bold(', '.join(invalid_serial_nos))
				if len(invalid_serial_nos) == 1:
					msg = (_("Row #{}: Serial No. {} has already been transacted into another POS Invoice. Please select valid serial no.")
								.format(d.idx, bold_invalid_serial_nos))
				elif invalid_serial_nos:
					msg = (_("Row #{}: Serial Nos. {} has already been transacted into another POS Invoice. Please select valid serial no.")
								.format(d.idx, bold_invalid_serial_nos))

			else:
				if allow_negative_stock:
					return

				available_stock = get_stock_availability(d.item_code, d.warehouse)
				item_code, warehouse, qty = frappe.bold(d.item_code), frappe.bold(d.warehouse), frappe.bold(d.qty)
				if flt(available_stock) <= 0:
					msg = (_('Row #{}: Item Code: {} is not available under warehouse {}.').format(d.idx, item_code, warehouse))
				elif flt(available_stock) < flt(d.qty):
					msg = (_('Row #{}: Stock quantity not enough for Item Code: {} under warehouse {}. Available quantity {}.')
								.format(d.idx, item_code, warehouse, qty))
			if msg:
				error_msg.append(msg)

		if error_msg:
			frappe.throw(error_msg, title=_("Item Unavailable"), as_list=True)

	def validate_serialised_or_batched_item(self):
		error_msg = []
		for d in self.get("items"):
			serialized = d.get("has_serial_no")
			batched = d.get("has_batch_no")
			no_serial_selected = not d.get("serial_no")
			no_batch_selected = not d.get("batch_no")

			msg = ""
			item_code = frappe.bold(d.item_code)
			serial_nos = get_serial_nos(d.serial_no)
			if serialized and batched and (no_batch_selected or no_serial_selected):
				msg = (_('Row #{}: Please select a serial no and batch against item: {} or remove it to complete transaction.')
							.format(d.idx, item_code))
			elif serialized and no_serial_selected:
				msg = (_('Row #{}: No serial number selected against item: {}. Please select one or remove it to complete transaction.')
							.format(d.idx, item_code))
			elif batched and no_batch_selected:
				msg = (_('Row #{}: No batch selected against item: {}. Please select a batch or remove it to complete transaction.')
							.format(d.idx, item_code))
			elif serialized and not no_serial_selected and len(serial_nos) != d.qty:
				msg = (_("Row #{}: You must select {} serial numbers for item {}.").format(d.idx, frappe.bold(cint(d.qty)), item_code))

			if msg:
				error_msg.append(msg)

		if error_msg:
			# frappe.throw(error_msg, title=_("Invalid Item"), as_list=True)
			return False
		else:
			return True

	def validate_return_items_qty(self):
		if not self.get("is_return"): return

		for d in self.get("items"):
			if d.get("qty") > 0:
				frappe.throw(
					_("Row #{}: You cannot add postive quantities in a return invoice. Please remove item {} to complete the return.")
					.format(d.idx, frappe.bold(d.item_code)), title=_("Invalid Item")
				)
			if d.get("serial_no"):
				serial_nos = get_serial_nos(d.serial_no)
				for sr in serial_nos:
					serial_no_exists = frappe.db.exists("POS Invoice Item", {
						"parent": self.return_against, 
						"serial_no": ["like", d.get("serial_no")]
					})
					if not serial_no_exists:
						bold_return_against = frappe.bold(self.return_against)
						bold_serial_no = frappe.bold(sr)
						frappe.throw(
							_("Row #{}: Serial No {} cannot be returned since it was not transacted in original invoice {}")
							.format(d.idx, bold_serial_no, bold_return_against)
						)
	
	def validate_non_stock_items(self):
		for d in self.get("items"):
			is_stock_item = frappe.get_cached_value("Item", d.get("item_code"), "is_stock_item")
			if not is_stock_item:
				frappe.throw(_("Row #{}: Item {} is a non stock item. You can only include stock items in a POS Invoice. ").format(
					d.idx, frappe.bold(d.item_code)
				), title=_("Invalid Item"))

	def validate_mode_of_payment(self):
		if len(self.payments) == 0:
			frappe.throw(_("At least one mode of payment is required for POS invoice."))

	def validate_change_account(self):
		if self.change_amount and self.account_for_change_amount and \
			frappe.db.get_value("Account", self.account_for_change_amount, "company") != self.company:
			frappe.throw(_("The selected change account {} doesn't belongs to Company {}.").format(self.account_for_change_amount, self.company))

	def validate_change_amount(self):
		grand_total = flt(self.rounded_total) or flt(self.grand_total)
		base_grand_total = flt(self.base_rounded_total) or flt(self.base_grand_total)
		if not flt(self.change_amount) and grand_total < flt(self.paid_amount):
			self.change_amount = flt(self.paid_amount - grand_total + flt(self.write_off_amount))
			self.base_change_amount = flt(self.base_paid_amount - base_grand_total + flt(self.base_write_off_amount))

		if flt(self.change_amount) and not self.account_for_change_amount:
			frappe.msgprint(_("Please enter Account for Change Amount"), raise_exception=1)

	def validate_payment_amount(self):
		total_amount_in_payments = 0
		for entry in self.payments:
			total_amount_in_payments += entry.amount
			if not self.is_return and entry.amount < 0:
				frappe.throw(_("Row #{0} (Payment Table): Amount must be positive").format(entry.idx))
			if self.is_return and entry.amount > 0:
				frappe.throw(_("Row #{0} (Payment Table): Amount must be negative").format(entry.idx))

		if self.is_return:
			invoice_total = self.rounded_total or self.grand_total
			if total_amount_in_payments and total_amount_in_payments < invoice_total:
				frappe.throw(_("Total payments amount can't be greater than {}").format(-invoice_total))

	def validate_loyalty_transaction(self):
		if self.redeem_loyalty_points and (not self.loyalty_redemption_account or not self.loyalty_redemption_cost_center):
			expense_account, cost_center = frappe.db.get_value('Loyalty Program', self.loyalty_program, ["expense_account", "cost_center"])
			if not self.loyalty_redemption_account:
				self.loyalty_redemption_account = expense_account
			if not self.loyalty_redemption_cost_center:
				self.loyalty_redemption_cost_center = cost_center

		if self.redeem_loyalty_points and self.loyalty_program and self.loyalty_points:
			validate_loyalty_points(self, self.loyalty_points)

	def set_status(self, update=False, status=None, update_modified=True):
		if self.is_new():
			if self.get('amended_from'):
				self.status = 'Draft'
			return

		if not status:
			if self.docstatus == 2:
				status = "Cancelled"
			elif self.docstatus == 1:
				if self.consolidated_invoice:
					self.status = "Consolidated"
				elif flt(self.outstanding_amount) > 0 and getdate(self.due_date) < getdate(nowdate()) and self.is_discounted and self.get_discounting_status()=='Disbursed':
					self.status = "Overdue and Discounted"
				elif flt(self.outstanding_amount) > 0 and getdate(self.due_date) < getdate(nowdate()):
					self.status = "Overdue"
				elif flt(self.outstanding_amount) > 0 and getdate(self.due_date) >= getdate(nowdate()) and self.is_discounted and self.get_discounting_status()=='Disbursed':
					self.status = "Unpaid and Discounted"
				elif flt(self.outstanding_amount) > 0 and getdate(self.due_date) >= getdate(nowdate()):
					self.status = "Unpaid"
				elif flt(self.outstanding_amount) <= 0 and self.is_return == 0 and frappe.db.get_value('POS Invoice', {'is_return': 1, 'return_against': self.name, 'docstatus': 1}):
					self.status = "Credit Note Issued"
				elif self.is_return == 1:
					self.status = "Return"
				elif flt(self.outstanding_amount)<=0:
					self.status = "Paid"
				else:
					self.status = "Submitted"
			else:
				self.status = "Draft"

		if update:
			self.db_set('status', self.status, update_modified = update_modified)

	def set_pos_fields(self, for_validate=False):
		"""Set retail related fields from POS Profiles"""
		from erpnext.stock.get_item_details import get_pos_profile_item_details, get_pos_profile
		if not self.pos_profile:
			pos_profile = get_pos_profile(self.company) or {}
			self.pos_profile = pos_profile.get('name')

		profile = {}
		if self.pos_profile:
			profile = frappe.get_doc('POS Profile', self.pos_profile)

		if not self.get('payments') and not for_validate:
			update_multi_mode_option(self, profile)
		
		if self.is_return and not for_validate:
			add_return_modes(self, profile)

		if profile:
			if not for_validate and not self.customer:
				self.customer = profile.customer

			self.ignore_pricing_rule = profile.ignore_pricing_rule
			self.account_for_change_amount = profile.get('account_for_change_amount') or self.account_for_change_amount
			self.set_warehouse = profile.get('warehouse') or self.set_warehouse

			for fieldname in ('currency', 'letter_head', 'tc_name',
				'company', 'select_print_heading', 'write_off_account', 'taxes_and_charges',
				'write_off_cost_center', 'apply_discount_on', 'cost_center', 'tax_category',
				'ignore_pricing_rule', 'company_address', 'update_stock'):
					if not for_validate:
						self.set(fieldname, profile.get(fieldname))

			if self.customer:
				customer_price_list, customer_group = frappe.db.get_value("Customer", self.customer, ['default_price_list', 'customer_group'])
				customer_group_price_list = frappe.db.get_value("Customer Group", customer_group, 'default_price_list')
				selling_price_list = customer_price_list or customer_group_price_list or profile.get('selling_price_list')
			else:
				selling_price_list = profile.get('selling_price_list')

			if selling_price_list:
				self.set('selling_price_list', selling_price_list)

			# set pos values in items
			for item in self.get("items"):
				try :
					if item.get('item_code'):
						profile_details = get_pos_profile_item_details(profile.get("company"), frappe._dict(item.as_dict()), profile)
						for fname, val in iteritems(profile_details):
							if (not for_validate) or (for_validate and not item.get(fname)):
								item.set(fname, val)
				except:
					pass

			# fetch terms
			if self.tc_name and not self.terms:
				self.terms = frappe.db.get_value("Terms and Conditions", self.tc_name, "terms")

			# fetch charges
			if self.taxes_and_charges and not len(self.get("taxes")):
				self.set_taxes()

		if not self.account_for_change_amount:
			self.account_for_change_amount = frappe.get_cached_value('Company',  self.company,  'default_cash_account')

		return profile



	def set_missing_values(self, for_validate=False):
		profile = self.set_pos_fields(for_validate)

		if not self.debit_to:
			self.debit_to = get_party_account("Customer", self.customer, self.company)
			self.party_account_currency = frappe.db.get_value("Account", self.debit_to, "account_currency", cache=True)
		if not self.due_date and self.customer:
			self.due_date = get_due_date(self.posting_date, "Customer", self.customer, self.company)

		super(SalesInvoice, self).set_missing_values(for_validate)

		print_format = profile.get("print_format") if profile else None
		if not print_format and not cint(frappe.db.get_value('Print Format', 'POS Invoice', 'disabled')):
			print_format = 'POS Invoice'

		if profile:
			return {
				"print_format": print_format,
				"campaign": profile.get("campaign"),
				"allow_print_before_pay": profile.get("allow_print_before_pay")
			}

	def set_account_for_mode_of_payment(self):
		self.payments = [d for d in self.payments if d.amount or d.base_amount or d.default]
		for pay in self.payments:
			if not pay.account:
				pay.account = get_bank_cash_account(pay.mode_of_payment, self.company).get("account")

	def create_payment_request(self):

		for pay in self.payments:
			if pay.type == "Phone":
				if pay.amount <= 0:
					frappe.throw(_("Payment amount cannot be less than or equal to 0"))

				if not self.contact_mobile:
					frappe.throw(_("Please enter the phone number first"))

				payment_gateway = frappe.db.get_value("Payment Gateway Account", {
					"payment_account": pay.account,
				})
				record = {
					"payment_gateway": payment_gateway,
					"dt": "POS Invoice",
					"dn": self.name,
					"payment_request_type": "Inward",
					"party_type": "Customer",
					"party": self.customer,
					"mode_of_payment": pay.mode_of_payment,
					"recipient_id": self.contact_mobile,
					"submit_doc": True
				}

				return make_payment_request(**record)
def get_mode_of_payment_info(mode_of_payment, company):
	return frappe.db.sql("""
		select mpa.default_account, mpa.parent, mp.type as type
		from `tabMode of Payment Account` mpa,`tabMode of Payment` mp
		where mpa.parent = mp.name and mpa.company = %s and mp.enabled = 1 and mp.name = %s""",
	(company, mode_of_payment), as_dict=1)
def add_return_modes(doc, pos_profile):
	def append_payment(payment_mode):
		payment = doc.append('payments', {})
		payment.default = payment_mode.default
		payment.mode_of_payment = payment_mode.parent
		payment.account = payment_mode.default_account
		payment.type = payment_mode.type

	for pos_payment_method in pos_profile.get('payments'):
		pos_payment_method = pos_payment_method.as_dict()
		mode_of_payment = pos_payment_method.mode_of_payment
		if pos_payment_method.allow_in_returns and not [d for d in doc.get('payments') if d.mode_of_payment == mode_of_payment]:
			payment_mode = get_mode_of_payment_info(mode_of_payment, doc.company)
			append_payment(payment_mode[0])

@frappe.whitelist()
def get_stock_availability(item_code, warehouse):
	latest_sle = frappe.db.sql("""select qty_after_transaction
		from `tabStock Ledger Entry`
		where item_code = %s and warehouse = %s
		order by posting_date desc, posting_time desc
		limit 1""", (item_code, warehouse), as_dict=1)

	pos_sales_qty = frappe.db.sql("""select sum(p_item.qty) as qty
		from `tabPOS Invoice` p, `tabPOS Invoice Item` p_item
		where p.name = p_item.parent
		and p.consolidated_invoice is NULL
		and p.docstatus = 1
		and p_item.docstatus = 1
		and p_item.item_code = %s
		and p_item.warehouse = %s
		""", (item_code, warehouse), as_dict=1)

	sle_qty = latest_sle[0].qty_after_transaction or 0 if latest_sle else 0
	pos_sales_qty = pos_sales_qty[0].qty or 0 if pos_sales_qty else 0

	if sle_qty and pos_sales_qty:
		return sle_qty - pos_sales_qty
	else:
		return sle_qty

@frappe.whitelist()
def make_sales_return(source_name, target_doc=None):
	from erpnext.controllers.sales_and_purchase_return import make_return_doc
	return make_return_doc("POS Invoice", source_name, target_doc)

@frappe.whitelist()
def make_merge_log(invoices):
	import json
	from six import string_types

	if isinstance(invoices, string_types):
		invoices = json.loads(invoices)

	if len(invoices) == 0:
		frappe.throw(_('Atleast one invoice has to be selected.'))

	merge_log = frappe.new_doc("POS Invoice Merge Log")
	merge_log.posting_date = getdate(nowdate())
	for inv in invoices:
		inv_data = frappe.db.get_values("POS Invoice", inv.get('name'),
			["customer", "posting_date", "grand_total"], as_dict=1)[0]
		merge_log.customer = inv_data.customer
		merge_log.append("pos_invoices", {
			'pos_invoice': inv.get('name'),
			'customer': inv_data.customer,
			'posting_date': inv_data.posting_date,
			'grand_total': inv_data.grand_total
		})

	if merge_log.get('pos_invoices'):
		return merge_log.as_dict()

def add_return_modes(doc, pos_profile):
	def append_payment(payment_mode):
		payment = doc.append('payments', {})
		payment.default = payment_mode.default
		payment.mode_of_payment = payment_mode.parent
		payment.account = payment_mode.default_account
		payment.type = payment_mode.type

	for pos_payment_method in pos_profile.get('payments'):
		pos_payment_method = pos_payment_method.as_dict()
		mode_of_payment = pos_payment_method.mode_of_payment
		if pos_payment_method.allow_in_returns and not [d for d in doc.get('payments') if d.mode_of_payment == mode_of_payment]:
			payment_mode = get_mode_of_payment_info(mode_of_payment, doc.company)
			append_payment(payment_mode[0])