# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe import _
import frappe
from datetime import date
import datetime
from frappe.utils import add_to_date
from frappe.utils import getdate
from frappe.utils import pretty_date, now, add_to_date
from erpnext.accounts.utils import get_balance_on
from operator import itemgetter


def execute(filters=None):
	return ExchangeCovenant(filters).run()


class ExchangeCovenant(object):
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})

	def run(self):
		self.get_columns()
		self.get_data()

		return self.columns , self.data

	def get_columns(self):
		#add columns wich appear data
		self.columns = [
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Data",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120
		},
		{
			"label": _("Advance Amount"),
			"fieldname": "advance_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Sanctioned Amount"),
			"fieldname": "sanctioned_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		]

		return self.columns


	def get_data(self):
		self.data = []
		self.conditions, self.values,self.query = self.get_conditions(self.filters)
		self.data = self.get_data_from_Employee_Advance(self.conditions,self.values,self.query)
		return self.data


	def get_data_from_Employee_Advance(self,conditions = '' ,values = '',query=''):
		additional_condition = 'GROUP  BY tc.employee' if self.filters.get("employee") else ''
		default_query = f"""
		select tc.employee, {query} from `tabExpense Claim` tc
		inner JOIN  `tabExpense Claim Detail` td
		ON tc.name = td.parent AND {conditions}
		inner JOIN `tabEmployee Advance` ta 
		on tc.employee = ta.employee
		{additional_condition}
		"""
		# frappe.errprint(f'default_query-->{default_query}')
		data_dict_p = frappe.db.sql(default_query,values=values,as_dict=1)
		# data_dict_p = frappe.db.sql(query,as_dict=1)
		return data_dict_p

	def get_conditions(self,filters):
		conditions = "1=1 "
		values = dict()
		q_test = 'ta.advance_amount,td.amount ,td.sanctioned_amount  '
		if filters.get("employee"):
			conditions += " AND tc.employee =  %(employee)s"
			values["employee"] = filters.get("employee")
			q_test = 'sum(ta.advance_amount)advance_amount,sum(td.amount)amount ,sum(td.sanctioned_amount)sanctioned_amount'
		return conditions, values,q_test


		# default_query = """
		# select tc.employee
		# from `tabExpense Claim` tc , `tabExpense Claim Detail` td,
		# `tabEmployee Advance` ta 
		#  WHERE tc.name = td.parent AND {conditions} 
		# """.format(conditions=conditions)
		# data_dict_p = frappe.db.sql(default_query,values=values,as_dict=1)

# query = 'ta.advance_amount,td.amount ,td.sanctioned_amount '
		# q1 =  """
		# select tc.employee,ta.advance_amount,td.amount ,td.sanctioned_amount 
		# from `tabExpense Claim` tc , `tabExpense Claim Detail` td,
		# `tabEmployee Advance` ta 
		#  WHERE tc.name = td.parent
		# """
# conditions += " AND ta.employee =  %(employee)s group by ta.employee"
			# values["employee"] = filters.get("employee")
			# query = 'sum(ta.advance_amount)advance_amount,sum(td.amount)amount ,sum(td.sanctioned_amount)sanctioned_amount'

#3-------------> sperate query:
# q1 = f"""
# 			select tc.employee,sum(ta.advance_amount)advance_amount,sum(td.amount)amount ,sum(td.sanctioned_amount)sanctioned_amount
# 			from `tabExpense Claim` tc 
# 			inner JOIN  `tabExpense Claim Detail` td
# 			ON tc.name = td.parent and tc.employee = '{filters.get("employee")}'
# 			inner JOIN `tabEmployee Advance` ta 
# 			on tc.employee = ta.employee
# 			GROUP  BY tc.employee
# 			"""


# q1 = """
# 			select tc.employee,ta.advance_amount,td.amount ,td.sanctioned_amount from `tabExpense Claim` tc 
# 		 	inner JOIN  `tabExpense Claim Detail` td
# 		 	ON tc.name = td.parent
# 			inner JOIN `tabEmployee Advance` ta 
# 		 	on tc.employee = ta.employee
# 		"""