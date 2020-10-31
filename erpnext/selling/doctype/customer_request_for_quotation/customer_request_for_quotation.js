// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Request for Quotation', {
    onload: function(frm) {

        if (frm.doc.docstatus == 1) {

            frm.add_custom_button(__("Create Quotation"), function() {
                frm.events.create_Quotation(frm)

            }).addClass("btn-primary");

        }



    },
    refresh: function(frm) {



        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__("Create Quotation"), function() {
                frm.events.create_Quotation(frm)

            }).addClass("btn-primary");

        }



    },
    create_Quotation: (frm) => {
        frappe.model.open_mapped_doc({
            method: "erpnext.selling.doctype.customer_request_for_quotation.customer_request_for_quotation.create_quotation",
            'frm': frm,

            'name': frm.doc.name







        });

    }
});