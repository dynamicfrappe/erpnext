// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Custody Movement', {
	refresh: function(frm) {
        frm.events.set_fields_status(frm)
        frm.events.set_fields_query(frm)

	},
    type: function(frm) {
        frm.events.set_fields_status(frm)
        frm.events.set_fields_query(frm)
         frm.clear_table("items")
        refresh_field('items')

	},
    to_customer_agreement: function(frm) {

        frm.events.set_fields_status(frm)
        frm.events.set_fields_query(frm)
         frm.clear_table("items")
        refresh_field('items')

	},
    from_customer_agreement: function(frm) {
        frm.events.set_fields_status(frm)
        frm.events.set_fields_query(frm)
         frm.clear_table("items")
        refresh_field('items')

	},
    is_custody: function(frm) {
        frm.events.set_fields_status(frm)
        frm.events.set_fields_query(frm)

	},
    set_fields_status:function (frm) {
        if (frm.doc.type == 'Send'){
            frm.set_df_property('to_customer_agreement','hidden',0)
            frm.set_df_property('to_customer_agreement','reqd',1)

            frm.set_df_property('to_employee','hidden',0)
            frm.set_df_property('to_employee','reqd',1)


            frm.set_df_property('target_warehouse','hidden',0)
            frm.set_df_property('target_warehouse','reqd',1)

            frm.set_df_property('from_employee','hidden',1)
            frm.set_df_property('from_employee','reqd',0)

            frm.set_df_property('from_customer_agreement','hidden',1)
            frm.set_df_property('from_customer_agreement','reqd',0)

            frm.set_df_property('source_warehouse','hidden',1)
            frm.set_df_property('source_warehouse','reqd',0)

            frm.set_df_property('custody_warehouse','hidden',1)
            frm.set_df_property('custody_warehouse','reqd',0)


        }
        if (frm.doc.type == 'Transfer'){
            frm.set_df_property('to_customer_agreement','hidden',0)
            frm.set_df_property('to_customer_agreement','reqd',1)

            frm.set_df_property('to_employee','hidden',0)
            frm.set_df_property('to_employee','reqd',1)


            frm.set_df_property('target_warehouse','hidden',0)
            frm.set_df_property('target_warehouse','reqd',1)

            frm.set_df_property('from_employee','hidden',0)
            frm.set_df_property('from_employee','reqd',1)

            frm.set_df_property('from_customer_agreement','hidden',0)
            frm.set_df_property('from_customer_agreement','reqd',1)

            frm.set_df_property('source_warehouse','hidden',0)
            frm.set_df_property('source_warehouse','reqd',1)

            frm.set_df_property('custody_warehouse','hidden',1)
            frm.set_df_property('custody_warehouse','reqd',0)
        }
        if (frm.doc.type == 'Return' || frm.doc.type == 'Deliver'){
            frm.set_df_property('to_customer_agreement','hidden',1)
            frm.set_df_property('to_customer_agreement','reqd',0)

            frm.set_df_property('to_employee','hidden',1)
            frm.set_df_property('to_employee','reqd',0)


            frm.set_df_property('target_warehouse','hidden',1)
            frm.set_df_property('target_warehouse','reqd',0)

            frm.set_df_property('from_employee','hidden',0)
            frm.set_df_property('from_employee','reqd',1)

            frm.set_df_property('from_customer_agreement','hidden',0)
            frm.set_df_property('from_customer_agreement','reqd',1)

            frm.set_df_property('source_warehouse','hidden',0)
            frm.set_df_property('source_warehouse','reqd',1)

            frm.set_df_property('custody_warehouse','hidden',1)
            frm.set_df_property('custody_warehouse','reqd',0)

        }
        if ( frm.doc.type == 'Receipt from Customer'){
            frm.set_df_property('to_customer_agreement','hidden',1)
            frm.set_df_property('to_customer_agreement','reqd',0)

            frm.set_df_property('to_employee','hidden',1)
            frm.set_df_property('to_employee','reqd',0)


            frm.set_df_property('target_warehouse','hidden',1)
            frm.set_df_property('target_warehouse','reqd',0)




            frm.set_df_property('source_warehouse','hidden',1)
            frm.set_df_property('source_warehouse','reqd',0)

            frm.set_df_property('custody_warehouse','hidden',0)
            frm.set_df_property('custody_warehouse','reqd',1)

             frm.set_df_property('from_customer_agreement','hidden',0)
            frm.set_df_property('from_customer_agreement','reqd',1)

             frm.set_df_property('from_employee','hidden',!cur_frm.doc.is_custody)
            frm.set_df_property('from_employee','reqd',cur_frm.doc.is_custody)


        }

    },
    set_fields_query:function(frm){


	    frm.fields_dict['from_employee'].get_query = function(doc, cdt, cdn){

                return {
                    query:"dynamicerp.dynamic_erp.doctype.stock_entry.stock_entry.get_Employee_query",
                    filters: {'customer_agreement': frm.doc.from_customer_agreement}
                }
            };
	    frm.fields_dict['to_employee'].get_query = function(doc, cdt, cdn){

                return {
                    query:"dynamicerp.dynamic_erp.doctype.stock_entry.stock_entry.get_Employee_query",
                    filters: {'customer_agreement': frm.doc.to_customer_agreement}
                }
            };


	     if (frm.doc.type == 'Send' ){

            frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn){

                return {
                    query:"dynamicerp.dynamic_erp.doctype.stock_entry.stock_entry.get_items_query",
                    filters: {'customer_agreement': frm.doc.to_customer_agreement}
                }
            };
	     }
        if (frm.doc.type == 'Transfer'){



            frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn){

                return {
                    query:"dynamicerp.dynamic_erp.doctype.stock_entry.stock_entry.get_inner_items_query",
                    filters: {
                        'from_customer_agreement': frm.doc.from_customer_agreement ,
                        'to_customer_agreement': frm.doc.to_customer_agreement
                    }
                }
            };


        }
        if (frm.doc.type == 'Return' || frm.doc.type == 'Deliver' || frm.doc.type == 'Receipt from Customer' ){

            frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn){
                return {
                    query:"dynamicerp.dynamic_erp.doctype.stock_entry.stock_entry.get_items_query",
                    filters: {'customer_agreement': cur_frm.doc.from_customer_agreement}
                }
            };



        }






        frm.set_query("custody_warehouse" , function(frm){
                 return {
                     filters :{
                        customer_custody_warehouse:1
                     }
                 }
             })





    }
});
