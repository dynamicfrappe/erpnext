# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AttendanceRule(Document):
	def validate(self):


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


