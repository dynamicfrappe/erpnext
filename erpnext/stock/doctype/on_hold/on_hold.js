// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('On Hold', {
	// refresh: function(frm) {

	// }

	sales_order:function(frm,cdt,cdn){
		var s_o = frm.doc.sales_order ;
		frappe.call({
			method: "frappe.client.get",
			args:{
				doctype:"Sales Order",
				name :s_o
							},
			callback:function(r){
				
				var i = 0
				for(i=0 ; i<r.message.items.length; i++){
								
								
								frm.clear_table('ob_hold_items')
								

								frappe.call({
									method:"erpnext.stock.doctype.on_hold.on_hold.get_item_wharehouse",
									args:{
										item :  r.message.items[i].item_code ,
										qtyy : r.message.items[i].stock_qty
										
									},
									callback:function(m){
										// console.log(m.message)
										if(m.message.data.length > 0 && m.message.check =="one"){
											var items_table = frm.add_child('ob_hold_items')
											items_table.item_code =   m.message.item_code
											items_table.qty =m.message.qty
											items_table.warehouse = m.message.data[0]
											frm.refresh_field("ob_hold_items")

										}

										if(m.message.data.length > 0 && m.message.check =="many"){
											
											var e = 0
											for (e=0 ; e < m.message.data.length ; e++){
												var items_table = frm.add_child('ob_hold_items')
												console.log(m.message.qty)
																						items_table.item_code =   m.message.item_code
																						items_table.qty =m.message.qty[e]
																						items_table.warehouse = m.message.data[e]
																					frm.refresh_field("ob_hold_items")}
											

										}
									}
								})
								
							}
							

			}
		}
		)
	}
});
