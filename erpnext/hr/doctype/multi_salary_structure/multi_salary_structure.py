# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate,today
from frappe import _
from frappe.model.document import Document

class Multisalarystructure(Document):
	def validate(self):
		self.validate_dates()
		if getdate(self.from_date) >getdate(today()):
			self.status="closed"

	def validate_dates(self):
		joining_date, relieving_date = frappe.db.get_value("Employee", self.employee,
			["date_of_joining", "relieving_date"])

		for st in self.salary_structure:
			if st.from_date:
				if frappe.db.exists("Salary structure Template", {"type": st.type, "from_date": st.from_date, "docstatus": 1,"employee":self.employee}):
					frappe.throw(_("Salary Structure Assignment for Employee already exists"))
				if joining_date and getdate(st.from_date) < joining_date:
					frappe.throw(_("From Date {0} cannot be before employee's joining Date {1}")
					.format(st.from_date, joining_date))
				if relieving_date and getdate(self.from_date) > relieving_date and not self.flags.old_employee:
					frappe.throw(_("From Date {0} cannot be after employee's relieving Date {1}")
					.format(st.from_date, relieving_date))
	def updateStatus(self):
		frappe.db.sql("update `tabMulti salary structure` set status='closed' where name='{}'".format(self.name))

	def checkSalryStructureComponent(self,salaryStructure):
		currentSalaryStructure=frappe.db.sql("select * from `tabSalary Detail` where parent='{}'".format(salaryStructure),as_dict=1)
		#frappe.msgprint(str(currentSalaryStructure))
		for S in self.salary_structure:			
			nextsalarystructure=frappe.db.sql("select * from `tabSalary Detail` where parent='{}'".format(S.salary_structure),as_dict=1)
			#frappe.msgprint(str(nextsalarystructure))
			if nextsalarystructure:
				for css in currentSalaryStructure:
					for nss in nextsalarystructure:
						if css.salary_component==nss.salary_component and salaryStructure!=S.salary_structure:
							return "false"
								
		return 'true'
	def getEmployeeSalaryStructure(self):
		mylist = []
		for salaryStructure in self.salary_structure:
			mylist.append(salaryStructure.salary_structure)
		return mylist

	def getcomponentValue(self,SalayDetails):
		#salarycomponentValue=frappe.db.sql("select amount from `tabSalary Detail` where salary_component='{}'".format(SalayDetails))
		for c in self.component:
			if c.componentname==SalayDetails:
				salarycomponentValue={"amount":c.amount}

		return salarycomponentValue
	def getAllSalaryStructureComponent(self):
		data=[]
		for ss in self.salary_structure:
			data +=frappe.db.sql("select salary_component,amount from `tabSalary Detail` where parent='{}'".format(ss.salary_structure),as_dict=1)
		for d in data:
			row=self.append("component",{})
			row.componentname=d.salary_component
			row.amount=d.amount
		return data

	def setSalaryComponent(self,salaryStructure):
		datalilslist=[]
		if salaryStructure:
			salaryStructureList=salaryStructure.split('-')
		salaryDetaills=frappe.db.sql("select salary_component from `tabSalary Detail` where parent='{}'".format(salaryStructureList[0]),as_dict=1)
		if salaryDetaills:
			for sd in salaryDetaills:
				datalilslist.append(sd['salary_component'])
		
		return datalilslist

	def updateComponentTable(self,component,amount,oldValue,date):
		frappe.db.sql("update `tabMulti salary structure` set docstatus=0 where name='{}'".format(self.name))
		self.from_date=date
		row=self.append("history",{})
		row.component=component
		row.amount=oldValue
		self.docstatus=1
		self.save()
		frappe.db.sql("update `tabSalary Components` set amount='{}' where componentname='{}' and parent='{}'".format(amount,component,self.name))

	def RenewDocument(self,date,newValue,salaryStructure,salaryDetails):
		frappe.db.sql("update `tabMulti salary structure` set status='closed' where name='{}'".format(self.name))
		doc = frappe.new_doc('Multi salary structure')
		doc.employee=self.employee
		doc.employee_name=self.employee_name
		doc.department=self.department
		doc.company=self.company
		doc.from_date=date
		doc.designation=self.designation
		doc.income_tax_slab=self.income_tax_slab
		doc.base=self.base
		doc.variable=self.variable
		doc.save()
		frappe.db.commit()
		for salarySructure in self.salary_structure:
			row=doc.append("salary_structure",{})
			row.salary_structure=salarySructure.salary_structure
			row.from_date=date
			row.type=salarySructure.type
			row.employee=salarySructure.employee
		doc.save()
		frappe.db.commit()
		frappe.db.sql("update `tabSalary Detail` set amount='{}' where salary_component='{}'".format(newValue,salaryDetails))






def get_assigned_salary_structure(employee, on_date):
	if not employee or not on_date:
		return None
	salary_structure = frappe.db.sql("""
		select salary_structure from `Salary structure Template`
		where employee=%(employee)s
		and docstatus = 1
		and %(on_date)s >= from_date order by from_date desc limit 1""", {
			'employee': employee,
			'on_date': on_date,
		})
	return salary_structure[0][0] if salary_structure else None

