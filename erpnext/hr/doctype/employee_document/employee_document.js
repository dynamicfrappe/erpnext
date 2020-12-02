// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Document', {

	refresh:function(frm){
		if(frm.doc.docstatus==1){
			cur_frm.add_custom_button(__("Renew"), function() {
		     //frappe.msgprint("Custom Information");
		    }); 
		}
	},
   start_date:function(frm){
   	  if(frm.doc.document_type){
   	  	 var satrtDate=new Date(frm.doc.start_date)

       satrtDate.setMonth( satrtDate.getMonth() + parseInt(frm.doc.docperiod) );
       var day=satrtDate.getDate();
       //if(day<10){day='0'+day}
       var month =satrtDate.getMonth()+1;
       var year =satrtDate.getFullYear();
       var fulldate=year+"-"+month+"-"+day
       cur_frm.set_value('end_date',fulldate)
       console.log(year)
   	  }
   }
});
