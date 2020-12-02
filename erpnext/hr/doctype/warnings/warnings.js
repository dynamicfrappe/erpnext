// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warnings', {
	// refresh: function(frm) {

	// }
    onload:function (frm){
        frm.trigger("get_description")
    },
    type : function (frm){
        frm.trigger("get_description")
    },
    get_description : function (frm){
        if (frm.doc.type)
        {
            frappe.call({
				 async: false,
				 method: "frappe.client.get",
				 args: {
					 "doctype": "Warnings Types",

					 "name": frm.doc.type // fieldname to be fetched
				 },
				 callback: function (res) {
					 if (res.message) {
					 	debugger;
						frm.doc.type_description  = res.message.warning_name;

					 }
				 }
			 });
        }else {
        	frm.doc.type_description  = ""
		}
        refresh_field("type_description")
    }
});
