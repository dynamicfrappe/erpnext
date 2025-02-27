// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

{% include 'erpnext/selling/sales_common.js' %};

erpnext.selling.POSInvoiceController = erpnext.selling.SellingController.extend({
	setup(doc) {
		this.setup_posting_date_time_check();
		this._super(doc);

	},

	onload(doc) {
		this._super();
		if(doc.__islocal && doc.is_pos && frappe.get_route_str() !== 'point-of-sale') {
			this.frm.script_manager.trigger("is_pos");
			this.frm.refresh_fields();
		}
	},


	refresh(doc) {
		this._super();
		if ( !doc.consolidated_invoice && doc.docstatus == 1 && doc.returned==0 && !doc.is_return && frappe.perm.has_perm(doc.doctype, 1, 'write')) {
			this.frm.add_custom_button(__('Return'), this.make_sales_return, __('Create'));
			this.frm.page.set_inner_btn_group_as_primary(__('Create'));
		}

		if (doc.is_return && doc.__islocal) {
			this.frm.return_print_format = "Sales Invoice Return";
			this.frm.set_value('consolidated_invoice', '');
		}

			


			frappe.call({
				method: "update_values_for_return" ,
				"doc" : doc
			})
  			
	},

	is_pos: function() {
		this.set_pos_data();
	},

	set_pos_data: async function() {
		if(this.frm.doc.is_pos) {
			this.frm.set_value("allocate_advances_automatically", 0);
			if(!this.frm.doc.company) {
				this.frm.set_value("is_pos", 0);
				frappe.msgprint(__("Please specify Company to proceed"));
			} else {
				const r = await this.frm.call({
					doc: this.frm.doc,
					method: "set_missing_values",
					freeze: true
				});
				if(!r.exc) {
					if(r.message) {
						this.frm.pos_print_format = r.message.print_format || "";
						this.frm.meta.default_print_format = r.message.print_format || "";
						this.frm.doc.campaign = r.message.campaign;
						this.frm.allow_print_before_pay = r.message.allow_print_before_pay;
					}
					this.frm.script_manager.trigger("update_stock");
					this.calculate_taxes_and_totals();
					this.frm.doc.taxes_and_charges && this.frm.script_manager.trigger("taxes_and_charges");
					frappe.model.set_default_values(this.frm.doc);
					this.set_dynamic_labels();
				}
			}
		}
	},

	customer() {

		if (!this.frm.doc.customer) return
		const pos_profile = this.frm.doc.pos_profile;
		if(this.frm.updating_party_details) return;
		erpnext.utils.get_party_details(this.frm,
			"erpnext.accounts.party.get_party_details", {
				posting_date: this.frm.doc.posting_date,
				party: this.frm.doc.customer,
				party_type: "Customer",
				account: this.frm.doc.debit_to,
				price_list: this.frm.doc.selling_price_list,
				pos_profile: pos_profile
			}, () => {
				this.apply_pricing_rule();
			});

	},

	amount: function(){

		this.write_off_outstanding_amount_automatically()

	},

	change_amount: function(){

		if(this.frm.doc.paid_amount > this.frm.doc.grand_total){
			this.calculate_write_off_amount();
		}else {
			this.frm.set_value("change_amount", 0.0);
			this.frm.set_value("base_change_amount", 0.0);
		}

		this.frm.refresh_fields();
	},

	loyalty_amount: function(){
		this.calculate_outstanding_amount();
		this.frm.refresh_field("outstanding_amount");
		this.frm.refresh_field("paid_amount");
		this.frm.refresh_field("base_paid_amount");
	},

	write_off_outstanding_amount_automatically: function() {

		if(cint(this.frm.doc.write_off_outstanding_amount_automatically)) {
			frappe.model.round_floats_in(this.frm.doc, ["grand_total", "paid_amount"]);
			// this will make outstanding amount 0
			this.frm.set_value("write_off_amount",
				flt(this.frm.doc.grand_total - this.frm.doc.paid_amount - this.frm.doc.total_advance, precision("write_off_amount"))
			);
			this.frm.toggle_enable("write_off_amount", false);

		} else {
			this.frm.toggle_enable("write_off_amount", true);
		}

		this.calculate_outstanding_amount(false);
		this.frm.refresh_fields();
	},

	make_sales_return: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.accounts.doctype.pos_invoice.pos_invoice.make_sales_return",
			frm: cur_frm
		});
	},
})

$.extend(cur_frm.cscript, new erpnext.selling.POSInvoiceController({ frm: cur_frm }))

frappe.ui.form.on('POS Invoice', {

	redeem_loyalty_points: function(frm) {
		frm.events.get_loyalty_details(frm);
	},

	loyalty_points: function(frm) {
		if (frm.redemption_conversion_factor) {
			frm.events.set_loyalty_points(frm);
		} else {
			frappe.call({
				method: "erpnext.accounts.doctype.loyalty_program.loyalty_program.get_redeemption_factor",
				args: {
					"loyalty_program": frm.doc.loyalty_program
				},
				callback: function(r) {
					if (r) {
						frm.redemption_conversion_factor = r.message;
						frm.events.set_loyalty_points(frm);
					}
				}
			});
		}
	},

	get_loyalty_details: function(frm) {
		if (frm.doc.customer && frm.doc.redeem_loyalty_points) {
			frappe.call({
				method: "erpnext.accounts.doctype.loyalty_program.loyalty_program.get_loyalty_program_details",
				args: {
					"customer": frm.doc.customer,
					"loyalty_program": frm.doc.loyalty_program,
					"expiry_date": frm.doc.posting_date,
					"company": frm.doc.company
				},
				callback: function(r) {
					if (r) {
						frm.set_value("loyalty_redemption_account", r.message.expense_account);
						frm.set_value("loyalty_redemption_cost_center", r.message.cost_center);
						frm.redemption_conversion_factor = r.message.conversion_factor;
					}
				}
			});
		}
	},

	set_loyalty_points: function(frm) {
		if (frm.redemption_conversion_factor) {
			let loyalty_amount = flt(frm.redemption_conversion_factor*flt(frm.doc.loyalty_points), precision("loyalty_amount"));
			var remaining_amount = flt(frm.doc.grand_total) - flt(frm.doc.total_advance) - flt(frm.doc.write_off_amount);
			if (frm.doc.grand_total && (remaining_amount < loyalty_amount)) {
				let redeemable_points = parseInt(remaining_amount/frm.redemption_conversion_factor);
				frappe.throw(__("You can only redeem max {0} points in this order.",[redeemable_points]));
			}
			frm.set_value("loyalty_amount", loyalty_amount);
		}
	},

	request_for_payment: function (frm) {
		frm.save().then(() => {
			frappe.dom.freeze();
			frappe.call({
				method: 'create_payment_request',
				doc: frm.doc,
			})
				.fail(() => {
					frappe.dom.unfreeze();
					frappe.msgprint('Payment request failed');
				})
				.then(() => {
					frappe.msgprint('Payment request sent successfully');
				});
		});
	},
	

});




frappe.ui.form.on('POS Invoice Item', {

	qty:function(frm,cdt,cdn){
		if (frm.doc.is_return)

    {
      		
  				frappe.call({
      			doc:frm.doc,
      			method:"update_values_for_return",
      			callback:function(r){
      				if (r.message){

      								refresh_field("payment")
      								refresh_field("paid_amount")
      								console.log(frm.doc.paid_amount)}
      								frm.refresh()
      			}
      						})}
				refresh_field("payment")
				refresh_field("paid_amount")
					frm.refresh()
			}
	
}) ; 





frappe.ui.form.on('Sales Invoice Payment', {


	mode_of_payment:function(frm, cdt,cdn){
		console.log("setup")
		// frm.set_df_property('mode_of_payment',"reqd", 0 , cdn, cdn);
		frm.get_field("payments").grid.toggle_reqd("mode_of_payment", false);
	}
})
