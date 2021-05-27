// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Agrement', {
    onload:function (frm) {
        if (frm.is_new()){
                frm.clear_table('dues')
                frm.clear_table('holds')
                refresh_field('holds')
               refresh_field('dues')
            }
    },
	 refresh:function (frm){
	     cur_frm.fields_dict["holds"].grid.wrapper.find('.grid-add-row').hide();
         frm.get_field("holds").grid.cannot_add_rows = true;
         frm.get_field("dues").grid.cannot_add_rows = true;
	     cur_frm.fields_dict["dues"].grid.wrapper.find('.grid-add-row').hide();
            frm.set_query("employee" ,"resourses" ,function(doc){
				return {
					filters: {
					    outsource: 1,
                        status:'Active'

			    	}
				};
			});

            frm.set_query("warehouse"  ,function(doc){
				return {
					filters: {
					    custody_warehouse: 1

			    	}
				};
			});
            frm.set_query("sorce_warehouse"  ,function(doc){
				return {
					filters: {
					    custody_warehouse: 0,
                        customer_custody_warehouse:0

			    	}
				};
			});
            if (!frm.is_new()){
                 frm.add_custom_button(__("Operation Invoice Due"),function() {
					frm.events.create_Due (frm);
				}, __("Create"));
                //  frm.add_custom_button(__('Deliver To Customer'), function() {
			    //     	frm.events.deliver_to_customer(frm)
		        // 	}, __('Create'));
                // frm.add_custom_button(__("Delivery Note"),function() {
                //         frm.events.create_delivery_note (frm);
                //     }, __("Create"));
                // frm.add_custom_button(__("Spent Asset"),function() {
                //      var emploee_list=[]
                //      for(let i=0;i<frm.doc.resourses.length;i++){
                //         emploee_list.push(frm.doc.resourses[i]["employee"])
                //      }
                //         let d = new frappe.ui.Dialog({
                //      title: 'select employee',
                //      fields: [
                //     {
                //         label:__("Employee"),
                //         fieldname: 'employee',
                //         fieldtype: 'Select',
                //         options:emploee_list,
                //         req:1
                //     }
                // ],primary_action:function(){
                //     var args = d.get_values();
                //     d.hide()
                //     frappe.call({
                //         'method':"create_stock_entry_backend",
                //         'doc':frm.doc,
                //         args:{
                //             employee:args.employee
                //         }
                //     })
                // }
                //  });
                //         d.show()
                //         //frm.events.create_stock_entry (frm);
                //     }, __("Create"));
                // frm.add_custom_button(__("Custody Return"),function() {
                //
                //     var qty=0;
                //      var emploee_list=[]
                //     var item_list=[]
                //      for(let i=0;i<frm.doc.resourses.length;i++){
                //         emploee_list.push(frm.doc.resourses[i]["employee"])
                //      }
                //      for(let i=0;i<frm.doc.tools.length;i++){
                //         item_list.push(frm.doc.tools[i]["item_code"])
                //      }
                //         let d = new frappe.ui.Dialog({
                //     title: 'select employee',
                //      fields: [
                //     {
                //         label:__("Employee"),
                //         fieldname: 'employee',
                //         fieldtype: 'Select',
                //         options:emploee_list,
                //         req:1
                //     },
                //     {
                //         label:__("Item"),
                //         fieldname: 'item',
                //         fieldtype: 'Select',
                //         options:item_list,
                //         req:1,
                //         onchange:function (){
                //             // d.fields_dict.qty.set_value(5);
                //             //         d.fields_dict.qty.refresh();
                //             for(let i=0;i<frm.doc.tools.length;i++){
                //
                //                 if(d.get_value("item")==frm.doc.tools[0]["item_code"]){
                //                      // console.log("hello from g")
                //                     d.fields_dict.qty.set_value(frm.doc.tools[i]["delivered_qty"] || 0);
                //                     d.fields_dict.qty.refresh();
                //                 }
                //             }
                //         }
                //     }, {
                //         label:__("Qty"),
                //         fieldname: 'qty',
                //         fieldtype: 'Int',
                //         readonly:1
                //     }
                // ],primary_action:function(){
                //     var args = d.get_values();
                //     d.hide()
                //     frappe.call({
                //         'method':"create_stock_entry_backend_return",
                //         'doc':frm.doc,
                //         args:{
                //             employee:args.employee,
                //             item:args.item,
                //             qty:args.qty
                //         }
                //     })
                // }
                //  });
                //         d.show()
                //         //frm.events.create_stock_entry (frm);
                //     }, __("Create"));
            }


        },
    start_date:function (frm) {
        frm.events.get_duration(frm)
    },
     end_date:function (frm) {
frm.events.get_duration(frm)
    },

deliver_to_customer:function(frm){
	   var selected_rows = [];
  		// frm.doc.tools.forEach((row) => {
        //
  		// 	if(row.__checked && row.item_code){
  		// 		selected_rows.push(row.reference);
  		// 	}
  		// });
  		// console.log(selected_rows)
        // if (selected_rows.length <= 0)
        //     frappe.throw(__("No Tools Selected"))
    let d = new frappe.ui.Dialog({
                     title: 'Select Delivery Type',
                     fields: [
                    {
                        label:__("Type"),
                        fieldname: 'type',
                        fieldtype: 'Select',
                        // options:['Deliver From Custody','Deliver From Stock'],
                        options:['Deliver From Stock'],
                        default :'Deliver From Stock' ,
                        translatable: 1,
                        req:1
                    }
                ],primary_action:function(){
                    var args = d.get_values();
                    d.hide()
                    if (args.type == 'Deliver From Stock') {
                        frappe.model.open_mapped_doc({
                            method: "erpnext.operations.doctype.customer_agrement.customer_agrement.create_delivery_note",
                            frm: frm,
                        })
                    }else {
                        //  frappe.model.open_mapped_doc({
                        //     method: "erpnext.operations.doctype.customer_agrement.customer_agrement.deliver_to_customer",
                        //     frm: frm,
                        // })
                    }
                }
                 });
                        d.show()

        //
        // frappe.call({
        //     method:"deliver_to_customer",
        //     doc:frm.doc,
        //     args:{
        //         selected : selected_rows
        //     },
        //     callback:function (r) {
        //
        //     }
        // })
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
    create_Due:function(frm){
	     // frm.save()
	     frm.doc.company = frappe.defaults.get_default("company")
	     frappe.model.open_mapped_doc({
			method: "erpnext.operations.doctype.customer_agrement.customer_agrement.create_Due",
			frm: frm

		})
    },
    create_delivery_note:function(frm){
	     frm.save()
	     frm.doc.company = frappe.defaults.get_default("company")
	     frappe.model.open_mapped_doc({
			method: "erpnext.operations.doctype.customer_agrement.customer_agrement.create_delivery_note",
			frm: frm

		})
    },
    create_stock_entry:function(frm){
	     frm.save()
	     frm.doc.company = frappe.defaults.get_default("company")
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
    },tax:function(frm,cdt,cdn)
    {
        frm.events.calculate_employee_totals(frm)
    },
    // gross_salary:function(frm,cdt,cdn)
    // {
    //     frm.events.calculate_employee_totals(frm)
    // },
    social_insurance:function(frm,cdt,cdn)
    {
        frm.events.calculate_employee_totals(frm)
    },
    life_insurance:function(frm,cdt,cdn)
    {
        frm.events.calculate_employee_totals(frm)
    },
    mobile_package:function(frm,cdt,cdn)
    {
        frm.events.calculate_employee_totals(frm)
    },
    ohs_courses:function(frm,cdt,cdn)
    {
        frm.events.calculate_employee_totals(frm)
    },

    medical_insurance:function(frm,cdt,cdn)
    {
        frm.events.calculate_employee_totals(frm)
    },
    laptop:function(frm,cdt,cdn)
    {
        frm.events.calculate_employee_totals(frm)
    }, mobile_allowance:function(frm,cdt,cdn)
    {
        frm.events.calculate_employee_totals(frm)
    }, ohs_tools:function(frm,cdt,cdn)
    {
        frm.events.calculate_employee_totals(frm)
    },
    //  other_ereanings:function(frm,cdt,cdn)
    // {
    //     frm.events.calculate_employee_totals(frm)
    // },
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

frappe.ui.form.on('Customer Agreement Dues', {
    create_invoice :function (frm,cdt,cdn) {
        var row = locals [cdt] [cdn]
        if (!row.invoiced) {
            frappe.call(
                {
                    method: "erpnext.operations.doctype.customer_agrement.customer_agrement.create_invoice_from_due",
                    args: {
                        "doc_name":row.due
                    },
                    callback: function (r) {
                        frappe.msgprint(__('Done'))
                        frm.refresh()
                    }
                }
            )
        }
    }
});
