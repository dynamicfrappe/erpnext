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
            'fieldname': "date",
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
        {	'fieldname': "transaction",
			'label': _("Transaction"),
			'fieldtype': "Data",
			"width": 100

        },
        {
            'fieldname': "cost_center",
            'label': _("Cost Center"),
            'fieldtype': "Data",
            "width": 100
        },
        {
            'fieldname': "bank_name",
            'label': _("Bank Name"),
            'fieldtype': "Data",
            "width": 120
        },
        {
            'fieldname': "description",
            'label': _("Description"),
            'fieldtype': "Data",
            "width": 120
        },

        {
            'fieldname': "bank__currency",
            'label': _("Bank  Currency"),
            'fieldtype': "float",
            "width": 120
        },

        {
            'fieldname': "out",
            'label': _("Out"),
            'fieldtype': "Data",
            "width": 120
        },
        {
            'fieldname': "rate",
            'label': _("Rate"),
            'fieldtype': "Data",
            "width": 120
        },

    ]
    return columns


def getdata(filters):
    conditions = "where 1=1 "


    sql = """
                select
        * from `tabBank Deposite`
        {conditions}

        """.format(conditions=conditions)
    # frappe.msgprint(str(sql))
    results = []
    results = frappe.db.sql(sql,as_dict=1)
    return results

