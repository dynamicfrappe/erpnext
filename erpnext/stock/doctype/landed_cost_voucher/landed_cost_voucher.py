# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _
from frappe.utils import flt
from frappe.model.meta import get_field_precision
from frappe.model.document import Document
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
from erpnext.accounts.doctype.account.account import get_account_currency

class LandedCostVoucher(Document):
	def get_items_from_purchase_receipts(self):
		self.set("items", [])
		for pr in self.get("purchase_receipts"):
			if pr.receipt_document_type and pr.receipt_document:
				pr_items = frappe.db.sql("""select pr_item.item_code, pr_item.description,
					pr_item.qty, pr_item.base_rate, pr_item.base_amount, pr_item.name,
					pr_item.cost_center, pr_item.is_fixed_asset
					from `tab{doctype} Item` pr_item where parent = %s
					and exists(select name from tabItem
						where name = pr_item.item_code and (is_stock_item = 1 or is_fixed_asset=1))
					""".format(doctype=pr.receipt_document_type), pr.receipt_document, as_dict=True)

				for d in pr_items:
					item = self.append("items")
					item.item_code = d.item_code
					item.description = d.description
					item.qty = d.qty
					item.rate = d.base_rate
					item.cost_center = d.cost_center or \
						erpnext.get_default_cost_center(self.company)
					item.amount = d.base_amount
					item.receipt_document_type = pr.receipt_document_type
					item.receipt_document = pr.receipt_document
					item.purchase_receipt_item = d.name
					item.is_fixed_asset = d.is_fixed_asset

	def validate(self):
		self.check_mandatory()
		if not self.get("items"):
			self.get_items_from_purchase_receipts()
		else:
			self.validate_applicable_charges_for_item()
		self.validate_purchase_receipts()
		self.validate_expense_accounts()
		self.set_total_taxes_and_charges()
		self.update_allocated_amount()

	def check_mandatory(self):
		if not self.get("purchase_receipts"):
			frappe.throw(_("Please enter Receipt Document"))


	def validate_purchase_receipts(self):
		receipt_documents = []

		for d in self.get("purchase_receipts"):
			if frappe.db.get_value(d.receipt_document_type, d.receipt_document, "docstatus") != 1:
				frappe.throw(_("Receipt document must be submitted"))
			else:
				receipt_documents.append(d.receipt_document)

		for item in self.get("items"):
			if not item.receipt_document:
				frappe.throw(_("Item must be added using 'Get Items from Purchase Receipts' button"))

			elif item.receipt_document not in receipt_documents:
				frappe.throw(_("Item Row {0}: {1} {2} does not exist in above '{1}' table")
					.format(item.idx, item.receipt_document_type, item.receipt_document))

			if not item.cost_center:
				frappe.throw(_("Row {0}: Cost center is required for an item {1}")
					.format(item.idx, item.item_code))

	def validate_expense_accounts(self):
		company_currency = erpnext.get_company_currency(self.company)
		for account in self.taxes:
			if get_account_currency(account.expense_account) != company_currency:
				frappe.throw(msg=_(""" Row {0}: Expense account currency should be same as company's default currency.
					Please select expense account with account currency as {1}""")
					.format(account.idx, frappe.bold(company_currency)), title=_("Invalid Account Currency"))


	def get_invoice_date(self):
		invoice = frappe.det_doc("Purchase Invoice" , self.purchase_receipts[0].receipt_document)
		return(invoice.posting_date)

	def set_total_taxes_and_charges(self):
		self.total_taxes_and_charges = sum([flt(d.amount) for d in self.get("taxes")])

	def validate_applicable_charges_for_item(self):
		based_on = self.distribute_charges_based_on.lower()

		total = sum([flt(d.get(based_on)) for d in self.get("items")])

		if not total:
			frappe.throw(_("Total {0} for all items is zero, may be you should change 'Distribute Charges Based On'").format(based_on))

		total_applicable_charges = sum([flt(d.applicable_charges) for d in self.get("items")])

		precision = get_field_precision(frappe.get_meta("Landed Cost Item").get_field("applicable_charges"),
		currency=frappe.get_cached_value('Company',  self.company,  "default_currency"))

		diff = flt(self.total_taxes_and_charges) - flt(total_applicable_charges)
		diff = flt(diff, precision)

		if abs(diff) < (2.0 / (10**precision)):
			self.items[-1].applicable_charges += diff
		else:
			frappe.throw(_("Total Applicable Charges in Purchase Receipt Items table must be same as Total Taxes and Charges"))

	def on_submit(self):
		self.update_landed_cost()

	def on_cancel(self):
		self.update_landed_cost()

	def update_landed_cost(self):
		for d in self.get("purchase_receipts"):
			doc = frappe.get_doc(d.receipt_document_type, d.receipt_document)
			# check if there are {qty} assets created and linked to this receipt document
			self.validate_asset_qty_and_status(d.receipt_document_type, doc)

			# set landed cost voucher amount in pr item
			doc.set_landed_cost_voucher_amount()

			# set valuation amount in pr item
			doc.update_valuation_rate("items")

			# db_update will update and save landed_cost_voucher_amount and voucher_amount in PR
			for item in doc.get("items"):
				item.db_update()

			# asset rate will be updated while creating asset gl entries from PI or PY

			# update latest valuation rate in serial no
			self.update_rate_in_serial_no_for_non_asset_items(doc)

		for d in self.get("purchase_receipts"):
			doc = frappe.get_doc(d.receipt_document_type, d.receipt_document)
			# update stock & gl entries for cancelled state of PR
			doc.docstatus = 2
			doc.update_stock_ledger(allow_negative_stock=True, via_landed_cost_voucher=True)
			doc.make_gl_entries_on_cancel(repost_future_gle=False)

			# update stock & gl entries for submit state of PR
			doc.docstatus = 1
			doc.update_stock_ledger(allow_negative_stock=True, via_landed_cost_voucher=True)
			doc.make_gl_entries()

	def validate_asset_qty_and_status(self, receipt_document_type, receipt_document):
		for item in self.get('items'):
			if item.is_fixed_asset:
				receipt_document_type = 'purchase_invoice' if item.receipt_document_type == 'Purchase Invoice' \
						else 'purchase_receipt'
				docs = frappe.db.get_all('Asset', filters={ receipt_document_type: item.receipt_document,
					'item_code': item.item_code }, fields=['name', 'docstatus'])
				if not docs or len(docs) != item.qty:
					frappe.throw(_('There are not enough asset created or linked to {0}. \
						Please create or link {1} Assets with respective document.').format(item.receipt_document, item.qty))
				if docs:
					for d in docs:
						if d.docstatus == 1:
							frappe.throw(_('{2} <b>{0}</b> has submitted Assets.\
								Remove Item <b>{1}</b> from table to continue.').format(
									item.receipt_document, item.item_code, item.receipt_document_type))
	def update_allocated_amount(self):
		# data = []
		if self.landed_cost_details == 1:
			# refrences = [i.refrence for i in self.landed_cost_voucher_expenses] 
			for i in  self.landed_cost_voucher_expenses :
				total = 0
				for e in self.taxes:
					if e.refrence == i.reference :
						total += e.amount
				if (i.amount - i.outstanding) < total :
					available = i.amount - i.outstanding

					frappe.throw("Invalid Value For Transaction '%s' Available Amount is '%s' and You Try To Add '%s' "%(i.reference ,
																			 str(available) , str(total)))
				else :
					i.allocated =total
	def set_applicable_charges_for_item(self):
		pass

	# def recaculate_all_values(self):
	# 	if self.landed_cost_details == 1:
	# 		for i in  self.landed_cost_voucher_expenses :
	# 			allocated = 0 
	# 			for e in self.taxes:
	# 					if e.refrence == i.reference :
	# 						allocated += e.amount





	def update_rate_in_serial_no_for_non_asset_items(self, receipt_document):
		for item in receipt_document.get("items"):
			if not item.is_fixed_asset and item.serial_no:
				serial_nos = get_serial_nos(item.serial_no)
				if serial_nos:
					frappe.db.sql("update `tabSerial No` set purchase_rate=%s where name in ({0})"
						.format(", ".join(["%s"]*len(serial_nos))), tuple([item.valuation_rate] + serial_nos))





@frappe.whitelist()
def set_frm_query(tpe =None , refrence= None ,*args , **kwargs):
	if tpe =='Purchase Invoice' :
		invoice = frappe.get_doc("Purchase Invoice" , refrence)
		accounts = []
		for item in invoice.items:
			accounts_dic = {"account" : item.expense_account ,"desc":item.item_name ,
			"amount":item.amount  , "party":None , 'party_type': None ,"name" :invoice.name}
			accounts.append(accounts_dic)
		return(accounts)

	if tpe =='Payment Entry' :
			invoice = frappe.get_doc("Payment Entry" , refrence)
			accounts=[{"account" : invoice.paid_to , "desc":invoice.remarks ,
			 "amount":invoice.paid_amount , "party_type":invoice.party_type , "party":invoice.party ,"name" :invoice.name}]
			return(accounts)

	if tpe =='Journal Entry' :
		accounts=[]
		pay = frappe.db.sql(""" SELECT account  ,party_type ,party  ,debit,parent
		 FROM `tabJournal Entry Account` WHERE parent ='%s'  AND debit > 0 
		 """%str(refrence)) 

		accounts += [{"account": account[0] , "desc": account[1] ,
					"party":account[2],"party_type":account[1] ,
					"amount":account[3],"name" :account[4]}for account in pay ]
		
		return accounts






	return True


@frappe.whitelist()
def get_purchase_items(invoice=None , *args , **kwargs):


	invoices = frappe.db.sql("""SELECT  p.parent  FROM `tabPurchase Invoice Item` AS p
								inner join   `tabItem` AS a on p.item_code = a.item_code
								WHERE a.is_stock_item = 0 
								group by p.parent   """)

 
	return invoices



@frappe.whitelist()
def get_query_type (*args,**kwargs):
	return[[ "Purchase Invoice"],["Payment Entry"] , ["Journal Entry"]]



@frappe.whitelist()
def complete_data(refre , typ,*args, **kwargs):
	unallocated_amount = frappe.db.sql(""" SELECT SUM(allocated) FROM `tabLanded Cost Voucher Expenses`  INNER JOIN `tabLanded Cost Voucher` 
	on `tabLanded Cost Voucher Expenses`.parent = `tabLanded Cost Voucher`.name 
	WHERE `tabLanded Cost Voucher Expenses`.reference = '%s'  AND `tabLanded Cost Voucher`.docstatus= 1 """%refre) 
	# frappe.throw(str(unallocated_amount))
	try :
		un_allocate = int(unallocated_amount[0][0])
	except:
		un_allocate = 0 
	if typ == "Purchase Invoice":
		invoice = frappe.get_doc("Purchase Invoice" , refre )
		data = {"unallocated_amount" :un_allocate,"grand_total" : invoice.grand_total}
		return (data)
	if typ == "Journal Entry" :

		journal = frappe.get_doc("Journal Entry" , refre)
		data = {"unallocated_amount" :un_allocate or 0,"grand_total" : journal.total_credit}
		return data
	if typ == "Payment Entry":
		payment = frappe.get_doc("Payment Entry" , refre)
		data = {"unallocated_amount" :un_allocate ,"grand_total" : payment.paid_amount}
		return (data)



try :
	from dynamicerp.dynamic_erp.doctype.landed_cost_voucher.landed_cost_voucher import set_applicable_charges_for_item
	LandedCostVoucher.set_applicable_charges_for_item = set_applicable_charges_for_item
except:
	pass