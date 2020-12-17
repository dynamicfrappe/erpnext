// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Device', {
	


	 refresh: function(frm) {
	 	frappe.realtime.on('update_progress', (data) => {
	 				frappe.show_progress(__('Getting Logs'),  data.progress , data.total,__('Getting Logs'))


		});

	 	if (!frm.is_new()) {
		 	if (frm.doc.is_active){
				frm.add_custom_button(__("Get Attendance"),
								function() {
									frappe.call({
										doc:frm.doc,
										method: "get_attendance",
										freeze: true,
										callback: function(r) {
											// frappe.hide_progress();
											frappe.msgprint(__("Done"));
											frm.refresh();




										}
									});
								}).addClass("btn-primary");
				frm.add_custom_button(__("Map Employees"),
								function() {
									frappe.call({
										method: "erpnext.hr.doctype.device.device.map_employees",
										freeze: true,
										callback: function(r) {

											frapp.msgprint(__("Done"));
											frm.refresh();
										}
									});
								}).addClass("btn-primary");
		 	}
		}
	}
});
