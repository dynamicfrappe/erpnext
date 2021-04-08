// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Agrement', {
	 refresh:function (frm){
            frm.set_query("employee" ,"resourses" ,function(doc){
				return {
					filters: {
					    outsource: 1,
                        status:'Active'

			    	}
				};
			});
        },
    start_date:function (frm) {
        frm.events.get_duration(frm)
    },
     end_date:function (frm) {
frm.events.get_duration(frm)
    },
    get_duration:function (frm) {
        if (frm.doc.start_date && frm.doc.end_date)
        {
            frappe.call({
                method : "get_total_durations",
                doc:frm.doc,
                callback:function (r){
                    refresh_field('start_date')
                    refresh_field('end_date')
                    refresh_field('total_duration_in_monthes')
                }
            })
        }
    },
    calculate_employee_totals:function (frm)
        {
             frappe.call({
                method : "calculate_employee_totals",
                doc:frm.doc,
                callback:function (r){
                    refresh_field('resourses')
                    refresh_field('total_resources')
                    refresh_field('total_resources_monthly_fee')
                    refresh_field('total_resources_fee')
                    refresh_field('grand_total_fee')


                }
            })
        },
    calculate_tools_totals:function (frm)
        {
             frappe.call({
                method : "calculate_tools_totals",
                doc:frm.doc,
                callback:function (r){
                    refresh_field('tools')
                    refresh_field('total_resources_fee')
                    refresh_field('total_equipments_fee')
                    refresh_field('grand_total_fee')


                }
            })
        },
});
frappe.ui.form.on('Customer Agrement Resources', {
    resourses_add:function(frm,cdt,cdn)
    {
        frm.events.calculate_employee_totals(frm)
    },
    resourses_remove:function(frm,cdt,cdn)
    {
        frm.events.calculate_employee_totals(frm)
    },
     salary:function(frm,cdt,cdn)
    {
        frm.events.calculate_employee_totals(frm)
    },
     other_ereanings:function(frm,cdt,cdn)
    {
        frm.events.calculate_employee_totals(frm)
    },
     company_revenue:function(frm,cdt,cdn)
    {
        frm.events.calculate_employee_totals(frm)
    },

});

frappe.ui.form.on('Customer Agrement Tools', {
     item_code:function(frm,cdt,cdn)
    {
        var item = locals [cdt][cdn]
        if (item.item_code){
            alert(frm.doc.customer)
            frappe.call({
                method:"erpnext.operations.doctype.customer_agrement.customer_agrement.get_item_price",
                args :{
                    args:{

                    company : frappe.defaults.get_default("company"),
                    customer : frm.doc.customer,
                    item_code : item.item_code
                    }
                },
                callback:function (r) {
                    debugger
                    item.rate = r.message
                    refresh_field('tools')
                    frm.events.calculate_tools_totals(frm)
                }
            })

        }
    },
    rate:function(frm,cdt,cdn)
    {
        frm.events.calculate_tools_totals(frm)
    },
    qty:function(frm,cdt,cdn)
    {
        frm.events.calculate_tools_totals(frm)
    },
     intersest_precentagefor_year:function(frm,cdt,cdn)
    {
        frm.events.calculate_tools_totals(frm)
    },
     monthly_installment:function(frm,cdt,cdn)
    {
        frm.events.calculate_tools_totals(frm)
    },



});

