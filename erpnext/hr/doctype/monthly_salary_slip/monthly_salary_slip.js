// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Monthly Salary Slip', {
	// refresh: function(frm) {

	// }
	onload:function(frm){
		frm.set_query("month",()=>{
				return{
					filters: {
					docstatus: 1 ,
					is_closed:0
				}
			}
		}
		)
	},
	start_date:function(frm){

	if (frm.doc.employee && frm.doc.month){
		
		frappe.call({
			method:"get_employee_active_salary_structure_type",
			doc:frm.doc,
			callback:function(r){
				frm.set_query("payroll_type" , (doc)=> {
					return{
										filters:{
											name: ["in" ,r.message]
										}
					}				})
				frm.refresh_field("payroll_type")
			}
		})
	}

	},
	month:function(frm){

		frappe.call({
			doc:frm.doc,
			method: "set_dates_above_month",
			callback:function(r){
				frm.set_df_property("start_date" , "read_only" , 1 )
				frm.set_df_property("end_date" , "read_only" , 1 )
				frm.refresh_field("start_date")
		     	frm.refresh_field("end_date")



		     	if (frm.doc.employee && frm.doc.month){
		
		frappe.call({
			method:"get_employee_active_salary_structure_type",
			doc:frm.doc,
			callback:function(r){
				frm.set_query("payroll_type" , (doc)=> {
					return{
										filters:{
											name: ["in" ,r.message]
										}
					}				})
				frm.refresh_field("payroll_type")
			}
		})
	}
			}

		})







	},
	


});
