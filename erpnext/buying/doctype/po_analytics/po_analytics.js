// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["po analytics"] = {
    "filters": [

      {
			"fieldname":"PurchaseOrder",
			"label": __("PurchaseOrder"),
			"fieldtype": "Link",
			"options":"Purchase Order"

		},
		{
			"fieldname":"Date",
			"label": __("Date"),
			"fieldtype": "Date"
			

		},

    ]
};