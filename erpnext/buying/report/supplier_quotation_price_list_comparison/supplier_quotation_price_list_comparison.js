// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplier Quotation Price List Comparison"] = {
	"filters": [
		{
			"fieldname":"RFQ_No",
			"label": __("RFQ No"),
			"fieldtype": "Link",
			"options": "Request for Quotation"
		}
	]
};
