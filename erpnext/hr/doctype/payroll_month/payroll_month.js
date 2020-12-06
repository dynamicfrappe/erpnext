// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll Month', {
	// refresh: function(frm) {

	// }
	onload:function(frm){
		frappe.call({
			method: "get_attendance_years",
			doc : frm.doc,
			callback: function(r) {
				frm.set_df_property("year", "options", r.message );
				refresh_field("year");
			}
		});

		

	},

	refresh: function(frm) {
	if (frm.doc.docstatus == 1){
			
				frm.add_custom_button(__("Create Payroll"), function() {
					frm.events.create_payroll(frm)
						
					}).addClass("btn-primary");
		}
	},
	create_payroll:function(frm){
		var dialog = new frappe.ui.Dialog({
			title: __("Payroll Type "),
			fields: [
				{	"fieldtype": "Select", "label": __("Payroll"),
					"fieldname": "payroll_type",
					"options": ["A" , "B"],
					"reqd": 1,
					 },
				{	"fieldtype": "Button", "label": __('Create Payroll Entrs'),
					"fieldname": "create_payroll_entry", "cssClass": "btn-primary" },
			]
		});
		dialog.fields_dict.create_payroll_entry.$input.click(function() {
			var args = dialog.get_values();
			console.log(args)
			dialog.hide();
		})
		dialog.show()

	},
	month:function(frm){
		frappe.call({
			doc:frm.doc ,
			"method":"month_for_year" ,
			callback:function(r){
				if (!r.message){
					var mo = frm.doc.month
					frm.set_value("month" ," ")
					frappe.throw((" year " + frm.doc.year + "Already Have Month " + mo ))
				}
			}
		})

	},
	start_date:function(frm){
		frappe.call({
			doc:frm.doc ,
			"method":"set_end_date" ,
			callback:function(r){
				frm.set_value("end_date" ,r.message)
				frm.refresh_field("end_date")
			}
		})
	}
});
