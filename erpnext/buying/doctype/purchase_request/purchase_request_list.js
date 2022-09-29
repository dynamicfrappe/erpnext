frappe.listview_settings['Purchase Request'] = {
	
	
	onload: function(listview) {
		
		
		
		return frappe.call({
			// doc: cur_frm.doc,
			"method":"erpnext.buying.doctype.purchase_request.purchase_request.query_set" ,
				args:{
					"purchase_requests":"1"},
				
			callback: function(r) {
				


				frappe.set_route('List','Material Request',{"DIR": "purchase request"
					   })  }
			
		});
	
	
	
},

}