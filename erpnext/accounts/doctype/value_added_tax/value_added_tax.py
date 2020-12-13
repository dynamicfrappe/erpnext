# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ValueAddedTax(Document):
	def getTaxes(self,fromDate,todate):
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
									taxes.tax_amount,
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

		                           where invoice.due_date >='{}' and invoice.due_date <='{}'         
									GROUP BY
									invoice.`name`
					""".format(fromDate,todate), as_dict=1)

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
									taxes.tax_amount,
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
		                             where invoice.due_date >='{}' and invoice.due_date <='{}'
									GROUP BY
									invoice.`name`


					""".format(fromDate,todate),as_dict=1)

		for inv in sales_invoices:
			row=self.append("details",{})
			row.doocumenttpe=inv.type
			row.documentnumber=inv.invoice_name
			row.partner_type='Supplier' if inv.type == "Purchase Invoice" else 'Customer'
			row.partner=inv.name
			row.docdate=inv.due_date
			row.cadno=inv.tax_id
			row.docamount=inv.total
			row.taxamount=inv.tax_amount
			row.taxcategory=inv.account_head
			if (inv.type=='Sales Invoice' and float(inv.tax_amount)>0) or  (inv.type=='Purchase Invoice' and float(inv.tax_amount)<0):
				row.taxtype="Collected"
				collected+=inv.tax_amount
			else:
				row.taxtype="Paid"
				paid+=inv.tax_amount
		self.collectedtax=collected
		self.paidtax=paid
		self.clearanceamount=collected-paid

		return "true"


