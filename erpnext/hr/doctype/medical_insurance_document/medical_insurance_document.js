// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Medical Insurance Document', {
	// refresh: function(frm) {

	// }
	add_time_table_for_payments:function(frm){
		if (!frm.doc.data_3 ){
			frappe.throw(" Pleas Add insurance Value First")
		}

		if (frm.doc.add_time_table_for_payments) {
			var count = frm.doc.payment_terms
			var i = 0 
			for(i=0 ; i < count ; i++){
				var child = frm.add_child("time_table")
				child.amount = frm.doc.data_3 / count
			}
			frm.refresh_field("time_table")
		}else {
			frm.clear_table("time_table")
			frm.refresh_field("time_table")
		}

	},
	payment__table_add:function(frm){
		console.log("add")
	}
});





frappe.ui.form.on('Incurance Payment Terms Table', {
	amount:function(frm ,cdt,cdn){
		var local = locals[cdt][cdn]
		frm.doc.data_3 = 0
		var i = 0 
		for (i =0 ; i < frm.doc.payment__table.length ; i ++){
			frm.doc.data_3 += frm.doc.payment__table[i].amount
			frm.refresh_field("data_3")
		}

	},
	payment__table_remove:function(frm){
		frm.doc.data_3 = 0
		var i = 0 
		for (i =0 ; i < frm.doc.payment__table.length ; i ++){
			frm.doc.data_3 += frm.doc.payment__table[i].amount
			frm.refresh_field("data_3")
		}
	}



})