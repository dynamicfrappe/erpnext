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
			"color": "#0e4194",
			"icon": "octicon octicon-repo",
			"type": "module",
			"description": "Accounts, billing, payments, cost center and budgeting."
		},
		{
			"module_name": "Selling",
			"category": "Modules",
			"label": _("Selling"),
			"color": "#0e4194",
			"icon": "octicon octicon-tag",
			"type": "module",
			"description": "Sales orders, quotations, customers and items."
		},
		{
			"module_name": "Buying",
			"category": "Modules",
			"label": _("Buying"),
			"color": "#0e4194",
			"icon": "octicon octicon-briefcase",
			"type": "module",
			"description": "Purchasing, suppliers, material requests, and items."
		},
		{
			"module_name": "Stock",
			"category": "Modules",
			"label": _("Stock"),
			"color": "#0e4194",
			"icon": "octicon octicon-package",
			"type": "module",
			"description": "Stock transactions, reports, serial numbers and batches."
		},
		{
			"module_name": "Assets",
			"category": "Modules",
			"label": _("Assets"),
			"color": "#0e4194",
			"icon": "octicon octicon-database",
			"type": "module",
			"description": "Asset movement, maintainance and tools."
		},
		{
			"module_name": "Projects",
			"category": "Modules",
			"label": _("Projects"),
			"color": "#0e4194",
			"icon": "octicon octicon-rocket",
			"type": "module",
			"description": "Updates, Timesheets and Activities."
		},
		{
			"module_name": "CRM",
			"category": "Modules",
			"label": _("CRM"),
			"color": "#0e4194",
			"icon": "octicon octicon-broadcast",
			"type": "module",
			"description": "Sales pipeline, leads, opportunities and customers."
		},
		{
			"module_name": "Support",
			"category": "Modules",
			"label": _("Support"),
			"color": "#0e4194",
			"icon": "fa fa-check-square-o",
			"type": "module",
			"description": "User interactions, support issues and knowledge base."
		},
		{
			"module_name": "HR",
			"category": "Modules",
			"label": _("Human Resources"),
			"color": "#0e4194",
			"icon": "octicon octicon-organization",
			"type": "module",
			"description": "Employees, attendance, payroll, leaves and shifts."
		},
		{
			"module_name": "Quality Management",
			"category": "Modules",
			"label": _("Quality"),
			"color": "#0e4194",
			"icon": "fa fa-check-square-o",
			"type": "module",
			"description": "Quality goals, procedures, reviews and action."
		},


		# Category: "Domains"
		{
			"module_name": "Manufacturing",
			"category": "Domains",
			"label": _("Manufacturing"),
			"color": "#0e4194",
			"icon": "octicon octicon-tools",
			"type": "module",
			"description": "BOMS, work orders, operations, and timesheets."
		},
		{
			"module_name": "Retail",
			"category": "Domains",
			"label": _("Retail"),
			"color": "#0e4194",
			"icon": "octicon octicon-credit-card",
			"type": "module",
			"description": "Point of Sale and cashier closing."
		},
		{
			"module_name": "Education",
			"category": "Domains",
			"label": _("Education"),
			"color": "#0e4194",
			"icon": "octicon octicon-mortar-board",
			"type": "module",
			"description": "Student admissions, fees, courses and scores."
		},

		{
			"module_name": "Healthcare",
			"category": "Domains",
			"label": _("Healthcare"),
			"color": "#0e4194",
			"icon": "fa fa-heartbeat",
			"type": "module",
			"description": "Patient appointments, procedures and tests."
		},
		{
			"module_name": "Agriculture",
			"category": "Domains",
			"label": _("Agriculture"),
			"color": "#0e4194",
			"icon": "octicon octicon-globe",
			"type": "module",
			"description": "Crop cycles, land areas, soil and plant analysis."
		},
		{
			"module_name": "Hotels",
			"category": "Domains",
			"label": _("Hotels"),
			"color": "#0e4194",
			"icon": "fa fa-bed",
			"type": "module",
			"description": "Hotel rooms, pricing, reservation and amenities."
		},

		{
			"module_name": "Non Profit",
			"category": "Domains",
			"label": _("Non Profit"),
			"color": "#0e4194",
			"icon": "octicon octicon-heart",
			"type": "module",
			"description": "Volunteers, memberships, grants and chapters."
		},
		{
			"module_name": "Restaurant",
			"category": "Domains",
			"label": _("Restaurant"),
			"color": "#0e4194",
			"icon": "fa fa-cutlery",
			"_doctype": "Restaurant",
			"type": "module",
			"link": "List/Restaurant",
			"description": "Menu, Orders and Table Reservations."
		},

		{
			"module_name": "Help",
			"category": "Administration",
			"label": _("Learn"),
			"color": "#0e4194",
			"icon": "octicon octicon-device-camera-video",
			"type": "module",
			"is_help": True,
			"description": "Explore Help Articles and Videos."
		},
		
	]
