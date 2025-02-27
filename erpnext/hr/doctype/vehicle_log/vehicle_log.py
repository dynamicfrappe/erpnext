# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cstr
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from frappe.utils import getdate, validate_email_address, today, add_years, format_datetime, cstr

class VehicleLog(Document):
	def validate(self):
		odoreading=self.odometer or 0
		for	service in self.service_detail:
			if float(service.odometer_reading) >float(odoreading):
				self.odometer=service.odometer_reading
				self.date=getdate(today())
		result=frappe.db.sql("""select type, max(odometer_reading) as 'r' 
		 from `tabVehicle Service` where parent='%s' group by type order by odometer_reading DESC"""%self.name,as_dict=1)
		card_name = frappe.db.sql("""select name from `tabVehicle Card` where vehicle='%s'""" % self.license_plate, as_dict=1)
		if card_name:
			count=0
			doc = frappe.get_doc("Vehicle Card", card_name[0].name)
			# frappe.msgprint(str(card_name[0].name))
			# for s in result:
			# 	if s.type==doc.maintainance[count].maintainance:
			# 		doc.maintainance[count].odometer_reading=s.r
			# 	count+=1
			for s in result:
				for d in doc.maintainance:
					if s.type==d.maintainance and s.r >d.odometer_reading:
						d.odometer_reading=s.r
			doc.save()


		# if flt(self.odometer) < flt(self.last_odometer):
		# 	frappe.throw(_("Current Odometer Value should be greater than Last Odometer Value {0}").format(self.last_odometer))

	def on_submit(self):
		frappe.db.set_value("Vehicle", self.license_plate, "last_odometer", self.odometer)
		for mainten in self.service_detail:
			if not mainten.odometer_reading:
				frappe.throw("You must enter Odometer Reading")
			if not mainten.expense_amount:
				frappe.throw("You must enter expense amount")
			if not mainten.price:
				frappe.throw("You must enter price")

	def on_cancel(self):
		distance_travelled = self.odometer - self.last_odometer
		if(distance_travelled > 0):
			updated_odometer_value = int(frappe.db.get_value("Vehicle", self.license_plate, "last_odometer")) - distance_travelled
			frappe.db.set_value("Vehicle", self.license_plate, "last_odometer", updated_odometer_value)

@frappe.whitelist()
def make_expense_claim(docname):
	pass
	expense_claim = frappe.db.exists("Expense Claim", {"vehicle_log": docname})
	if expense_claim:
		frappe.throw(_("Expense Claim {0} already exists for the Vehicle Log").format(expense_claim))

	vehicle_log = frappe.get_doc("Vehicle Log", docname)
	service_expense = sum([flt(d.expense_amount) for d in vehicle_log.service_detail])

	claim_amount = service_expense + (flt(vehicle_log.price) * flt(vehicle_log.fuel_qty) or 1)
	if not claim_amount:
		frappe.throw(_("No additional expenses has been added"))

	exp_claim = frappe.new_doc("Expense Claim")
	exp_claim.employee = vehicle_log.employee
	exp_claim.vehicle_log = vehicle_log.name
	exp_claim.remark = _("Expense Claim for Vehicle Log {0}").format(vehicle_log.name)
	exp_claim.append("expenses", {
		"expense_date": vehicle_log.date,
		"description": _("Vehicle Expenses"),
		"amount": claim_amount
	})
	return exp_claim.as_dict()
