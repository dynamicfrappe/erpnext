/*frappe.ui.form.on('Employee Medical Insurance Members',{

	company_share_ratio:function(frm,cdt,cdn){
		var cur_row = locals [cdt] [cdn] ;
		debugger;
		if (cur_row.company_share_ratio > 100)
			cur_row.company_share_ratio = 100 ;		
		if (cur_row.company_share_ratio < 0)
			cur_row.company_share_ratio = 0 ;
		cur_row.employee_share_ratio = 100 - cur_row.company_share_ratio ;
		frm.refresh_field("company_share_ratio");
		frm.refresh_field("employee_share_ratio");

	},
	employee_share_ratio:function(frm,cdt,cdn){
		var cur_row = locals [cdt] [cdn] ;
		if (cur_row.employee_share_ratio > 100)
			cur_row.employee_share_ratio = 100 ;
		if (cur_row.employee_share_ratio < 0)
			cur_row.employee_share_ratio = 0 ;
		cur_row.company_share_ratio = 100 - cur_row.employee_share_ratio ;
		frm.refresh_field("company_share_ratio");
		frm.refresh_field("employee_share_ratio");

	}
});*/