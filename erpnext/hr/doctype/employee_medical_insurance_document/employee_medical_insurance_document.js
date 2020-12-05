// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Medical Insurance Document', {
	// refresh: function(frm) {

	// }
	setup:function(frm){

    	frm.set_query("employee",  (doc) => {
			return {
				
				
				query : "erpnext.hr.doctype.employee_medical_insurance_document.employee_medical_insurance_document.get_employee"
			
			};

		})
	},
	refresh :function(frm){
		if (frm.doc.include_family_members == 0){
		
				frm.set_df_property('employee_medical_insurance_members' , 'hidden' ,1);
				frm.refresh_field('employee_medical_insurance_members')
		}else{
			frm.set_df_property('employee_medical_insurance_members' , 'hidden' ,1);
			frm.refresh_field('employee_medical_insurance_members')
		}

	},
	include_family_members:function(frm){
		if (frm.doc.include_family_members == '1'){
			frm.set_df_property('employee_medical_insurance_members' , 'hidden' ,0);
			frm.refresh_field('employee_medical_insurance_members')
		}
		else{
			frm.clear_table('employee_medical_insurance_members')
			frm.set_df_property('employee_medical_insurance_members' , 'hidden' ,1);
			frm.refresh_field('employee_medical_insurance_members')
		}
	}
});
