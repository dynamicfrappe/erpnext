# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime

class ValueAddedTax(Document):
	def on_submit(self):
		frappe.db.sql("update `tabTax Period Details` set date='{}' where parent='{}' and refdoc='{}' and taxclass='{}'".format(self.postingdate,self.docname,self.name,self.taxtype))
	def updateDocStatus(self):
		frappe.db.sql("update `tabValue Added Tax` set docstatus=1 where name='{}'".format(self.name))
		return "done"
	def createJournalEntry(self):
		Accountdata = { "data":[]}
		myTable=self.details
		for i in myTable:
			Amount = 0
			Account={}
			if i.taxcategory in [x["name"] for x in Accountdata["data"]] and i.taxtype in [x["taxtype"] for x in Accountdata["data"]]:
				continue
			Account["name"] = i.taxcategory
			Account["partner_type"]=i.partner_type
			Account["partner"]=i.partner
			Account["category"]=i.taxcategory
			Account["partner_type"]=i.partner_type
			Account["partner"]=i.partner
			if not i.taxtype:
				Account["taxtype"] = "Collected"
			else:
				Account["taxtype"] = i.taxtype
			for j in myTable:
				if i.taxcategory==j.taxcategory and i.taxtype==j.taxtype:
					Amount+=abs(j.taxamount)
			Account["Amount"]=Amount
			Accountdata["data"].append(Account)
		if self.collectedtax <self.paidtax:
			doc = frappe.new_doc('Journal Entry')
			doc.posting_date = datetime.today().strftime('%Y-%m-%d')
			row = doc.append("accounts", {})
			for acc in Accountdata["data"]:
				if acc["taxtype"]=="Paid":
					row = doc.append("accounts", {})
					row.account = acc["category"]
					row.party_type = acc["partner_type"]
					row.party = acc["partner"]
					row.credit_in_account_currency = abs(acc["Amount"])
			row = doc.append("accounts", {})
			row.account=self.accountname
			row.debit_in_account_currency=abs(self.collectedtax)
			doc.save()
			frappe.msgprint("Created")
			return "true"


		doc = frappe.new_doc('Journal Entry')
		doc.posting_date=datetime.today().strftime('%Y-%m-%d')
		for z in Accountdata["data"]:
			#frappe.msgprint("type="+str(z["taxtype"]))
			if z["taxtype"]=="Collected":
				row = doc.append("accounts", {})
				row.account = z["category"]
				row.party_type=z["partner_type"]
				row.party=z["partner"]
				row.debit_in_account_currency = abs(z["Amount"])
				#frappe.msgprint("collected"+str(z["Amount"]))
			else:
				#frappe.msgprint("typepaid=" + str(z["taxtype"]))
				row = doc.append("accounts", {})
				row.account = z["category"]
				row.party_type = z["partner_type"]
				row.party = z["partner"]
				row.credit_in_account_currency = abs(z["Amount"])

				#frappe.msgprint("paid"+str(z["Amount"]))
		# for p in Accountdata["data"]:
		# 	if p["taxtype"] == "Paid":
		# 		row = doc.append("accounts", {})
		# 		row.account = p["category"]
		# 		row.credit_in_account_currency=abs(p["Amount"])
		# 		frappe.msgprint(str(z["Amount"]))

		Row = doc.append("accounts", {})
		Row.account=self.accountname
		Row.credit_in_account_currency=abs(self.clearanceamount)
		#frappe.msgprint("clearence"+str(self.clearanceamount))

		doc.save()
		doc2=frappe.new_doc('Journal Entry')
		doc2.posting_date = datetime.today().strftime('%Y-%m-%d')
		row2=doc2.append("accounts",{})
		row2.account=self.account
		row2.credit_in_account_currency=abs(self.collectedtax)
		row3 = doc2.append("accounts", {})
		row3.account = self.accountname
		row3.debit_in_account_currency = abs(self.collectedtax)
		doc2.save()
		frappe.msgprint("done")
		frappe.db.sql("update `tabValue Added Tax` set journal_created=1,status='Closed',docstatus=1 where name='{}'".format(self.name))
		frappe.db.sql("update `tabTax Period Details` set date='{}' where parent='{}' and refdoc='{}' and taxclass='{}'".format(self.postingdate, self.docname, self.name,self.taxtype))
		frappe.msgprint("Journal Entry Created")
		# for m in Accountdata["data"]:
		# 	frappe.msgprint(str(m))
		return "true"








	def getTaxes(self,fromDate,todate):
		data=frappe.db.sql("select * from `tabValue Added Tax` where ((fromdae between '{}' and '{}') or (todate between '{}' and '{}')) and status='Closed' and taxtype='{}'".format(fromDate,todate,fromDate,todate,self.taxtype))
		if data and self.docstatus==0:
			frappe.throw("already exist")
		condition=""
		if self.taxtype:
			condition+= "and taxes.tax_class='{}'".format(self.taxtype)
		collected=0
		paid=0

		sales_invoices = frappe.db.sql("""

		                SELECT
		                            'Sales Invoice' as type,
									invoice.`name`  as invoice_name ,
									invoice.due_date,
									invoice.customer_name as name ,
									customer.tax_id ,
									invoice.total,
									invoice.net_total,
									invoice.tax_category,
									taxes.account_head,
									taxes.tax_class,
									taxes.tax_amount as 'tax_amount',
									IFNULL(SUM(case when  taxes.rate > 0 then taxes.rate  else 0 END ),0) as tax_rate_positive,
									IFNULL(SUM(case when  taxes.tax_amount > 0 then taxes.tax_amount else 0 END ),0) as tax_amount_positive,
		       						IFNULL(SUM(case when  taxes.rate < 0 then taxes.rate * -1  else 0 END ),0) as tax_rate_negative,
									IFNULL(SUM(case when  taxes.tax_amount < 0 then ((taxes.tax_amount * -1))   else 0 END ),0)
		                             + IFNULL((select SUM(IFNULL(note.discount_amoint,0)) from `tabDiscount Note` note where note.document_type = invoice.name and note.type = "Sales Invoice" and note.docstatus = 1 ),0) as tax_amount_negative
		                            , CAST(IFNULL(invoice.discount_amount,0) AS CHAR) as discount_amount

								FROM
									`tabSales Invoice` invoice
									INNER JOIN
									`tabSales Taxes and Charges` taxes
									ON
										invoice.`name` = taxes.parent
									INNER JOIN
									  tabCustomer  customer
									ON
									  invoice.customer = customer.`name`

		                           where invoice.due_date >='{}' and invoice.due_date <='{}' and invoice.docstatus=1  {condition}      
									GROUP BY
									invoice.`name`, taxes.tax_amount
					""".format(fromDate,todate,self.taxtype,condition=condition), as_dict=1)

		sales_invoices += frappe.db.sql("""

		SELECT
		                            'Purchase Invoice' as type,
									invoice.`name`  as invoice_name ,
									invoice.due_date,
									invoice.supplier_name as name ,
									supplier.tax_id ,
									invoice.total,
									invoice.net_total,
									invoice.tax_category,
									taxes.account_head,
									taxes.tax_amount as 'tax_amount',
									taxes.tax_class,
									IFNULL(SUM(case when  taxes.rate > 0 then taxes.rate  else 0 END ),0) as tax_rate_positive,
									IFNULL(SUM(case when  taxes.tax_amount > 0 then taxes.tax_amount else 0 END ),0) as tax_amount_positive,
		       						IFNULL(SUM(case when  taxes.rate < 0 then taxes.rate * -1  else 0 END ),0) as tax_rate_negative,
									IFNULL(SUM(case when  taxes.tax_amount < 0 then ((taxes.tax_amount * -1))   else 0 END ),0)
		                             + IFNULL((select SUM(IFNULL(note.discount_amoint,0)) from `tabDiscount Note` note where note.document_type = invoice.name and note.type = "Sales Invoice" and note.docstatus = 1 ),0) as tax_amount_negative
		                            , CAST(IFNULL(invoice.discount_amount,0) AS CHAR) as discount_amount

								FROM
									`tabPurchase Invoice` invoice
									INNER JOIN
									`tabPurchase Taxes and Charges` taxes
									ON
										invoice.`name` = taxes.parent
									INNER JOIN
									  tabSupplier  supplier
									ON
									  invoice.supplier = supplier.`name`
		                             where invoice.due_date >='{}' and invoice.due_date <='{}' and invoice.docstatus=1 {condition}
									GROUP BY
									invoice.`name`, taxes.tax_amount


					""".format(fromDate,todate,self.taxtype,condition=condition),as_dict=1)

		for inv in sales_invoices:
			row=self.append("details",{})
			row.doocumenttpe=inv.type
			row.documentnumber=inv.invoice_name
			row.partner_type='Supplier' if inv.type == "Purchase Invoice" else 'Customer'
			row.partner=inv.name
			row.docdate=inv.due_date
			row.cadno=inv.tax_id
			row.docamount=inv.total
			row.taxamount=abs(inv.tax_amount)
			row.taxcategory=inv.account_head
			row.taxclass=inv.tax_class
			if (inv.type=='Sales Invoice' and float(inv.tax_amount)>0) or  (inv.type=='Purchase Invoice' and float(inv.tax_amount)<0):
				row.taxtype="Collected"
				collected+=abs(inv.tax_amount)
			if (inv.type == 'Sales Invoice' and float(inv.tax_amount) < 0) or (inv.type == 'Purchase Invoice' and float(inv.tax_amount) > 0):
				row.taxtype="Paid"
				paid+=abs(inv.tax_amount)
		self.collectedtax=collected
		self.paidtax=paid
		self.clearanceamount=collected-paid

		return "true"


