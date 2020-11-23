frappe.listview_settings['Employee Attendance Logs'] = {
	get_indicator: function (doc) {
		if (doc.type === "Present") {
			return [__("Present"), "green", "type,=,Present"];
		} else if (doc.type === "Absent") {
			return [__("Absent"), "red", "type,=,Absent"];
		} else if (doc.type === "Half Day") {
			return [__("Half Day"), "deeppink", "type,=,Half Day"];
		} else if (doc.type === "Leave") {
			return [__("Leave"), "deeppink", "type,=,Leave"];
		} else if (doc.type === "Holiday") {
			return [__("Holiday"), "blue", "type,=,Holiday"];
		} else if (doc.type === "Business Trip") {
			return [__("Business Trip"), "darkblue", "type,=,Business Trip"];
		} else if (doc.type === "Mission") {
			return [__("Mission"), "darkblue", "type,=,Mission"];
		} else {
			return [__("Mission All Day"), "darkblue", "type,=,Mission All Day"];
		}
	}
};
