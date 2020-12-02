// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Violations', {
	setup: function(frm) {
		frm.set_query("salary_component", function() {
			return {
				filters: {
					"type": "Deduction",
					"amount_based_on_formula": 1
				}
			}
		});
	},
	 refresh: function(frm) {

	//frm.trigger("toggle_feilds");
    },
	onload: function(frm) {

	//frm.trigger("toggle_feilds");
    },
    penality_type:function(frm){

	//frm.trigger("toggle_feilds");
	},


   toggle_feilds:function (frm){

	 	var flag = false
    	if (frm.doc.penality_type)
		{
			 frappe.call({
				 async: false,
				 method: "frappe.client.get",
				 args: {
					 "doctype": "Penality Type",

					 "name": frm.doc.penality_type // fieldname to be fetched
				 },
				 callback: function (res) {
					 if (res.message) {
						if (res.message.code == 1)
						{
							flag = true
						}


					 }
				 }
			 });
		}
    	frm.toggle_reqd("penality_rules",flag == true);
    	frm.toggle_display("penality_rules", flag == true);
   }

});
