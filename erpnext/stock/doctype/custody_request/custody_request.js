// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Custody request', {
	setup:function(frm){
		frm.set_query("reference_document_type", function()  {
			return {
				filters: {
				}
			};
		})



	},
	
	refresh: function(frm) {


		if(frm.doc.workflow_state == "Stock Audit Agreement"){
		
				frm.add_custom_button(__("Create Asset Movement"), function() {
					frm.events.create_asset_movement(frm)
						
					}).addClass("btn-primary");
		}
		if(frm.doc.workflow_state == "Created"){
		frm.add_custom_button(__("Get Employee Custody"), function() {
			frm.events.get_employee_custody(frm)
				
			}).addClass("btn-secondary");}
	},






	create_asset_movement:(frm)=>{
		frappe.model.open_mapped_doc({
			
			method : "erpnext.stock.doctype.custody_request.custody_request.create_asset_movement",

						'frm' :frm,
						'name' : frm.doc.name,
						

		})
		

	},


	get_employee_custody:function(frm){
		var text = "<b>Employee Custody </b>"+"<hr>"+"<ul>"
		frappe.call({
        method: "erpnext.stock.doctype.custody_request.custody_request.get_asset_costudian",
        args: {
           
            "name": frm.doc.reference_document_name,
        },
        callback(r) {

            if(r.message) {
            	var text = "<b>Employee Custody </b>"+"<hr>"+"<ul>"
                var task = r.message;
                var totall_custody = 0
                var i =0 
                for (i =0 ; i < r.message.length ; i++){
                	var price = r.message[i][1]
                	text += "<li><b> Asst : - " + r.message[i][0].toString() + "</b>  <b>" +" | Asset Value :"+ price.toString() + "</b></li>"}
                	totall_custody += price

                text+= "<hr><b>" + "Employee total custody :" +  totall_custody.toString() + "</b> "
                msgprint(text)
                
                
            
        }
    }


    

		
	} )
	},


   onload:function(frm){
   

   	 frm.fields_dict.custody_request_item.grid.get_field('item').get_query =
			function() {
				return {
					filters: {
						"is_fixed_asset":1
						
					}
				}
			}


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
            doctype: "Employee",
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
   
   required_date:function(frm){
   	if (frm.doc.required_date < frappe.datetime.get_today()){
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