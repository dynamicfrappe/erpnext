// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Value Added Tax', {
	refresh:function (frm){

         if(frm.doc.docstatus==0 && frm.doc.details !=null &&frm.doc.journal_created==0){
         	frm.add_custom_button(__("Create Journal Entry"), function() {
                 frappe.call({
					 method: "createJournalEntry",
					 doc:frm.doc,
					 callback(r) {
                      //frm.page.clear_primary_action();
					 }
				 })

        		}).addClass("btn-primary");

		 }
	},
	todate:function (frm){
	  if(frm.doc.todate &&frm.doc.fromdae){
	  	frm.add_custom_button(__("Get Taxes"), function() {
	  		cur_frm.clear_table("details");
	  		frm.call({
				method:"getTaxes",
				doc:frm.doc,
				args:{
					 "fromDate":frm.doc.fromdae,
					"todate":frm.doc.todate
				},
				callback(r){
				var template = "<table style='border: 1px solid black;width: 100%;border-collapse: collapse;'><tr><th style='border: 1px solid #000000'>Document Type</th><th style='border: 1px solid black'>Document Number</th><th style='border: 1px solid black'>Date</th><th style='border: 1px solid black'>Document Amount</th><th style='border: 1px solid black'>Tax Amount</th><th style='border: 1px solid black'>Tax Category</th><th style='border: 1px solid black'>Tax Type</th></tr>"
         	for (var i=0;i<frm.doc.details.length;i++){
               template+="<tr><td style='border: 1px solid black'>"+frm.doc.details[i]["doocumenttpe"]+"</td><td style='border: 1px solid black'>"+frm.doc.details[i]["documentnumber"]+"</td>"+"<td style='border: 1px solid black'>"+frm.doc.details[i]["docdate"]+"</td>"+"<td style='border: 1px solid black'>"+frm.doc.details[i]["docamount"]+"</td>"+"<td style='border: 1px solid black'>"+frm.doc.details[i]["taxamount"]+"</td>"+"<td style='border: 1px solid black'>"+frm.doc.details[i]["taxcategory"]+"</td>"+"<td style='border: 1px solid black'>"+frm.doc.details[i]["taxtype"]+"</td>"+"</tr>";
			}
         	 frm.set_df_property('htmltemplate', 'options',template);
                 frm.refresh_field("details")
					frm.save();
				}
			})


        }).addClass("btn-primary");

	  }
	},
	drawTable:function (frm){
				var template = "<table style='border: 1px solid black;width: 100%;border-collapse: collapse;'><tr><th style='border: 1px solid black'>Document Type</th><th style='border: 1px solid black'>Document Number</th><th style='border: 1px solid black'>Date</th><th style='border: 1px solid black'>Document Amount</th><th style='border: 1px solid black'>Tax Amount</th><th style='border: 1px solid black'>Tax Category</th><th style='border: 1px solid black'>Tax Type</th></tr>"
         	for (var i=0;i<frm.doc.details.length;i++){
               template+="<tr><td style='border: 1px solid black'>"+frm.doc.details[i]["doocumenttpe"]+"</td><td style='border: 1px solid black'>"+frm.doc.details[i]["documentnumber"]+"</td>"+"<td style='border: 1px solid black'>"+frm.doc.details[i]["docdate"]+"</td>"+"<td style='border: 1px solid black'>"+frm.doc.details[i]["docamount"]+"</td>"+"<td style='border: 1px solid black'>"+frm.doc.details[i]["taxamount"]+"</td>"+"<td style='border: 1px solid black'>"+frm.doc.details[i]["taxcategory"]+"</td>"+"<td style='border: 1px solid black'>"+frm.doc.details[i]["taxtype"]+"</td>"+"</tr>";
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
