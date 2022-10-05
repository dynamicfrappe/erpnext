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
            'fieldname': "end_date",
            'label': _("End Date"),
            'fieldtype': "Date",
            "width": 150
        },

        {
            'fieldname': "bank_name",
            'label': _("Bank Name"),
            'fieldtype': "Data",
            "width": 100
        },
		{
			'fieldname': "client",
			'label': _("Client"),
			'fieldtype': "Data",
			"width": 100
		},
        {	'fieldname': "lg_type",
			'label': _("LG Type"),
			'fieldtype': "Data",
			"width": 100

        },
        {
            'fieldname': "number_of_lg",
            'label': _("Number Of LG"),
            'fieldtype': "Data",
            "width": 100
        },
        {
            'fieldname': "cash_cover",
            'label': _("Cash Cover"),
            'fieldtype': "float",
            "width": 120
        },
        {
            'fieldname': "facility",
            'label': _("Facility"),
            'fieldtype': "float",
            "width": 120
        },

        {
            'fieldname': "total",
            'label': _("Total"),
            'fieldtype': "float",
            "width": 120
        },

        {
            'fieldname': "cost_center",
            'label': _("Cost Center"),
            'fieldtype': "Data",
            "width": 120
        },

    ]
    return columns


def getdata(filters):
    conditions = "where 1=1 "

    sql = """
                select
        * from `tabLetter of Guarantee`
        {conditions}

        """.format(conditions=conditions)
    # frappe.msgprint(str(sql))
    results = []
    results = frappe.db.sql(sql,as_dict=1)
    return results

