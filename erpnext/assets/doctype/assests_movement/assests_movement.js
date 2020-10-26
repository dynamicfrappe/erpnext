// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('assests movement', {
	
	setup:function(frm){
		console.log("setup")
		frm.fields_dict.assets.grid.get_field('item').get_query =
			function() {
				return {
					filters: {
						"is_fixed_asset":1
						
					}
				}
			}
	},
    make_asset_movement: function(frm) {
		
		console.log(frm.doc.assets)
		frappe.call({
			method: "erpnext.assets.doctype.assests_movement.assests_movement.make_Asset_Movement",
			args: {
				"assets": frm.doc.assets,
				"purpose": frm.doc.purpose,
				//"transactiondate":frm.doc.transactiondate
				"frmname":frm.doc.name
			},
			callback: function(r) {
				if (r.message) {
					var doclist = frappe.model.sync(r.message);
					frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
					
					
				}
			}
		})
	},
	refresh:function(frm){
		if (frm.doc.docstatus==1) {
			frm.add_custom_button(__("Asset movement"), function() {
				frm.trigger("make_asset_movement");
			}, __('Create'));
		}
	},
	validate: function(frm) {
		if (frm.doc.transactiondate < get_today()) {
			frappe.msgprint(__("You can not select past date in From Date"));
			frappe.validated = false;
	}}
	 ,
	 empcode:function(frm){
		var value =  frappe.db.get_value("Employee", frm.doc.empcode, "first_name",(message)=>{
		   
		   frm.set_value("employee_name", message.first_name)
		   //frm.toggle_display("employee_name")
		   frm.refresh_field("employee_name")
		})
		
		
		//var doc=frappe.get_doc("Employee",HR-EMP-00001)
		
	 },
	 to:function(frm){
		 switch(frm.doc.referenceto){
			 case 'Employee':
				 calc(frm,"first_name",frm.doc.empcode)
			 default:
				frm.set_value("employee_name", frm.doc.to)
			
		 }
	 
		
	},


	
	
});


/*
frappe.ui.form.on("assests movement", "validate", function(frm) {
	if (frm.doc.transactiondate < get_today()) {
		frappe.msgprint(__("You can not select past date in From Date"));
		frappe.validated = false;
	}
});

*/

//

function calc(frm,name,code){
	var value =  frappe.db.get_value(frm.doc.referenceto, code, name,(message)=>{
		
		frm.set_value("employee_name", message.name)
	   
		frm.refresh_field("employee_name")
	 })
}


frappe.ui.form.on("assests movement", {
	setup: function(frm) {
		frm.set_query("referenceto", function() {
			return {
				filters: [
					["DocType","name", "in", ["Employee", "Customer","Project","Department"]]
				]
			}
		});
	}
});





