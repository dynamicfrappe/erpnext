/* global Clusterize */
frappe.provide('erpnext.PointOfSale');
{% include "erpnext/selling/page/point_of_sale/pos_controller.js" %}
frappe.provide('erpnext.queries');

frappe.pages['point-of-sale'].on_page_load = function(wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Point of Sale'),
		single_column: true
	});

	wrapper.pos = new erpnext.PointOfSale.Controller(wrapper);
	window.cur_pos = wrapper.pos;
};

frappe.pages['point-of-sale'].refresh = function(wrapper) {
<<<<<<< HEAD
=======
	// wrapper.pos = new erpnext.PointOfSale.Controller(wrapper);
>>>>>>> 2651465621527375f662d5fbef2d1d1e3abaf961
	window.cur_pos = wrapper.pos;
	if (document.scannerDetectionData) {
		onScan.detachFrom(document);
		wrapper.pos.wrapper.html("");
		wrapper.pos.check_opening_entry();
	}
}
