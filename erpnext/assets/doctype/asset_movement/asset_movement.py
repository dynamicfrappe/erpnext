# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class AssetMovement(Document):
	def validate(self):
		self.validate_asset()
		self.validate_location()
		self.validate_employee()

	def validate_asset(self):
		for d in self.assets:
			status, company = frappe.db.get_value("Asset", d.asset, ["status", "company"])
			if self.purpose == 'Transfer' and status in ("Draft", "Scrapped", "Sold"):
				frappe.throw(_("{0} asset cannot be transferred").format(status))

			if company != self.company:
				frappe.throw(_("Asset {0} does not belong to company {1}").format(d.asset, self.company))

			if not (d.source_location or d.target_location or d.from_employee or d.to_employee):
				frappe.throw(_("Either location or employee must be required"))

	def validate_location(self):
		for d in self.assets:
			if self.purpose in ['Transfer', 'Issue']:
				if not d.source_location:
					d.source_location = frappe.db.get_value("Asset", d.asset, "location")

				if not d.source_location:
					frappe.throw(_("Source Location is required for the Asset {0}").format(d.asset))

				if d.source_location:
					current_location = frappe.db.get_value("Asset", d.asset, "location")

					if current_location != d.source_location:
						frappe.throw(_("Asset {0} does not belongs to the location {1}").
							format(d.asset, d.source_location))
			
			if self.purpose == 'Issue':
				if d.target_location:
					frappe.throw(_("Issuing cannot be done to a location. \
						Please enter employee who has issued Asset {0}").format(d.asset), title="Incorrect Movement Purpose")
				if not d.to_employee:
					frappe.throw(_("Employee is required while issuing Asset {0}").format(d.asset))
			
			if self.purpose == 'Transfer':
				if d.to_employee:
					frappe.throw(_("Transferring cannot be done to an Employee. \
						Please enter location where Asset {0} has to be transferred").format(
							d.asset), title="Incorrect Movement Purpose")
				if not d.target_location:
					frappe.throw(_("Target Location is required while transferring Asset {0}").format(d.asset))
				if d.source_location == d.target_location:
					frappe.throw(_("Source and Target Location cannot be same"))
			
			if self.purpose == 'Receipt':
				# only when asset is bought and first entry is made
				if not d.source_location and not (d.target_location or d.to_employee):
					frappe.throw(_("Target Location or To Employee is required while receiving Asset {0}").format(d.asset))
				elif d.source_location:
					# when asset is received from an employee
					if d.target_location and not d.from_employee:
						frappe.throw(_("From employee is required while receiving Asset {0} to a target location").format(d.asset))
					if d.from_employee and not d.target_location:
						frappe.throw(_("Target Location is required while receiving Asset {0} from an employee").format(d.asset))
					if d.to_employee and d.target_location:
						frappe.throw(_("Asset {0} cannot be received at a location and \
							given to employee in a single movement").format(d.asset))

	def validate_employee(self):
		for d in self.assets:
			if d.from_employee:
					current_custodian = frappe.db.get_value("Asset", d.asset, "custodian")

					if current_custodian != d.from_employee:
						frappe.throw(_("Asset {0} does not belongs to the custodian {1}").
							format(d.asset, d.from_employee))
			
			if d.to_employee and frappe.db.get_value("Employee", d.to_employee, "company") != self.company:
				frappe.throw(_("Employee {0} does not belongs to the company {1}").
							format(d.to_employee, self.company))

	def on_submit(self):
		if self.reference_doctype == "Custody request" and self.reference_name != None :
			request_custody = frappe.get_doc("Custody request" ,self.reference_name)
			if request_custody.reference_document_type == "Department"  :
				
				for d in self.assets :
					# frappe.throw(request_custody.reference_document_name)
					data = frappe.db.sql("UPDATE `tabAsset` SET  department = '%s' WHERE name ='%s'"%(request_custody.reference_document_name, d.asset))
					frappe.db.commit()
			if request_custody.reference_document_type == "Project"  :
				for d in self.assets :
					# frappe.throw(request_custody.reference_document_name)
					data = frappe.db.sql("UPDATE `tabAsset` SET  project = '%s' WHERE name ='%s'"%(request_custody.reference_document_name, d.asset))
					frappe.db.commit()

			final = frappe.db.sql("UPDATE `tabCustody request` SET workflow_state = 'Completed' , docstatus = 1 WHERE name = '%s' "%self.reference_name)
			frappe.db.commit()
		if self.reference_doctype == "Assets Return" and self.reference_name != None :
			asset_return = frappe.get_doc("Assets Return" ,self.reference_name)
			if asset_return.reference_document_type == "Department"  :
				
				for d in self.assets :
					# frappe.throw(request_custody.reference_document_name)
					data = frappe.db.sql("UPDATE `tabAsset` SET  department = '',custodian = '' WHERE name ='%s'"%(d.asset))
					frappe.db.commit()
			if asset_return.reference_document_type == "Project"  :
				for d in self.assets :
					# frappe.throw(request_custody.reference_document_name)
					data = frappe.db.sql("UPDATE `tabAsset` SET  project = '' WHERE name ='%s'"%(d.asset))
					frappe.db.commit()
			if asset_return.reference_document_type == "Employee"  :
				for d in self.assets :
					# frappe.throw(request_custody.reference_document_name)
					data = frappe.db.sql("UPDATE `tabAsset` SET  custodian = '' WHERE name ='%s'"%(d.asset))
					frappe.db.commit()

			final = frappe.db.sql("UPDATE `tabCustody request` SET  workflow_state = 'Completed' ,docstatus = 1 WHERE name = '%s' "%self.reference_name)
			frappe.db.commit()
		self.set_latest_location_in_asset()
	
	def before_cancel(self):
		self.validate_last_movement()
		
	def on_cancel(self):
		self.set_latest_location_in_asset()
	
	def validate_last_movement(self):
		for d in self.assets:
			auto_gen_movement_entry = frappe.db.sql(
				"""
				SELECT asm.name
				FROM  `tabAsset Movement Item` asm_item, `tabAsset Movement` asm
				WHERE 
					asm.docstatus=1 and
					asm_item.parent=asm.name and
					asm_item.asset=%s and
					asm.company=%s and
					asm_item.source_location is NULL and
					asm.purpose=%s
				ORDER BY
					asm.transaction_date asc
				""", (d.asset, self.company, 'Receipt'), as_dict=1)

			if auto_gen_movement_entry and auto_gen_movement_entry[0].get('name') == self.name:
				frappe.throw(_('{0} will be cancelled automatically on asset cancellation as it was \
					auto generated for Asset {1}').format(self.name, d.asset))

	def set_latest_location_in_asset(self):
		current_location, current_employee = '', ''
		cond = "1=1"

		for d in self.assets:
			args = {
				'asset': d.asset,
				'company': self.company
			}

			# latest entry corresponds to current document's location, employee when transaction date > previous dates
			# In case of cancellation it corresponds to previous latest document's location, employee
			latest_movement_entry = frappe.db.sql(
				"""
				SELECT asm_item.target_location, asm_item.to_employee 
				FROM `tabAsset Movement Item` asm_item, `tabAsset Movement` asm
				WHERE 
					asm_item.parent=asm.name and
					asm_item.asset=%(asset)s and
					asm.company=%(company)s and 
					asm.docstatus=1 and {0}
				ORDER BY
					asm.transaction_date desc limit 1
				""".format(cond), args)
			if latest_movement_entry:
				current_location = latest_movement_entry[0][0]
				current_employee = latest_movement_entry[0][1]

			frappe.db.set_value('Asset', d.asset, 'location', current_location)
			frappe.db.set_value('Asset', d.asset, 'custodian', current_employee)



@frappe.whitelist() 
def get_items_from_custody_request(request,*args,**kwargs):
	frm =  frappe.get_doc("Custody request" , request)
	doc = frappe.db.sql("""  

		SELECT item FROM `tabCustody Request Item` WHERE parent ='%s'
		"""%request)
	employee = frappe.db.sql("SELECT reference_document_name ,reference_document_type,location FROM `tabCustody request` WHERE name ='%s'"%request)

	data = []
	data.append([doc])
	if frm.reference_document_type  in ["Employee" , "Department"]:

		data.append([employee[0][0]])
	if frm.reference_document_type == "Project":
		data.append(frm.employee)
	data.append([employee[0][1]])
	if len(employee[0] )> 2 :
		data.append([employee[0][2]])
	

	return data


@frappe.whitelist()
def get_department_location(request ,*args ,**kwargs):
	pass
try:
	if 'fleet' in frappe.get_active_domains():
		from dynamicerp.fleet.doctype.asset_movement.asset_movement import set_latest_location_in_asset
		from dynamicerp.fleet.doctype.asset_movement.asset_movement import on_submit
		AssetMovement.set_latest_location_in_asset = set_latest_location_in_asset
		AssetMovement.on_submit = on_submit
except :
	pass

