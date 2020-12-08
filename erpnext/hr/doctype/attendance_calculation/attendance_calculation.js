// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Calculation', {
	setup:function (frm){
		frm.set_query('payroll_month', function(doc) {
			return {
				filters: {
					"is_closed": 0,
					"docstatus":1
				}
			};
		});
	},
	payroll_month:function(frm) {
		if (frm.doc.payroll_month){
			frappe.call({

					method:"frappe.client.get" ,
					args:{
   						doctype: "Payroll Month",
   						name : frm.doc.payroll_month


   				   			},callback:function(r){

   				   				if (r.message)
								{
									if (r.message.docstatus != 1 || r.message.is_closed  )
										frm.doc.payroll_month = null
								}
   				   				frm.refresh_field("payroll_month")

   				   			}
				})
		}
	},
	refresh: function(frm) {


		 	if (!frm.is_new()) {
			 	if (frm.doc.docstatus == 0){

					frm.add_custom_button(__("Calculate"),
									function() {
										frm.events.Calculate_attendance(frm);	

									}).addClass("btn-primary");
			 	}
			 	else{

			 		if (frm.doc.payroll_month){
			frappe.call({

					method:"frappe.client.get" ,
					args:{
   						doctype: "Payroll Month",
   						name : frm.doc.payroll_month


   				   			},callback:function(r){

   				   				if (r.message)
								{
									if (r.message.docstatus == 1 || ! r.message.is_closed  )
										frm.add_custom_button(__("Post Additional Salaries"),
										function() {
										frm.events.Post_attendance(frm);

									}).addClass("btn-primary");
								}
   				   				frm.refresh_field("payroll_month")

   				   			}
				})
		}


			 		// frm.add_custom_button(__("Post Additional Salaries"),
					// 				function() {
					// 					frm.events.Post_attendance(frm);
					//
					// 				}).addClass("btn-primary");
			 	}
		 	}

			frappe.realtime.on('update_progress', (data) => {

				    frappe.show_progress(__('Calculating Attendance'),  data.progress , data.total,__('Calculating Attendance'))
			});


	},

	Calculate_attendance: function (frm) {

								frappe.call({
											doc: frm.doc,
											method: "Calculate_attendance",
											
											callback: function(r) {
												// frappe.msgprint(__("Done"))
												frappe.hide_progress()

											},
											freeze: true
										});
	},
	Post_attendance: function (frm) {

								frappe.call({
											doc: frm.doc,
											method: "on_submit",

											callback: function(r) {
												// frappe.msgprint(__("Done"))
												frappe.hide_progress()

											},
											freeze: true
										});
	}
});
