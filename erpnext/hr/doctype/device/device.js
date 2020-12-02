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
											frm.refresh(frm)
										}
									});
								}).addClass("btn-primary");
				frm.add_custom_button(__("Map Employees"),
								function() {
									frappe.call({
										method: "erpnext.hr.doctype.device.device.map_employees",
										callback: function(r) {
											frm.refresh(frm)
										}
									});
								}).addClass("btn-primary");
		 	}
		}
	}
});
