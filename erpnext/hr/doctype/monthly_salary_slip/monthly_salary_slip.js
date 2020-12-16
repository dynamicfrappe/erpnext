// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Monthly Salary Slip', {
    // refresh: function(frm) {

    // }
    onload: function(frm) {
        frm.set_query("month", () => {
            return {
                filters: {
                    docstatus: 1,
                    is_closed: 0
                }
            }
        })
    },
    start_date: function(frm) {

        if (frm.doc.employee && frm.doc.month) {

            frappe.call({
                method: "get_employee_active_salary_structure_type",
                doc: frm.doc,
                callback: function(r) {
                    frm.set_query("payroll_type", (doc) => {
                        return {
                            filters: {
                                name: ["in", r.message]
                            }
                        }
                    })
                    frm.refresh_field("payroll_type")
                }
            })
        }

    },
    month: function(frm) {

        frappe.call({
            doc: frm.doc,
            method: "set_dates_above_month",
            callback: function(r) {
                frm.set_df_property("start_date", "read_only", 1)
                frm.set_df_property("end_date", "read_only", 1)
                frm.refresh_field("start_date")
                frm.refresh_field("end_date")



                if (frm.doc.employee && frm.doc.month) {

                    frappe.call({
                        method: "get_employee_active_salary_structure_type",
                        doc: frm.doc,
                        callback: function(r) {
                            frm.set_query("payroll_type", (doc) => {
                                return {
                                    filters: {
                                        name: ["in", r.message]
                                    }
                                }
                            })
                            frm.refresh_field("payroll_type")
                        }
                    })
                }
            }

        })
    },

    employee: function(frm) {
        if (frm.doc.employee)
		frm.events.get_Employee_Salary_Details(frm);
	},
    end_date: function(frm) {
        if (frm.doc.end_date)
		    frm.events.get_Employee_Salary_Details(frm);
	},
    payroll_type: function(frm) {

        //     if (frm.doc.payroll_type){
        //             frappe.call({
        //             method: "frappe.client.get",
        //             args: {
        //                 doctype: "Salary Structure Type",
        //                 .name: frm.doc.payroll_type,
        //             },
        //             callback(r) {
        //                 if(r.message) {
        //                         debugger;
        //                        frm.set_value("calculate_income_tax" ,r.message.is_main )
        //                        frm.refresh_field("calculate_income_tax")
        //                     frm.doc.is_main = r.message.is_main;
        //                         frm.set_value("is_main" ,r.message.is_main )
        //                        frm.refresh_field("is_main")
        //
        //
        //
        //             }
        //         }
        //     });
        // }

		    frm.events.get_Employee_Salary_Details(frm);
	},
    get_Employee_Salary_Details: function(frm) {
        debugger;
        // alert(frm.doc.is_main);
        if (frm .doc.employee && frm .doc.start_date && frm .doc.end_date && frm .doc.month && frm.doc.payroll_type  )
            //
            // frappe.call({
            //         method: "frappe.client.get",
            //         args: {
            //             doctype: "Salary Structure Type",
            //             name: frm.doc.payroll_type,
            //         },
            //         callback(r) {
            //             if(r.message) {
            //                     debugger;
            //                    frm.set_value("calculate_income_tax" ,r.message.is_main )
            //                    frm.refresh_field("calculate_income_tax")
            //                 frm.doc.is_main = r.message.is_main;
            //                     frm.set_value("is_main" ,r.message.is_main )
            //                    frm.refresh_field("is_main")
            //
            //
            //
            //         }
            //     }
            // });



            return frappe.call({
                method: 'get_Employee_Salary_Details',
                doc: frm.doc,
                callback: function(r, rt) {
                    debugger;
                    frm.refresh();
                    refresh_field("earnings");
                    refresh_field("deductions");
                }
            });

         frm.refresh();
    }


});