// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Social Insurance Settings', {
	setup: function(frm) {
		frm.set_query("salary_component", () => {
			return {
				filters: {
					type: "Deduction"
				}
			};

		})

	}
});
