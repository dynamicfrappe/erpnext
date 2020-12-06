// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.hr");
erpnext.hr.EmployeeController = frappe.ui.form.Controller.extend({
	setup: function() {
		this.frm.fields_dict.user_id.get_query = function(doc, cdt, cdn) {
			return {
				query: "frappe.core.doctype.user.user.user_query",
				filters: {ignore_user_type: 1}
			}
		}
		this.frm.fields_dict.reports_to.get_query = function(doc, cdt, cdn) {
			return { query: "erpnext.controllers.queries.employee_query"} }
	},
    designation:function(frm){
    	         frappe.call({
    	         doc:frm,
                 method:'gettemp',
                callback(r) {
                  refresh_field("required_document");
                }
    });

    },
    national_id:function(frm){
    	
    	var nationalID=frm.national_id;
    	if(nationalID.length!=14 || isNaN(nationalID)){
    		
    		frappe.msgprint("please enter valid ID")
    	}
    },
	refresh: function() {
		var me = this;
		erpnext.toggle_naming_series();
	},

	date_of_birth: function() {
		return cur_frm.call({
			method: "get_retirement_date",
			args: {date_of_birth: this.frm.doc.date_of_birth}
		});
	},


	salutation: function() {
		if(this.frm.doc.salutation) {
			this.frm.set_value("gender", {
				"Mr": "Male",
				"Ms": "Female"
			}[this.frm.doc.salutation]);
		}
	},

});
frappe.ui.form.on('Employee',{
	setup: function(frm) {
		frm.set_query("leave_policy", function() {
			return {
				"filters": {
					"docstatus": 1
				}
			};
		});
	},
	onload:function(frm) {
		if (!frm.doc.total_working_hours_per_day){
			frappe.db.get_single_value("HR Settings", "total_hours_per_day").then(duration => {
				if (duration) {
					debugger;
					frm.doc.total_working_hours_per_day = duration;
					refresh_field("total_working_hours_per_day");
				}

			});
		}


		frm.set_query("department", function() {
			return {
				"filters": {
					"company": frm.doc.company,
				}
			};
		});
	},
	prefered_contact_email:function(frm){		
		frm.events.update_contact(frm)		
	},
	personal_email:function(frm){
		frm.events.update_contact(frm)
	},
	company_email:function(frm){
		frm.events.update_contact(frm)
	},
	user_id:function(frm){
		frm.events.update_contact(frm)
	},
	update_contact:function(frm){
		var prefered_email_fieldname = frappe.model.scrub(frm.doc.prefered_contact_email) || 'user_id';
		frm.set_value("prefered_email",
			frm.fields_dict[prefered_email_fieldname].value)
	},
	status: function(frm) {
		return frm.call({
			method: "deactivate_sales_person",
			args: {
				employee: frm.doc.employee,
				status: frm.doc.status
			}
		});
	},
	create_user: function(frm) {
		if (!frm.doc.prefered_email)
		{
			frappe.throw(__("Please enter Preferred Contact Email"))
		}
		frappe.call({
			method: "erpnext.hr.doctype.employee.employee.create_user",
			args: { employee: frm.doc.name, email: frm.doc.prefered_email },
			callback: function(r)
			{
				frm.set_value("user_id", r.message)
			}
		});
	},
	get_members:function(frm) {
		if (frm.doc.family_members){
				frm.clear_table("members");
				for (var j = 0; j < frm.doc.family_members.length; j++) {

					var cur_row = frm.doc.family_members[j] ;
					if (cur_row.include_in_medical_insurance){
						var new_row = frm.add_child("members");
				    	new_row.member = cur_row.name1;
				        new_row.age = cur_row.age;
				        new_row.company_share_ratio = 50 ;
				        new_row.employee_share_ratio = 50 ;

				        new_row.relation = cur_row.relation;

					}

				}
			    frm.refresh_field("members");

      	}
	}
	,
	company_share_ratio:function (frm){
		var cur_row = frm.doc ;
		console.log(cur_row);
		debugger;
		if (cur_row.company_share_ratio > 100)
			cur_row.company_share_ratio = 100 ;
		if (cur_row.company_share_ratio < 0)
			cur_row.company_share_ratio = 0 ;
		cur_row.employee_share_ratio = 100 - cur_row.company_share_ratio ;
		refresh_field("company_share_ratio");
		refresh_field("employee_share_ratio");
	}
	,
	employee_share_ratio:function (frm){
		var cur_row = frm.doc ;
		if (cur_row.employee_share_ratio > 100)
			cur_row.employee_share_ratio = 100 ;
		if (cur_row.employee_share_ratio < 0)
			cur_row.employee_share_ratio = 0 ;
		cur_row.company_share_ratio = 100 - cur_row.employee_share_ratio ;
		refresh_field("company_share_ratio");
		refresh_field("employee_share_ratio");

	}
});




frappe.ui.form.on('Employee Medical Insurance Members',"company_share_ratio",function(frm,cdt,cdn){
		var cur_row = locals [cdt] [cdn] ;
		console.log(cur_row);
		debugger;
		if (cur_row.company_share_ratio > 100)
			cur_row.company_share_ratio = 100 ;
		if (cur_row.company_share_ratio < 0)
			cur_row.company_share_ratio = 0 ;
		cur_row.employee_share_ratio = 100 - cur_row.company_share_ratio ;
		refresh_field("company_share_ratio", cur_row.name, cur_row.parentfield);
		refresh_field("employee_share_ratio", cur_row.name, cur_row.parentfield);



	}
);
frappe.ui.form.on('Employee Medical Insurance Members',"employee_share_ratio",function(frm,cdt,cdn){
		var cur_row = locals [cdt] [cdn] ;
		if (cur_row.employee_share_ratio > 100)
			cur_row.employee_share_ratio = 100 ;
		if (cur_row.employee_share_ratio < 0)
			cur_row.employee_share_ratio = 0 ;
		cur_row.company_share_ratio = 100 - cur_row.employee_share_ratio ;
		refresh_field("company_share_ratio", cur_row.name, cur_row.parentfield);
		refresh_field("employee_share_ratio", cur_row.name, cur_row.parentfield);

	}

);
cur_frm.cscript = new erpnext.hr.EmployeeController({frm: cur_frm});
