// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Business Trip', {

	to_date:(frm)=>{
		if (frm.doc.from_date) {
             var sDate=Date.parse(frm.doc.from_date);
             var tDate=Date.parse(frm.doc.to_date);
             var days=Math.ceil(Math.abs(tDate - sDate) / (1000 * 60 * 60 * 24));
               console.log(sDate)
               console.log(tDate)
               console.log(tDate-sDate)
               frm.doc.number_of_day=days;
               refresh_field("number_of_day")
		}else
		{
			frappe.msgprint('please set start date');
		}
	}

	
});
