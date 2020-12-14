// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Value Added Tax', {
	todate:function (frm){
	  if(frm.doc.todate &&frm.doc.fromdae){
	  	frm.add_custom_button(__("Get Taxes"), function() {
	  		frm.call({
				method:"getTaxes",
				doc:frm.doc,
				args:{
					 "fromDate":frm.doc.fromdae,
					"todate":frm.doc.todate
				},
				callback(r){
                 frm.refresh_field("details")
				}
			})


        }).addClass("btn-primary");
	  }
	},
	setup: function(frm) {
		frm.fields_dict['details'].grid.get_field("doocumenttpe").get_query = function(doc, cdt, cdn) {
	return {
		filters: [
			['DocType', 'name', 'in','Sales Invoice,Purchase Invoice'],

		]
	}
}

	},


});

  frappe.ui.form.on("Value Added Tax Details",
	  {
	  	doocumenttpe:function (frm,cdt,cdn) {
	  		var local = locals[cdt][cdn]
			if (local.doocumenttpe=="Sales Invoice"){
				//frm.set_value(cdt,cdn,"","Customer")
				local.partner_type="Customer"
				frm.refresh_field('details')
			}else {
				local.partner_type="Supplier"
				frm.refresh_field('details')
			}


		}
	  })
