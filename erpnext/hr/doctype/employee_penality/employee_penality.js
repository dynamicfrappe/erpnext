// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Penality', {
	setup: function(frm) {
		frm.set_query("penality", function() {
			return {
				filters: [
					["Violations","docstatus", "in", ["1"]]
				]
			}
		});
	},
	 refresh: function(frm) {
		frm.trigger("get_pervious_Penalities")
	 },
	onload: function(frm) {
		frm.trigger("get_pervious_Penalities")
	 },
	employee: function(frm) {
		if (frm.doc.employee && frm.doc.decision_maker)
		{
			if (frm.doc.employee == frm.doc.decision_maker)
			{
				frm.doc.employee = null;
				refresh_field("employee")
				frappe.throw(__("Employee and the Decision Maker Must be different"))
			}
		}
		frm.trigger("get_pervious_Penalities")

		frm.trigger("get_Employee_details")

	 },
	decision_maker: function(frm) {
		if (frm.doc.employee && frm.doc.decision_maker)
		{
			if (frm.doc.employee == frm.doc.decision_maker)
			{
				frm.doc.decision_maker = null;
				refresh_field("decision_maker")
				frappe.throw(__("Employee and the Decision Maker Must be different"))
			}
		}
		frm.trigger("get_decision_maker_details")


	 },
	penality: function(frm) {
		frm.trigger("get_pervious_Penalities")
		// frm.trigger("get_pervious_Penalities")
	 },
    get_pervious_Penalities:function (frm){
		if (frm.doc.docstatus)
			return;
		frappe.call({

				method: "get_pervious_Penalities",
				doc:frm.doc,
				callback: function(r) {
					debugger;

					refresh_field("pervious_penalities");
					refresh_field("penality_type");
					refresh_field("penality_description");
					refresh_field("penality_factor");
					refresh_field("article_number");

				}
			});
    },
	get_Employee_details:function (frm){
    	if (frm.doc.employee)
		{
			 frappe.call({
				 async: false,
				 method: "frappe.client.get",
				 args: {
					 "doctype": "Employee",

					 "name": frm.doc.employee // fieldname to be fetched
				 },
				 callback: function (res) {
					 if (res.message) {
					 	debugger;
						frm.doc.employee_name = res.message.employee_name;
						frm.doc.hiring_date = res.message.date_of_joining;
						frm.doc.job = res.message.designation

					 }
				 }
			 });
		}else {

    		frm.doc.employee_name = null;
			frm.doc.hiring_date = null;
			frm.doc.job = null
		}
    	refresh_field("employee_name");
    	refresh_field("hiring_date");
		refresh_field("job");
   },
	get_decision_maker_details:function (frm){

    	if (frm.doc.decision_maker)
		{
			 frappe.call({
				 async: false,
				 method: "frappe.client.get",
				 args: {
					 "doctype": "Employee",

					 "name": frm.doc.decision_maker // fieldname to be fetched
				 },
				 callback: function (res) {
					 if (res.message) {
						frm.doc.decision_maker_name = res.message.employee_name;


					 }
				 }
			 });
		}
    	else {
    		frm.doc.decision_maker_name = null;

		}
		refresh_field("decision_maker_name");
   }

});
