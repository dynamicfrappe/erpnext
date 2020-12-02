# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Permission(Document):

	def validate(self):
		department=frappe.db.sql("""select department from tabEmployee where name='{}'""".format(self.name),as_dict=1)
		if not department:
			frappe.throw("employee have no department")

	def updateStaus(self):
		EmpDepartment=frappe.db.sql("""
          select department from tabEmployee where name='{}'
			""".format(self.employee),as_dict=1)
		rolelist=frappe.db.sql("""
          select * from `tabDepartment Managment` where parent='{}'
			""".format(EmpDepartment[0]['department']),as_dict=1)
		docstatus=frappe.db.sql("""
              select status from tabPermission where name='{}'
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
		if docstatus :
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

		res1=frappe.db.sql("""update `tabPermission` set status='{}' where name='{}'""".format(Action,self.name))
		frappe.db.commit()
		if(Action=='Completed'):
			#frappe.msgprint(Action)
			frappe.db.sql("""update `tabPermission` set docstatus=1 where name='{}'""".format(self.name))
			frappe.db.commit()
			return "Done"
		if res1:
			return 'True'
		return res1
