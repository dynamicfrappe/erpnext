// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Multi salary structure', {
       getcomponent:function (frm){
      
           frm.clear_table("component")
       		  frappe.call({
			  method:"getAllSalaryStructureComponent",
			  doc:frm.doc,
			  callback(r){
                 if(r.data){
                     frm.refresh_field('component');
				 }
			  }
		  })
	   },

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
			    frm.add_custom_button(__("Update"),function(){
			  		 var d = new frappe.ui.Dialog({
					    title: 'Enter details',
					    fields: [
					        {
					            "label": 'Date',
					            "fieldname": 'date',
					            "fieldtype": 'Date',
					             onchange(){
					             	frappe.call({
					             		method:"getEmployeeSalaryStructure",
					             		doc:frm.doc
					             	}).then(r=>{d.set_df_property("salaryStructure","options",r.message)})
					             }
					        },
					        {
					            "label": 'Salary Structure',
					            "fieldname": 'salaryStructure',
					            "fieldtype": 'Select',
					            "options":[],
					            onchange(){
                                   if((d.get_value('salaryStructure')).length>1){
                                   	    frappe.call({
					            		method:"setSalaryComponent",
					            		doc:frm.doc,
					            		args:{
					            			"salaryStructure":d.get_values().salaryStructure
					            		}
					            	}).then(r=>{d.set_df_property("salaryDetails","options",r.message)})
                                   }
					            }
					        },
					        {
					            "label": 'Salary Component',
					            "fieldname": 'salaryDetails',
					            "fieldtype": 'Select',
					            "options":[],
					            onchange(){
					            	
					            	frappe.call({
                                	method:"getcomponentValue",
                                	doc:frm.doc,
                                	args:{
                                      "SalayDetails":d.get_values().salaryDetails
                                	},
                                    }).then(r=>{
                                    	//console.log(r.message[0][0])
                                	   d.set_value("value",r.message.amount)
                                	})
					            }	

					        },
					        {
					            "label": 'Value',
					            "fieldname": 'value',
					            "fieldtype": 'Data',
					             "read_only": 1
					        },
					        {
					            "label": 'New Value',
					            "fieldname": 'newValue',
					            "fieldtype": 'Data'
					        },
					    ],
					    primary_action_label: 'Submit',
					    primary_action(values) {


							frappe.call({
								method:"updateComponentTable",
								doc:frm.doc,
								args:{
									"component":values.salaryDetails,
									"amount":values.newValue,
									"oldValue":values.value,
									"date":values.date

								}
							})

                           d.hide();
							cur_frm.refresh_fields('component');
                            //frappe.set_route("List", "Multi salary structure");
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
				method: "frappe.client.get",
				args:{
					doctype: "Employee",
					name: frm.doc.employee

				},
				callback: function(data) {
					if(data.message){
						frm.set_value("company", data.message.company);
						if (!data.message.attendance_role)
							frappe.throw(__("Employee has not assigned To Attendance Rule"));
						frm.set_value("employee", "");
						refresh_field("employee");
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
				    	//console.log(r.message)
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
             var dict=frm.doc.salary_structure
			 var count=0;
			 for(let i=0;i<dict.length;i++){

			 	if(dict[i]['salary_structure']==child.salary_structure){
			 		count++;
			 		if(count==2){
			 		frappe.msgprint("salary structure already exist")
					child.salary_structure=""
			 		}
				}
			 }
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