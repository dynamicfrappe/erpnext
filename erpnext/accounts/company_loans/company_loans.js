// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Company Loans', {
    
	  in:(frm)=>{
          update_total(frm);
	  /*	frappe.call({
	  		doc:frm.doc,
	  		method:'show_payment_shedule',
	  		callback :function(r){
	  			console.log(r.message)
	  		}
	  	})*/

	  	

      

  },



	
});

frappe.ui.form.on('benifits rates', 'rate', function(frm){
	

  update_total(frm);


    
});



function update_total(frm){
	
   	 var total =0;
	//console.log(d)
	//console.log(frm.doc.benifits)
     for(var i=0;i<frm.doc.benifits.length;i++){
     	if(frm.doc.benifits[i]["add_in_total"]==1){
     		total +=frm.doc.benifits[i]["rate"]|0;

     	}
     }
     if(frm.doc.in){
     	var profit=total*frm.doc.in;
     	var net=(profit/100)+frm.doc.in;
     	cur_frm.set_value("total", net);
     }
	 cur_frm.set_value("total_percent", total);
	 refresh_field("total_percent");
	 show_payment_shedule(frm)
}

function show_payment_shedule(frm){
	frm.clear_table("payment_shedules"); 
	frm.refresh_fields();
	// console.log(frm.doc)
	//frappe.throw(';test')
         frappe.call({
        'doc': frm.doc,
        'method': 'show_payment_shedule',
       
        callback: function(r) {
          console.log('r')
        }
    });
}