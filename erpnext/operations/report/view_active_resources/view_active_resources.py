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
            "label": _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 100
        },
        {
            "label": _("Employee Name"),
            "fieldname": "employee_name",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Salary"),
            "fieldname": "salary",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Total Monthly Fee"),
            "fieldname": "total_monthly_fee",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Total Monthly Fee"),
            "fieldname": "total_monthly_fee",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Cost Center"),
            "fieldname": "cost_center",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100
        },

    ]

    return columns


def get_data(filters):
    condition = " where 1=1"
    if filters.get("employee"):
        condition += " and employee='%s'" % filters.get("employee")
    if filters.get("cost_center"):
        condition += " and cost_center='%s'" % filters.get("cost_center")
    if filters.get("status"):
        condition += " and status='%s'" % filters.get("status")

    results = frappe.db.sql("""  
               select employee,employee_name,salary,
       total_monthly_fee,cost_center,status

    from `tabCustomer Agrement Resources`
			{condition}
	""".format(condition=condition), as_dict=1)

    return results

