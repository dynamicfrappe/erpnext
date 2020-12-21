// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Insurance Organization', {
	refresh: function(frm) {
		if (! frm.is_new()){
			frm.add_custom_button(__('Create Disbursement Entry'), function () {
				// frm.trigger("make_jv");
				// console.log("here")
				frappe.call({
					doc : frm.doc ,
					method : "get_print"
					,callback:function(r){
						 frm.set_df_property('html', 'options',r.message );
						 frm.refresh_field('html')

					}
				})
				
			})
		}
	}
});



