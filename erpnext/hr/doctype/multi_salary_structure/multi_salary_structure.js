// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Multi salary structure', {


        refresh:function(frm){
        	if(frm.doc.docstatus==1 &&frm.doc.status=="open"){
			  frm.add_custom_button(__("close"),function(){
			  		  frappe.call({
				                method:'updateStatus',
				                doc:frm.doc,
				                callback(r) {
				                	
				                	frm.page.clear_primary_action();
				                	frm.refresh();
				                }
				              
				            });
                       	 
                        
               }).addClass('btn-primary')
			    frm.add_custom_button(__("Renew"),function(){
			  		 var d = new frappe.ui.Dialog({
					    title: 'Enter details',
					    fields: [
					        {
					            "label": 'Date',
					            "fieldname": 'date',
					            "fieldtype": 'Date',
					              
					        },
					        {
					            "label": 'Salary Structure',
					            "fieldname": 'salaryStructure',
					            "fieldtype": 'Link',
					            "options":"Salary structure Template",
					            "get_query":function(){
					            	return{
                                        filters:[
                                             ["Salary structure Template","employee","=",frm.doc.employee]
                                        ]
					            	};
					            }
					        },
					        {
					            "label": 'Salary Component',
					            "fieldname": 'salaryComponent',
					            "fieldtype": 'Link',
					            "options":"Salary Detail",
					            "get_query":function(){
					            	return{
                                        filters:[
                                             ["Salary Detail","parent","=",d.get_values().salaryStructure]
                                        ]
					            	};
					            },
					            on_change:function(e){
					            	frappe.call({
                                	method:"getcomponentValue",
                                	doc:frm.doc
                                    }).then(r=>{
                                	   d.set_value("value",r.message
                                	)})
					            }	

					        },
					        {
					            "label": 'Value',
					            "fieldname": 'value',
					            "fieldtype": 'Data'
					        },
					        {
					            "label": 'New Value',
					            "fieldname": 'newValue',
					            "fieldtype": 'Data'
					        },
					    ],
					    primary_action_label: 'Submit',
					    primary_action(values) {
					        console.log(values);
					        d.hide();
					    }
					});

					d.show();
                       	 
                        
               }).addClass('btn-primary')
		}
	},
		setup: function(frm) {

		frm.set_query("employee", function() {
			return {
				query: "erpnext.controllers.queries.employee_query",
				filters: {
					company: frm.doc.company
				}
			}
		});
		frm.set_query("salary_structure", function() {
			return {
				filters: {
					company: frm.doc.company,
					docstatus: 1,
					is_active: "Yes"
				}
			}
		});

		frm.set_query("income_tax_slab", function() {
			return {
				filters: {
					company: frm.doc.company,
					docstatus: 1,
					disabled: 0
				}
			}
		});
	},

		employee: function(frm) {
		if(frm.doc.employee){
			frappe.call({
				method: "frappe.client.get_value",
				args:{
					doctype: "Employee",
					fieldname: "company",
					filters:{
						name: frm.doc.employee
					}
				},
				callback: function(data) {
					if(data.message){
						frm.set_value("company", data.message.company);
					}
				}
			});
		}
		else{
			frm.set_value("company", null);
		}
	}

});
	   frappe.ui.form.on("Salary structure Template", "salary_structure", function (frm, cdt, cdn) {
            var child=locals[cdt][cdn]
            child.employee=frm.doc.employee
            cur_frm.refresh_field("salary_structure");

            	frappe.call({
				    method:'checkSalryStructureComponent',
				    doc:frm.doc,
				     args:{
				        'salaryStructure':child.salary_structure
				    },
				    callback(r) {
				    	console.log(r.message)
				            if(r.message =='false'){
				            	frappe.msgprint("existing component")
                                 child.salary_structure=""
                                 cur_frm.refresh_field("salary_structure");
				            }
                                 
				                }
				              
				            });


            
		})
	     frappe.ui.form.on("Salary structure Template", "salary_structure", function (frm, cdt, cdn) {
            var child=locals[cdt][cdn]
            child.from_date=frm.doc.from_date
            cur_frm.refresh_field("salary_structure");
            
		})

	   	   frappe.ui.form.on("Salary structure Template", "type", function (frm, cdt, cdn) {
            var child=locals[cdt][cdn]
            var count=0
            for(var i=0 ;i<(frm.doc["salary_structure"]).length;i++){
            	//console.log(frm.doc["salary_structure"][i])
            	if(child.type==frm.doc["salary_structure"][i].type){
            		count ++;
            		if(count==2){
            			frappe.msgprint("type already exist");
            			 
            			child.type="";
            			cur_frm.refresh_field("type");
            			break;
            		}
            	}
            }
            
		})