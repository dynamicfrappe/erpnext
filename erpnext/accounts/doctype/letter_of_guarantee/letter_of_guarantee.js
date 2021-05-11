// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Letter of Guarantee', {
	refresh: function(frm) {
        if(frm.doc.docstatus==1 && frm.doc.status=='End' && frm.doc.renewed==0){

            frm.add_custom_button(__("Renew"), function() {
                 var d= new frappe.ui.Dialog({
            'fields':[
                  {
                    'label': __('Start Date'),
                    'fieldname': 'start_date',
                    'fieldtype': 'Date',
                      'reqd':1
                },
                {
                    'label': __('End Date'),
                    'fieldname': 'end_date',
                    'fieldtype': 'Date',
                      'reqd':1
                },

            ],
            primary_action:function(){
                d.hide()
                var args=d.get_values()
                console.log(args)
                frappe.call({
                    method:"renew_letter_of_grantee",
                    doc:frm.doc,
                    args:{
                        "start_date":args.start_date,
                        "end_date":args.end_date
                    }
                })

            }

        });
        d.show();
		});
        }
	}

});
