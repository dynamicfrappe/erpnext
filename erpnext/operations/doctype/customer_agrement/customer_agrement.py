# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime ,time , timedelta
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, now, date_diff , nowdate , nowtime
from dateutil.relativedelta import relativedelta

from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item, set_transaction_type
import json


class CustomerAgrement(Document):
	def get_total_durations(self):
		duration = 0

		if self.start_date and self.end_date :
			self.start_date =datetime.strptime(str(self.start_date),'%Y-%m-%d').date()
			self.end_date =datetime.strptime(str(self.end_date),'%Y-%m-%d').date()
			if (self.start_date > self.end_date):
				frappe.msgprint(_("Start Date Cann't be after End Date"),indicator='red')
				self.start_date = self.end_date
			duration = (self.end_date - self.start_date).days +1

		self.total_duration_in_monthes =  duration
	def calculate_employee_totals(self):
		self.resourses = getattr(self,'resourses',[])
		self.total_resources_fee = 0
		self.total_resources_monthly_fee = 0
		self.total_resources = len(self.resourses) or 0
		self.grand_total_fee = 0
		for i in self.resourses:
			i.salary = i.salary if i.salary else 0
			i.other_ereanings = i.other_ereanings if i.other_ereanings else 0
			i.company_revenue = flt(i.company_revenue) if i.company_revenue else 1
			percent = i.company_revenue if i.company_revenue > 1 else 0


			i.total_monthly_fee = ((i.salary + i.other_ereanings)+((i.salary + i.other_ereanings)*percent/100) ) or 0
			self.total_resources_fee += i.total_monthly_fee
		self.total_resources_monthly_fee = self.total_resources_fee
		self.grand_total_fee = self.total_resources_fee + getattr(self,'total_equipments_fee',0)

	def calculate_tools_totals(self):
		self.tools = getattr(self, 'tools', [])
		self.tools_qty = 0
		self.total_equipments_fee=0
		self. grand_total_fee = 0
		for i in self.tools:
			i.qty = i.qty or 0
			i.rate = i.rate or 0
			i.total_amount = (i.qty * i.rate) or 0
			i.intersest_precentagefor_year = flt(i.intersest_precentagefor_year or 0 )
			i.monthly_installment = i.monthly_installment or 1
			percent = ((i.intersest_precentagefor_year /100) * i.monthly_installment) /12
			i.grand_total = i.total_amount
			if i.monthly_installment > 1:
				i.grand_total+= (i.total_amount * percent)
			i.monthly_fee = i.grand_total / i.monthly_installment
			self.tools_qty += i.qty
			self.total_equipments_fee += i.grand_total

		self.grand_total_fee = self.total_equipments_fee + getattr(self,'total_resources_fee',0)
	def hold (self):
		self.save()
		self.set('holds',[])
		for i in getattr(self,'resourses',[]):
			if i.status == 'Hold':
				self.append('holds',{
					'reference_type': i.doctype,
					'reference_name': i.name,
					'reference_item': i.employee,

				})

		for i in getattr(self, 'tools', []):
			if i.status == 'Hold':

				self.append('holds', {
					'reference_type': i.doctype,
					'reference_name': i.name,
					'reference_item': i.item_code,

				})

		self.save()



@frappe.whitelist()
def create_delivery_note(doc):
	self = frappe.get_doc('Customer Agrement', doc)

	dn = frappe.new_doc("Delivery Note")
	dn.posting_date =  nowdate()
	dn.posting_time =  nowtime()
	dn.set_posting_time = 1
	dn.is_custdy = 1
	dn.project = self.project
	dn.customer_agreement = self.name
	dn.customer = self.customer or "_Test Customer"
	dn.is_return = 0
	for i in getattr(self,'tools',[]):
		if i.status == 'Active':
			undeliverd_qty = (i.qty - i.delivered_qty) or 0
			if undeliverd_qty > 0:
				dn.append("items", {
					"item_code": i.item_code,
					"warehouse": self.warehouse ,
					"qty": undeliverd_qty or 1,
					"rate": i.rate ,
					"uom": i.uom ,
					"stock_uom": i.stock_uom ,
					"conversion_factor": i.conversion_rate,
					"allow_zero_valuation_rate":  1,
					"expense_account": i.account ,
					"cost_center": i.cost_center ,
					"customer_tool": i.name ,
					"project": self.project
				})
	if not getattr(dn,'items',None):
		frappe.throw(_('There is no Items To Deliver'))


	dn.insert()

	return dn
@frappe.whitelist()
def create_stock_entry(doc):
	self = frappe.get_doc('Customer Agrement', doc)

	stock_entry = frappe.new_doc("Stock Entry")

	stock_entry.stock_entry_type = "Material Transfer"
	stock_entry.to_warehouse = self.warehouse
	stock_entry.from_warehouse  = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	stock_entry.customer_agreement = self.name
	stock_entry.is_custody = 1
	stock_entry.project = self.project
	for item in getattr(self,'tools',[]):
		if item.status == 'Active':
			untransferred_qty = item.qty - item.transferred_qty
			if untransferred_qty > 0 :
				se_child = stock_entry.append('items')
				se_child.item_code = item.item_code
				se_child.item_name = item.item_name
				se_child.uom = item.uom
				se_child.stock_uom = item.stock_uom
				se_child.qty = untransferred_qty
				se_child.t_warehouse = self.warehouse
				se_child.s_warehouse = stock_entry.from_warehouse
				# in stock uom
				se_child.transfer_qty = flt(untransferred_qty)
				se_child.conversion_factor = flt(item.conversion_rate)
				se_child.project = self.project
				se_child.cost_center = item.cost_center
				se_child.expense_account = item.account
				se_child.customer_tool = item.name

	if not getattr(stock_entry,'items',None):
		frappe.throw(_('There is no Items To Transfer'))
	
	stock_entry.insert()
	return stock_entry



@frappe.whitelist()
def create_Due(doc):
	self = frappe.get_doc('Customer Agrement', doc)

	invoice = frappe.new_doc("Operations Invoice Dues")
	invoice.agreement = self.name
	invoice.date = self.start_date
	res = frappe.db.sql("""select MAX(date) from `tabOperations Invoice Dues` where agreement = '{}' and docstatus < 2 
	""".format(self.name))
	if res and len(res) > 0:
		date = res[0][0]
		if date:
			invoice.date = date + relativedelta(months=1)
	if self.end_date:
		if invoice.date >  self.end_date :
			frappe.throw(_("""All Operations Invoice Dues Was Created"""))

	invoice.invoiced = 0
	invoice.total_resources = 0
	invoice.total_tools = 0
	invoice.total_resources_fee = 0
	invoice.total_equipments_fee = 0
	invoice.total_fee = 0
	invoice.total_qty = 0
	invoice.total_invoiced = 0
	invoice.total_remaining = 0

	for item in getattr(self,'tools',[]):

			# untransferred_qty = item.qty - item.transferred_qty
			# if untransferred_qty > 0 :
			if item.status != 'Finished':
				invoice_child = invoice.append('items')
				invoice_child.status = item.status
				invoice_child.item_code = item.item_code
				invoice_child.item_name = item.item_name
				invoice_child.rate = item.monthly_fee / item.qty
				invoice_child.qty =item.qty
				invoice_child.total = item.monthly_fee
				invoice_child.cost_center = item.cost_center
				invoice_child.account = item.account
				invoice_child.tool = item.name
				invoice.total_tools += item.qty
				invoice.total_tools_fee += item.monthly_fee

	for item in getattr(self,'resourses',[]):
			# untransferred_qty = item.qty - item.transferred_qty
			# if untransferred_qty > 0 :
			if item.status != 'Finished':
				employee_number = frappe.db.get_value('Employee',item.employee , 'employee_number') or ''
				key = 'item-' + str(employee_number)+ '-' + item.employee_name
				res = frappe.db.sql (""" select item_code , item_name from tabItem where item_name  like '%{}%'
					order by creation desc limit 1 """.format(key))
				if res :
					item.item_code = res[0][0]
					item.item_name = res[0][1]
					invoice_child = invoice.append('items')

					invoice_child.status = item.status
					invoice_child.item_code = item.item_code
					invoice_child.item_name = item.item_name
					invoice_child.rate =  item.total_monthly_fee
					invoice_child.qty = 1
					invoice_child.total = item.total_monthly_fee
					invoice_child.cost_center = item.cost_center
					invoice_child.account = item.account
					invoice_child.resource = item.name
					invoice.total_resources += 1
					invoice.total_resources_fee += item.total_monthly_fee

	invoice.total_fee = invoice.total_tools_fee + invoice.total_resources_fee
	invoice.total_qty = invoice.total_tools + invoice.total_resources
	invoice.total_remaining = invoice.total_qty

	if not getattr(invoice,'items',None):
		frappe.throw(_('There is no Items To Transfer'))
	invoice.insert()
	self.append('dues',{
		'due':invoice.name,
		'date':invoice.date,
		'invoiced': invoice.invoiced,
	})
	self.save()
	return invoice


@frappe.whitelist()
def get_item_price(args):
	rate = 0
	args = json.loads(str(args))
	args = frappe._dict(args)
	item = args.item_code
	customer = args.customer
	company = args.company
	price_list = None
	rate = 0

	if customer :
		price_list = frappe.db.get_value("Customer",customer , 'default_price_list')
	if  not price_list :
		company_cond = ""
		if company:
			company_cond =" and company = '{}'".format(company)
		price_list = frappe.db.sql("""
		select default_price_list from `tabItem Default` where parent = '{}' {}
		order by creation desc limit 1
		""".format(item,company_cond))

	if not price_list:
		price_list = (frappe.db.get_single_value('Selling Settings', 'selling_price_list')
					  or frappe.db.get_value('Price List', _('Standard Selling')))
	sql = """
					select price_list_rate 
					from `tabItem Price` 
					where item_code = '{}' 
					and (price_list = '{}' or selling = 1)
					and curdate() >=  ifnull(valid_from,curdate()) 
					and curdate() <=  ifnull(valid_upto,curdate())
					order by creation desc limit 1
	""".format(item,price_list)
	res = frappe.db.sql(sql)

	if res :
		rate = res[0][0] or 0
	return  rate

@frappe.whitelist()
def get_item_conversion_factor(item,uom):
	sql = """ select conversion_factor  from `tabUOM Conversion Detail` where parent='{}' and uom = '{}' """.format(item,uom)
	res = frappe.db.sql(sql,as_dict=1)
	if res :
		return res [0].conversion_factor
	return 1



@frappe.whitelist()
def create_invoice_from_due(doc_name=None):
	names = []
	if doc_name :
		names.append(doc_name)
	else :
		names = frappe.db.sql_list (""" select name from `tabOperations Invoice Dues`
		 where  invoiced <>1 """.format())
	if names or len(names) > 0 :
		for name in names :
			try :
				doc = frappe.get_doc("Operations Invoice Dues", name)
				doc.create_invoice()
			except Exception as e:
				frappe.msgprint(_("Error while Creating Operations Sales Invoice for  Operations Invoice Dues {} \n{}".format(name,str(e))))
		frappe.db.sql("""update `tabCustomer Agreement Dues` set invoiced = (select t.invoiced from `tabOperations Invoice Dues` t where  t.name= due) where invoiced <>1""")
		frappe.db.commit()












