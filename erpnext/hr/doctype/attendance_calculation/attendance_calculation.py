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
#   13 => Working On Weekend
#   14 => 
#   15 => 
#   16 => 
#   17 => 
#   18 => 

class AttendanceCalculation(Document):
	# attendances = []
	# employees = []
	def on_cancel (self):
		self.update_attendance_logs(status=0)
		self.delete_Additional_salary()

	def on_submit(self):
		self.delete_Additional_salary()
		self.post_attendance()
		self.update_attendance_logs(status = 1)

	def update_attendance_logs (self , status = 1):
		frappe.db.sql (""" 
		update `tabEmployee Attendance Logs` set docstatus = {status} , is_calculated = {status} where   date(date) between date('{from_date}') and date ('{to_date}') ;
		""".format(status=status  , from_date = self.from_date , to_date = self.to_date ))
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

		joining_date, relieving_date = frappe.get_cached_value("Employee", employee,["date_of_joining", "relieving_date"])
		if joining_date and day < joining_date:
			return
		if relieving_date and day > relieving_date:
			return


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
		doc.shift_actual_start = ''
		doc.shift_actual_end = ''
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
				if Holidays[0].type == "Official":
					self.Present(doc,user_records_in_day[0],Shift ,type =5)
				else:
					self.Present(doc,user_records_in_day[0],Shift ,type =6)

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
		elif type == 5:
			# Working On Holiday
			doc.type = "Working On Holiday"
			doc.type_number = 9
			IN = to_timedelta(str(log.IN.time()))
			OUT = to_timedelta(str(log.OUT.time()))
		elif type == 6 :
			# Working On Holiday
			doc.type = "Working On Weekend"
			doc.type_number = 13
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
		if IN == OUT:
			doc = self.forget_fingerPrint(doc)

		# Calculate delayes
		if doc.late_in > timedelta(minutes=0):
			doc = self.calculate_Delays(doc)


		doc.insert()
	def forget_fingerPrint (self,doc):
		doc.forget_fingerprint = 1
		in_min = abs((doc.early_in + doc.late_in).seconds / 60)
		out_min = abs((doc.early_out +  doc.late_out).seconds / 60)

		if in_min <= out_min :
			# Forgetten is OUT
			doc.fingerprint_type='Out'
			doc.shift_actual_end = ''
			doc.late_out = timedelta(minutes=0)
			doc.early_out = timedelta(minutes=0)
		else:
			# Forgetten is IN
			doc.fingerprint_type = 'IN'
			doc.shift_actual_start = ''
			doc.early_in = timedelta(minutes=0)
			doc.late_in = timedelta(minutes=0)
		return doc


	def calculate_Delays(self,doc):
		employee = frappe.get_doc("Employee",doc.employee)
		doc.late_penality = 0
		doc.late_factor = 0
		if  employee.attendance_role:
			#frappe.throw(_("Please Assign Attendance Rule to Employee {}".format(employee.name)))

			attendance_role = frappe.get_doc("Attendance Rule",employee.attendance_role)
			if doc.type == "Working On Holiday":
				if not attendance_role.caclulate_deduction_in_working_on_holiday :
					return doc
			if doc.type == "Working On Weekend":
				if not attendance_role.caclulate_deduction_in_working_on_weekend :
					return doc
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
							# frappe.msgprint(str(level))
							level_factor = penality.level_onefactor
						elif level == 2  :
							# frappe.msgprint(str(level))

							level_factor = penality.level_towfactor
						elif level == 3 :
							# frappe.msgprint(str(level))

							level_factor = penality.level__threefactor
						elif level == 4 :
							# frappe.msgprint(str(level))

							level_factor = penality.level_fourfactor
						elif level == 5  :
							# frappe.msgprint(str(level))

							level_factor = penality.leve_five_factor
						else:
							# frappe.msgprint(str(level))

							level_factor = penality.leve_five_factor or penality.level_fourfactor or penality.level__threefactor or penality.level_towfactor or penality.level_onefactor or 0

						doc.late_penality = level_factor * penality.factor

						if penality.add_deduction:
							if penality.deduction_factor :
								doc.late_factor = penality.deduction_factor
							else:
								doc.late_factor = doc.late_in.seconds/60






		return doc


	def check_sal_struct(self,employee):
		joining_date = employee.date_of_joining or self.from_date
		relieving_date = employee.relieving_date or self.to_date
		cond = """and sa.employee=%(employee)s and (sa.from_date <= %(start_date)s or
				sa.from_date <= %(end_date)s or sa.from_date <= %(joining_date)s)"""

		st_name = frappe.db.sql("""
			select sa.salary_structure
			from `tabSalary Structure Assignment` sa join `tabSalary Structure` ss
			where sa.salary_structure=ss.name
				and sa.docstatus = 1 and ss.docstatus = 1 and ss.is_active ='Yes' %s
			order by sa.from_date desc
			limit 1
		""" %cond, {'employee': employee.name, 'start_date': self.from_date,
			'end_date': self.to_date, 'joining_date': joining_date})

		if st_name:
			self.salary_structure = st_name[0][0]
			return self.salary_structure

		else:
			self.salary_structure = None
			frappe.msgprint(_("No active or default Salary Structure found for employee {0} for the given dates")
				.format(employee.name), title=_('Salary Structure Missing'))


	def post_attendance(self):
		if self.from_date and self.to_date:
			sql = """
				select  employee ,SUM(case when type = "Absent" then 1 else 0 end) as AbsentDays ,
			   SUM(case when type = "Working On Holiday" then 1 else 0 end) as working_on_holiday ,
			  sec_to_time( SUM(time_to_sec(late_in) ) ) as late_in ,
			  sec_to_time( SUM(time_to_sec(early_out) ) ) as early_out ,
			  sec_to_time( SUM(time_to_sec(early_in) ) ) as early_in ,
			  sec_to_time( SUM(time_to_sec(late_out) ) ) as late_out ,
			  ifnull(SUM(late_factor),0) as late_factor ,
			  ifnull(SUM(late_penality),0) as late_penality,
			  ifnull(SUM(case when forget_fingerprint = 1 and fingerprint_type = "IN" then 1 else 0 end ),0) as forget_fingerprint_in,
			  ifnull(SUM(case when forget_fingerprint = 1 and fingerprint_type = "Out" then 1 else 0 end ),0) as forget_fingerprint_out
				from `tabEmployee Attendance Logs`
				where date(date) between  date('{start_date}')
				and docstatus = 1 and is_calculated = 1
				and date('{end_date}') group by  employee
				;
			""".format( start_date = self.from_date , end_date = self.to_date )
			attendances = frappe.db.sql(sql ,as_dict=1)
			if attendances :
				for attendance in attendances:
					employee = frappe.get_doc("Employee", attendance.employee)
					self.check_sal_struct(employee)
					if not getattr(self, '_salary_structure_doc', None) and  getattr(self, 'salary_structure', None):
						self._salary_structure_doc = frappe.get_doc('Salary Structure', self.salary_structure)
					if getattr(self, '_salary_structure_doc', None) :
						total_hourly_salary = 0
						for item in self._salary_structure_doc.get(
								"earnings"):  # if not (len(self.get("earnings")) or len(self.get("deductions"))):
							salary_compnent = frappe.get_doc("Salary Component", item.salary_component)
							if salary_compnent:
								if salary_compnent.consider_in_hour_rate and salary_compnent.type == "Earning" and item.amount:
									total_hourly_salary += item.amount
						total_working_days =  frappe.db.get_single_value("HR Settings","total_working_days")
						total_working_hours_per_day =employee.total_working_hours_per_day
						if not total_working_hours_per_day:
							frappe.msgprint(
								_("Please Set The Total Working Hours in Employee {}".format(employee)), title='Error',
								indicator='red')
						self.daily_rate = total_hourly_salary / (total_working_days)
						self.hour_rate = self.daily_rate / total_working_hours_per_day

						# Over Time
						overtime_salary_component_name = frappe.db.get_single_value("HR Settings" , "overtime_salary_component")
						overtime_salary_component = frappe.get_doc("Salary Component"  , overtime_salary_component_name)
						late_out_rate = frappe.db.get_single_value("HR Settings" , "late_out_rate")
						early_in_rate = frappe.db.get_single_value("HR Settings" , "early_in_rate")
						if overtime_salary_component and late_out_rate and early_in_rate :
								# overtime_factor = int(attendance.AbsentDays) * self.daily_rate
								early_in_Hours =  (attendance.early_in.seconds)/3600
								late_out_Hours =  (attendance.late_out.seconds)/3600
								overtime_factor = ((late_out_Hours * late_out_rate )/total_working_hours_per_day ) + ((early_in_Hours* early_in_rate)/total_working_hours_per_day)
								overtime_amount = overtime_factor * self.daily_rate
								if overtime_amount :
									desc = 'Overtime value : ' + str (overtime_factor)
									self.submit_Additional_salary(employee.name, overtime_salary_component_name ,overtime_amount, desc )
						#Delays


						early_out_Hours =  (attendance.early_out.seconds)/3600
						late_in_Hours =  (attendance.late_in.seconds)/3600
						# delays_factor =  ((early_out_Hours* early_out_rate)/total_working_hours_per_day)

						# delays_amount = delays_factor * self.daily_rate
						penality_amount = 0
						late_amount = 0
						penality_factor = 0
						late_factor = 0
						if employee.attendance_role:
							attendance_role = frappe.get_doc("Attendance Rule" , employee.attendance_role)
							if attendance_role.type:
								if attendance_role.type == "Daily":
									penality_amount = (attendance.late_penality * self.daily_rate) or 0
									late_factor = attendance.late_factor * (attendance_role.late_penalty_factor_by_date or 0)
									late_amount = (late_factor * self.hour_rate ) or 0

								elif attendance_role.type == "Monthly":

									late_minutes = (attendance.late_in.seconds / 60) or 0
									penality = None
									for i in attendance_role.late_role_table:
										if i.from_min <= late_minutes:
											penality = i

									if penality:

										penality_factor = penality.level_onefactor * penality.factor
										penality_amount = (penality_factor  * self.daily_rate) or 0

										late_factor = 0
										if penality.add_deduction:
											if penality.deduction_factor:
												late_factor = (penality.deduction_factor * attendance_role.late_penalty_factor_by_date) or 0
											else:
												late_factor = ((attendance.late_in.seconds / 60)* attendance_role.late_penalty_factor_by_date) or 0
										late_amount = late_factor * self.daily_rate

							if attendance_role.salary_componat_for_late and late_amount:
								desc = 'Delays : ' + str(late_factor)
								self.submit_Additional_salary(employee.name, attendance_role.salary_componat_for_late,late_amount, desc)

							if attendance_role.salary_component_for_late_penalty and penality_amount  :
								desc = 'Delays Penality: ' + str(penality_factor)
								self.submit_Additional_salary(employee.name, attendance_role.salary_component_for_late_penalty,penality_amount, desc)

							# forget finger print
							fingerprint_factor_in = attendance_role.fingerprint_forgetten_in_penality or 0
							fingerprint_amount = (fingerprint_factor_in * attendance.forget_fingerprint_in * self.daily_rate ) or 0
							fingerprint_factor_out = attendance_role.fingerprint_forgetten_out_penality or 0
							fingerprint_amount += (fingerprint_factor_out * attendance.forget_fingerprint_out * self.daily_rate) or 0
							if attendance_role.fingerprint_forgetten_penlaity_salary_component and fingerprint_amount :
								desc = 'Fingerprint IN forgetten times: ' + str(fingerprint_factor_in)
								desc += '\nFingerprint OUT forgetten times: ' + str(fingerprint_factor_out)
								self.submit_Additional_salary(employee.name,attendance_role.fingerprint_forgetten_penlaity_salary_component,fingerprint_amount, desc)

							# Absents Days
							absent_rate = frappe.db.get_single_value("HR Settings", "absent_rate") or 0
							absents_salary_component = attendance_role.absent__component
							abset_penalty_component = attendance_role.abset_penalty_component

							if attendance_role.absent_rules  :
									absent_rule = frappe.get_doc("Absent Rules", attendance_role.absent_rules)
									if absent_rule.senario == 'Deduction from Salary':
										self.absent_days = int(attendance.AbsentDays)
										absent_rate = 0
										absent_penality_rate = 0
										flag = 1
										if absent_rule.ruletemplate :
											for i in range (1,self.absent_days+1):
												if len(absent_rule.ruletemplate) >= i :
													absent_rate += absent_rule.ruletemplate[i-1].deduction
													absent_penality_rate += absent_rule.ruletemplate[i-1].penality
												else:
													absent_rate += absent_rule.ruletemplate[-1].deduction
													absent_penality_rate += absent_rule.ruletemplate[-1].penality
										absent_amount = absent_rate  * self.daily_rate
										absent_penality_amount = absent_penality_rate *   self.daily_rate
										if absent_amount:
											desc = '\nAbsent Days Factor: ' + str(absent_rate)
											self.submit_Additional_salary(employee.name,absents_salary_component,absent_amount, desc)
										if absent_penality_amount:
											desc = '\nAbsent Days Penaliteies: ' + str(absent_penality_rate)
											self.submit_Additional_salary(employee.name, abset_penalty_component,absent_penality_amount, desc)



							# Worhing On Holiday
							working_holiday_rate = attendance_role.working_on_holiday_rate or 0
							additional_days_salary_component_name = attendance_role.additional_days_salary_component or None
							if additional_days_salary_component_name and working_holiday_rate:
								self.adding_days = int(attendance.working_on_holiday)
								add_days_amount = working_holiday_rate * int(attendance.working_on_holiday) * self.daily_rate
								if add_days_amount:
									# frappe.msgprint("str(additional_days_salary_component)")
									# frappe.msgprint(str(additional_days_salary_component))
									desc = 'Addiotinal Days : ' + str(attendance.working_on_holiday)
									self.submit_Additional_salary(employee.name, additional_days_salary_component_name, add_days_amount, desc)

	def submit_Additional_salary(self, employee, salary_component, amount, desc):
		last_doc = frappe.db.get_value('Additional Salary', { "salary_component":salary_component , "employee":employee ,"attendance_calculation" : self.name}, ['name'])

		if not last_doc:
				component = frappe.get_doc("Salary Component", salary_component)
				# Data for update_component_row
				doc = frappe.new_doc("Additional Salary")
				doc.amount = amount
				doc.salary_component = salary_component
				doc.employee = employee
				doc.overwrite_salary_structure_amount = 1
				doc.amount_based_on_formula = 0
				doc.type = component.type
				doc.payroll_date = self.payroll_effect_date
				doc.description = desc
				doc.attendance_calculation = self.name
				doc.insert()
				doc.submit()
		else:
			frappe.msgprint(_("Employee {employee} has this Additional Salary {name} before".format(employee=employee , name=last_doc)))


	def delete_Additional_salary(self):
		frappe.db.sql("""delete from `tabAdditional Salary` where  attendance_calculation= '{name}' and salary_slip is null """.format(name=self.name))




