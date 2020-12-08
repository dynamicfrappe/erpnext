# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
from datetime import  datetime
class PayrollMonth(Document):
	def get_attendance_years(self):
		year = datetime.today().year
		year_list = range(2019 ,year+2 )
		return "\n".join(str(x) for x in year_list)
