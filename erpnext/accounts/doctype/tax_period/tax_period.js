// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tax period', {
    gettax:function (frm){
    	            if (!frm.doc.taxperioddetails){
    	            	frappe.throw("Please Enter Tax Type")
					}
      		        var d = new frappe.ui.Dialog({
					    title: 'Enter details',
					    fields: [
					        {
					            "label": 'Posting Date',
					            "fieldname": 'date',
					            "fieldtype": 'Date',
								"reqd": 1,
                                onchange(){
					            	frappe.call({
                                        method:"getTaxType",
                                        doc:frm.doc,
                                        callback(r){
                                        	console.log(r)
                                         d.set_df_property("class","options",r.message)
                                        }
                                    })
								}
					        },
							 {
					            "label": 'Class',
					            "fieldname": 'class',
					            "fieldtype": 'Select',
								 "options":[],

					        },

					    ],
					    primary_action_label: 'Submit',
					    primary_action(values) {
					    	var type=""
							if ( values.class){
								type=values.class
							}
					    	frappe.call({
								method: "createAddTax",
								doc:frm.doc,
								args:{
									type:type
								},
								callback(r) {
									//console.log(r.message)
                                   frappe.set_route("Form","Value Added Tax", r.message);
								}
							})
                           d.hide();

                           	}
					});

					d.show();
    }
});
	   	   frappe.ui.form.on("Tax Period Details", "taxclass", function (frm, cdt, cdn) {
            var child=locals[cdt][cdn]
            var count=0
            for(var i=0 ;i<(frm.doc["taxperioddetails"]).length;i++){
            	//console.log(frm.doc["salary_structure"][i])
            	if(child.taxclass==frm.doc["taxperioddetails"][i].taxclass){
            		count ++;
            		if(count==2){
            			frappe.msgprint("tax already exist");

            			child.taxclass="";
            			cur_frm.refresh_field("taxclass");
            			break;
            		}
            	}
            }

		})