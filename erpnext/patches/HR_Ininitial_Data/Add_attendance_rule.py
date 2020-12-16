# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	try:
		add_warnning_types()
	except Exception as e:
		frappe.log_error(message=e , title="add_warnning_types")





def add_warnning_types():
	pass


