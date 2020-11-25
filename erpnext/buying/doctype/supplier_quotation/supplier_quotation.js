// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// attach required files
{% include 'erpnext/public/js/controllers/buying.js' %};

erpnext.buying.SupplierQuotationController = erpnext.buying.BuyingController.extend({
	setup: function() {
		this.frm.custom_make_buttons = {
			'Purchase Order': 'Purchase Order',
			'Quotation': 'Quotation'
		}

		this._super();


		if (this.frm.doc.material_request){
			this.frm.get_field("items").grid.set_multiple_add();
			this.frm.get_field('items').grid.cannot_add_rows = true;
		}

		if (this.frm.doc.rfq){
			this.frm.get_field("items").grid.set_multiple_add();
			this.frm.get_field('items').grid.cannot_add_rows = true;
		}
		if (this.frm.doc.purchase_request){
			this.frm.get_field("items").grid.set_multiple_add();
			this.frm.get_field('items').grid.cannot_add_rows = true;
			this.frm.set_df_property("link_to_mrs", "hidden", "1")
		}



		var i =0 
		try{
				for (i = 0 ;i < this.frm.doc.items.length ; i++){
						this.frm.doc.items[i].rate = 0
						this.frm.doc.items[i].price_list_rate=  0}

		}
		catch(err) {
 			console.log("no items")
			}

	},

	refresh: function() {
		var me = this;
		if (this.frm.doc.material_request){
			this.frm.get_field("items").grid.set_multiple_add();
			this.frm.get_field('items').grid.cannot_add_rows = true;
		}

		if (this.frm.doc.rfq){
			this.frm.get_field("items").grid.set_multiple_add();
			this.frm.get_field('items').grid.cannot_add_rows = true;
		}
		this._super();
		
		if (this.frm.doc.__islocal && !this.frm.doc.valid_till) {
			this.frm.set_value('valid_till', frappe.datetime.add_months(this.frm.doc.transaction_date, 1));
		}
		if (this.frm.doc.docstatus === 1) {
			cur_frm.add_custom_button(__("Purchase Order"), this.make_purchase_order,
				__('Create'));
			cur_frm.page.set_inner_btn_group_as_primary(__('Create'));
			cur_frm.add_custom_button(__("Quotation"), this.make_quotation,
				__('Create'));
		}
		else if (this.frm.doc.docstatus===0) {

			this.frm.add_custom_button(__('Material Request'),
				function() {
					erpnext.utils.map_current_doc({
						method: "erpnext.stock.doctype.material_request.material_request.make_supplier_quotation",
						source_doctype: "Material Request",
						target: me.frm,
						setters: {
							company: me.frm.doc.company
						},
						get_query_filters: {
							material_request_type: "Purchase",
							docstatus: 1,
							status: ["!=", "Stopped"],
							per_ordered: ["<", 99.99]
						}
					})
				}, __("Get items from"));

			this.frm.add_custom_button(__("Request for Quotation"),
			function() {
				if (!me.frm.doc.supplier) {
					frappe.throw({message:__("Please select a Supplier"), title:__("Mandatory")})
				}
				erpnext.utils.map_current_doc({
					method: "erpnext.buying.doctype.request_for_quotation.request_for_quotation.make_supplier_quotation_from_rfq",
					source_doctype: "Request for Quotation",
					target: me.frm,
					setters: {
						company: me.frm.doc.company,
						transaction_date: null
					},
					get_query_filters: {
						supplier: me.frm.doc.supplier
					},
					get_query_method: "erpnext.buying.doctype.request_for_quotation.request_for_quotation.get_rfq_containing_supplier"

				})
			}, __("Get items from"));
		}
	},

	make_purchase_order: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.make_purchase_order",
			frm: cur_frm
		})
	},
	make_quotation: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.buying.doctype.supplier_quotation.supplier_quotation.make_quotation",
			frm: cur_frm
		})

	},

	material_request:function(frm){
		console.log("MAT")

	}
});

// for backward compatibility: combine new and previous states
$.extend(cur_frm.cscript, new erpnext.buying.SupplierQuotationController({frm: cur_frm}));

cur_frm.fields_dict['items'].grid.get_field('project').get_query =
	function(doc, cdt, cdn) {
		return{
			filters:[
				['Project', 'status', 'not in', 'Completed, Cancelled']
			]
		}
	}
