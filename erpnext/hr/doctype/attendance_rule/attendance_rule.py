# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class AttendanceRule(Document):
	def validate(self):

		list = []
		list.append(str(self.fingerprint_forgetten_penlaity_salary_component))
		list.append(str(self.salary_componat_for_late))
		list.append(str(self.salary_component_for_late_penalty))
		list.append(str(self.absent__component))
		list.append(str(self.abset_penalty_component))
		list.append(str(self.additional_days_salary_component))
		list.append(str(self.overtime_salary_component))
		message = ''
		if list.count(str(self.fingerprint_forgetten_penlaity_salary_component)) > 1 :
			message += '\n' + _('Fingerprint Forgetten penlaity Salary Component')
		if list.count(str(self.salary_componat_for_late)) > 1 :
			message += '\n' + _('Salary Componat for Late')
		if list.count(str(self.salary_component_for_late_penalty)) > 1 :
			message += '\n' + _('Salary Component For Late Penalty')
		if list.count(str(self.absent__component)) > 1 :
			message += '\n' + _('Absent  Component')
		if list.count(str(self.abset_penalty_component)) > 1 :
			message += '\n' + _('Absent Penalty Component')
		if list.count(str(self.additional_days_salary_component)) > 1 :
			message += '\n' + _('Additional Days Salary Component')
		if list.count(str(self.overtime_salary_component)) > 1 :
			message += '\n' + _('Overtime Salary Component')

		if message != '' :
			frappe.throw (_("this elements is Duplicated {}".format(message)))

		self.set_col_values()


	def set_col_values(self):
		for i in self.late_role_table :
			level_dict= []
			level_dict.append(float(i.level_onefactor) or 0)
			level_dict.append(float(i.level_towfactor) or 0)
			level_dict.append(float(i.level__threefactor) or 0)
			level_dict.append(float(i.level_fourfactor) or 0)
			level_dict.append(float(i.leve_five_factor )or 0 )
			
			for e in level_dict :
				try:
					level_dict.remove(0)
				except:
					pass
			for f in range(0 , 6):
				if f > len(level_dict) :
					level_dict.append(max(level_dict)) 
				
			level_dict.sort()
			i.level_onefactor = level_dict[0]
			i.level_towfactor =level_dict[1] 
			i.level_threefactor = level_dict[2]
			i.level_fourfactor = level_dict[3]
			i.level_five_factor = level_dict[4]


