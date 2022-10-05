// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Operations Invoice Dues', {
    onload: function(frm) {
        frm.get_field("items").grid.cannot_add_rows = true;
       

	},
	refresh: function(frm) {
        if (!frm.doc.invoiced)
        {
             frm.add_custom_button(__('Operations Invoice'),function (frm) {
                 frappe.call({
                     method: "create_invoice",
                     doc:cur_frm.doc,
                     callback: function(r){
                         frm.refresh()
                     }
                 })
             },__('Create'))
        }
	}
});

frappe.ui.form.on('Operations Invoice Dues Items', {
	items_add: function(frm,cdt,cdn) {
	    var  d = locals [cdt] [cdn]
	    // frm.fields_dict["items"].grid.grid_rows[d.idx- 1].remove();
        // frappe.throw(__("Cann't Add"))
    },
    before_items_remove: function(frm,cdt,cdn) {
        // frappe.throw(__("Cann't Delete"))
    },
    status: function(frm,cdt,cdn) {
        // frappe.throw(__("Cann't Delete"))
        frappe.call({
            method : "set_totals",
            doc : frm.doc,
            callback:function (r) {
                frm.refresh()
            }
        })
    }
});
