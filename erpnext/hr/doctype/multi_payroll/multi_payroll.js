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
		if (frm.doc.docstatus == 1) {
					if (frm.custom_buttons) frm.clear_custom_buttons();
					frm.events.add_context_buttons(frm);
				}




	},
	add_context_buttons: function(frm) {
    	debugger;
		if(frm.doc.salary_slips_submitted || (frm.doc.__onload && frm.doc.__onload.submitted_ss)) {
			frm.events.add_bank_entry_button(frm);
		} else if(frm.doc.salary_slips_created) {
			frm.add_custom_button(__("Submit Salary Slip"), function() {
				submit_salary_slip(frm);
			}).addClass("btn-primary");
			frm.add_custom_button(__("Calculate"),
				function() {
					frm.events.calculate_salary_slip(frm);
				}
			).toggleClass('btn-primary', !(frm.doc.employees || []).length);
		}
	},

	add_bank_entry_button: function(frm) {
		frappe.call({
			method: 'erpnext.hr.doctype.multi_payroll.multi_payroll.payroll_entry_has_bank_entries',
			args: {
				'name': frm.doc.name
			},
			callback: function(r) {
				if (r.message && !r.message.submitted) {
					frm.add_custom_button("Make Bank Entry", function() {
						make_bank_entry(frm);
					}).addClass("btn-primary");
				}
			}
		});
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
const submit_salary_slip = function (frm) {
	frappe.confirm(__('This will submit Salary Slips and create accrual Journal Entry. Do you want to proceed?'),
		function() {
			frappe.call({
				method: 'submit_salary_slips',
				args: {},
				callback: function() {frm.events.refresh(frm);},
				doc: frm.doc,
				freeze: true,
				freeze_message: __('Submitting Salary Slips and creating Journal Entry...')
			});
		},
		function() {
			if(frappe.dom.freeze_count) {
				frappe.dom.unfreeze();
				frm.events.refresh(frm);
			}
		}
	);
};

let make_bank_entry = function (frm) {
	var doc = frm.doc;
	if (doc.payment_account) {
		return frappe.call({
			doc: cur_frm.doc,
			method: "make_payment_entry",
			callback: function(r) {
				debugger;
				frappe.set_route(
					'List', 'Journal Entry', {"Journal Entry Account.reference_name": frm.doc.name}
				);
			},
			freeze: true,
			freeze_message: __("Creating Payment Entries......")
		});
	} else {
		frappe.msgprint(__("Payment Account is mandatory"));
		frm.scroll_to_field('payment_account');
	}
};

let render_employee_attendance = function(frm, data) {
	frm.fields_dict.attendance_detail_html.html(
		frappe.render_template('employees_to_mark_attendance', {
			data: data
		})
	);
}