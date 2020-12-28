// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle', {
	setup: function(frm) {
		var max = new Date().getFullYear()
		  var min = max - 20
		  var years = []

		  for (var i = max; i >= min; i--) {
			years.push(i)
		  }
		  
	}
});
