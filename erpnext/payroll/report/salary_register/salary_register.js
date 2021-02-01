// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Salary Register"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(),-1),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"to_date",
			"label": __("To"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname": "currency",
			"fieldtype": "Link",
			"options": "Currency",
			"label": __("Currency"),
			"default": erpnext.get_currency(frappe.defaults.get_default("Company")),
			"width": "50px"
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "100px"
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"width": "100px",
			"reqd": 1
		},
		{
			"fieldname":"docstatus",
			"label":__("Document Status"),
			"fieldtype":"Select",
			"options":["Draft", "Submitted", "Cancelled"],
			"default": "Submitted",
			"width": "100px"
		}
	],
	"onload": function(report) {
		// let date = new Date();
		// date.setDate(1)
		// frappe.query_report.set_filter_value('from_date',date)
		report.page.add_inner_button(__("Export to Exel"), function() {
			// printAttendanceSheetDetails(report);
			let d = new frappe.ui.Dialog({
    title: 'Enter details',
    fields: [
    	  {
            label: 'From Date',
            fieldname: 'fromDate',
            fieldtype: 'Date',

        },
		{
            label: 'Bank',
            fieldname: 'bank',
            fieldtype: 'Link',
			 "options":"Bank"
        },

		{

            fieldname: 'cbreak',
            fieldtype: 'Column Break',

        },
			 {
            label: 'To Date',
            fieldname: 'toDate',
            fieldtype: 'Date',

        },

        {
            label: 'Bank Template',
            fieldname: 'template',
            fieldtype: 'Select',
			 "options": "QNB\nCIB\nHSBC",
        },

    ],
			primary_action_label: 'Export',
			primary_action(values) {
				frappe.call({
					method: "erpnext.hr.utils.bankSheet",
					args:{
						"fromDate":values.fromDate,
						"toDate":values.toDate,
					},
					callback(r){
						console.log(r.message)
					}
				})

				d.hide();
			}
		});

		d.show();

		});

	}

}

