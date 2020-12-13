// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Contract', {
	// refresh: function(frm) {

	// }
	national_id:function(frm){

    	var nationalID=frm.doc.national_id;
    	if((nationalID.length!=14 || isNaN(nationalID)) && nationalID.length!=0){
    		frappe.msgprint("please enter valid ID")
    		cur_frm.set_value("national_id","")
    	}
    },

	onload:function(frm){

		frm.set_df_property("__newname", "hidden", '1');
		frm.refresh_field("__newname")


	


	},
	contract_duration:function(frm){
		if (frm.doc.contract_start_date && frm.doc.contract_duration  ){
			frappe.call({
				method:"erpnext.hr.doctype.employee_contract.employee_contract.sumdates" ,
				args :{
					"start":frm.doc.contract_start_date , 
					"dura" : frm.doc.contract_duration
				},
				callback : function(r){
					frm.set_value('contract_end_date',r.message)
		       		frm.refresh_field('contract_end_date')
				}
			})
		}




	},



	contract_start_date:function(frm){
			if (frm.doc.contract_start_date && frm.doc.contract_duration  ){
			frappe.call({
				method:"erpnext.hr.doctype.employee_contract.employee_contract.sumdates" ,
				args :{
					"start":frm.doc.contract_start_date , 
					"dura" : frm.doc.contract_duration
				},
				callback : function(r){
					frm.set_value('contract_end_date',r.message)
		       		frm.refresh_field('contract_end_date')
				}
			})
		}


	} , 


testing_duration:function(frm){


		if (frm.doc.testing_start_date &&  frm.doc.testing_duration  ){
			frappe.call({
				method:"erpnext.hr.doctype.employee_contract.employee_contract.sumdates" ,
				args :{
					"start":frm.doc.testing_start_date , 
					"dura" : frm.doc.testing_duration
				},
				callback : function(r){
					frm.set_value('testing_end_date',r.message)
		       		frm.refresh_field('testing_end_date')
				}
			})
		}


},

testing_start_date:function(frm){



		if (frm.doc.testing_start_date &&  frm.doc.testing_duration  ){
			frappe.call({
				method:"erpnext.hr.doctype.employee_contract.employee_contract.sumdates" ,
				args :{
					"start":frm.doc.testing_start_date , 
					"dura" : frm.doc.testing_duration
				},
				callback : function(r){
					frm.set_value('testing_end_date',r.message)
		       		frm.refresh_field('testing_end_date')
				}
			})
		}


}


});
