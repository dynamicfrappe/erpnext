// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Request for expence claim', {
    setup: function(frm) {
		frappe.call({
            method:"getEmployee",
            doc:frm.doc,
            callback(r){
                frm.set_query("employee", function() {
			return {
				filters: [
					["Employee","name", "in", r.message]
				]
			}
		});
            }
        })
	}
});