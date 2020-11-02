# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = getColumns(filters)
	data = getdata(filters)
	return columns, data

def getdata (filters):
	conditions = ""
	if filters.get("company"):
		conditions = " and a.`company` =%(company)s"
	
		if filters.get("asset_category"):
			conditions += " and a.asset_category =%(asset_category)s"	
		if filters.get("asset"):
			conditions += " and a.`name` =%(asset)s"
		results = frappe.db.sql("""
						SELECT
						a.`name`, 
						a.asset_name, 
						a.location, 
						a.purchase_date, 
						a.available_for_use_date, 
						ifnull((sum(case when ds.schedule_date >= %(from_date)s and ds.schedule_date <= %(to_date)s and isnull(ds.journal_entry) = 0
															and (ifnull(a.disposal_date, 0) = 0 or ds.schedule_date <= a.disposal_date) then
													   ds.depreciation_amount
												  else
													   0
												  end))+(a.opening_accumulated_depreciation), 0) as depreciation_amount_during_the_period,
					ifnull((sum(case when ds.schedule_date <= CURDATE()
													and isnull(ds.journal_entry) = 0		and (ifnull(a.disposal_date, 0) = 0 or ds.schedule_date <= a.disposal_date) then
													   ds.depreciation_amount
												  else
													   0
												  end))+(a.opening_accumulated_depreciation), 0) as total_depreciation_amount,
					(select ifnull(sum(tt.difference_amount),0) as difference_amount from `tabAsset Value Adjustment` tt where tt.asset = a.`name` and docstatus = 1)  as  total_additional_costs,
   					(select ifnull(sum(tt.repair_cost),0) as cost from `tabAsset Repair` tt where tt.asset_name = a.`name` and docstatus = 1)  as total_repair_cost ,
	
						a.gross_purchase_amount, 
						finance.value_after_depreciation, 
						a.insured_value

						
					FROM
						tabAsset a
						INNER Join 
                         `tabAsset Finance Book` finance 
                         on  finance.parenttype = 'Asset' and a.name  = finance.parent 
						INNER  JOIN	
						`tabDepreciation Schedule` ds
						ON 
							a.`name` = ds.parent
						LEFT  JOIN
						`tabAsset Maintenance` ms
						ON 
							a.`name` = ms.parent
							
						where a.docstatus = 1
						{conditions}
							GROUP BY a.`name` 
							
			
			""".format(conditions=conditions), filters, as_dict=1)
		return results


def getColumns (filters):
	columns = [
		{
			'fieldname': "name",
			'label': _("Asset"),
			'fieldtype': "Link",
			'options': "Asset",
			"width": 150
		},
		{
			'fieldname': "asset_name",
			'label': _("Asset Name"),
			'fieldtype': "Data",
			"width": 150
		},
		{
			'fieldname': "location",
			'label': _("Location"),
			'fieldtype': "Data",
			"width": 100
		},
		{
			'fieldname': "purchase_date",
			'label': _("Purchase Date"),
			'fieldtype': "Date",
			"width": 120
		},
		{
			'fieldname': "available_for_use_date",
			'label': _("Avaliable for use Date"),
			'fieldtype': "Date",
			"width": 150
		},
		{
			'fieldname': "depreciation_amount_during_the_period",
			'label': _("Deperciation amount in Duration"),
			'fieldtype': "float",
			"width": 220
		},
		{
			'fieldname': "total_depreciation_amount",
			'label': _("Total Depreciation Amount Until Today"),
			'fieldtype': "float",
			"width": 250
		},
		{
			'fieldname': "total_additional_costs",
			'label': _("Total Additional costs"),
			'fieldtype': "float",
			"width": 150
		},
		{
			'fieldname': "gross_purchase_amount",
			'label': _("Purchase Amount"),
			'fieldtype': "float",
			"width": 150
		},
		{
			'fieldname': "value_after_depreciation",
			'label': _("Current Amount"),
			'fieldtype': "float",
			"width": 150
		}
	]
	return columns