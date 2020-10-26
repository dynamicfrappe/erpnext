// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Assets Return', {
	setup:function(frm){
		frm.set_query("reference_document_type", function()  {
			return {
				filters: {
					name: ["in", ["Employee", "Department","Customer","Project"]]
				}
			};
		})



	},
	reference_document_type:(frm)=>{
		if (frm.doc.employee_name){
			   frm.set_value("employee_name" ,'')}
		frm.set_value("reference_document_name" ,'')
 
	},
	reference_document_name:(frm)=>{
		if (frm.doc.reference_document_type ==="Employee" && frm.doc.reference_document_name.length > 0 ){
 
			frappe.call({
		 method: "frappe.client.get",
		 args: {
			 doctype: frm,
			 name: frm.doc.reference_document_name,
		 },
		 callback(r) {
			 if(r.message) {
				 var task = r.message;
				 frm.set_value("employee_name" ,task.employee_name )
					frm.refresh_field("employee_name")
			   
			 }
		 }
	 });
 
 
 
			
			
 
		}
	},

	onload:function(frm){

   	 frm.fields_dict.custody_request_item.grid.get_field('asset').get_query =
			function() {
				return {
					filters: {
						"custodian":frm.doc.reference_document_name
						
					}
				}
			}


   },


   refresh: function(frm) {




	frm.add_custom_button(__("Create Asset Movement"), function() {
		frm.events.create_asset_movement(frm)
			
		}).addClass("btn-primary");
},






create_asset_movement:(frm)=>{
	

	
	frappe.model.open_mapped_doc({
		
		method : "erpnext.stock.doctype.assets_return.assets_return.create_asset_movement",

					'frm' :frm,
					'name' : frm.doc.name,
					//'assets':frm.doc.custody_request_item

	})
	
      console.log(frm.doc.custody_request_item)
},

});
