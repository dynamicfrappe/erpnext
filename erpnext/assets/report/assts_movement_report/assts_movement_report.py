# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data    = get_data(filters)
	return columns, data





def get_columns(filters):
	columns = [
		{
			"label": _("Asset"),
			"fieldname": "asset_code",
			"fieldtype": "Link",
			"options":"Asset",
			"width": 150
		},
			{
			"label": _("Asset Name"),
			"fieldname": "assetName",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("serial number"),
			"fieldname": "serialNumber",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Employee Code"),
			"fieldname": "custodian",
			"fieldtype": "Link",
			"options":"Employee",
			"width": 150
		},
			{
			"label": _("Project"),
			"fieldname": "Project",
			"fieldtype": "Link",
			"options":"Project",
			"width": 150
		},

			{
			"label": _("Department"),
			"fieldname": "department",
			"fieldtype": "Link",
			"options":"Department",
			"width": 150
		},
		
		{
			"label": _("value"),
			"fieldname": "value",
			"fieldtype": "Data",
			"width": 150
		},
		
		
	]
	

	return columns

def get_data(filters):
	condition=""
	if filters.get("asset_name"):
		condition +="AND tabAsset.name = '%s'"%filters.get("asset_name")
	if filters.get("employee_name"):
		condition += " AND tabAsset.custodian = '%s' "%filters.get("employee_name")
	if filters.get("Project"):
		condition += " AND tabAsset.project = '%s' "%filters.get("Project")
	if filters.get("Department"):
		condition += " AND tabAsset.department = '%s' "%filters.get("department")


	print(condition)
	results=frappe.db.sql("""  
			SELECT
			tabAsset.`name` as 'asset_code',
			tabAsset.`asset_name` as 'assetName',
			tabEmployee.`employee_name` as 'employee',
			tabAsset.`custodian` as 'custodian',
	        (case when tabAsset.`value_after_depreciation`=0 then tabAsset.`gross_purchase_amount` else tabAsset.`value_after_depreciation` end) as 'value',
            tabAsset.project as 'project',
            tabAsset.department as 'department'
		    FROM
			tabAsset
            	LEFT JOIN
			tabEmployee
	        on
	        tabAsset.`custodian`=tabEmployee.employee
		    WHERE (
                      (tabAsset.custodian is not null and tabAsset.custodian !='')
                      or
                     ( tabAsset.project is not null and  tabAsset.project!='')
                      or
                     ( tabAsset.department is not null and tabAsset.department!='')
                  );


			{condition}
	""".format(condition=condition) ,as_dict=1)

	return results

