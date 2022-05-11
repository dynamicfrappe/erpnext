// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplier Quotation Price List Comparison"] = {
	"filters": [
		{
			"fieldname":"RFQ_No",
			"label": __("RFQ No"),
			"fieldtype": "Link",
			"options": "Request for Quotation",
			reqd: 1

		},
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options" : "Request for Quotation Item",
			/*"get_query": frappe.call({
				method: "erpnext.buying.report.supplier_quotation_price_list_comparison.supplier_quotation_price_list_comparison.get_items",
				args: {
					filters: frappe.query_report.get_filter_value("RFQ_No")
				}
				
			})
			*/
			
			"get_query": function(){
/*
				var items = []

				if (frappe.query_report.filters[0].value != null)
				{
				frappe.call({
					method: "erpnext.buying.report.supplier_quotation_price_list_comparison.supplier_quotation_price_list_comparison.get_items",
					args: {
						RFQ: frappe.query_report.filters[0].value,
					},
					callback: function(r) {
						if(r.message) {
							items = [] 
							r.message.forEach(element => {
								items.push(element.item_code)
							});
							return {
								filters: [
									["Item", "item_code", "IN", items]
								]
							};
						}
					}
				});
				
			}*/
				return {'filters': [['Request for Quotation Item', 'parent','IN', frappe.query_report.get_filter_value("RFQ_No") ]]}
			}
			
			
		}
	]
};
