// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Agreement Items"] = {
	"filters": [
					{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options":"Item"

		},
		{
			"fieldname":"proejct",
			"label": __("Project"),
			"fieldtype": "Link",
			"options":"Project"

		},
		{
			"fieldname":"cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options":"Cost Center"


		}
	]
};
