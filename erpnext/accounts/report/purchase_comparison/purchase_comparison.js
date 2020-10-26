// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Comparison"] = {
	"filters": [
		{
			"fieldname":"Invoice_No",
			"label": __("Invoice No"),
			"fieldtype": "Link",
			"options": "Purchase Invoice"
		},
		{
			"fieldname":"Purchase_Order",
			"label": __("Purchase Order"),
			"fieldtype": "Link",
			"options": "Purchase Order"
		}
	]
};
