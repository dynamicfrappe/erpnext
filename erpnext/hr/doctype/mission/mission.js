// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mission', {

	end_time:function(frm){
		var sDate=(frm.doc.start_time).split(':')
        var tDate=(frm.doc.end_time).split(':')
        var difInHourse=tDate[0]-sDate[0]
        var difInMinutes=tDate[1]-sDate[1]
        difInMinutes+=difInHourse*60;
        console.log(difInMinutes);
		frm.set_value('duration', difInMinutes);
	}

});
