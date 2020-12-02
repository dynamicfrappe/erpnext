# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime,date
from frappe import msgprint, _
class EmployeeDocument(Document):

	def checkNotification(self):
		documents=frappe.db.sql("""select * from  `tabEmployee Document` where is_notified=0""",as_dict=1)
		for i in range(0,len(documents)):
			end_date=datetime.strptime(str(documents[i]["end_date"]), '%Y-%m-%d')
			#diff=end_date-(datetime.today())
			#frappe.msgprint(str(date.today()))
			diff=end_date-datetime.strptime(str(date.today()), '%Y-%m-%d')
			days=str(diff)
			day=days.split(' ')
			if(int(day[0])<=int(documents[i]["notificationperiod"])):
				frappe.db.sql("""update `tabEmployee Document` set is_notified=1 where name='{}'""".format(documents[i]["name"]))
				doc = frappe.new_doc('Employee Documents Notification')
				doc.emp_name=documents[i]["emp_name"]
				doc.document_type=documents[i]["document_type"]
				doc.start_date=documents[i]["start_date"]
				doc.end_date=documents[i]["end_date"]
				doc.save()
				frappe.db.commit()


