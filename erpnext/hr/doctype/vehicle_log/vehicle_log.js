// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Log", {
	onload:(frm)=>{
		frm.set_query("employee", function() {
			return{
				filters:{
					"vehicle":frm.doc.license_plate
				}
			}
		})
	},
	setup:(frm)=>{
		frm.set_query("license_plate",function(frm){
			return {
				filters:{
					vehicle_status:'Active',
					is_passed:1
				}
			}
		})
	},
	refresh: function(frm) {
		if(frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Expense Claim'), function() {
				frm.events.expense_claim(frm);
			}, __('Create'));
			frm.page.set_inner_btn_group_as_primary(__('Create'));
		}
	},

	expense_claim: function(frm){
		frappe.call({
			method: "erpnext.hr.doctype.vehicle_log.vehicle_log.make_expense_claim",
			args:{
				docname: frm.doc.name
			},
			callback: function(r){
				var doc = frappe.model.sync(r.message);
				frappe.set_route('Form', 'Expense Claim', r.message.name);
			}
		});
	}
});

