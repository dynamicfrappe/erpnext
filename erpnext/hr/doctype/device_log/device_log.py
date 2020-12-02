# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class DeviceLog(Document):
	def after_insert (self):
		self.map_employees()
	def map_employees(self):
		frappe.db.sql("""update `tabDevice Log` log set employee = (select name from `tabEmployee` where attendance_device_id = log.enroll_no)
			where employee is null """)