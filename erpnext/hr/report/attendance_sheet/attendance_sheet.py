# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _
from calendar import monthrange

def execute(filters=None):
	if not filters: filters = {}

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	att_map = get_attendance_list(conditions, filters)
	emp_map = get_employee_details(filters)

	holiday_list = [emp_map[d]["holiday_list"] for d in emp_map if emp_map[d]["holiday_list"]]
	default_holiday_list = frappe.get_cached_value('Company',  filters.get("company"),  "default_holiday_list")
	holiday_list.append(default_holiday_list)
	holiday_list = list(set(holiday_list))
	holiday_map = get_holiday(holiday_list, filters["month"])

	data = []
	leave_types = frappe.db.sql("""select name from `tabLeave Type`""", as_list=True)
	leave_list = [d[0] for d in leave_types]
	columns.extend(leave_list)
	columns.extend([_("Total Early Entries Min") + ":Time:200",_("Total Times Early Entries") + ":Data:200",_("Total Late Entries Min") + ":Time:200",_("Total Times Late Entries") + ":Data:200", _("Total Early Exits Min ") + ":Time:200",_("Total Times Early Exits") + ":Data:200",_("Total Late Exits Min") + ":Time:200",_("Total Times Late Exits") + ":Data:200"])
	status_map = {"Week End":"<b style='color : blue'>Off </b>","Working On Holiday":"<b style='color : green'>WH </b>","Present": "<b style='color : green'>P </b>  ", "Absent": "<b style='color : red '>A </b> ", "Half Day": "<b style='color : deeppink '>HD </b> ", "Leave": "<b style='color : deeppink '>L </b> ", "None": "", "Holiday":"<b style='color : blue '>H</b>" , "Business Trip" :"<b style='color : darkblue '>BT </b> " , "Mission":"<b style='color : darkblue '>M </b> ","Mission All Day":"<b style='color : darkblue '>MA </b> "} 
	leave_dict = get_leaveTypes()
	status_map.update(leave_dict)
	for emp in sorted(att_map):
		emp_det = emp_map.get(emp)
		if not emp_det:
			continue

		row = [emp, emp_det.employee_name, emp_det.branch, emp_det.department, emp_det.designation,
			emp_det.company]

		total_p = total_a = total_l = total_m = total_ma = total_h   = total_bt=  0.0
		for day in range(filters["total_days_in_month"]):
			status = att_map.get(emp).get(day + 1, "None")

			if status == "None" and holiday_map:
				emp_holiday_list = emp_det.holiday_list if emp_det.holiday_list else default_holiday_list
				if emp_holiday_list in holiday_map and (day+1) in holiday_map[emp_holiday_list]:
					status = "Holiday"
			row.append(status_map[status])

			if status == "Present" :
				total_p += 1
			elif status == "Absent":
				total_a += 1
			elif status in leave_dict:
				total_l += 1
			elif status == "Half Day":
				total_p += 0.5
				total_a += 0.5
				total_l += 0.5
			elif status == "Holiday" :
				total_h += 1
			elif status == "Business Trip":
				total_bt +=1
			elif status == "Mission":
				total_m += 1
			elif status == "Mission All Day":
				total_ma += 1
			elif status == "Working On Holiday":
				total_p +=1

		row += [total_p, total_l, total_a , total_h , total_m , total_ma ,total_bt]

		if not filters.get("employee"):
			filters.update({"employee": emp})
			conditions += " and `tabEmployee Attendance Logs`.employee = %(employee)s"
		elif not filters.get("employee") == emp:
			filters.update({"employee": emp})

		leave_details = frappe.db.sql("""select leave_type, type as status , count(*) as count from `tabEmployee Attendance Logs`
			inner join `tabLeave Application` l on reference_name = l.name and reference_type = 'Leave Application'
			where leave_type is not NULL %s group by leave_type, type;""" % conditions, filters, as_dict=1)
		
		time_default_counts = frappe.db.sql(""" select SEC_TO_TIME( SUM( TIME_TO_SEC( early_in) ) ) AS early_in    ,SEC_TO_TIME( SUM( TIME_TO_SEC( early_out) ) ) AS early_out ,SEC_TO_TIME( SUM( TIME_TO_SEC( late_in) ) ) AS late_in ,SEC_TO_TIME( SUM( TIME_TO_SEC( late_out) ) ) AS late_out from `tabEmployee Attendance Logs` where 1=1 %s""" % (conditions), filters , as_dict=1)
		total_counts = frappe.db.sql("""  select (select COUNT(*)  from `tabEmployee Attendance Logs` where early_out > '00:00:00'  %s ) as total_early_out,
 (select COUNT(*)  from `tabEmployee Attendance Logs` where early_in > '00:00:00' %s  ) as total_early_in,
 (select COUNT(*)  from `tabEmployee Attendance Logs` where late_in > '00:00:00'  %s ) as total_late_in,
 (select COUNT(*)  from `tabEmployee Attendance Logs` where late_out > '00:00:00'  %s ) as total_late_out
"""%(conditions,conditions,conditions,conditions)  , filters,as_dict=1)

		leaves = {}
		for d in leave_details:
			if d.status == "Half Day":
				d.count = d.count * 0.5
			if d.leave_type in leaves:
				leaves[d.leave_type] += d.count
			else:
				leaves[d.leave_type] = d.count

		for d in leave_list:
			if d in leaves:
				row.append(leaves[d])
			else:
				row.append("0.0")
		
		row.extend([time_default_counts[0].early_in,total_counts[0].total_early_in,time_default_counts[0].late_in ,total_counts[0].total_late_in,time_default_counts[0].early_out,total_counts[0].total_early_out,time_default_counts[0].late_out,total_counts[0].total_late_out])
		data.append(row)
	return columns, data

def get_columns(filters):
	columns = [
		_("Employee") + ":Link/Employee:120", _("Employee Name") + "::140", _("Branch")+ ":Link/Branch:120",
		_("Department") + ":Link/Department:120", _("Designation") + ":Link/Designation:120",
		 _("Company") + ":Link/Company:120"
	]

	for day in range(filters["total_days_in_month"]):
		columns.append(cstr(day+1) +"::50")

	columns += [_("Total Present") + ":Float:120", _("Total Leaves") + ":Float:120",  _("Total Absent") + ":Float:120"]
	columns += [_("Total Holidays") + ":Float:120", _("Total Mission while Day") + ":Float:160",  _("Total Mission in All Day") + ":Float:160",  _("Total Business Trips Days") + ":Float:160"]
	return columns

def get_attendance_list(conditions, filters):

	attendance_list = frappe.db.sql("""select employee, day(date) as day_of_month,
		type as status from `tabEmployee Attendance Logs` where docstatus = 0   %s   order by employee ASC, date ASC""" %
		conditions, filters, as_dict=1)

	att_map = {}
	for d in attendance_list:
		att_map.setdefault(d.employee, frappe._dict()).setdefault(d.day_of_month, "")
		att_map[d.employee][d.day_of_month] = d.status

	return att_map

def get_conditions(filters):
	if not (filters.get("month") and filters.get("year")):
		msgprint(_("Please select month and year"), raise_exception=1)

	filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
		"Dec"].index(filters.month) + 1

	filters["total_days_in_month"] = monthrange(cint(filters.year), filters.month)[1]

	conditions = " and  month(date) = %(month)s  and  year(date) = %(year)s "

	if filters.get("company"): conditions += " and `tabEmployee Attendance Logs`.company = %(company)s"
	if filters.get("employee"): conditions += " and `tabEmployee Attendance Logs`.employee = %(employee)s"

	return conditions, filters

def get_employee_details(filters):
	emp_map = frappe._dict()
	for d in frappe.db.sql("""select name, employee_name, designation, department, branch, company,
		holiday_list from tabEmployee where company = "%s" """ % (filters.get("company")), as_dict=1):
		emp_map.setdefault(d.name, d)

	return emp_map

def get_holiday(holiday_list, month):
	holiday_map = frappe._dict()
	for d in holiday_list:
		if d:
			holiday_map.setdefault(d, frappe.db.sql_list('''select day(holiday_date) from `tabHoliday`
				where parent=%s and month(holiday_date)=%s''', (d, month)))

	return holiday_map

@frappe.whitelist()
def get_attendance_years():
	year_list = frappe.db.sql_list("""select distinct YEAR(date) from `tabEmployee Attendance Logs` ORDER BY YEAR(date) DESC""")
	if not year_list:
		year_list = [getdate().year]

	return "\n".join(str(year) for year in year_list)


def get_leaveTypes():
	leave_types = frappe.db.sql("""select DISTINCT name , CONCAT('<b style = "color:deeppink">' , IFNULL(abbreviation,'L')  ,'</b>') as app from `tabLeave Type` where 1= 1""" , as_dict = 1)
	leave_dict = {}
	if  leave_types:
		for l in leave_types:
			leave_dict[str(l.name)] = str(l.app)

	return leave_dict
