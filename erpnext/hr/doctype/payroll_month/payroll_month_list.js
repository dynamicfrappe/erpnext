frappe.listview_settings['Payroll Month'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		var indicator = [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
		indicator[1] = {"Opened": "green", "Closed": "blue", "Draft": "red"}[doc.status];
		return indicator;
	}
};
