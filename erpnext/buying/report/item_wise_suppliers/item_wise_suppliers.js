// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Wise Suppliers"] = {
	 "filters": [

      {
			"fieldname":"Supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options":"Supplier"

		},
		{
			"fieldname":"fromDate",
			"label": __("From Date"),
			"fieldtype": "Date"
			

		},

			{
			"fieldname":"toDate",
			"label": __("To Date"),
			"fieldtype": "Date"
			

		},


    ]
};
