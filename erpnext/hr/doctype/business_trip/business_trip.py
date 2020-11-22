# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe import msgprint, _
class BusinessTrip(Document):

	def on_submit(self):
		leaveApplicationResult=frappe.db.sql("""
           select * from `tabLeave Application` where employee='{}' and (from_date between '{}' and '{}' or to_date between '{}' and '{}')
          
			""".format(self.employee,self.from_date,self.to_date,self.from_date,self.to_date),as_dict=1)
		BusinessTripResult=frappe.db.sql("""
           select * from `tabBusiness Trip` where employee='{}' and (from_date between '{}' and '{}' or to_date between '{}' and '{}')
          
			""".format(self.employee,self.from_date,self.to_date,self.from_date,self.to_date),as_dict=1)
		if (len(leaveApplicationResult)>0 or len(BusinessTripResult)>0):
			frappe.throw(_("Employee have Trip in the same time"))

		leave_approver=frappe.db.sql("""  select leave_approver from tabEmployee WHERE name = '%s'""" %self.employee)
		doc = frappe.new_doc('Leave Application')
		doc.employee=self.employee
		doc.employee_name=self.employee_name
		doc.leave_type=self.leave_type
		doc.from_date=datetime.strptime(self.from_date, '%Y-%m-%d')
		doc.posting_date=datetime.strptime(self.posting_date, '%Y-%m-%d')
		doc.to_date=datetime.strptime(self.to_date, '%Y-%m-%d')
		doc.description=self.description
		doc.company=self.company
		doc.status="Approved"
		doc.leave_approver=leave_approver[0][0]
		doc.save()
		doc.submit()

	
