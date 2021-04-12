// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Agrement', {
	 refresh:function (frm){
	     cur_frm.fields_dict["holds"].grid.wrapper.find('.grid-add-row').hide();
            frm.set_query("employee" ,"resourses" ,function(doc){
				return {
					filters: {
					    outsource: 1,
                        status:'Active'

			    	}
				};
			});
            if (!frm.is_new()){
                 frm.add_custom_button(__("Invoice"),function() {
					frm.events.create_invoice (frm);
				}, __("Create"));
                frm.add_custom_button(__("Delivery Note"),function() {
                        frm.events.create_delivery_note (frm);
                    }, __("Create"));
                frm.add_custom_button(__("Stock Entry"),function() {
                        frm.events.create_stock_entry (frm);
                    }, __("Create"));
            }

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
                    refresh_field('tools_qty')


                }
            })
        },
    get_item_conversion_factor (frm,cdt,cdn){
	     var item = locals [cdt][cdn]
            if (item.item_code && item.uom)
            {
                frappe.call({
                    method : "erpnext.operations.doctype.customer_agrement.customer_agrement.get_item_conversion_factor"
                    ,args:{
                     item: item.item_code,
                     uom:   item.uom
                    }
                    ,callback:function (r) {
                        item.conversion_rate = r.message
                        refresh_field('tools')
                    }
                })
            }

    },
    hold :function(frm,cdt,cdn){

	     var d = locals [cdt][cdn]
         if (d.status == 'Active')
         {
             d.status = 'Hold';
             frappe.call({
             method:"hold",
             doc:frm.doc,
             callback:function (r){
                frm.refresh()
             }
         })
         }

    },
    create_invoice:function(frm){
	     frm.save()
	     frm.doc.comapny = frappe.defaults.get_default("company")
	     frappe.model.open_mapped_doc({
			method: "erpnext.operations.doctype.customer_agrement.customer_agrement.create_invoice",
			frm: frm

		})
    },
    create_delivery_note:function(frm){
	     frm.save()
	     frm.doc.comapny = frappe.defaults.get_default("company")
	     frappe.model.open_mapped_doc({
			method: "erpnext.operations.doctype.customer_agrement.customer_agrement.create_delivery_note",
			frm: frm

		})
    },
    create_stock_entry:function(frm){
	     frm.save()
	     frm.doc.comapny = frappe.defaults.get_default("company")
	     frappe.model.open_mapped_doc({
			method: "erpnext.operations.doctype.customer_agrement.customer_agrement.create_stock_entry",
			frm: frm

		})
    }
});
frappe.ui.form.on('Customer Agreement Holds', {
    before_holds_remove:function(frm,cdt,cdn){
        var d = locals [cdt] [cdn]
        if (d.reference_name)
             frappe.throw('Cannot Remove')
    },before_holds_add:function(frm,cdt,cdn){
        frappe.throw('Cannot Add')
    },
    unhold:function(frm,cdt,cdn)
    {
         var d = locals [cdt][cdn]
        var i = locals [d.reference_type ][ d.reference_name]

        if (i.status == 'Hold')
        {
            i.status = 'Active';

            frappe.call({
             method:"hold",
             doc:frm.doc,
             callback:function (r){
                frm.refresh()

             }
         })
        }



    }
})
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
    hold :function(frm,cdt,cdn){
        frm.events.hold(frm,cdt,cdn)
    }

});

frappe.ui.form.on('Customer Agrement Tools', {
     item_code:function(frm,cdt,cdn)
    {
        var item = locals [cdt][cdn]
        if (item.item_code){
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

                    item.rate = r.message
                    refresh_field('tools')
                    frm.events.calculate_tools_totals(frm)
                }
            })
                    frm.events.get_item_conversion_factor(frm,cdt,cdn)


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
    uom:function (frm,cdt,cdn){
        frm.events.get_item_conversion_factor(frm,cdt,cdn)
    },
    hold :function(frm,cdt,cdn){
        frm.events.hold(frm,cdt,cdn)
    }



});

