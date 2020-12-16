// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Medical Insurance Document', {
	// refresh: function(frm) {

	// }
	setup:function(frm ,cdt,cdn){
		// frm.set_df_property("member", "options", 'a', cdn, 'employee_medical_insurance_members')
		// frm.refresh_field('employee_medical_insurance_members')

		// frm.set_query("member", 'employee_medical_insurance_members', (doc) => {
		// 	return {
		// 		query :"erpnext.hr.doctype.employee_medical_insurance_document.employee_medical_insurance_document.get_employee_family_members"
		// 	};

		// })
    	frm.set_query("employee",  (doc) => {
			return {
				
				
				query : "erpnext.hr.doctype.employee_medical_insurance_document.employee_medical_insurance_document.get_employee"
			
			};

		})
	},
	family_member_count:function(frm){
			if (frm.doc.family_member_count > 0 ){
						frappe.call({
							method:"set_family_members" ,
							doc:frm.doc,
							callback:function(r){
								
								frm.get_field('employee_medical_insurance_members').grid.cannot_add_rows = true
									frm.refresh_field('employee_medical_insurance_members')
							}
						})}
			if (frm.doc.family_member_count==0){
					frm.get_field('employee_medical_insurance_members').grid.cannot_add_rows = false
									frm.refresh_field('employee_medical_insurance_members')
						

			}

		
	},
	employee_fee:function(frm){
		frm.set_value("employee_insurance_cost" , frm.doc.employee_fee)
						frm.set_df_property('employee_insurance_cost' , 'read_only' ,1);
						frm.refresh_field('employee_insurance_cost')



						frm.events.set_all_member_employee_fee(frm)






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
	compnay_fee:function(frm){
		
		if (frm.doc.compnay_fee &&  frm.doc.employee_medical_insurance_members){
			frm.events.set_all_member_employee_fee(frm)

		}
		if (!frm.doc.employee_medical_insurance_members){
			frm.doc.total_company_fee = frm.doc.compnay_fee
			frm.refresh_field('total_company_fee')
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
	},
	set_all_member_employee_fee:function(frm){
		if (frm.doc.employee_medical_insurance_members.length > 0 ){
			var i = 0 
			frm.doc.employee_family_cost = 0 
			frm.doc.total_company_fee = 0 
			frm.refresh_field('total_company_fee')
			frm.doc.total_document_fee_monthly = frm.doc.employee_insurance_cost
			for (i=0 ; i < frm.doc.employee_medical_insurance_members.length ; i++){
				frm.doc.employee_family_cost += frm.doc.employee_medical_insurance_members[i].employee_share_ratio
			
				frm.doc.total_company_fee += frm.doc.employee_medical_insurance_members[i].company_share_ratio
			}
			frm.doc.total_company_fee += frm.doc.compnay_fee
			frm.refresh_field('total_company_fee')
			frm.refresh_field('employee_family_cost')
			frm.doc.total_document_fee_monthly +=frm.doc.employee_family_cost
			frm.refresh_field('total_document_fee_monthly')
			frm.refresh_field('total_company_fee')

		}
	}
	

});



frappe.ui.form.on('Employee Medical Insurance Members', {
	setup:function(frm,cdt,cdn){
		console.log("here")
		frm.set_df_property(cdt,cdn,"member", "options", ['a','b'] );
		frm.refresh_field(cdt,cdn,"member")

	},
	company_share_ratio:function(frm){
 		frm.events.set_all_member_employee_fee(frm)
	},
	employee_share_ratio:function(frm){
		frm.events.set_all_member_employee_fee(frm)
	},
	refresh:function(frm,cdt,cdn){
		console.log("here")
	},
	relation:function(frm,cdt,cdn){
		frm.set_df_property("member", "options", ['a','b'],cdn, 'employee_medical_insurance_members' )
		frm.refresh_field('employee_medical_insurance_members')
;},
	employee_medical_insurance_members_add :function(frm,cdt,cdn){

		if(frm.doc.employee)
		{frm.set_query("relation", 'employee_medical_insurance_members', () => {
					return {
						query :"erpnext.hr.doctype.employee_medical_insurance_document.employee_medical_insurance_document.get_employee_family_members",
					
							filters:{"employee" :frm.doc.employee}
						
						
					}
		
				})}
	frm.set_df_property(cdt,cdn,"member", "options", ['a','b'] );
	// frm.set_df_property("member", "options", 'a',cdn, 'employee_medical_insurance_members')
	frm.refresh_field('employee_medical_insurance_members')


	}




})