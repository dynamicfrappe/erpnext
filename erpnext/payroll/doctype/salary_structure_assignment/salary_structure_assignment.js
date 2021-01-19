// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Salary Structure Assignment', {
	setup: function(frm) {
		debugger;
		var grid = frm.get_field('deductions').grid
		frm.get_field('deductions').grid.cannot_add_rows = true;
		frm.get_field('earnings').grid.cannot_add_rows = true;


		frm.set_query("employee", function() {
			return {
				query: "erpnext.controllers.queries.employee_query",
			}
		});
		frm.set_query("salary_structure", function() {
			return {
				filters: {
					company: frm.doc.company,
					docstatus: 1,
					is_active: "Yes"
				}
			}
		});

		frm.set_query("income_tax_slab", function() {
			return {
				filters: {
					company: frm.doc.company,
					docstatus: 1,
					disabled: 0,
					currency: frm.doc.currency
				}
			};
		});

		frm.set_query("payroll_payable_account", function() {
			var company_currency = erpnext.get_currency(frm.doc.company);
			return {
				filters: {
					"company": frm.doc.company,
					"root_type": "Liability",
					"is_group": 0,
					"account_currency": ["in", [frm.doc.currency, company_currency]],
				}
			}
		});
	},

	employee: function(frm) {
		if(frm.doc.employee){
			frappe.call({
				method: "frappe.client.get_value",
				args:{
					doctype: "Employee",
					fieldname: "company",
					filters:{
						name: frm.doc.employee
					}
				},
				callback: function(data) {
					if(data.message){
						frm.set_value("company", data.message.company);
					}
				}
			});
		}
		else{
			frm.set_value("company", null);
		}
	},

	company: function(frm) {
		if (frm.doc.company) {
			frappe.db.get_value("Company", frm.doc.company, "default_payroll_payable_account", (r) => {
				frm.set_value("payroll_payable_account", r.default_payroll_payable_account);
			});
		}
	}
	,
	salary_structure: function(frm) {
		frm.clear_table('earnings')
		frm.clear_table('deductions')
		frm.refresh_field("earnings");
		frm.refresh_field("deductions");
		if (!frm.doc.salary_structure)
			return
		frappe.call({
			method:"frappe.client.get" ,
					args:{
   						doctype: "Salary Structure",
   						name : frm.doc.salary_structure


   				   			},callback:function(r){
						debugger;
   				   				if (r.message)
								{
									debugger
									r.message.earnings.forEach((e)=>{
										debugger;
										var child = frm.add_child("earnings");
										child.salary_component = e.salary_component
										child.abbr = e.abbr
										child.amount = e.amount
										child.additional_salary = e.additional_salary
										child.statistical_component = e.statistical_component
										child.depends_on_payment_days = e.depends_on_payment_days
										child.exempted_from_income_tax = e.exempted_from_income_tax
										child.is_tax_applicable = e.is_tax_applicable
										child.is_flexible_benefit = e.is_flexible_benefit
										child.variable_based_on_taxable_salary = e.variable_based_on_taxable_salary
										child.do_not_include_in_total = e.do_not_include_in_total
										child.deduct_full_tax_on_selected_payroll_date = e.deduct_full_tax_on_selected_payroll_date
										child.condition = e.condition
										child.amount_based_on_formula = e.amount_based_on_formula
										child.formula = e.formula
										child.default_amount = e.default_amount
										child.additional_amount = e.additional_amount
										child.tax_on_flexible_benefit = e.tax_on_flexible_benefit
										child.tax_on_additional_salary = e.tax_on_additional_salary

									});
									r.message.deductions.forEach((e)=>{
										debugger;
										var child = frm.add_child("deductions");
										child.salary_component = e.salary_component
										child.abbr = e.abbr
										child.additional_salary = e.additional_salary
										child.statistical_component = e.statistical_component
										child.depends_on_payment_days = e.depends_on_payment_days
										child.exempted_from_income_tax = e.exempted_from_income_tax
										child.is_tax_applicable = e.is_tax_applicable
										child.is_flexible_benefit = e.is_flexible_benefit
										child.variable_based_on_taxable_salary = e.variable_based_on_taxable_salary
										child.do_not_include_in_total = e.do_not_include_in_total
										child.deduct_full_tax_on_selected_payroll_date = e.deduct_full_tax_on_selected_payroll_date
										child.condition = e.condition
										child.amount_based_on_formula = e.amount_based_on_formula
										child.formula = e.formula
										child.default_amount = e.default_amount
										child.additional_amount = e.additional_amount
										child.tax_on_flexible_benefit = e.tax_on_flexible_benefit
										child.tax_on_additional_salary = e.tax_on_additional_salary

									})
									frm.refresh_field("earnings");
									frm.refresh_field("deductions");
									// frm.doc.earnings = r.message.earnings;
									// frm.doc.deductions = r.message.deductions;
								}


   				   			}
		});

	}
});

frappe.ui.form.on('Salary Detail', {

	before_earnings_remove: function(frm) {
		frappe.throw(__("Cann't remove Row")) ;
	},

	before_deductions_remove: function(frm) {
		frappe.throw(__("Cann't remove Row")) ;
	},
});