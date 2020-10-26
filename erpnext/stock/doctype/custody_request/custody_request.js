// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Custody request', {
    setup: function(frm) {
        frm.set_query("reference_document_type", function() {
            return {
                filters: {
                    name: ["in", ["Employee", "Department", "Customer", "Project"]]
                }
            };
        })



    },

    refresh: function(frm) {




        frm.add_custom_button(__("Create Asset Movement"), function() {
            frm.events.create_asset_movement(frm)

        }).addClass("btn-primary");
    },






    create_asset_movement: (frm) => {
        frappe.model.open_mapped_doc({

            method: "erpnext.stock.doctype.custody_request.custody_request.create_asset_movement",

            'frm': frm,
            'name': frm.doc.name,


        })


    },
    onload: function(frm) {

        frm.fields_dict.custody_request_item.grid.get_field('item').get_query =
            function() {
                return {
                    filters: {
                        "is_fixed_asset": 1

                    }
                }
            }


    },
    reference_document_type: (frm) => {
        if (frm.doc.employee_name) {
            frm.set_value("employee_name", '')
        }
        frm.set_value("reference_document_name", '')

    },
    reference_document_name: (frm) => {
        if (frm.doc.reference_document_type === "Employee" && frm.doc.reference_document_name.length > 0) {

            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Employee",
                    name: frm.doc.reference_document_name,
                },
                callback(r) {
                    if (r.message) {
                        var task = r.message;
                        frm.set_value("employee_name", task.employee_name)
                        frm.refresh_field("employee_name")

                    }
                }
            });






        }
    },

    required_date: function(frm) {
        if (frm.doc.required_date < frappe.datetime.get_today()) {
            frappe.throw(("You can not select past date in Reqired Date"));

        }
    }

});


frappe.ui.form.on('Custody Request Item', {
    // onload:function(frm){
    // 		frm.set_query("item" ,function (){
    // 			return {
    // 				filters :{
    // 					"is_fixed_asset":1
    // 				}
    // 			}
    // 		})

    // },

})