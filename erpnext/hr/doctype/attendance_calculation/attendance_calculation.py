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
#   9 => Working On Holiday
#   10 => Week End
#   11 => Sick Leave
#   12 => Privilege Leave
#   13 => 
#   14 => 
#   15 => 
#   16 => 
#   17 => 
#   18 => 

class AttendanceCalculation(Document):
	# attendances = []
	# employees = []

	
	def Calculate_attendance(self):
		self.attendances = frappe.db.sql("""
			select emp.name as employee , Date(log_time) as Day  , MIN(log_time) as 'IN' ,  MAX(log_time) as 'OUT'  from `tabDevice Log`
			inner join `tabEmployee` emp on emp.attendance_device_id = `tabDevice Log`.enroll_no
			where emp.name is not null
			group by Date(log_time),emp.name  
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
		self.Permissions = None
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
		self.Permissions = frappe.db.sql("""
		select permission.name , type.code , SUBTIME (permission.to_time,permission.from_time) as Duration
			from tabPermission permission inner join `tabPermission Type` type on type.name = permission.permission_type where permission.docstatus = 1 and status = "Completed" and date(date) = date('{day}') and employee = '{employee}'
			group by  permission.name ;
		""".format(day = day , employee = employee),as_dict=1)
		if Holidays :
			# Day is Holiday
			if not user_records_in_day:
				
				doc.reference_type = "Holiday List"
				doc.reference_name =  	holiday_list
				if Holidays[0].type == "Official":
					self.In_Holiday(doc , type = 'Official')
				else: 
					self.In_Holiday(doc , type = 'Week End')

			else : 
				self.Present(doc,user_records_in_day[0],Shift ,type =5)
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
					
					doc.type = Leaves[0].leave_type	
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
	def In_Holiday (self,doc,type = 'Week End'):
		if type == 'Week End' :
			doc.type = "Week End"
			doc.type_number = 10
		else :
			doc.type = "Holiday"
			doc.type_number = 4
		doc.insert()	

	def In_BusinessTrip (self,doc):
		doc.type = "Business Trip"
		doc.type_number = 5
		doc.insert()

	def In_Leave (self,doc):
#		doc.type = "Leave"

		doc.type_number = 3
		doc.insert()	

	def Absent (self,doc):
		doc.type = "Absent"
		doc.type_number = 2
		doc.insert()




	# 	doc.insert()

	def Present (self,doc , log ,shift , missions = None , type = 1):
		# type document 
		#	1 => Normal Present 
		#	2 => Present With Missions in day
		#	3 => Present With missions all the day
		#	4 => Half Day
		#	5 => Working On Holiday
		#
		#
		#
		#
		doc.reference_type= "Shift Type"
		doc.reference_name= shift.name
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
			# Half Day
			doc.type = "Half Day"
			doc.type_number = 8
			IN = to_timedelta(str(log.IN.time()))
			OUT = to_timedelta(str(log.OUT.time()))
		elif type == 5 :
			# Working On Holiday
			doc.type = "Working On Holiday"
			doc.type_number = 9
			IN = to_timedelta(str(log.IN.time()))
			OUT = to_timedelta(str(log.OUT.time()))


		doc.shift_actual_start = IN
		doc.shift_actual_end = OUT
		doc.early_in = shift.start_time - IN
		doc.late_in =  IN - shift.start_time
		doc.early_out =  shift.end_time  - OUT
		doc.late_out = OUT - shift.end_time

		if self.Permissions :
			for i in self.Permissions:
				if i.code == 1:
					# start of the Day
					doc.late_in -= i.Duration
					doc.early_in = timedelta(minutes=0)
					# frappe.msgprint('str(doc.late_in)')
					# frappe.msgprint(str(doc.late_in))
				elif i.code == 2:
					# end of the day
					doc.late_out = timedelta(minutes=0)
					doc.early_out -= i.Duration
					# frappe.msgprint('str(doc.early_out)')
					# frappe.msgprint(str(doc.early_out))
				doc.reference_type = "Permission"
				doc.reference_name = i.name

		if doc.early_in < timedelta(minutes=0):
			doc.early_in = timedelta(minutes=0)
		if doc.early_out < timedelta(minutes=0):
			doc.early_out = timedelta(minutes=0)
		if doc.late_out < timedelta(minutes=0):
			doc.late_out = timedelta(minutes=0)
		if doc.late_in < timedelta(minutes=0):
			doc.late_in = timedelta(minutes=0)
		# Calculate delayes
		if doc.late_in > timedelta(minutes=0):
			doc = self.calculate_Delays(doc)


		doc.insert()

	def calculate_Delays(self,doc):
		employee = frappe.get_doc("Employee",doc.employee)
		doc.late_penality = 0
		doc.late_factor = 0
		if  employee.attendance_role:
			#frappe.throw(_("Please Assign Attendance Rule to Employee {}".format(employee.name)))

			attendance_role = frappe.get_doc("Attendance Rule",employee.attendance_role)
			if not attendance_role.late_role_table :
				frappe.msgprint(_("this Rule {} doesn't Contain Attendance Late Rules".format(attendance_role.name)))
			if  attendance_role.late_role_table :
				if attendance_role.type == 'Daily':
					# frappe.msgprint(str(attendance_role.late_role_table))
					late_minutes = doc.late_in.seconds /60
					doc.late_minutes =late_minutes
					penality = None
					for i in attendance_role.late_role_table:

						if i.from_min <= late_minutes  :
							penality = i


					if penality :
						doc.late_componant = penality.late_componant

						perviuos_penality_component = frappe.db.sql("""
						select count(*) as count from `tabEmployee Attendance Logs` where employee = '{employee}' and date(date) between date('{from_date}') and date('{to_date}') and late_componant = '{component}'
						""".format(employee=employee.name , from_date = self.from_date , to_date = doc.date , component = penality.late_componant ))
						level = perviuos_penality_component [0][0] + 1
						message = "employee {} ".format(employee.name) + "date {}".format(doc.date) + " Level {}".format(level) + "component {}".format( penality.late_componant)
						# frappe.msgprint(message)
						# frappe.msgprint(str())
						level_factor = 0
						if level == 1  :
							frappe.msgprint(str(level))
							level_factor = penality.level_onefactor
						elif level == 2  :
							frappe.msgprint(str(level))

							level_factor = penality.level_towfactor
						elif level == 3 :
							frappe.msgprint(str(level))

							level_factor = penality.level__threefactor
						elif level == 4 :
							frappe.msgprint(str(level))

							level_factor = penality.level_fourfactor
						elif level == 5  :
							frappe.msgprint(str(level))

							level_factor = penality.leve_five_factor
						else:
							frappe.msgprint(str(level))

							level_factor = penality.leve_five_factor or penality.level_fourfactor or penality.level__threefactor or penality.level_towfactor or penality.level_onefactor or 0

						doc.late_penality = level_factor * penality.factor

						if penality.add_deduction:
							if penality.deduction_factor :
								doc.late_factor = penality.deduction_factor
							else:
								doc.late_factor = doc.late_in.seconds/60






		return doc


