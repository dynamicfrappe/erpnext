# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime, timedelta


def execute(filters=None):
    columns, data = [], []
    columns = getColumns(filters)
    data = getdata(filters)
    return columns, data


def getColumns(filters):
    columns = [
        {
            'fieldname': "laondate",
            'label': _("Date"),
            'fieldtype': "Date",
            "width": 150
        },{
            'fieldname': "due_date",
            'label': _("Due Date"),
            'fieldtype': "Date",
            "width": 150
        },

        {
            'fieldname': "liabilities",
            'label': _("Liabilities"),
            'fieldtype': "Data",
            "width": 100
        },
		{
			'fieldname': "no_of_days",
			'label': _("No Of Days"),
			'fieldtype': "Data",
			"width": 100
		},
        {	'fieldname': "description",
			'label': _("Description"),
			'fieldtype': "Data",
			"width": 100

        },
        {
            'fieldname': "in",
            'label': _("IN"),
            'fieldtype': "Data",
            "width": 100
        },
        {
            'fieldname': "corridor_rate",
            'label': _("Corridor Rate"),
            'fieldtype': "float",
            "width": 120
        },
        {
            'fieldname': "interest_rate",
            'label': _("Interest Rate"),
            'fieldtype': "float",
            "width": 120
        },

        {
            'fieldname': "hdb",
            'label': _("HDB"),
            'fieldtype': "float",
            "width": 120
        },

        {
            'fieldname': "total",
            'label': _("Total"),
            'fieldtype': "Data",
            "width": 120
        },

    ]
    return columns


def getdata(filters):
    conditions = "where 1=1 "

    # if filters.get("company"):
    #     conditions += " and  company = %(company)s "
    #
    #     if filters.get("employee"):
    #         conditions += " and employee = %(employee)s "
    #     if filters.get("department"):
    #         conditions += " and department = %(department)s "
    #     if filters.get("driver"):
    #         conditions += " and driver = %(driver)s "
    #     if filters.get("from_date"):
    #         conditions += " and posting_date >= %(from_date)s  "
    #     if filters.get("to_date"):
    #         conditions += " and posting_date <= %(to_date)s "

    sql = """
                select
        * from `tabBank Loan`
        {conditions}

        """.format(conditions=conditions)
    # frappe.msgprint(str(sql))
    results = []
    results = frappe.db.sql(sql,as_dict=1)
    return results

