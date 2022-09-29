# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    columns = [
        {
            "label": _("item_code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 100
        },
        {
            "label": _("QTY"),
            "fieldname": "qty",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Rate"),
            "fieldname": "rate",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Total Amount"),
            "fieldname": "total_amount",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Intersest Precentagefor Year"),
            "fieldname": "intersest_precentagefor_year",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Monthly Installment"),
            "fieldname": "monthly_installment",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Monthly Fee"),
            "fieldname": "monthly_fee",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Proejct"),
            "fieldname": "proejct",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Cost Center"),
            "fieldname": "cost_center",
            "fieldtype": "Data",
            "width": 100
        },

    ]

    return columns


def get_data(filters):
    condition = " where 1=1"
    if filters.get("item_code"):
        condition += " and item_code='%s'" % filters.get("item_code")
    if filters.get("proejct"):
        condition += " and proejct='%s'" % filters.get("proejct")
    if filters.get("cost_center"):
        condition += " and cost_center='%s'" % filters.get("cost_center")

    results = frappe.db.sql("""  
                select item_code,item_name,
       qty,rate,total_amount,
       intersest_precentagefor_year,
       monthly_installment,
       monthly_fee,
       proejct,
       cost_center,
       case when finishedinstallment=1 then "Paid"
        end as status

    from `tabCustomer Agrement Tools`
			{condition}
	""".format(condition=condition), as_dict=1)

    return results

