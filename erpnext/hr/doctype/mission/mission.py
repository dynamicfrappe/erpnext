# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _
class Mission(Document):

	def on_submit(self):
		result=frappe.db.sql("""select * from tabMission where employee='{}' and (start_time between '{}' and '{}' or end_time between '{}' and '{}') and date='{}'""".format(self.employee,self.start_time,self.end_time,self.start_time,self.end_time,self.date),as_dict=1)
		if(len(result)>0):
			
			frappe.throw(_("Employee have mission in the same time"))

	
