// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Assets Return', {
    setup: function(frm) {
        frm.set_query("reference_document_type", function() {
            return {
                filters: {
                    name: ["in", ["Employee", "Department", "Project"]]
                }
            };
        })



    },
    reference_document_type: (frm) => {
        	if (frm.doc.reference_document_type ==="Project"){
   	 		frm.set_df_property("employee" ,"hidden" , 0)
   			frm.set_query("reference_document_name", function()  {
			return {
				filters: {
					status:"Open"
				}
			};
		})
   	}

    },
    reference_document_name: (frm) => {
        if (frm.doc.reference_document_type === "Employee" && frm.doc.reference_document_name.length > 0) {

            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: frm,
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

    reference_document_name: function(frm) {

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
      
       frm.fields_dict.custody_request_item.grid.get_field('asset').get_query =
            function() {
            	if(frm.doc.reference_document_type=="Department"){
            		return {
                        filters: {
                            "department": frm.doc.reference_document_name

                        }
                    }
            	}
            	if(frm.doc.reference_document_type=="Project"){
            		return {
                        filters: {
                            "project": frm.doc.reference_document_name,
                            "custodian": frm.doc.employee

                        }
                    }
            	}

            	if(frm.doc.reference_document_type=="Employee"){
            		return {
                        filters: {
                            "custodian": frm.doc.reference_document_name

                        }
                    }
            	}

            	return 0;
            	
            }
      
    },


    refresh: function(frm) {
    try {


        if(frm.doc.workflow_state == (__("Stock Audit Agreement"))){
        frm.add_custom_button(__("Create Asset Movement"), function() {
            frm.events.create_asset_movement(frm)

        }).addClass("btn-primary");
      } }


      catch(err) {
          console.log(err)
          }
    },



 onload:function(frm){
 	
 	frm.clear_table("custody_request_item")
 	if (frm.doc.reference_document_type != "Project"){  
	     	frm.set_df_property("employee" ,"hidden" , 1)}

 },


    create_asset_movement: (frm) => {



        frappe.model.open_mapped_doc({

            method: "erpnext.stock.doctype.assets_return.assets_return.create_asset_movement",

            'frm': frm,
            'name': frm.doc.name,
            //'assets':frm.doc.custody_request_item

        })


    },

});

/*
frappe.ui.form.on('custtoreturn assets', {

   custody_request_item_add:function(frm){
   	frm.set_query("asset","custody_request_item",function(){
   			return{
   				filters:{
   					"department": frm.doc.reference_document_name
   				}
   			}
   		})
   	console.log(frm.doc.reference_document_type)
   	if(frm.doc.reference_document_type==="Department"){
   		console.log("|JJJJ")
   		frm.set_query("asset","custody_request_item",function(){
   			return{
   				filters:{
   					"department": frm.doc.reference_document_name
   				}
   			}
   		})
   	 
   }
   	}


})*/