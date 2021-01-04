// ["Error","Submitted","Draft","Pending"]
frappe.listview_settings['Material Request'] = {
	add_fields: ["material_request_type", "status", "per_ordered", "per_received"],


	get_indicator: function(doc) {
		if(doc.status=="Stopped") {
			return [__("Stopped"), "red", "status,=,Stopped"];
		} else if(doc.docstatus==1 && flt(doc.per_ordered, 2) == 0) {
			return [__("Pending"), "orange", "per_ordered,=,0"];
		}  else if(doc.docstatus==1 && flt(doc.per_ordered, 2) < 100) {
			return [__("Partially ordered"), "yellow", "per_ordered,<,100"];
		} else if(doc.docstatus==1 && flt(doc.per_ordered, 2) == 100) {
			if (doc.material_request_type == "Purchase" && flt(doc.per_received, 2) < 100 && flt(doc.per_received, 2) > 0) {
				return [__("Partially Received"), "yellow", "per_received,<,100"];
			} else if (doc.material_request_type == "Purchase" && flt(doc.per_received, 2) == 100) {
				return [__("Received"), "green", "per_received,=,100"];
			} else if (doc.material_request_type == "Purchase") {
				return [__("Ordered"), "green", "per_ordered,=,100"];
			} else if (doc.material_request_type == "Material Transfer") {
				return [__("Transfered"), "green", "per_ordered,=,100"];
			} else if (doc.material_request_type == "Material Issue") {
				return [__("Issued"), "green", "per_ordered,=,100"];
			} else if (doc.material_request_type == "Customer Provided") {
				return [__("Received"), "green", "per_ordered,=,100"];
			} else if (doc.material_request_type == "Manufacture") {
				return [__("Manufactured"), "green", "per_ordered,=,100"];
			}
		}
	},
	onload: function(listview) {
		frappe.route_options = {"status":["in", ["Pending" ,"Draft" , "Submitted"],false]};
		listview.page.add_action_item(__('Make Action'), function() {
			const selected = listview.get_checked_items();
			debugger;
						alert(selected);

		});
		this.add_button(__("Run"), "primary", function() {

			frappe.call({
				method:"erpnext.stock.doctype.material_request.material_request.get_items",
				freeze: true,
				callback:function (r){
					listview.page.refresh();
				}
			});
		});


	},
	add_button(name, type, action, wrapper_class=".page-actions") {
		const button = document.createElement("button");
		button.classList.add("btn", "btn-" + type, "btn-sm", "ml-2");
		button.innerHTML = name;
		button.onclick = action;
		document.querySelector(wrapper_class).prepend(button);
	}
};
