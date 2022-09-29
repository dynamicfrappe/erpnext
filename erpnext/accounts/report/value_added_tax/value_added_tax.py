# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []
    columns = getColumns(filters)
    data = getdata(filters)
    return columns, data


def getColumns(filters):
    columns = [
        {
            'fieldname': "type",
            'label': _("Invoice Type"),
            'fieldtype': "Data",
            "hidden": 1
        },
        {
            'fieldname': "invoice_name",
            'label': _("Invoice"),
            'fieldtype': "Dynamic Link",
            'options': "type",
            "width": 250
        },
        {
            'fieldname': "posting_date",
            'label': _("Date"),
            'fieldtype': "Date",
            "width": 250
        },
        {
            'fieldname': "name",
            'label': _("Partner"),
            'fieldtype': "Data",
            "width": 250
        },
        # {
        #     'fieldname': "total",
        #     'label': _("Total"),
        #     'fieldtype': "float",
        #     "width": 75
        # },
        # {
        #     'fieldname': "net_total",
        #     'label': _("Net Total"),
        #     'fieldtype': "float",
        #     "width": 75
        # },
        {
            'fieldname': "tax_rate_positive",
            'label': _("Tax Rate"),
            'fieldtype': "float",
            "width": 250
        },
        {
            'fieldname': "tax_amount_positive",
            'label': _("Tax Amount"),
            'fieldtype': "float",
            "width": 250
        }
		# ,
        # {
        #     'fieldname': "tax_rate_negative",
        #     'label': _("Tax Rate -"),
        #     'fieldtype': "float",
        #     "width": 80
        # },
        # {
        #     'fieldname': "tax_amount_negative",
        #     'label': _("Tax Amount -"),
        #     'fieldtype': "float",
        #     "width": 120
        # },
        # {
        #     'fieldname': "discount_amount",
        #     'label': _("Discount"),
        #     'fieldtype': "float",
        #     "width": 100
        # }
    ]
    return columns


def getdata(filters):
    conditions = "where invoice.is_return = 0 and invoice.total > 0 "
    if filters.get("Company"):
        conditions = " and invoice.`company` =%(Company)s"
        if filters.get("from_date"):
            conditions += " and invoice.posting_date >=%(from_date)s"
        if filters.get("to_date"):
            conditions += " and invoice.posting_date <=%(to_date)s"
        sales_invoices = frappe.db.sql("""

                SELECT
                            'Sales Invoice' as type,
							invoice.`name`  as invoice_name ,
							invoice.posting_date,
							invoice.customer_name as name ,
							customer.tax_id ,
							invoice.total,
							invoice.net_total,
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

                            {conditions}
							GROUP BY
							invoice.`name`
			""".format(conditions=conditions), filters, as_dict=1)

        sales_invoices_totals = frappe.db.sql("""
        SELECT IFNULL(SUM(case when taxes.tax_amount > 0 then taxes.tax_amount else 0 END), 0) as tax_amount_positive,
                               IFNULL(SUM(case when taxes.tax_amount < 0 then ((taxes.tax_amount * -1 )) else 0 END), 0)
                                   + IFNULL((select SUM(IFNULL(note.discount_amoint, 0))
                                             from `tabDiscount Note` note
                                             where note.document_type = invoice.name
                                               and note.type = "Sales Invoice"
                                               and note.docstatus = 1), 0)                           as tax_amount_negative
                        FROM `tabSales Invoice` invoice
                                 INNER JOIN
                             `tabSales Taxes and Charges` taxes
                             ON
                                 invoice.`name` = taxes.parent
                                                    {conditions}

            			""".format(conditions=conditions), filters, as_dict=1)

        sales_total_row = frappe._dict()
        sales_total_row["name"] = "<b> Sales Invoices Total</b>"
        sales_total_row['tax_amount_positive'] = "<b> " + str(sales_invoices_totals[0].tax_amount_positive) + "</b>"
        sales_total_row['tax_amount_negative'] = "<b> " + str(sales_invoices_totals[0].tax_amount_negative) + "</b>"

        empty_row = frappe._dict()
        sales_invoices.append(empty_row)
        sales_invoices.append(sales_total_row)
        empty_row = frappe._dict()
        sales_invoices.append(empty_row)

        Purchase_invoices = frappe.db.sql("""

        SELECT
                                    'Purchase Invoice' as type,
        							invoice.`name`  as invoice_name ,
        							invoice.posting_date,
        							invoice.supplier_name as name ,
        							supplier.tax_id ,
        							invoice.total,
        							invoice.net_total,
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
                                    {conditions}
        							GROUP BY
        							invoice.`name`


        			""".format(conditions=conditions), filters, as_dict=1)
        purchase_invoices_totals = frappe.db.sql("""
                        SELECT IFNULL(SUM(case when taxes.tax_amount > 0 then taxes.tax_amount  else 0 END),
                                      0)                                   as tax_amount_positive,
                               IFNULL(SUM(case when taxes.tax_amount < 0 then ((taxes.tax_amount * -1)) else 0 END), 0)
                                   + IFNULL((select SUM(IFNULL(note.discount_amoint, 0))
                                             from `tabDiscount Note` note
                                             where note.document_type = invoice.name
                                               and note.type = "Sales Invoice"
                                               and note.docstatus = 1), 0) as tax_amount_negative


                        FROM `tabPurchase Invoice` invoice
                                 INNER JOIN
                             `tabPurchase Taxes and Charges` taxes
                             ON
                                 invoice.`name` = taxes.parent
                            {conditions}
            			""".format(conditions=conditions), filters, as_dict=1)

        purchase_total_row = frappe._dict()
        purchase_total_row["name"] = "<b> Purchase Invoices Total</b>"
        purchase_total_row['tax_amount_positive'] = "<b> " + str(
            purchase_invoices_totals[0].tax_amount_positive) + "</b>"
        purchase_total_row['tax_amount_negative'] = "<b> " + str(
            purchase_invoices_totals[0].tax_amount_negative) + "</b>"
        empty_row = frappe._dict()
        Purchase_invoices.append(empty_row)
        Purchase_invoices.append(purchase_total_row)
        empty_row = frappe._dict()
        Purchase_invoices.append(empty_row)

        results = sales_invoices + Purchase_invoices

        total_row = frappe._dict()
        total_row['name'] = "<b> Total Taxes </b>"
        total_row['tax_amount_positive'] = "<b> " + str(
            sales_invoices_totals[0].tax_amount_positive - purchase_invoices_totals[0].tax_amount_positive) + "</b>"
        total_row['tax_amount_negative'] = "<b> " + str(
            purchase_invoices_totals[0].tax_amount_negative - sales_invoices_totals[0].tax_amount_negative) + "</b>"
        results.append(total_row)
        return results
