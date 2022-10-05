# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now, getdate, cast_fieldtype
from frappe import _
class LetterofGuarantee(Document):
	def renew_letter_of_grantee(self,start_date,end_date):
		if getdate(end_date) >getdate(now()):
			doc=frappe.new_doc("Letter of Guarantee")
			doc.date=start_date
			doc.end_date=end_date
			doc.bank_name=self.bank_name
			doc.client=self.client
			doc.lg_type=self.lg_type
			doc.number_of_lg=self.number_of_lg
			doc.cash_cover=self.cash_cover
			doc.facility=self.facility
			doc.total=self.total
			doc.cost_center=self.cost_center
			doc.save()
			self.staus="End"
			self.renewed=1
			frappe.msgprint(_("letter of grantee renewed successfully"))
		else:
			frappe.throw("please enter valid date")


def check_letter_of_grantee_date(*args,**kwargs):
	data=frappe.db.sql("""select name from `tabLetter of Guarantee` where CURDATE() > end_date""",as_dict=1)
	for d in data:
		# frappe.msgprint("asd")
		frappe.db.sql("""update  `tabLetter of Guarantee` set status='End' where name='%s'"""%d.name)
		frappe.db.commit()