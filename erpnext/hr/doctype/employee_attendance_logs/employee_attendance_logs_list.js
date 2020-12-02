frappe.listview_settings['Employee Attendance Logs'] = {
	add_fields: ["type"],
	get_indicator: function(doc) {
		var indicator = [__(doc.type), frappe.utils.guess_colour(doc.type), "type,=," + doc.type];
		indicator[1] = {"Present": "green", "Absent": "red", "Half Day": "deeppink",
		"Leave": "deeppink", "Holiday": "blue", "Business Trip": "darkblue",
		"Mission": "darkblue", "Mission All Day": "darkblue", "Half Day": "deeppink",
		"Week End": "blue", "Working On Holiday": "green" , default : "blue"
		}[doc.type];
		return indicator;
	}
};


//
// frappe.listview_settings['Employee Attendance Logs'] = {
// 	get_indicator: function (doc) {
// 		if (doc.type === "Present") {
// 			return [__("Present"), "green", "type,=,Present"];
// 		} else if (doc.type === "Absent") {
// 			return [__("Absent"), "red", "type,=,Absent"];
// 		} else if (doc.type === "Half Day") {
// 			return [__("Half Day"), "deeppink", "type,=,Half Day"];
// 		} else if (doc.type === "Leave") {
// 			return [__("Leave"), "deeppink", "type,=,Leave"];
// 		} else if (doc.type === "Holiday") {
// 			return [__("Holiday"), "blue", "type,=,Holiday"];
// 		} else if (doc.type === "Business Trip") {
// 			return [__("Business Trip"), "darkblue", "type,=,Business Trip"];
// 		} else if (doc.type === "Mission") {
// 			return [__("Mission"), "darkblue", "type,=,Mission"];
// 		}else if (doc.type === "Working On Holiday") {
// 			return [__("Working On Holiday"), "green", "type,=,Working On Holiday"];
// 		} else if (doc.type === "Week End") {
// 			return [__("Week End"), "blue", "type,=,Week End"];
// 		} else if (doc.type === "Mission All Day") {
// 			return [__("Mission All Day"), "darkblue", "type,=,Mission All Day"];
// 		} else return [__(doc.type), "blue", "type,=,"+doc.type+""]
// 	}
// };
