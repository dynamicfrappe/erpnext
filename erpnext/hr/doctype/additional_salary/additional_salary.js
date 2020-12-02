// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Additional Salary', {
	setup: function(frm) {
		frm.add_fetch("salary_component", "deduct_full_tax_on_selected_payroll_date", "deduct_full_tax_on_selected_payroll_date");

		frm.set_query("employee", function() {
			return {
				filters: {
					company: frm.doc.company,
					status:  "Active"
				}
			};
		});
	},
	salary_component:function(frm){
		frm.set_value("amount_based_on_formula" ,0)
		frm.set_df_property("count", "reqd", 0);
		frm.set_df_property("count", "hidden", 1);
		frm.set_value("count" ,0)
		frm.set_df_property("amount", "read_only", 0);
		frm.set_df_property("amount", "hidden", 0);
		frm.refresh_field("amount_based_on_formula")
		frm.refresh_field("count")
		frm.refresh_field("amount")


		if (frm.doc.salary_component){
			frappe.call({

				"method" :  "frappe.client.get_value" ,
				"args":{
					'doctype': "Salary Component" , 
					"filters":{
					"name":frm.doc.salary_component},
					fieldname:["amount_based_on_formula"]
				},
				callback:function(r){
					if(r.message.amount_based_on_formula){
						frm.set_value("amount_based_on_formula" ,1)
						frm.refresh_field("amount_based_on_formula")
						frm.set_df_property("count", "hidden", 0);
						frm.set_df_property("count", "reqd", 1);
						frm.refresh_field("count")
						frm.set_value("amount" ,1)
						frm.set_df_property("amount", "read_only", 1);
						frm.set_df_property("amount", "hidden", 1);
						frm.refresh_field("amount")

					}
				}
			})
		}
	}
});
