# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class SocialInsuranceSettings(Document):
	pass





@frappe.whitelist()
def caculate_employee_insurance(employee,payrol_date, *args , **kwargs):
	component = None
	frappe.msgprint("wo")
	employee = frappe.get_doc("Employee" , employee)
	frappe.throw(str(employee))
	try :
		component = frappe.db.get_single_value("Social Insurance Settings" ,"salary_component")
		if not component :
			frappe.throw(_("Please Set Salary Component In Social Insurance Settings "))

	except:
		frappe.throw(_("Please Set Salary Component In Social Insurance Settings "))
	insurance_salary = get_employee_social_insurance (employee , payrol_date)
	return(insurance_salary)
def get_employee_social_insurance(employee , payroll_date):
	insurance_salary = frappe.db.sql(""" SELECT insurance_salary  FROM `tabEmployee Social Insurance Data` WHERE
	 employee ='%s' and docstatus=1 """%employee )
	return (insurance_salary)


