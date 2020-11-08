# coding=utf-8

from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		# Modules
		
		{
			"module_name": "Accounts",
			"category": "Modules",
			"label": _("Accounting"),
			"color": "#3498db",
			"icon": "icon accounting-blue",
			"type": "module",
			"description": "Accounts, billing, payments, cost center and budgeting."
		},
		{
			"module_name": "Selling",
			"category": "Modules",
			"label": _("Sales Management"),
			"color": "#1abc9c",
			"icon": "icon selling-blue",
			"type": "module",
			"description": "Sales orders, quotations, customers and items."
		},
		{
			"module_name": "Buying",
			"category": "Modules",
			"label": _("Purchasing Management"),
			"color": "#c0392b",
			"icon": "icon buying-blue",
			"type": "module",
			"description": "Purchasing, suppliers, material requests, and items."
		},
		{
			"module_name": "Stock",
			"category": "Modules",
			"label": _("Stock"),
			"color": "#f39c12",
			"icon": "icon stock-blue",
			"type": "module",
			"description": "Stock transactions, reports, serial numbers and batches."
		},
		{
			"module_name": "Assets",
			"category": "Modules",
			"label": _("Assets"),
			"color": "#4286f4",
			"icon": "icon assets-blue",
			"type": "module",
			"description": "Asset movement, maintainance and tools."
		},
		
		
		{
			"module_name": "HR",
			"category": "Modules",
			"label": _("Human Resources"),
			"color": "#2ecc71",
			"icon": "icon hr-blue",
			"type": "module",
			"description": "Employees, attendance, payroll, leaves and shifts."
		},
		{
			"module_name": "Operations",
			"category": "Modules",
			"label": _("Operations"),
			"color": "#3498db",
			"icon": "icon accounting-blue",
			"type": "module",
			"description": "Accounts, billing, payments, cost center and budgeting."
		},
		{
			"module_name": "Manufacturing",
			"category": "Modules",
			"label": _("Manufacturing"),
			"color": "#7f8c8d",
			"icon": "icon manufacture-blue",
			"type": "module",
			"description": "BOMS, work orders, operations, and timesheets."
		},
		


		# Category: "Domains"
		{
			"module_name": "Manufacturing",
			"category": "Domains",
			"label": _("Manufacturing"),
			"color": "#7f8c8d",
			"icon": "icon manufacture-blue",
			"type": "module",
			"description": "BOMS, work orders, operations, and timesheets."
		},
		{
			"module_name": "Retail",
			"category": "Domains",
			"label": _("Retail"),
			"color": "#7f8c8d",
			"icon": "icon retail-blue",
			"type": "module",
			"description": "Point of Sale and cashier closing."
		},
		{
			"module_name": "Education",
			"category": "Domains",
			"label": _("Education"),
			"color": "#428B46",
			"icon": "icon education-blue",
			"type": "module",
			"description": "Student admissions, fees, courses and scores."
		},

		{
			"module_name": "Healthcare",
			"category": "Domains",
			"label": _("Healthcare"),
			"color": "#FF888B",
			"icon": "icon healthcare-blue",
			"type": "module",
			"description": "Patient appointments, procedures and tests."
		},
		{
			"module_name": "Agriculture",
			"category": "Domains",
			"label": _("Agriculture"),
			"color": "#8BC34A",
			"icon": "icon agriculture-blue",
			"type": "module",
			"description": "Crop cycles, land areas, soil and plant analysis."
		},
		{
			"module_name": "Hotels",
			"category": "Domains",
			"label": _("Hotels"),
			"color": "#EA81E8",
			"icon": "icon hotel-blue",
			"type": "module",
			"description": "Hotel rooms, pricing, reservation and amenities."
		},

		{
			"module_name": "Non Profit",
			"category": "Domains",
			"label": _("Non Profit"),
			"color": "#DE2B37",
			"icon": "icon non-profit-blue",
			"type": "module",
			"description": "Volunteers, memberships, grants and chapters."
		},
		{
			"module_name": "Restaurant",
			"category": "Domains",
			"label": _("Restaurant"),
			"color": "#EA81E8",
			"icon": "icon restaurant-blue",
			"_doctype": "Restaurant",
			"type": "module",
			"link": "List/Restaurant",
			"description": "Menu, Orders and Table Reservations."
		},

		
	]