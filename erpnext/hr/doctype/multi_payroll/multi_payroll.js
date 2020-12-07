// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Multi Payroll', {
	refresh: function(frm) {
		if (frm.doc.docstatus == 0 && frm.doc.employees.length == 0) {
			if(!frm.is_new()) {
				frm.page.clear_primary_action();
				frm.add_custom_button(__("Get Employees"),
					function() {
						frm.events.get_employee_details(frm);
					}
				).toggleClass('btn-primary', !(frm.doc.employees || []).length);
			}





		}
		if (frm.doc.docstatus == 0 && frm.doc.employees.length > 0) {

			if(!frm.is_new()) {

				frm.page.clear_primary_action();
				frm.add_custom_button(__("Create Salary Slip "),
					function() {
						frm.events.get_employee_details(frm);
					}
				).toggleClass('btn-primary', !(frm.doc.employees || []).length);


			}
		}

	},



	get_employee_details: function (frm) {
		return frappe.call({
			doc: frm.doc,
			method: 'fill_employee_details',
			callback: function(r) {
				if (r.docs[0].employees){
					frm.save();
					frm.refresh();
					if(r.docs[0].validate_attendance){
						render_employee_attendance(frm, r.message);
					}
				}
			}
		})
	},
});
