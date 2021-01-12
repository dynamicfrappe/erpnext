// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// For license information, please see license.txt

// for communication
cur_frm.email_field = "email_id";

frappe.ui.form.on("Job Applicant", {
	refresh: function(frm) {
		var status = ["Pending","HR Approved" , "Technical Approved"]
		if (!frm.is_new())
		{
			debugger;

			if(frm.doc.docstatus =='0' && frm.doc.status == "Open" &&status.includes(frm.doc.workflow_status)){
		      frm.page.clear_primary_action();
		      frm.disable_save();
		        frappe.call({
                //method: "erpnext.hr.doctype.mission.mission.updateStaus",
                method:'get_user_roles',
                doc:frm.doc,
                callback(r) {
                	debugger;
                	console.log(r.message)
                    if (r.message) {
                    	var user = r.message.user
						var logged = frappe.session.user
						var agreement_type = r.message.agreement_type
						if (user != logged)
							frappe.throw(__("This Applicant is under {} Agremeent".format(user)))


						 frm.add_custom_button(__("Approve"),function(){
                       	 // frm.event.updateAction("Approve");
                       	 frm.event.updateAction(frm ,agreement_type,user, "Approve");


                       },__("Actions"))
						 frm.add_custom_button(__("Reject"),function(){
                       	 frm.event.updateAction(frm ,agreement_type,user, "Reject");


                       },__("Actions"))

                    }
                }
            });
		  }

		}

		if (!frm.doc.__islocal) {
			if (frm.doc.__onload && frm.doc.__onload.job_offer) {
				frm.add_custom_button(__("Job Offer"), function() {
					frappe.set_route("Form", "Job Offer", frm.doc.__onload.job_offer);
				}, __("View"));
			} else {
				frm.add_custom_button(__("Job Offer"), function() {
					frappe.route_options = {
						"job_applicant": frm.doc.name,
						"applicant_name": frm.doc.applicant_name,
						"designation": frm.doc.job_opening,
					};
					frappe.new_doc("Job Offer");
				});
			}
		}

		frm.set_query("job_title", function() {
			return {
				filters: {
					'status': 'Open'
				}
			};
		});

	}
	, updateAction:function (frm , status , user , action){
		frappe.call({
                //method: "erpnext.hr.doctype.mission.mission.updateStaus",
                method:'update_action',
                doc:frm.doc,
				args:{
                	"status" :  status,
					"user" :user ,
					"action":action
				}
				,
                callback(r) {
                	frm.refresh()
				}

		});




	},Make_Data_bank:function (frm) {
		frappe.call({
			//method: "erpnext.hr.doctype.mission.mission.updateStaus",
			method: 'Make_Data_bank',
			doc: frm.doc,
			args: {
				"status": status,
				"user": user,
				"action": action
			}
			,
			callback(r) {
				frm.refresh()
			}

		});
	}
});