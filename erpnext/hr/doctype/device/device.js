// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Device', {
	


	 refresh: function(frm) {
	 	if (!frm.is_new()) {
		 	if (frm.doc.is_active){
				frm.add_custom_button(__("Get Attendance"),
								function() {
									frappe.call({
										method: "erpnext.hr.doctype.device.device.get_attendance",
										args: {
											device_name: frm.doc.name,
										},
										callback: function(r) {
											
										}
									});
								}).addClass("btn-primary");
		 	}
		}
	}
});
