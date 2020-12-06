// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Rule', {
	// refresh: function(frm) {

	// }
});


frappe.ui.form.on('Late Attendance Componant Table', {
	// refresh: function(frm) {

	// }
	level_onefactor:function(frm,cdt,cdn){

	},

	from_min:function(frm,cdt,cdn){
		var loal = locals[cdt][cdn] ;
		var i = 0 
		for (i =1 ; i < frm.doc.late_role_table.length ; i++){
		
					
					if (frm.doc.late_role_table[i-1].late_componant ==  frm.doc.late_role_table[i].late_componant){
						frm.doc.late_role_table[i].late_componant  = ""
						frm.doc.late_role_table[i].from_min  = ""
						frm.doc.late_role_table[i].to_min  = ""
						frm.refresh_filed("late_role_table")
						frappe.throw("You Dublicated Late Component")
					}
		
				}
		if(frm.doc.type == 'Daily')
		{for (i =1 ; i < frm.doc.late_role_table.length ; i++){
		
					var to_min = frm.doc.late_role_table[i-1].to_min
					if (frm.doc.late_role_table[i-1].to_min > frm.doc.late_role_table[i].from_min){
						frm.doc.late_role_table[i].late_componant  = ""
						frm.doc.late_role_table[i].from_min  = ""
						frm.doc.late_role_table[i].to_min  = ""
						
						frappe.throw("Please Arange Times")
					}

		
				}


			}


	}
});