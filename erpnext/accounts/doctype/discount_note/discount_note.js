// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
// //
frappe.ui.form.on('Discount Note', {
	// refresh: function(frm) {

	// }

	setup:function(frm){
		frm.set_query("type", function()  {
			return {
				filters: {
					name: ["in", ["Sales Invoice", "Purchase Invoice"]]
				}
			};
		})
		frm.set_query("document_type", function()  {
			return {
				filters: {
					docstatus:1
				}
			};
		})

		},

		
		document_type:function(frm){
			if (frm.doc.type == 'Sales Invoice' && frm.doc.document_type ){
			
				frappe.call({

					method:"frappe.client.get" ,
					args:{
   						doctype: "Sales Invoice",
   						name : frm.doc.document_type


   				   			},callback:function(r){
   				   				frm.set_value("customer" , r.message.customer)
   				   				frm.set_df_property("customer" , "read_only", 1)
   				   				frm.refresh_field("customer")
   				   				if(r.message.outstanding_amount > 0 ){
   				   												frm.set_value("cost_center" , r.message.cost_center)
   				   												frm.refresh_field("cost_center")
   				   				   				   				frm.set_value("unallocated_amount" , r.message.outstanding_amount)
   				   				   				   				frm.set_df_property("unallocated_amount" , "read_only", 1)
   				   				   				   				frm.set_value("grand_total" , r.message.total)
   				   				   				   				frm.refresh_field("unallocated_amount")
   				   				   				   				frm.refresh_field("grand_total")
   				   				}else{
   				   					// frm.set_value('document_type' , '')
   				   					frm.set_value("customer" ,'')
   				   					frm.set_value("unallocated_amount" ,'')
   				   					frappe.throw("No Outstanding Amount ")

   				   				}
   				   			}
				})
			}

			if (frm.doc.type == 'Purchase Invoice'&& frm.doc.document_type){
							frappe.call({

									method:"frappe.client.get" ,
							args:{
   								doctype: "Purchase Invoice",
   								name : frm.doc.document_type

   								},

   								callback:function(r){
   									if (frm.doc.customer){
   											frm.set_value("customer" , '')

   									}
   									frm.set_value("supplier" ,r.message.supplier )
   									frm.set_df_property("supplier" , "read_only", 1)
   									 frm.refresh_field("supplier")
   									 if(r.message.outstanding_amount > 0 ){
   									 							frm.set_value("cost_center" , r.message.cost_center)
   				   												frm.refresh_field("cost_center")
   				   				   				   				frm.set_value("unallocated_amount" , r.message.outstanding_amount)
   				   				   				   				frm.set_df_property("unallocated_amount" , "read_only", 1)
   				   				   				   				frm.refresh_field("unallocated_amount")
   				   				   				   				frm.set_value("grand_total" , r.message.total)
   				   				   				   				frm.refresh_field("grand_total")


   								}
   								else{
   				   					// frm.set_value('document_type' , '')
   				   					frm.set_value("supplier" ,'')
   				   					frm.set_value("unallocated_amount" ,'')
   				   					frappe.throw("No Outstanding Amount ") }




								}})


			}


		},
		type:function(frm){
			frm.set_value("document_type" , '')
			frm.refresh_field("document_type")
			if (frm.doc.type == 'Sales Invoice'){
				frm.set_df_property("customer" , "hidden", 0)
				frm.set_df_property("supplier" , "hidden", 1)
				frm.set_df_property("customer" , "read_only", 1)
				frm.set_value("supplier", '')
				frm.set_value('supplier_name' , '')
				frm.set_value('supplier_tax_id' , '')

				frappe.call({
		        method: "frappe.client.get",
		        args: {
		            doctype: "Company",
		            name: frm.doc.company,
		        },
		        callback:function(r){
		        	//Default Receivable Account
		        	frm.set_value("from_account" , r.message.default_receivable_account)
		        	frm.refresh_field('from_account')
		        	frm.set_value("to_account" , '')
		        	frm.refresh_field('to_account')
		        }




		    })

			}

			if (frm.doc.type == 'Purchase Invoice'){
				frm.set_df_property("customer" , "hidden", 1)
				frm.set_df_property("supplier" , "hidden", 0)
				frm.set_df_property("supplier" , "read_only", 1)
				frm.set_value("customer", '')
				frm.set_value('customer_name' , '')
				frm.set_value('tax_id' , '')

				frappe.call({
		        method: "frappe.client.get",
		        args: {
		            doctype: "Company",
		            name: frm.doc.company,
		        },
		        callback:function(r){
		        	//Default Payable Account
		        	frm.set_value("to_account" , r.message.default_payable_account)
		        	frm.refresh_field('to_account')
		        	//Default Receivable Account
		        	frm.set_value("from_account" ,'')
		        	frm.refresh_field('from_account')

		        }




		    })


			}

		}




	});

