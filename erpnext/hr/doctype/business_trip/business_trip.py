# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe import msgprint, _
class BusinessTrip(Document):

	def validate(self):
		leaveApplicationResult=frappe.db.sql("""
           select * from `tabLeave Application` where employee='{}' and (from_date between '{}' and '{}' or to_date between '{}' and '{}')
            and docstatus=1
			""".format(self.employee,self.from_date,self.to_date,self.from_date,self.to_date),as_dict=1)
		BusinessTripResult=frappe.db.sql("""
           select * from `tabBusiness Trip` where employee='{}' and (from_date between '{}' and '{}' or to_date between '{}' and '{}')
           and docstatus=1
			""".format(self.employee,self.from_date,self.to_date,self.from_date,self.to_date),as_dict=1)
		if  BusinessTripResult:
			frappe.throw(_("Employee have Trip in the same time"))
		if leaveApplicationResult:
			frappe.throw(_("Employee have Leave  in the same time"))


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

	
	def updateStaus(self):
		EmpDepartment=frappe.db.sql("""
          select department from tabEmployee where name='{}'
			""".format(self.employee),as_dict=1)
		rolelist=frappe.db.sql("""
          select * from `tabDepartment Managment` where parent='{}'
			""".format(EmpDepartment[0]['department']),as_dict=1)
		docstatus=frappe.db.sql("""
              select status from `tabBusiness Trip` where name='{}'
			""".format(self.name),as_dict=1)
		rolee=""
		mylist=[]
		#index=0
		flag=0
		issubmitable=0
		#frappe.msgprint(rolelist[0].email)
		#frappe.throw(str(frappe.session.user))
		#frappe.msgprint(docstatus[0]["status"])
		for role in rolelist:
			
			#frappe.msgprint(frappe.session.user_email)
			#mylist.append(role.role_name)
			if role.email==str(frappe.session.user):
				rolee=role.role_name
				#index=len(mylist)
			if role.is_submitted ==1 and role.email==str(frappe.session.user):
				issubmitable=1
		
		if docstatus[0]["status"]=="Created" and rolee=="SuperVisor Approved":
			flag=1
		elif docstatus[0]["status"]=="SuperVisor Approved" and rolee=="Manager Approved":
			flag=1
		else:
			profile=frappe.db.sql("select role_profile_name from tabUser where name='{}'".format(str(frappe.session.user)),as_dict=1)
			#frappe.msgprint(profile[0]['role_profile_name'])
			if profile[0]['role_profile_name']=='hr' and docstatus[0]["status"]=="Manager Approved":
				flag=1
				rolee='Completed'
			else:
				flag=0
			
	
		if(flag==1):
			return rolee
		else:
			return 'false'


	def updateAction(self,Action):

		res1=frappe.db.sql("""update `tabBusiness Trip` set status='{}' where name='{}'""".format(Action,self.name))
		frappe.db.commit()
		if(Action=='Completed'):
			#frappe.msgprint(Action)
			frappe.db.sql("""update `tabBusiness Trip` set docstatus=1 where name='{}'""".format(self.name))
			frappe.db.commit()
			return "Done"
		if res1:
			return 'True'
		return res1