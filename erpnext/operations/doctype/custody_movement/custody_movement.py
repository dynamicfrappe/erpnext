# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _
import frappe
from frappe.model.document import Document

class CustodyMovement(Document):
	def validate(self):
		self.validate_items()
	def validate_items(self):
		for i in self.items:
			sql = ''
			if self.type != 'Transfer':
				agreement = self.from_customer_agreement or self.to_customer_agreement
				sql = """select DISTINCT item_code from `tabCustomer Agrement Tools` 
							where parent = '{}' 
   				 """.format(agreement)
			else :
				sql = """
					select DISTINCT item_code from `tabCustomer Agrement Tools`
					where parent in ('{}','{}')
					group by item_code
					HAVING COUNT(item_code) > 1
  					  """.format(self.from_customer_agreement,self.to_customer_agreement)
			valid_items = frappe.db.sql_list (sql)
			if i.item_code not in valid_items:
				frappe.throw(_("Item {} not Valid in row {}".format(i.item_code,i.idx)))


	def on_submit (self):
		self.create_stock_entry()

	def create_stock_entry(self):
		types = {
			'Deliver': 'Material Issue',
			'Transfer': 'Custody Transfer',
			'Send': 'Custody Send',
			'Receipt from Customer': 'Material Receipt',
			'Return': 'Custody Return'
		}
		# IN Case Transfer
		source_warehouse = self.source_warehouse
		target_warehouse = self.target_warehouse
		stock_entry = frappe.new_doc("Stock Entry")
		stock_entry.is_custody = 1
		# IN Case Send
		agreement = None
		if self.type == 'Send':
			source_warehouse , target_warehouse = frappe.db.get_value('Customer Agrement',self.to_customer_agreement , ['sorce_warehouse','warehouse'])

		# IN Case Return  And Deliver
		elif  self.type in ['Return','Deliver'] :
			target_warehouse , source_warehouse   = frappe.db.get_value('Customer Agrement',self.from_customer_agreement , ['sorce_warehouse','warehouse'])
		elif  self.type in ['Receipt from Customer'] :
			target_warehouse    = self.custody_warehouse
			source_warehouse    =  self.custody_warehouse
			agreement = frappe.get_doc('Customer Agrement', self.from_customer_agreement)
			# validiate items deliver > 0
			for i in self.items :

				delivered_qty = sum([item.delivered_qty for item in agreement.tools if item.item_code == i.item_code and item.uom  == i.uom and item.delivered_qty > 0  ])
				if delivered_qty < i.qty :
					frappe.throw(_("Item {} in row {} has been delivered only {} {}".format(i.item_code , i.idx , delivered_qty , i.uom )))
			stock_entry.is_custody = self.is_custody




		stock_entry.stock_entry_type = types [self.type]
		stock_entry.from_warehouse = source_warehouse
		stock_entry.to_warehouse = target_warehouse

		stock_entry.from_customer_agreement = self.from_customer_agreement
		stock_entry.customer_agreement = self.to_customer_agreement


		stock_entry.from_employee = self.from_employee
		stock_entry.employee = self.to_employee


		for item in self.items:
				if (item.qty) > 0:  # and not item.delivered and item.delivered_qty < item.qty:
					se_child = stock_entry.append('items')
					se_child.item_code = item.item_code
					se_child.item_name = item.item_name
					se_child.qty = item.qty
					se_child.s_warehouse = source_warehouse
					se_child.t_warehouse = target_warehouse
					# in stock uom

					# se_child.expense_account = self.customer_installment_account
					se_child.conversion_factor = 1
					se_child.uom = item.stock_uom
					se_child.stock_uom = item.stock_uom
		if len(getattr(stock_entry, 'items', [])) == 0:
			frappe.throw(_('All items have been delivered before'))
		stock_entry.insert()
		stock_entry.submit()
		self.stock_entry = stock_entry.name
		self.save()
		if self.type in ['Receipt from Customer']:
			for i in self.items:
				delivered = [item for item in agreement.tools if item.item_code == i.item_code and item.uom == i.uom and item.delivered_qty > 0]
				qty = i.qty
				for item in	delivered :
					if qty > 0:
						if item.delivered_qty >= qty :
							frappe.db.set_value("Customer Agrement Tools",item.name,'delivered_qty',item.delivered_qty-qty)
							qty = 0
						else :
							frappe.db.set_value("Customer Agrement Tools",item.name,'delivered_qty',0)
							qty -= item.delivered_qty


		l = """ <b><a href="#Form/{0}/{1}">{1}</a></b>""".format(stock_entry.doctype, stock_entry.name)
		msg = _("A {} {} is Created for Company {}").format(stock_entry.doctype, l, stock_entry.company)
		frappe.msgprint(msg)






