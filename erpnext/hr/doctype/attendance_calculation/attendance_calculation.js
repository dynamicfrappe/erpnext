// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Calculation', {
	 refresh: function(frm) {

		 	if (!frm.is_new()) {
			 	if (frm.doc.docstatus == 0){
					frm.add_custom_button(__("Calculate"),
									function() {
										frappe.call({
											doc: frm.doc,
											method: "Calculate_attendance",
											
											callback: function(r) {
												frappe.msgprint(__("Done"))
											}
										});
									}).addClass("btn-primary");
			 	}
			}

	 }
});
