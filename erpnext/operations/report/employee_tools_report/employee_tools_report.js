// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Tools Report"] = {
	"filters": [
					{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options":"Employee"

		},
		{
			"fieldname":"customer_agreement",
			"label": __("Customer Agreement"),
			"fieldtype": "Link",
			"options":"Customer Agrement"

		},
		{
			"fieldname":"item_status",
			"label": __("item Status"),
			"fieldtype": "Select",
			"options":["Delivered","Returned"]


		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options":"Customer"
		},

	]
};
