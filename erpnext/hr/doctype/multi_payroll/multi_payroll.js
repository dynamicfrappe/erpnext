// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Multi Payroll', {
    onload: function(frm) {
		frm.set_query('payroll_month', function(doc) {
			return {
				filters: {
					"docstatus": 1,
					"company": doc.company,
					"is_closed":0
				}
			};
		});
	},
	payroll_month : function(frm) {
	      frm.events.validate_payroll_month (frm);
	},
	company:function(frm){
         frm.events.validate_payroll_month (frm);
	}
	,
    validate_payroll_month:function(frm){
      if (frm.doc.payroll_month)
	        {
	            	frappe.call({

					method:"frappe.client.get" ,
					args:{
   						doctype: "Payroll Month",
   						name : frm.doc.payroll_month


   				   			},callback:function(r){
   				   				if (r.message){
   				   				    if ((r.message.is_closed) || (!r.message.docstatus) || (r.message.company != frm.doc.company))
   				   				    {
   				   				       frm.set_value("payroll_month", "" );
   				   				       refresh_field("payroll_month");
   				   				    }
   				   				}
   				   			}
				})
	        }
    },
	refresh: function(frm) {
		debugger;
		if (frm.doc.docstatus == 0 && (frm.doc.employees || []).length == 0) {
			if(!frm.is_new()) {
				frm.page.clear_primary_action();
				frm.add_custom_button(__("Get Employees"),
					function() {
						frm.events.get_employee_details(frm);
					}
				).toggleClass('btn-primary', !(frm.doc.employees || []).length);
			}



		}
		if (frm.doc.docstatus == 0 && (frm.doc.employees || []).length > 0) {

			if(!frm.is_new() && frm.doc.salary_slips_created == 0) {

				frm.page.clear_primary_action();
				frm.add_custom_button(__("Create Salary Slip "),
					function() {
						frm.events.creat_salary_slip(frm);
					}
				).toggleClass('btn-primary', !(frm.doc.employees || []).length);


			}
		}



		if(!frm.is_new() && frm.doc.salary_slips_created == 1) {

			frm.page.clear_primary_action();
			frm.add_custom_button(__("Calculate"),
				function() {
					frm.events.calculate_salary_slip(frm);
				}
			).toggleClass('btn-primary', !(frm.doc.employees || []).length);


		}


	},
	calculate_salary_slip : function (frm){
		return frappe.call({
			doc: frm.doc,
			method: 'calculate_salary_slip',
			callback: function(r) {

				// frappe.msgprint(__("Done"));
				frm.refresh();
			}

		})
	}
	,
	creat_salary_slip:function(frm){
		return frappe.call({
			doc: frm.doc,
			method: 'create_salary_slips',
			callback: function(r) {
                debugger;
				// frappe.msgprint(__("Done"));
				frm.refresh();
			}
			
		})





	},



	get_employee_details: function (frm) {
		return frappe.call({
			doc: frm.doc,
			method: 'fill_employee_details',
			callback: function(r) {
				if (r.docs[0].employees){
					frm.save();
					frm.refresh();
					if(r.docs[0].validate_attendance){
						render_employee_attendance(frm, r.message);
					}
				}
			}
		})
	},
});
