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
			frm.set_df_property('model', 'options', years);
	}
});
  frappe.ui.form.on("Licence Grid", "active", function (frm, cdt, cdn) {
  	var child = locals[cdt][cdn]
  		var count =0;
  	  for (var c=0; c< frm.doc.licences.length;c++){
  	  	// console.log(frm.doc.licences[c])
  	  	 if(frm.doc.licences[c].active==1){
  	  	 	count ++

		 }
  	  	 if (count>1){

  	  	 	child.active=0;
  	  	 	refresh_field("licences");
  	  	 	frappe.throw("You Cant Select two licence");
		 }
	  }

	  frappe.call({
		  method: 'checkLicenceValidation',
		  doc: frm.doc,
		  args:{
		  	"endDtae":child.end_date
		  },
		  callback(r) {


				if(r.message=='false'){
					child.active=0;
					frappe.msgprint("This Licence is expired")
					 refresh_field("licences");

				}
		  }

	  });
  })

frappe.ui.form.on("Licence Grid", "licence", function(frm,cdt,cdn){
       var child = locals[cdt][cdn]
         var count=0
		 for (var c=0; c< frm.doc.licences.length;c++){

  	  	 if (child.licence==frm.doc.licences[c].licence ){
			count++
			 if (count>1) {
				 child.licence = "";
				 refresh_field("licences");
				 frappe.throw("Licence Already Exist");
			 }
		 }
	  }

});