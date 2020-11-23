# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime,timedelta,time
from frappe.utils import now, cint, get_datetime, to_timedelta,update_progress_bar

# Type Number Codes : 
# 	1 => Present
# 	2 => Absent
# 	3 => Leave
# 	4 => Holiday
# 	5 => Business Trip
#   6 => Mission
#   7 => Mission All Day
#   8 => Half Day

class AttendanceCalculation(Document):
	# attendances = []
	# employees = []

	
	def Calculate_attendance(self):
		self.attendances = frappe.db.sql("""
			select employee , Date(log_time) as Day  , MIN(log_time) as 'IN' ,  MAX(log_time) as 'OUT'  from `tabDevice Log`
	        
			group by Date(log_time),employee   
			having  Day between '{from_date}' and '{to_date}'
			""".format(from_date=self.from_date,to_date=self.to_date),as_dict=1)
		day = datetime.strptime(self.from_date,'%Y-%m-%d').date()
		self.to_date = datetime.strptime(self.to_date,'%Y-%m-%d').date()
		self.from_date = datetime.strptime(self.from_date,'%Y-%m-%d').date()
		self.employees = list(set([x.employee for x in self.attendances]))
		total_days = (self.to_date - self.from_date).days +1
		count = 0.5
		if self.attendances and self.employees:
			while day <= self.to_date:
				frappe.publish_realtime('update_progress', {
				    'progress': count,
				    'total': total_days
				})

				
				count +=1
				result = [self.calculate(employee = employee , day = day ) for employee in self.employees]
				
				day += timedelta(days=1)
		return True

	def calculate(self,employee , day):
		doc = frappe.new_doc('Employee Attendance Logs')
		doc.name = "Att-{employee}-{date}".format(employee=str(employee) , date = str(day))
		doc.employee = employee
		doc.date = day 
		doc.early_in = 0
		doc.early_out = 0
		doc.late_in = 0
		doc.late_out = 0


		Holidays = None
		Leaves = None
		Shift = None
		doc.is_calculated=0
		company , holiday_list,default_shift =  frappe.db.get_value('Employee', employee, ['company','holiday_list', 'default_shift'])
		old_doc =  frappe.db.get_value('Employee Attendance Logs', {'employee':employee , 'date' : day}, ['name' , 'is_calculated'] , as_dict=1)
		if old_doc:
			if old_doc.is_calculated:
				return
			else:
			 doc.name = old_doc.name
			 frappe.delete_doc('Employee Attendance Logs', old_doc.name)
		
		if not default_shift:
			default_shift = frappe.db.get_value('Company', company, ['default_shift'])
			if default_shift and not holiday_list:
				holiday_list = frappe.db.get_value('Shift Type', default_shift, ['holiday_list'])
		if not holiday_list:
			holiday_list = frappe.db.get_value('Company', company, ['default_holiday_list'])

		if not holiday_list:
			frappe.throw(_("Please Set Default Holiday List In Company or in Each Employee"))
		if not default_shift:
			frappe.throw(_("Please Set Default Shift Type  In Company or in Each Employee"))
		doc.company = company

		Holidays = frappe.db.sql("""
			select * from `tabHoliday` where parent = '{holiday_list}' and holiday_date = '{day}'
			""".format(holiday_list=holiday_list,day=day),as_dict=1)
		Shift = frappe.db.get_value('Shift Type', default_shift, ['start_time', 'end_time'], as_dict=1)
		doc.shift_start = Shift.start_time
		doc.shift_end = Shift.end_time
		doc.shift_actual_start = timedelta(minutes=0)
		doc.shift_actual_end = timedelta(minutes=0)
		user_records_in_day = [x for x in self.attendances if x.employee == employee and x.Day == day]
		if Holidays :
			# Day is Holiday
			doc.reference_type = "Holiday List"
			doc.reference_name =  	holiday_list
			self.In_Holiday(doc)
		else :
			# Not Holiday
			Leaves = frappe.db.sql("""
			select * from `tabLeave Application` where employee = '{employee}' and from_date <= '{day}' and to_date >= '{day}' and docstatus = 1 and status = 'Approved'
			""".format(employee=employee,day=day),as_dict=1)
			if Leaves :
				# In Leave
				doc.reference_type = "Leave Application"
				doc.reference_name =  	Leaves[0].name

				if  Leaves[0].half_day:
					if Leaves[0].half_day_date == day :
						if user_records_in_day :
							# Present in Half Day
							self.Present(doc,user_records_in_day[0],Shift ,type =4)
						else :
							# half day with no records
							self.Absent(doc)
				else:
					self.In_Leave (doc)
			else :
				BusinessTrips = frappe.db.sql("""
					select * from `tabBusiness Trip` where docstatus = 1 and from_date <= '{day}' and to_date >= {day}
					and employee = '{employee}'
					""".format(day=day,employee=employee) ,as_dict =1)
				if BusinessTrips :
					doc.reference_type = "Business Trip"
					doc.reference_name =  	BusinessTrips[0].name
					self.In_BusinessTrip(doc)
					

				else :

						doc.reference_type = "Shift Type"
						doc.reference_name = default_shift
						# frappe.msgprint(str(datetime.strptime(x.Day,"%Y-%m-%d") for x in self.attendances) + "  " + str(day))
						# frappe.msgprint(str(user_records_in_day))
						missions = frappe.db.sql("""
							select * from `tabMission` where docstatus = 1 and tabMission.date = '{day}'  and employee = '{employee}' order by start_time asc ,  end_time asc
							""".format(day=day,employee=employee),as_dict=1)
						if missions and user_records_in_day:
							self.Present(doc,user_records_in_day[0],Shift ,missions=missions,type =2)

						elif missions and not user_records_in_day:
							self.Present(doc,user_records_in_day[0],Shift ,missions = missions,type =3)
						elif not user_records_in_day:
							# Absent
							self.Absent(doc)
						elif user_records_in_day:
							# Present 
							self.Present(doc,user_records_in_day[0],Shift)




		#frappe.msgprint(str(employee) ,str(day))
		#doc.insert()
	def In_Holiday (self,doc):
		doc.type = "Holiday"
		doc.type_number = 4
		doc.insert()	

	def In_BusinessTrip (self,doc):
		doc.type = "Business Trip"
		doc.type_number = 5
		doc.insert()

	def In_Leave (self,doc):
		doc.type = "Leave"
		doc.type_number = 3
		doc.insert()	

	def Absent (self,doc):
		doc.type = "Absent"
		doc.type_number = 2
		doc.insert()

	# def Present (self,doc , log ,shift , missions = None , type = 1):
	# 	doc.type = "Present"
	# 	doc.type_number = 1
	# 	doc.shift_actual_start = log.IN.time()
	# 	doc.shift_actual_end = log.OUT.time()
	# 	doc.early_in = shift.start_time - to_timedelta(str(log.IN.time()))
	# 	doc.late_in =  to_timedelta(str(log.IN.time())) - shift.start_time
	# 	doc.early_out =  shift.end_time  -to_timedelta(str(log.OUT.time()))
	# 	doc.late_out = to_timedelta(str(log.OUT.time())) - shift.end_time
	# 	if doc.early_in < timedelta(minutes=0):
	# 		doc.early_in = timedelta(minutes=0)
	# 	if doc.early_out < timedelta(minutes=0):
	# 		doc.early_out = timedelta(minutes=0)
	# 	if doc.late_out < timedelta(minutes=0):
	# 		doc.late_out = timedelta(minutes=0)
	# 	if doc.late_in < timedelta(minutes=0):
	# 		doc.late_in = timedelta(minutes=0)


	# 	doc.insert()

	def Present (self,doc , log ,shift , missions = None , type = 1):
		doc.type = "Present"
		doc.type_number = 1
		IN = None
		OUT = None
		if type == 1 :
			# Normal Present
			IN = to_timedelta(str(log.IN.time()))
			OUT = to_timedelta(str(log.OUT.time()))
		elif type == 2 :
			# Present With Missions in day
			doc.type = "Mission"
			doc.type_number = 6
			if missions[0].start_time < to_timedelta(str(log.IN.time())):
				IN = missions[0].start_time
			else : 
				IN = to_timedelta(str(log.IN.time()))
			if missions[-1].end_time > to_timedelta(str(log.OUT.time())):
				OUT = missions[-1].end_time
			else:
				OUT = to_timedelta(str(log.OUT.time()))
		elif type == 3 :
			# Present With missions all the day
			doc.type = "Mission All Day"
			doc.type_number = 7
			IN = missions[0].start_time
			OUT = missions[-1].end_time

		elif type == 4 :
			doc.type = "Half Day"
			doc.type_number = 8
			IN = to_timedelta(str(log.IN.time()))
			OUT = to_timedelta(str(log.OUT.time()))


		doc.shift_actual_start = IN
		doc.shift_actual_end = OUT
		doc.early_in = shift.start_time - IN
		doc.late_in =  IN - shift.start_time
		doc.early_out =  shift.end_time  - OUT
		doc.late_out = OUT - shift.end_time
		if doc.early_in < timedelta(minutes=0):
			doc.early_in = timedelta(minutes=0)
		if doc.early_out < timedelta(minutes=0):
			doc.early_out = timedelta(minutes=0)
		if doc.late_out < timedelta(minutes=0):
			doc.late_out = timedelta(minutes=0)
		if doc.late_in < timedelta(minutes=0):
			doc.late_in = timedelta(minutes=0)


		doc.insert()


