// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Order Based On Quotation"] = {
	"filters": [
		
		{
			fieldname: "Company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd :1,
			default: frappe.defaults.get_user_default("Company")
		},
		{
			fieldname: "Quotation",
			label: __("Quotation"),
			fieldtype: "Link",
			options: "Quotation",
			"get_query": function(){

				return {'filters': [['Quotation', 'company','=', frappe.query_report.get_filter_value("Company") ]]}

			}
		}

	]
};
