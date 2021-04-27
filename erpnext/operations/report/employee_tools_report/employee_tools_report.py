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
            "width": 150
        },
        {
            "label": _("Employee Name"),
            "fieldname": "employee_name",
            "fieldtype": "Date",
            "width": 150
        },
        {
            "label": _("Customer Agreement"),
            "fieldname": "customer_agreement",
            "fieldtype": "Link",
            "options":"Customer Agreement",
            "width": 150
        },

        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Item"),
            "fieldname": "item",
            "fieldtype": "Link",
            "options":"Item",
            "width": 150
        },
        {
            "label": _("QTY"),
            "fieldname": "qty",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Item Status"),
            "fieldname": "item_status",
            "fieldtype": "Data",
            "width": 150
        },

    ]

    return columns


def get_data(filters):
    condition = " where 1=1"
    if filters.get("employee"):
        condition += " and employee='%s'" % filters.get("employee")
    if filters.get("customer_agreement"):
        condition += " and child.customer_agrement='%s'"%filters.get("customer_agreement")
    if filters.get("item_status"):
        condition += " and child.status='%s'"%filters.get("item_status")
    if filters.get("customer"):
        condition += " and child.customer='%s'"%filters.get("customer")

    results = frappe.db.sql("""  
               select employee,employee_name,customer_agreement,child.item_code as 'item',child.status as 'item_status',
               child.qty as 'qty',child.customer as 'customer',child.customer_agrement as 'customer_agrement'
                from `tabEmployee Tools`
                inner join `tabEmployee Tools Item` child
                on child.parent=`tabEmployee Tools`.name
                {condition}
                group by employee, employee_name, customer_agreement, child.item_code, child.status, child.qty, child.customer
			
	""".format(condition=condition), as_dict=1)

    return results

