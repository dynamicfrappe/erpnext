# -*- coding: utf-8 -*-
# Copyright (c) 2020, Dynamic Technologies - Beshoy Atef


from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, getdate, new_line_sep, nowdate, add_days
from erpnext.stock.doctype.item.item import get_item_defaults
from frappe.model.mapper import get_mapped_doc

class PurchaseRequest(Document):
	pass


def set_missing_values(source, target_doc):
	if target_doc.doctype == "Purchase Order" and getdate(target_doc.schedule_date) <  getdate(nowdate()):
		target_doc.schedule_date = None
	target_doc.run_method("set_missing_values")
	target_doc.run_method("calculate_taxes_and_totals")

def update_item(obj, target, source_parent):
	target.conversion_factor = obj.conversion_factor
	target.qty = flt(flt(obj.stock_qty) - flt(obj.ordered_qty))/ target.conversion_factor
	target.stock_qty = (target.qty * target.conversion_factor)
	if getdate(target.schedule_date) < getdate(nowdate()):
		target.schedule_date = None

@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None):

	def postprocess(source, target_doc):
		if frappe.flags.args and frappe.flags.args.default_supplier:
			# items only for given default supplier
			supplier_items = []
			for d in target_doc.items:
				default_supplier = get_item_defaults(d.item_code, target_doc.company).get('default_supplier')
				if frappe.flags.args.default_supplier == default_supplier:
					supplier_items.append(d)
			target_doc.items = supplier_items

		set_missing_values(source, target_doc)

	def select_item(d):
		return d.ordered_qty < d.stock_qty

	doclist = get_mapped_doc("Purchase Request", source_name, 	{
		"Purchase Request": {
			"doctype": "Purchase Order",
			"validation": {
				"docstatus": ["=", 1],
				"material_request_type": ["=", "Purchase"]
			}
		},
		"Purchase Request Item": {
			"doctype": "Purchase Order Item",
			"field_map": [
				["name", "purchase_request_item"],
				["parent", "purchase_request"],
				["uom", "stock_uom"],
				["uom", "uom"],
				["sales_order", "sales_order"],
				["sales_order_item", "sales_order_item"]
			],
			"postprocess": update_item,
			"condition": select_item
		}
	}, target_doc, postprocess)

	return doclist



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_default_supplier_query(doctype, txt, searchfield, start, page_len, filters):
	doc = frappe.get_doc("Purchase Request", filters.get("doc"))
	item_list = []
	for d in doc.items:
		item_list.append(d.item_code)

	return frappe.db.sql("""select default_supplier
		from `tabItem Default`
		where parent in ({0}) and
		default_supplier IS NOT NULL
		""".format(', '.join(['%s']*len(item_list))),tuple(item_list))


@frappe.whitelist()
def make_supplier_quotation(source_name, target_doc=None):
	def postprocess(source, target_doc):
		set_missing_values(source, target_doc)

	doclist = get_mapped_doc("Purchase Request", source_name, {
		"Purchase Request": {
			"doctype": "Supplier Quotation",
			"validation": {
				"docstatus": ["=", 1],
				
			}
		},
		"Purchase Request Item": {
			"doctype": "Supplier Quotation Item",
			"field_map": {
				"name": "purchase_request_item",
				"parent": "purchase_request",
				"sales_order": "sales_order"
			}
		}
	}, target_doc, postprocess)

	return doclist



@frappe.whitelist()
def make_request_for_quotation(source_name, target_doc=None):
	doclist = get_mapped_doc("Purchase Request", source_name, 	{
		"Purchase Request": {
			"doctype": "Request for Quotation",
			"validation": {
				"docstatus": ["=", 1],
				
			}
		},
		"Purchase Request Item": {
			"doctype": "Request for Quotation Item",
			"field_map": [
				["name", "purchase_request_item"],
				["parent", "purchase_request"],
				["uom", "uom"]
			]
		}
	}, target_doc)

	return doclist