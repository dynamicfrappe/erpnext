// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Operations Settings', {

	onload: function(frm) {

	    frm.set_query("one_invoice_item_service",  function(doc) {
            return {
                filters: {
                    "item_group": "Services"
                }
            };
		});
	}
	,
	refresh: function(frm) {}
});
