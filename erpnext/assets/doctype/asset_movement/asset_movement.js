// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Asset Movement', {
	setup: (frm) => {
		frm.set_query("to_employee", "assets", (doc) => {
			return {
				filters: {
					company: doc.company
				}
			};

		})
		frm.set_query("from_employee", "assets", (doc) => {
			return {
				filters: {
					company: doc.company
				}
			};
		})
		frm.set_query("reference_name", (doc) => {
			return {
				filters: {
					company: doc.company,
					docstatus: 1
				}
			};
		})
		frm.set_query("reference_doctype", () => {
			return {
				filters: {
					name: ["in", ["Purchase Receipt", "Purchase Invoice","Custody request"]]
				}
			};
		}),
		frm.set_query("asset", "assets", () => {
			return {
				filters: {
					status: ["not in", ["Draft"]]
				}
			}
		})


		
	},

	onload: (frm,cdt,cdn) => {

		frm.trigger('set_required_fields');
		/*if(frm.doc.reference_doctype=="Assets Return"){
			console.log("hiiiiiiii")
		  frm.set_df_property("target_location", "read_only", 1,cdn, 'assets');
		}*/
	},
      
	purpose: (frm) => {
		frm.trigger('set_required_fields');
	},

	set_required_fields: (frm, cdt, cdn) => {
		let fieldnames_to_be_altered;
		if (frm.doc.purpose === 'Transfer') {
			fieldnames_to_be_altered = {
				target_location: { read_only: 0, reqd: 1 },
				source_location: { read_only: 1, reqd: 1 },
				from_employee: { read_only: 1, reqd: 0 },
				to_employee: { read_only: 1, reqd: 0 }
			};
		}
		else if (frm.doc.purpose === 'Receipt') {
			fieldnames_to_be_altered = {
				target_location: { read_only: 0, reqd: 1 },
				source_location: { read_only: 1, reqd: 0 },
				from_employee: { read_only: 0, reqd: 1 },
				to_employee: { read_only: 1, reqd: 0 }
			};
		}
		else if (frm.doc.purpose === 'Issue') {
			fieldnames_to_be_altered = {
				target_location: { read_only: 1, reqd: 0 },
				source_location: { read_only: 1, reqd: 1 },
				from_employee: { read_only: 1, reqd: 0 },
				to_employee: { read_only: 0, reqd: 1 }
			};
		}
		Object.keys(fieldnames_to_be_altered).forEach(fieldname => {
			let property_to_be_altered = fieldnames_to_be_altered[fieldname];
			Object.keys(property_to_be_altered).forEach(property => {
				let value = property_to_be_altered[property];
				frm.set_df_property(fieldname, property, value, cdn, 'assets');
			});
		});
		frm.refresh_field('assets');
	},
	reference_doctype:(frm)=>{
		if (frm.doc.reference_doctype ==='Custody request'){
			var ref = frappe.db.get_doc('Custody request' , frm.doc.reference_name)
			frm.set_query("assets",'to_employee', () => {
			return {
				filters: {
					name: ref.name
				}
			}
		})




		}
	},


});

frappe.ui.form.on('Asset Movement Item', {






	asset: function(frm, cdt, cdn) {
		// on manual entry of an asset auto sets their source location / employee
		const asset_name = locals[cdt][cdn].asset;
		if (asset_name){
			frappe.db.get_doc('Asset', asset_name).then((asset_doc) => {
				if(asset_doc.location) frappe.model.set_value(cdt, cdn, 'source_location', asset_doc.location);
				if(asset_doc.custodian) frappe.model.set_value(cdt, cdn, 'from_employee', asset_doc.custodian);
			}).catch((err) => {
				console.log(err); // eslint-disable-line
			});


		}
	


},
	onload: (frm,cdt,cdn) => {

		var local = locals[cdt][cdn]
		
		if(frm.doc.reference_doctype=="Assets Return"){
				frm.set_query("target_location" , "assets" ,() =>{
						
							return{
								filters:local.target_location }
						} )
		  
		}
	},
      
	
	assets_add:function(frm,cdt,cdn){
		var docyment_type =''

		
		if (frm.doc.reference_doctype ==='Custody request' && frm.doc.reference_name != null )


		{
			frappe.call({
		        method: "frappe.client.get",
		        args: {
		            doctype: "Company",
		            name: frm.doc.company,
		        },
        callback(r) {
            if(r.message) {
           
                var com = r.message;
     			var locat = com.default_asset_location
     		
     			
     			frappe.call({
				method:"erpnext.assets.doctype.asset_movement.asset_movement.get_items_from_custody_request",
				args:{
					"request":frm.doc.reference_name
				},
				callback:function(r){
					if (frm.doc.purpose=='Issue'){
										if (r.message[2][0] == "Employee"){
																				frm.set_query("to_employee" , "assets" ,() => { return {filters :{name:r.message[1].toString() }}})}}
					if (frm.doc.purpose=='Transfer'){
					
						frm.set_query("target_location" , "assets" ,() =>{
						
							return{
								filters: {name:r.message[3][0].toString()} }
						} )
					}			
					frm.set_query("asset","assets", () => {
					return {
						filters: {
							item_code:["in" , r.message[0].toString()],
							location :locat,
							status: ["not in", ["Draft" ,"Cancelled"]]
						}
					}
				})


				}

			})



     			if(!locat){
     				frappe.throw(_("Company Has No default asset location"))
     			}              
            }
        }
    });


		



			

			}
	},



});

