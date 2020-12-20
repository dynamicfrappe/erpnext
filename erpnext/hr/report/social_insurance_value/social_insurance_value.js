// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Social Insurance Value"] = {
	"filters": [
		{

			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1 ,
			on_change: function() {

				frappe.query_report.set_filter_value("month", []);

			}

		},
		{

			"fieldname":"month",
			"label": __("month"),
			"fieldtype": "MultiSelectList",
			"get_data":function(txt) {
				return frappe.db.get_link_options("Payroll Month", txt ,
					{
						company: frappe.query_report.get_filter_value("company"),
						year: frappe.query_report.get_filter_value("year")
					});

			}

		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Select",
			"reqd": 1,
			on_change: function() {
				frappe.query_report.set_filter_value("month", []);
			}
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"get_query": function() {
					var company = frappe.query_report.get_filter_value('company');
					return {
						"doctype": "Employee",
						"filters": {
							"company": company,
						}
					}
				}
		},
		{
            'fieldname': "department",
            'label': __("Department"),
            'fieldtype': "Link",
			"options": "Department" ,
            "get_query": function() {
					var company = frappe.query_report.get_filter_value('company');
					return {
						"doctype": "Department",
						"filters": {
							"company": company,
						}
					}
				}
        }


	],
	"onload": function() {

		return  frappe.call({
			method: "erpnext.hr.report.income_tax_settlement.income_tax_settlement.get_attendance_years",
			callback: function(r) {
				var year_filter = frappe.query_report.get_filter('year');
				year_filter.df.options = r.message;
				year_filter.df.default = r.message.split("\n")[1];
				year_filter.refresh();
				year_filter.set_input(year_filter.df.default);
			}
		});
	}
};
