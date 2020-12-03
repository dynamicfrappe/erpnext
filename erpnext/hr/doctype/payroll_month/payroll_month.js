// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll Month', {
	// refresh: function(frm) {

	// }
    setup: function(frm) {
		frm.trigger("get_years");
	 },
	 get_years: function(frm) {
		return  frappe.call({
			method: "get_attendance_years",
			doc : frm.doc,
			callback: function(r) {
				debugger;
				frm.set_df_property("year", "options", r.message );
				refresh_field("year");
			}
		});
	}
});
