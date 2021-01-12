# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from frappe import _
from frappe.utils import comma_and, validate_email_address

sender_field = "email_id"

class DuplicationError(frappe.ValidationError): pass

class JobApplicant(Document):
	def get_user_roles(self):
		status_no = 0
		list = frappe.db.sql("""
			select user , agreement_type from `tabJob openening Approvrer` where parent = '{parent}' order by idx asc
		""".format(parent = self.job_title),as_dict=1)
		if list:
			status_list = [x.agreement_type for x in list]
			frappe.msgprint(str(status_list))
			frappe.msgprint(self.workflow_status)
			# user_list =  [x.user for x in list]
			if self.workflow_status == 'Pending' :
				status_no = 0
			else:
				if self.workflow_status in status_list:

					status_no = status_list.index(self.workflow_status)
				if status_no == len(status_list) -1 :
					return
			return  list [status_no]
	def update_action (self, status , user , action):
		if action == "Approve":
			if status == "HR":
				self.workflow_status = "HR Accepted"
			if status == "Technical":
				self.workflow_status = "Technical Accepted"
			if status == "Mangerial":
				self.workflow_status = "Mangerial Accepted"
		else :

			if status == "HR":
				self.workflow_status = "HR Rejected"
			if status == "Technical":
				self.workflow_status = "Technical Rejected"
			if status == "Mangerial":
				self.workflow_status = "Mangerial Rejected"
		self.save()

	def onload(self):
		job_offer = frappe.get_all("Job Offer", filters={"job_applicant": self.name})
		if job_offer:
			self.get("__onload").job_offer = job_offer[0].name

	def autoname(self):
		keys = filter(None, (self.applicant_name, self.email_id, self.job_title))
		if not keys:
			frappe.throw(_("Name or Email is mandatory"), frappe.NameError)
		self.name = " - ".join(keys)

	def validate(self):
		self.check_email_id_is_unique()
		if self.email_id:
			validate_email_address(self.email_id, True)

		if not self.applicant_name and self.email_id:
			guess = self.email_id.split('@')[0]
			self.applicant_name = ' '.join([p.capitalize() for p in guess.split('.')])


	def check_email_id_is_unique(self):
		if self.email_id:
			names = frappe.db.sql_list("""select name from `tabJob Applicant`
				where email_id=%s and name!=%s and job_title=%s""", (self.email_id, self.name, self.job_title))

			if names:
				frappe.throw(_("Email Address must be unique, already exists for {0}").format(comma_and(names)), frappe.DuplicateEntryError)

