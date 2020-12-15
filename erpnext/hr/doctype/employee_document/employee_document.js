// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Document', {

   is_recived:function (frm){
   	 frm.set_df_property("recived_by", "reqd", 1);
   },
    document_type:function (frm){
       frappe.call({
		   method: "isWorkLetter",
		   doc:frm.doc,
		   callback(r){
               if(r.message=="true"){
               	   frm.set_df_property("workletterdetails","hidden",0)
			   }else {
               	 frm.set_df_property("workletterdetails","hidden",1)
			   }
		   }
	   })
	},
	refresh:function(frm){
		var todayDate = new Date()
		var enddate=new Date(frm.doc.end_date)
		if(frm.doc.docstatus==1 && todayDate.getTime()>enddate.getTime()){
			cur_frm.add_custom_button(__("Renew"), function() {
		        var d = new frappe.ui.Dialog({
					    title: 'Enter details',
					    fields: [
					        {
					            "label": 'New Start Date',
					            "fieldname": 'date',
					            "fieldtype": 'Date',
								"reqd": 1,
                                onchange(){
					            	d.set_df_property("number","options",[frm.doc.doc_number])
								}
					        },
							 {
					            "label": 'Number',
					            "fieldname": 'number',
					            "fieldtype": 'Select',
								 "options":[],

					        },
								 {
					            "label": 'New Number',
					            "fieldname": 'newnumber',
					            "fieldtype": 'Data',

					        },
							 {
							   "fieldname": "document",
							   "fieldtype": "Attach",
							   "label": "Document",
							   "reqd": 1
							  },

					    ],
					    primary_action_label: 'Submit',
					    primary_action(values) {
					    	var newnumber="";
					    	if(values.newnumber){
					    		newnumber=values.newnumber;
							}
                            frappe.call({
					        	method:"RenewDocument",
					        	doc:frm.doc,
					        	args:{
					        		"date":values.date,
                                     "newnumber":newnumber,
									"document":values.document
					        	}
					        })
                           d.hide();

                           	}
					});

					d.show();
		    }); 
		}
	},
   start_date:function(frm){
   	  if(frm.doc.document_type){
   	  	 var satrtDate=new Date(frm.doc.start_date)

       satrtDate.setMonth( satrtDate.getMonth() + parseInt(frm.doc.docperiod) );
       var day=satrtDate.getDate();
       //if(day<10){day='0'+day}
       var month =satrtDate.getMonth()+1;
       var year =satrtDate.getFullYear();
       var fulldate=year+"-"+month+"-"+day-1
       cur_frm.set_value('end_date',fulldate)
       console.log(year)
   	  }
   }
});
