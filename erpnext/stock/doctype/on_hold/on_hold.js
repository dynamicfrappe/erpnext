// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('On Hold', {
	// refresh: function(frm) {

	// }
	onload:(frm) =>{
			if (frm.doc.docstatus == 0 && !(frm.doc.end_date) )
			{
					frappe.db.get_single_value("Stock Settings", "item_holding_duration").then(duration => {
						debugger;
						if (duration == null){ 
							duration = 0;
						}
						var date = new Date(frm.doc.start_date);
						date.setDate( date.getDate() +duration);
							frm.doc.end_date = date.getFullYear()+"-"+  (date.getMonth()+1) +"-"+ date.getDay()  ;
						});

			}
		
	
	},
	sales_order:function(frm,cdt,cdn){
		var s_o = frm.doc.sales_order ;
		frm.clear_table('ob_hold_items')
		if (s_o){
			frappe.call({
				method: "frappe.client.get",
				args:{
					doctype:"Sales Order",
					name :s_o
								},
				callback:function(r){
					
					var i = 0
					for(i=0 ; i<r.message.items.length; i++){
									frappe.call({
										method:"erpnext.stock.doctype.on_hold.on_hold.get_item_wharehouse",
										args:{
											item :  r.message.items[i].item_code ,
											qtyy : r.message.items[i].stock_qty ,
											name : frm.doc.name
											
										},
										callback:function(r){
											debugger ;
											if (r.message)
											{
												r.message.forEach(function(item) {
												var row = frm.add_child("ob_hold_items");
												row.item_code = item.item_code;
												row.warehouse = item.warehouse;
												row.qty = item.qty
												});
												frm.refresh_field("ob_hold_items")
											}
											
										}
									})
									
								}
								

				}
			});

		}
	}
});
