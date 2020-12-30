# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate
from frappe.model.document import Document
from frappe.utils import getdate, validate_email_address, today, add_years, format_datetime, cstr
import datetime
from dateutil.relativedelta import relativedelta
class Vehicle(Document):
	def validate(self):
		pass
		# if getdate(self.start_date) > getdate(self.end_date):
		# 	frappe.throw(_("Insurance Start date should be less than Insurance End date"))
		# if getdate(self.carbon_check_date) > getdate():
		# 	frappe.throw(_("Last carbon check date cannot be a future date"))

	def checkLicenceValidation(self,endDtae):
		if getdate(endDtae) > getdate(today()):
			return 'true'
		return 'false'
