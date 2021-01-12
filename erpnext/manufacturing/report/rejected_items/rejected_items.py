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
            'fieldname': "Code",
            'label': _("Item Code"),
            'fieldtype': "Link",
            'options': "Item",
            "width": 170
        },
        {
            'fieldname': "itemName",
            'label': _("Item Name"),
            'fieldtype': "Data",
            "width": 150
        },
        {
            'fieldname': "Wo",
            'label': _("Work Order"),
            'fieldtype': "Link",
            'options': 'Work Order',
            "width": 200
        },
        {
            'fieldname': "date",
            'label': _("Date"),
            'fieldtype': "Date",
            "width": 100
        },
        {
            'fieldname': "rejWarehouse",
            'label': _("Rejected Warehouse"),
            'fieldtype': "Link",
            'options': 'Warehouse',
            "width": 200
        },
        {
            'fieldname': "rejectedQ",
            'label': _("Qty"),
            'fieldtype': "float",
            "width": 50
        },
        {
            'fieldname': "reason",
            'label': _("Reason"),
            'fieldtype': "Data",
            "width": 100
        },


    ]
    return columns


def getdata(filters):
        conditions = ""
        if filters.get("Wo"):
            conditions +=" and work_order='{}'".format(filters.get("Wo"))
        if filters.get("fromdate"):
            conditions += "and posting_date >= '{}'".format(filters.get("fromdate"))
        if filters.get("tomdate"):
            conditions += "and posting_date <= '{}'".format(filters.get("todate"))

        results = frappe.db.sql("""
					select item_code as 'Code'
                 ,item_name as 'itemName'
                 ,work_order as 'Wo'
                 ,posting_date as 'date',
                   `tabStock Entry`.rejected_warehouse as 'rejWarehouse',
                   rejected_quantity as 'rejectedQ',
                   reason_of_rejection as 'reason'
            from `tabStock Entry Detail`
            inner join
                `tabStock Entry`
                on `tabStock Entry Detail`.parent=`tabStock Entry`.name
            where `tabStock Entry`.rejected=1 and `tabStock Entry Detail`.t_warehouse !=`tabStock Entry`.rejected_warehouse
                    {conditions}
			""".format(conditions =conditions))
        return results