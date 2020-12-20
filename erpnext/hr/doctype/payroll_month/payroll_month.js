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

		frm.events.set_dates(frm);



	},

	refresh: function(frm) {
	if (frm.doc.docstatus == 1){


				if (!frm.doc.is_closed)
				{
					frm.add_custom_button(__("Close Month"), function() {
					frm.events.close_month(frm);

					}).addClass("btn-primary");
					frm.add_custom_button(__("Create Payroll"), function() {
					frm.events.create_payroll(frm)

					}).addClass("btn-primary");
				}

		}
		// frm.events.set_dates(frm);
	},
	year:function(frm){
		frm.events.set_dates(frm);
	},
	Company:function(frm){
		frm.events.set_dates(frm);
	}
	,
	create_payroll:function(frm){


		var dialog = new frappe.ui.Dialog({

			title: __("Payroll Type "),
			fields: [
				{
					"fieldtype": "Select", "label": __("By Type"),
					"fieldname": "search_type",
					"options": ["ALL" , "By Department" ],
					"reqd": 1,
					onchange() {
						if(dialog.get_value('search_type') ){
							frappe.call({
								doc:frm.doc,
								method: 'get_strcuture_type_option',
							}).then(r => {
								dialog.set_df_property("payroll_type", "options", r.message)
						});
						}
						if(dialog.get_value('search_type') == "By Department"){
							dialog.set_df_property("department", "reqd", 1)
							dialog.set_df_property("department", "hidden",0)
						}
						if(dialog.get_value('search_type') == "ALL"){
							dialog.set_df_property("department", "hidden", 1)
							dialog.set_df_property("department", "reqd", 0)
						}
					}
				},

				{

					"fieldtype": "Select", "label": __("Payroll"),
					"fieldname": "payroll_type",
					"options":[],
					"reqd": 1,
				},
				{

					"fieldtype": "Link", "label": __("Department"),
					"fieldname": "department",
					"options":'Department',
					"reqd": 0,
				}
					 ,
				{	"fieldtype": "Button", "label": __('Create Payroll Entrs'),
					"fieldname": "create_payroll_entry", "cssClass": "btn-primary" },
			]
		});

		dialog.fields_dict.create_payroll_entry.$input.click(function() {
			var args = dialog.get_values();
			console.log(args.payroll_type)
			frm.events.make_payroll_entry(frm , args.search_type,args.payroll_type, args.department)
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
		frm.events.set_dates(frm);

	},

	make_payroll_entry: function(frm ,serach,frc ,department) {

		frappe.call({
				method: "erpnext.hr.doctype.payroll_month.payroll_month.make_payroll_entry",
				args:{
							"name":frm.doc.name,
							"type":serach,
			             	"frcv" : frc,
		                	"department":department
			                },

				callback:function(r){
					frappe.set_route("Form", "Multi Payroll", r.message);
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
	},
	attendance_start_date:function(frm){
		frappe.call({
			doc:frm.doc ,
			"method":"set_attendance_end_date" ,
			callback:function(r){
				frm.set_value("attendance_end_date" ,r.message)
				frm.refresh_field("attendance_end_date")
			}
		})
	},
	set_dates : function (frm) {
		if (frm.is_new())
		{
					frappe.call({
					method: "set_start_date",
					doc : frm.doc,
					callback: function(r) {
							refresh_field("start_date");
							refresh_field("attendance_start_date");
							refresh_field("end_date");
							refresh_field("attendance_end_date");
							refresh_field("month");
							refresh_field("year");
							frm.refresh();
						}
					});
		}
	},
	close_month : function (frm) {
		frappe.confirm( __('Are you sure you want to Close This Payroll Month?') , () => {

			frappe.call({
						method: "close_month",
						doc : frm.doc,
						callback: function(r) {
								refresh_field("is_closed")
								frm.refresh();
							}
						});

		}, () => {} )



	}
});
