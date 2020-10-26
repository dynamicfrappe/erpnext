// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */




frappe.query_reports["Request for Quotation Analytics"] = {


	
	


	"filters": [
	{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			fieldname: "r_f_q",
			label: __("Request for Quotation"),
			fieldtype: "Link",
			options: "Request for Quotation",
			
			reqd: 1
		},
		{
			fieldname:"Test",
			label:__("test"),
			fieldtype:"Select",

			options:["test"]
		}



	]

	
};
