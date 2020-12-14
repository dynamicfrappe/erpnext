# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate, date_diff

class AdditionalSalary(Document):
	def __init__(self, *args, **kwargs) :
		super().__init__(*args,**kwargs)
		
	def before_insert(self):
		
			
		if frappe.db.exists("Additional Salary", {"employee": self.employee, "salary_component": self.salary_component,
			"amount": self.amount, "payroll_date": self.payroll_date, "company": self.company, "docstatus": 1}):

			frappe.throw(_("Additional Salary Component Exists."))

	def validate(self):
		
		if self.amount_based_on_formula  and self.count > 0 :
		
			self.amount = self.count * float(self.get_active_salary_structure_component())
		
		self.validate_dates()
		if self.amount_based_on_formula and  self.count < 0 :
			frappe.throw(_("count should not be less than zero."))
		if self.amount < 0:
			frappe.throw(_("Amount should not be less than zero."))

	def validate_dates(self):
 		date_of_joining, relieving_date = frappe.db.get_value("Employee", self.employee,
			["date_of_joining", "relieving_date"])
 		if date_of_joining and getdate(self.payroll_date) < getdate(date_of_joining):
 			frappe.throw(_("Payroll date can not be less than employee's joining date"))

	def get_active_salary_structure_component(self):
		component = frappe.get_doc("Salary Component",self.salary_component) 
		payroll_date = self.payroll_date
		if not payroll_date :
			frappe.throw("validation error in date")
		salary_structure = frappe.db.sql(""" 
			SELECT   max(from_date), salary_structure FROM `tabSalary Structure Assignment` WHERE
			employee = '%s' and docstatus=1 and from_date <= '%s'

			"""%(self.employee ,self.payroll_date))
		if not salary_structure :
			frappe.throw("validation error in Salary Structure")
		data ={}
		for i in component.based_on_componant :
			value = frappe.db.sql(""" SELECT amount FROM `tabSalary Detail` WHERE parent ='%s' and
				abbr = '%s' """ %(str(salary_structure[0][1]) , i.component_short_name))
			if value :
				data[str(i.component_short_name)] = float(value[0][0])
			else :
				data[str(i.component_short_name)] = 0
				# frappe.throw("Validation error in component '%s' pleas check if employee have it in his salary struct "%i.component_short_name)

		
		formula = component.formula
		if formula :
			return self.get_amount_pase_on_formula(formula ,data)
		else :
			return 0 

	def get_amount_pase_on_formula(self,formula , data):
		# formula is string 
		#data is dic
		func  =formula.strip(" ").replace("\n", " ")
		d =[i for  i in data.keys() ]
		for e in range(0,len(d)) :
			func  = func.replace(str(max(d ,key=len)) , str(data[max(d ,key=len)]))
			d.remove(max(d ,key=len))
			
		try :
			return (eval(func))
		except:
			return("error")
	

		

	def get_amount(self, sal_start_date, sal_end_date):
		start_date = getdate(sal_start_date)
		end_date = getdate(sal_end_date)
		total_days = date_diff(getdate(self.to_date), getdate(self.from_date)) + 1
		amount_per_day = self.amount / total_days
		if getdate(sal_start_date) <= getdate(self.from_date):
			start_date = getdate(self.from_date)
		if getdate(sal_end_date) > getdate(self.to_date):
			end_date = getdate(self.to_date)
		no_of_days = date_diff(getdate(end_date), getdate(start_date)) + 1
		return amount_per_day * no_of_days

	def set_amount_amount_based_on_formula(self):
		return 1000
		

@frappe.whitelist()
def get_additional_salary_component(employee, start_date, end_date, component_type):
	additional_components = frappe.db.sql("""
		select salary_component, sum(amount) as amount, overwrite_salary_structure_amount, deduct_full_tax_on_selected_payroll_date
		from `tabAdditional Salary`
		where employee=%(employee)s
			and docstatus = 1
			and payroll_date between %(from_date)s and %(to_date)s
			and type = %(component_type)s
		group by salary_component, overwrite_salary_structure_amount
		order by salary_component, overwrite_salary_structure_amount
	""", {
		'employee': employee,
		'from_date': start_date,
		'to_date': end_date,
		'component_type': "Earning" if component_type == "earnings" else "Deduction"
	}, as_dict=1)

	additional_components_list = []
	component_fields = ["depends_on_payment_days", "salary_component_abbr", "is_tax_applicable", "variable_based_on_taxable_salary", 'type']
	for d in additional_components:
		struct_row = frappe._dict({'salary_component': d.salary_component})
		component = frappe.get_all("Salary Component", filters={'name': d.salary_component}, fields=component_fields)
		if component:
			struct_row.update(component[0])

		struct_row['deduct_full_tax_on_selected_payroll_date'] = d.deduct_full_tax_on_selected_payroll_date
		struct_row['is_additional_component'] = 1

		additional_components_list.append(frappe._dict({
			'amount': d.amount,
			'type': component[0].type,
			'struct_row': struct_row,
			'overwrite': d.overwrite_salary_structure_amount,
		}))
	return additional_components_list

@frappe.whitelist()
def get_additional_salary_component_with_salary_component(employee, start_date, end_date, component_type , component_list):
	additional_components = frappe.db.sql("""
		select salary_component, sum(amount) as amount, overwrite_salary_structure_amount, deduct_full_tax_on_selected_payroll_date
		from `tabAdditional Salary`
		where employee=%(employee)s
			and docstatus = 1
			and payroll_date between %(from_date)s and %(to_date)s
			and type = %(component_type)s
			and salary_component in %(component_list)s
		group by salary_component, overwrite_salary_structure_amount
		order by salary_component, overwrite_salary_structure_amount
	""", {
		'employee': employee,
		'from_date': start_date,
		'to_date': end_date,
		'component_type': "Earning" if component_type == "earnings" else "Deduction",
		'component_list' : component_list
	}, as_dict=1)

	additional_components_list = []
	component_fields = ["depends_on_payment_days", "salary_component_abbr", "is_tax_applicable", "variable_based_on_taxable_salary", 'type']
	for d in additional_components:
		struct_row = frappe._dict({'salary_component': d.salary_component})
		component = frappe.get_all("Salary Component", filters={'name': d.salary_component}, fields=component_fields)
		if component:
			struct_row.update(component[0])

		struct_row['deduct_full_tax_on_selected_payroll_date'] = d.deduct_full_tax_on_selected_payroll_date
		struct_row['is_additional_component'] = 1

		additional_components_list.append(frappe._dict({
			'amount': d.amount,
			'type': component[0].type,
			'struct_row': struct_row,
			'overwrite': d.overwrite_salary_structure_amount,
		}))
	return additional_components_list