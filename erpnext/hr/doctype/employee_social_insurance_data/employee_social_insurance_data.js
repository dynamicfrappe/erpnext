// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Social Insurance Data', {
    	setup:function(frm){
		frm.set_query("employee_document",function(){
			return{
					filters: {
					employee: ["in", [frm.doc.employee]]
				}
			}
		})
	},

	insurance_salary:function(frm){
        		frappe.call({
                method:'getInsuranceSetting',
                doc:frm.doc,
                callback(r) {
                   
                   var insSalary=parseInt(frm.doc.insurance_salary)
                   
                   if(insSalary <r.message.min || insSalary>r.message.max){
                   	frappe.msgprint("insurance salary must between "+r.message.min+" and "+r.message.max)
                   	cur_frm.set_value("insurance_salary","")
                   }
                }
            });
	},
	basic_salary:function(frm){
        		frappe.call({
                method:'getbasicSalarySetting',
                doc:frm.doc,
                callback(r) {
                      var basicSalary=parseInt(frm.doc.basic_salary)
                   
                   if(basicSalary <r.message.min || basicSalary>r.message.max){
                   	frappe.msgprint("basic Salary date must between "+r.message.min+" and "+r.message.max)
                   	cur_frm.set_value("basic_salary","")
                   }
                }
            });

	}
});
