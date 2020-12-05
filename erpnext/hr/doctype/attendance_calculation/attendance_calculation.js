// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Calculation', {
	refresh: function(frm) {

		 	if (!frm.is_new()) {
			 	if (frm.doc.docstatus == 0){

					frm.add_custom_button(__("Calculate"),
									function() {
										frm.events.Calculate_attendance(frm);	

									}).addClass("btn-primary");
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
								}
});
