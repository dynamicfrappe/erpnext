# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data    = get_data(filters)
	return columns, data


def get_columns(filters):
	columns = [
		{
			"label": _("Document Name"),
			"fieldname": "docName",
			"fieldtype": "Link",
			"options": "Employee Document",
			"width": 150
		},
		{
			"label": _("Document Type"),
			"fieldname": "docType",
			"fieldtype": "Link",
			"options":"Employee document type",
			"width": 150
		},
		{
			"label": _("Is Recived"),
			"fieldname": "isRecived",
			"fieldtype": "Check",
			"width": 150
		},
		{
			"label": _("Recived By"),
			"fieldname": "RecivedBy",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 150
		},


	]

	return columns


def get_data(filters):
	results = []
	if filters.get("employee"):
		results = frappe.db.sql("""  
		 select name as 'docName',document_type as 'docType',is_recived as 'isRecived',recived_by as 'RecivedBy' from `tabEmployee Document` where employee='{}'
		""".format(filters.get("employee")),as_dict=1)

	return results
