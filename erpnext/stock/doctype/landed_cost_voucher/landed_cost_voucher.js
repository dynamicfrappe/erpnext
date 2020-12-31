
// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt


frappe.provide("erpnext.stock");

erpnext.stock.LandedCostVoucher = erpnext.stock.StockController.extend({
	setup: function() {
		var me = this;
		this.frm.fields_dict.purchase_receipts.grid.get_field('receipt_document').get_query =
			function (doc, cdt, cdn) {
				var d = locals[cdt][cdn]

				var filters = [
					[d.receipt_document_type, 'docstatus', '=', '1'],
					[d.receipt_document_type, 'company', '=', me.frm.doc.company],
				]

				if (d.receipt_document_type == "Purchase Invoice") {
					filters.push(["Purchase Invoice", "update_stock", "=", "1"])
				}

				if (!me.frm.doc.company) frappe.msgprint(__("Please enter company first"));
				return {
					filters: filters
				}
			};

		this.frm.add_fetch("receipt_document", "supplier", "supplier");
		this.frm.add_fetch("receipt_document", "posting_date", "posting_date");
		this.frm.add_fetch("receipt_document", "base_grand_total", "grand_total");

		this.frm.set_query("expense_account", "taxes", function() {
			return {
				query: "erpnext.controllers.queries.tax_account_query",
				filters: {
					"account_type": ["Tax", "Chargeable", "Income Account", "Expenses Included In Valuation", "Expenses Included In Asset Valuation"],
					"company": me.frm.doc.company
				}
			};
		});


			this.frm.set_query("type", "landed_cost_voucher_expenses", (doc) => {
			return {
				
				query : "erpnext.stock.doctype.landed_cost_voucher.landed_cost_voucher.get_query_type"
			};

		})

			

		this.frm.fields_dict.landed_cost_voucher_expenses.grid.get_field('reference').get_query =
		function(doc,cdt,cdn) {
			var d = locals[cdt][cdn]

				

				if (d.type == "Payment Entry") {
					var filters = [
					[d.type, 'docstatus', '=', '1'],
					[d.type, 'company', '=', me.frm.doc.company],
				]
					filters.push(["Payment Entry", "payment_type", "=", "Pay"])
				}
				
				var filters = [
					[d.type, 'docstatus', '=', '1'],
					[d.type, 'company', '=', me.frm.doc.company],
				]
				if (d.type == "Purchase Invoice") {



					return {
						query : "erpnext.stock.doctype.landed_cost_voucher.landed_cost_voucher.get_purchase_items"
					}

					
				}

				if (!me.frm.doc.company) frappe.msgprint(__("Please enter company first"));
				return {
					filters: filters
				}
			
		}
		



	},
	

	refresh: function(frm) {
		var help_content =
			`<br><br>
			<table class="table table-bordered" style="background-color: #f9f9f9;">
				<tr><td>
					<h4>
						<i class="fa fa-hand-right"></i>
						${__("Notes")}:
					</h4>
					<ul>
						<li>
							${__("Charges will be distributed proportionately based on item qty or amount, as per your selection")}
						</li>
						<li>
							${__("Remove item if charges is not applicable to that item")}
						</li>
						<li>
							${__("Charges are updated in Purchase Receipt against each item")}
						</li>
						<li>
							${__("Item valuation rate is recalculated considering landed cost voucher amount")}
						</li>
						<li>
							${__("Stock Ledger Entries and GL Entries are reposted for the selected Purchase Receipts")}
						</li>
					</ul>
				</td></tr>
			</table>`;

		set_field_options("landed_cost_help", help_content);
	},

	get_items_from_purchase_receipts: function() {
		var me = this;
		if(!this.frm.doc.purchase_receipts.length) {
			frappe.msgprint(__("Please enter Purchase Receipt first"));
		} else {
			return this.frm.call({
				doc: me.frm.doc,
				method: "get_items_from_purchase_receipts",
				callback: function(r, rt) {
					me.set_applicable_charges_for_item();
				}
			});
		}
	},

	amount: function(frm) {
		this.set_total_taxes_and_charges();
		this.set_applicable_charges_for_item();
		frappe.call({
				method : "update_allocated_amount",
				doc:this.frm.doc ,
				callback:function(r){
					refresh_field("landed_cost_voucher_expenses")
				}
			})

		
	},
	

	set_total_taxes_and_charges: function() {
		var total_taxes_and_charges = 0.0;
		$.each(this.frm.doc.taxes || [], function(i, d) {
			total_taxes_and_charges += flt(d.amount)
		});
		cur_frm.set_value("total_taxes_and_charges", total_taxes_and_charges);
	},

	set_applicable_charges_for_item: function() {
		var me = this;

		if(this.frm.doc.taxes.length) {

			var total_item_cost = 0.0;
			var based_on = this.frm.doc.distribute_charges_based_on.toLowerCase();
			$.each(this.frm.doc.items || [], function(i, d) {
				total_item_cost += flt(d[based_on])
			});

			var total_charges = 0.0;
			$.each(this.frm.doc.items || [], function(i, item) {
				item.applicable_charges = flt(item[based_on]) * flt(me.frm.doc.total_taxes_and_charges) / flt(total_item_cost)
				item.applicable_charges = flt(item.applicable_charges, precision("applicable_charges", item))
				total_charges += item.applicable_charges
			});

			if (total_charges != this.frm.doc.total_taxes_and_charges){
				var diff = this.frm.doc.total_taxes_and_charges - flt(total_charges)
				this.frm.doc.items.slice(-1)[0].applicable_charges += diff
			}
			refresh_field("items");
		}
	},
	
	distribute_charges_based_on: function (frm) {
		this.set_applicable_charges_for_item();
	},
	taxes_remove(frm){
		frappe.call({
				method : "update_allocated_amount",
				doc:this.frm.doc ,
				callback:function(r){
				
					refresh_field("landed_cost_voucher_expenses")
				}
			})
	},

	items_remove: () => {
		this.trigger('set_applicable_charges_for_item');
	},
	reference:function(frm){
		
		this.set_total_taxes_and_charges();
		this.set_applicable_charges_for_item();
	},
	// taxes_add:function(frm){
	// 	var i = 0 
	// 	for(i =0 ; i < frm.doc.taxes.length ;i++){
	// 		console.log(i.refrence , i.amount)
	// 	} 

	// },
	landed_cost_voucher_expenses_remove:function(frm){
		
		this.frm.clear_table("taxes")
		this.frm.refresh_field("taxes")

		if (this.frm.doc.landed_cost_voucher_expenses.length > 0){
			
			var i = 0 
			var me = this ;
			for (i=0 ; i < this.frm.doc.landed_cost_voucher_expenses.length ; i ++){
						

						frappe.call({
								method:'erpnext.stock.doctype.landed_cost_voucher.landed_cost_voucher.set_frm_query',
								args:{
								tpe : me.frm.doc.landed_cost_voucher_expenses[i].type ,
						    	refrence :me.frm.doc.landed_cost_voucher_expenses[i].reference,
									},				
				callback:function(r){
					
					var e = 0 
					for (e=0;e < r.message.length ; e++){




						// 

						// 
						var child = me.frm.add_child("taxes")
						// console.log(r.message[e].name)
						child.description = r.message[e].desc
						child.expense_account = r.message[e].account
						child.amount = r.message[e].amount	
						child.refrence = r.message[e].name
						if (r.message[e].party){
												child.party = r.message[e].party
												child.party_type= r.message[e].party_type}

							me.frm.refresh_field("taxes")
						
					}
				}
			
	
	})

			}


			


		}
		frappe.call({
				method : "update_allocated_amount",
				doc:this.frm.doc ,
				callback:function(r){
					console.log("work")
					frm.refresh_field("landed_cost_voucher_expenses")
				}
			})

	}




});

frappe.ui.form.on('Landed Cost Voucher',{
	onload:function(frm){
		frm.clear_table("taxes");
		frm.set_df_property("landed_cost_voucher_expenses",'hidden' ,1)
		// frm.events.show_general_ledger(frm)

	},
	refresh:function(frm){
		if(frm.doc.docstatus===1) {

			var i = 0 
			for(i =0 ; i < frm.doc.purchase_receipts.length ; i ++){
				
						frm.add_custom_button(__('Accounting Ledger'), function() {
							frappe.route_options = {
								voucher_no: frm.doc.purchase_receipts[0].receipt_document,
								from_date: frm.doc.purchase_receipts[0].posting_date,
								to_date: frm.doc.purchase_receipts[0].posting_date,
								company: frm.doc.company,
								group_by: "Group by Voucher (Consolidated)"
							};
							frappe.set_route("query-report", "General Ledger");
						}, __("View"));}
		}

	} ,
	

landed_cost_details:function(frm){
	var num = 1
	if (frm.doc.landed_cost_details == 1){num=0}
	frm.set_df_property("landed_cost_voucher_expenses",'hidden' ,num)
	frm.refresh_field("landed_cost_voucher_expenses")

},

show_general_ledger: function(frm) {
		// var me = this;
		if(frm.doc.docstatus===1) {
			frm.add_custom_button(__('Accounting Ledger'), function() {


				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company,
					group_by: "Group by Voucher (Consolidated)"
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		}
	}


	})



// frappe.ui.form.on('Landed Cost Taxes and Charges', {
// 	amount:function(frm ,cdt,cdn){
// 		var local = locals[cdt][cdn]
// 		// console.log(local.amount)
// 	}
// })
frappe.ui.form.on('Landed Cost Voucher Expenses', {

type:function(frm ,cdt,cdn){
	var local = locals[cdt][cdn] },
allocated:function(frm,cdt,cdn){
		var local = locals[cdt][cdn]
		console.log(local.allocated)
	}	,
reference:function(frm,cdt,cdn){
	// frm.doc
	// console.log(frm.doc)
	var local = locals[cdt][cdn] 
	if (local.reference.length ){
			frappe.call({ 
				method :'erpnext.stock.doctype.landed_cost_voucher.landed_cost_voucher.complete_data',
				args:{
					"refre":local.reference,
					"typ":local.type
				},
				callback:function(r){
					local.amount = r.message['grand_total']
					local.outstanding = r.message['unallocated_amount']
					console.log(r.message['unallocated_amount'])
					frm.refresh_field('landed_cost_voucher_expenses')
				}
			})
			frappe.call({
				method:'erpnext.stock.doctype.landed_cost_voucher.landed_cost_voucher.set_frm_query',
				args:{
								tpe : local.type ,
						    	refrence :local.reference,
				},				
				callback:function(r){
					
					var i = 0 
					for (i=0;i < r.message.length ; i++){
						var child = frm.add_child("taxes")
						child.description = r.message[i].desc
						child.expense_account = r.message[i].account
						
						var tot = local.allocated + local.outstanding 
						var available = local.amount - tot
						child.refrence = r.message[i].name
						if (available < r.message[i].amount)  {
							child.amount = available
						}
						else{
							child.amount = r.message[i].amount
						}
						local.allocated += child.amount
						if (r.message[i].party){
												child.party = r.message[i].party
												child.party_type= r.message[i].party_type}
						frm.refresh_field("taxes")
						frm.refresh_field("landed_cost_voucher_expenses")
					}
				}
			
	
	})}


		// 	frappe.call({
		// 	doc:frm.doc,
		// 	method:"update_allocated_amount",
		// 	callback:function(r){
		// 		refresh_field('landed_cost_voucher_expenses')
		// 	}
		// })

} })



cur_frm.script_manager.make(erpnext.stock.LandedCostVoucher);