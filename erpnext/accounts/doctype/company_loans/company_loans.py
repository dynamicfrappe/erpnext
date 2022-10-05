# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import datetime
class CompanyLoans(Document):

	def show_payment_shedule(self):
		if self.no_of_days  and self.due_date  and self.the_number_of_payments_made and self.total :
			start_days=datetime.datetime.strptime(self.date,'%Y-%m-%d')
			date =datetime.datetime.strptime(self.due_date,'%Y-%m-%d')
			numofpyments=int(self.the_number_of_payments_made)
			total=float(self.total)
			amountscedules=float(total)/float(numofpyments)
			numofdays=int(self.no_of_days)
			for i in range(0,int(numofpyments)):
				date += datetime.timedelta(days=numofdays)
				row = self.append("payment_shedules", {})
				row.date=date
				row.amount=amountscedules

			return "success"
		return"failed"

		


        


		

