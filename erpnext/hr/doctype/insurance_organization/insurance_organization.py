# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class InsuranceOrganization(Document):
	pass





@frappe.whitelist()
def get_jinja_data(doc):
	return frappe.db.sql("""select * from `tabEmployee Social Insurance Data` where employee_strat_insurance_date < DATE_SUB(CURDATE (), INTERVAL 1 YEAR)  order by insurancenumber Asc`""",as_dict=True)
