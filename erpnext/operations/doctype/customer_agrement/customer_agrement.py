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
from dynamicerp.sky.doctype.operation_sales_invoice.operation_sales_invoice import get_item_valuation_rate

class CustomerAgrement(Document):

	def validate(self):
		self.calculate_tools_totals()
		self.set_resources_cost_center_and_account()
		self.set_tools_cost_center_project_account()
		self.calculate_un_delevered()

	def set_resources_cost_center_and_account(self):
		for resource in self.resourses :
			if not resource.cost_center :
				resource.cost_center = self.cost_center
			if not resource.account:
				resource.account = self.resourses_income_account

	def calculate_un_delevered(self):
		for item in self.tools :
			item.un_transfear_tools = float(item.qty or 0) - (float(item.transferred_qty or 0) + float(item.delivered_qty or 0))

	def set_tools_cost_center_project_account(self):
		for item in self.tools :
			if self.project and not item.proejct :
				item.proejct = self.project
			if not item.cost_center :
				item.cost_center = self.cost_center
			if not item.account :
				item.account= self.customer_installment_account

	def get_total_durations(self):
		duration = 0

		if self.start_date and self.end_date :
			self.start_date =datetime.strptime(str(self.start_date),'%Y-%m-%d').date()
			self.end_date =datetime.strptime(str(self.end_date),'%Y-%m-%d').date()
			if (self.start_date > self.end_date):
				frappe.msgprint(_("Start Date Cann't be after End Date"),indicator='red')
				self.start_date = self.end_date
			duration = (12 * self.end_date.year + self.end_date.month) - (12 * self.start_date.year + self.start_date.month)
			self.end_date = self.start_date +  relativedelta(months=duration)

		self.total_duration_in_monthes =  duration

	def get_months(self):
		start_date = datetime.strptime(str(self.start_date), '%Y-%m-%d').date()
		end_date = datetime.strptime(str(self.end_date), '%Y-%m-%d').date()

		diff = (12 * end_date.year + end_date.month) - (12 * start_date.year + start_date.month)
		self.total_duration_in_monthes =   diff + 1
	# calculate Resources Totals

	def calculate_employee_totals(self):
		self.resourses = getattr(self,'resourses',[])
		self.total_resources_fee = 0
		self.total_resources_monthly_fee = 0
		self.total_resources = len(self.resourses) or 0
		self.grand_total_fee = 0
		for i in self.resourses:
			i.salary = i.salary if i.salary else 0
			i.tax = i.tax or 0
			i.gross_salary = i.salary + i.tax
			i.social_insurance = i.social_insurance or 0
			i.life_insurance = i.life_insurance or 0
			i.mobile_package = i.mobile_package or 0
			i.ohs_courses = i.ohs_courses or 0
			i.medical_insurance = i.medical_insurance or 0
			i.laptop = i.laptop or 0
			i.mobile_allowance = i.mobile_allowance or 0
			i.ohs_tools = i.ohs_tools or 0
			i.other_ereanings = i.medical_insurance + i.laptop + i.mobile_allowance + i.ohs_tools +i.social_insurance + i.life_insurance + i.mobile_package +i.ohs_courses
			i.total = (i.gross_salary + i.other_ereanings) or 0
			i.company_revenue = flt(i.company_revenue) if i.company_revenue else 1
			percent = i.company_revenue if i.company_revenue > 1 else 0


			i.total_monthly_fee = (i.total+ (i.total*percent/100) ) or 0
			self.total_resources_fee += i.total_monthly_fee
		self.total_resources_monthly_fee = self.total_resources_fee
		self.grand_total_fee = self.total_resources_fee + getattr(self,'total_equipments_fee',0)
# calculate Tools Totals
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
			i.valuation_rate = get_item_valuation_rate(i.item_code , self.sorce_warehouse)
			if i.valuation_rate > 0 and   i.monthly_installment > 1 :
				i.itemproejct= float( i.valuation_rate) / float(i.monthly_installment)
			else :
				i.monthl_valuation_rate =  float( i.valuation_rate)
			percent = ((i.intersest_precentagefor_year /100) * i.monthly_installment) /12
			i.grand_total = i.total_amount
			if i.monthly_installment > 1:
				i.grand_total+= (i.total_amount * percent)
			i.monthly_fee = i.grand_total / i.monthly_installment
			self.tools_qty += i.qty
			self.total_equipments_fee += i.grand_total

		self.grand_total_fee = self.total_equipments_fee + getattr(self,'total_resources_fee',0)
# Hold/Unhold Items based on js status
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

	def create_stock_entry_backend(self,employee,*args,**kwargs):
		doc=frappe.new_doc("Stock Entry")
		doc.stock_entry_type="Custody Send"
		doc.employee=employee
		doc.from_warehouse=self.sorce_warehouse
		doc.to_warehouse=self.warehouse
		doc.customer_agreement=self.name
		doc.is_custody=1
		for item in self.tools:
			if item.un_transfear_tools==0:
				frappe.throw("un transfered tools equal 0")
			doc.append('items',{
				'item_code':item.item_code,
				'qty':item.un_transfear_tools,
				's_warehouse': self.sorce_warehouse,
				't_warehouse':self.warehouse
				})
		doc.save()

	def create_stock_entry_backend_return(self,employee,item,qty):
		doc = frappe.new_doc("Stock Entry")
		doc.stock_entry_type = "Custody Return"
		doc.employee = employee
		doc.from_employee=employee
		doc.from_warehouse = self.warehouse
		doc.to_warehouse =  self.sorce_warehouse
		doc.customer_agreement = self.name
		doc.from_customer_agreement=self.name
		doc.is_custody = 1
		doc.append('items', {
			'item_code': item,
			'qty': qty,
			's_warehouse':  self.warehouse,
			't_warehouse': self.sorce_warehouse
		})
		doc.save()


@frappe.whitelist()
# Create Custody Movement with type Deliver
def deliver_to_customer(doc):
		doc = frappe.get_doc("Customer Agrement",doc)
		# Validate Warehouse
		# if getattr(doc,'sorce_warehouse',None):
		# 	custody_warehouse , customer_custody_warehouse = frappe.db.get_value ('Warehouse',doc.sorce_warehouse , ['custody_warehouse','customer_custody_warehouse'])
		# 	if not  custody_warehouse and not customer_custody_warehouse :
		# 		return create_delivery_note(doc.name)

		if getattr(doc,'tools',None):
			custody_movement = frappe.new_doc("Custody Movement")
			custody_movement.type = 'Deliver'
			custody_movement.from_customer_agreement = doc.name
			custody_movement.source_warehouse = doc.sorce_warehouse
			# stock_entry = frappe.new_doc("Stock Entry")
			# stock_entry.stock_entry_type = "Material Issue"
			# stock_entry.from_warehouse = doc.warehouse
			# stock_entry.from_customer_agreement = doc.name
			# stock_entry.is_custody= is_custody
			# # for item in getattr(doc, 'tools', []):
			# # 	if item.status != 'Hold':
			# # 		if (item.qty-item.delivered_qty) > 0:  # and not item.delivered and item.delivered_qty < item.qty:
			# # 			se_child = stock_entry.append('items')
			# # 			se_child.item_code = item.item_code
			# # 			se_child.item_name = item.item_name
			# # 			se_child.qty = item.qty-item.delivered_qty
			# # 			se_child.s_warehouse = doc.warehouse
			# # 			# in stock uom
			# #
			# # 			se_child.expense_account = doc.customer_installment_account
			# # 			se_child.conversion_factor = 1
			# # 			se_child.uom = item.stock_uom
			# # 			se_child.stock_uom = item.stock_uom
			# # if len(getattr(stock_entry, 'items', [])) == 0:
			# # 	frappe.throw(_('All items have been delivered before'))
			# # try:
			# # 	stock_entry.insert()
			# # except Exception as e:
			# # 	frappe.msgprint(str(e))
			# # l = """ <b><a href="#Form/{0}/{1}">{1}</a></b>""".format(stock_entry.doctype, stock_entry.name)
			# # msg = _("A {} {} is Created for Company {}").format(stock_entry.doctype, l, stock_entry.company)
			#
			# return stock_entry
			return custody_movement


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
		if i.status != 'Hold':
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
# Not Used
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
		if  i.status != 'Hold':
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


# Create Due from Create Button on Cutomer Agreement
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
				invoice_child.stock_rate = item.itemproejct


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
					invoice_child.stock_rate = item.total


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
	frappe.msgprint(_('Done'))
	# return invoice

# fetch item price when add item to tools
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


# Convert Due to invoice where not invoiced
# Run Daily in hooks.py to create Invoice from uninvoiced Dues

@frappe.whitelist()
def create_invoice_from_due(doc_name=None):
	names = []
	if doc_name :
		# called from Create Button
		names.append(doc_name)
	else :
		# called from hooks
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

# Run Daily in hooks.py to create Auto Dues
@frappe.whitelist()
def create_Todays_due():
	active_docs = frappe.db.sql("""
	select t1.name from `tabCustomer Agrement` t1
	where curdate() between t1.start_date and t1.end_date
  	and t1.status = 'Open'
    and  curdate() >= date_add( ifnull((select MAX(t2.date)  from `tabCustomer Agreement Dues` t2 where t2.parent = t1.name),t1.start_date) , interval 1 MONTH)

	""")
	if active_docs :
		for doc in active_docs :
			try:
				# Create Due
				create_Due(doc)
			except:
				pass











