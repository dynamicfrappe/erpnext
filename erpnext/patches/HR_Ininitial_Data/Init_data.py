# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	try:
		add_warnning_types()
	except Exception as e:
		frappe.log_error(message=e , title="add_warnning_types")
	try:
		add_Permission_types()
	except Exception as e:
		frappe.log_error(message=e, title="add_Permission_types")
	try:
		add_penality_types()
	except Exception as e:
		frappe.log_error(message=e, title="add_penality_types")




def add_warnning_types():
	if not frappe.db.exists('Warnings Types', '1'):
		doc = frappe.get_doc({
			'doctype': 'Warnings Types',
			'warning_name': 'Termination Warning' ,
			'code' : '1'
		})
		doc.insert()
	if not frappe.db.exists('Warnings Types', '2'):
		doc = frappe.get_doc({
			'doctype': 'Warnings Types',
			'warning_name': 'Warning Letter' ,
			'code' : '2'
		})
		doc.insert()




def add_Permission_types():
	if not frappe.db.exists({
		'doctype':'Permission Type',
		'code' : 3
	}):

		doc = frappe.get_doc({
			'doctype': 'Permission Type',
			'permission_name': 'Middle of The Day',
			'code': 3
		})
		doc.insert()


	if not frappe.db.exists({
		'doctype':'Permission Type',
		'code' : 2
	}):

		doc = frappe.get_doc({
			'doctype': 'Permission Type',
			'permission_name': 'End of The Day',
			'code': 2
		})
		doc.insert()


	if not frappe.db.exists({
		'doctype':'Permission Type',
		'code' : 1
	}):

		doc = frappe.get_doc({
			'doctype': 'Permission Type',
			'permission_name': 'Morining',
			'code': 1
		})
		doc.insert()


def add_penality_types():
	if not frappe.db.exists({
		'doctype': 'Penality Type',
		'code': '1'
	}):
		doc = frappe.get_doc({
			'doctype': 'Penality Type',
			'description': 'خصم من الاجر',
			'code': '1'
		})
		doc.insert()

	if not frappe.db.exists({
		'doctype': 'Penality Type',
		'code': '1'
	}):
		doc = frappe.get_doc({
			'doctype': 'Penality Type',
			'description': 'خصم من الاجر',
			'code': '1'
		})
		doc.insert()

	if not frappe.db.exists({
		'doctype': 'Penality Type',
		'code': '2'
	}):
		doc = frappe.get_doc({
			'doctype': 'Penality Type',
			'description': 'لفت نظر',
			'code': '2'
		})
		doc.insert()

	if not frappe.db.exists({
		'doctype': 'Penality Type',
		'code': '3'
	}):
		doc = frappe.get_doc({
			'doctype': 'Penality Type',
			'description': 'انذار بالفصل',
			'code': '3'
		})
		doc.insert()

	if not frappe.db.exists({
		'doctype': 'Penality Type',
		'code': '4'
	}):
		doc = frappe.get_doc({
			'doctype': 'Penality Type',
			'description': 'حرمان من الزيادة السنوية / او جزء منها',
			'code': '4'
		})
		doc.insert()

	if not frappe.db.exists({
		'doctype': 'Penality Type',
		'code': '5'
	}):
		doc = frappe.get_doc({
			'doctype': 'Penality Type',
			'description': 'تأجيل العلاوة مدة لا تتجاوز الثلاث شهور',
			'code': '5'
		})
		doc.insert()

	if not frappe.db.exists({
		'doctype': 'Penality Type',
		'code': '6'
	}):
		doc = frappe.get_doc({
			'doctype': 'Penality Type',
			'description': 'الحرمان من جزء من العلاوة بما لا يجاوز نصفها',
			'code': '6'
		})
		doc.insert()

	if not frappe.db.exists({
		'doctype': 'Penality Type',
		'code': '7'
	}):
		doc = frappe.get_doc({
			'doctype': 'Penality Type',
			'description': 'تأجيل الترقية مدة لا تزيد عن سنة',
			'code': '7'
		})
		doc.insert()

	if not frappe.db.exists({
		'doctype': 'Penality Type',
		'code': '8'
	}):
		doc = frappe.get_doc({
			'doctype': 'Penality Type',
			'description': 'خفض الاجر بمقدار علاوة',
			'code': '8'
		})
		doc.insert()

	if not frappe.db.exists({
		'doctype': 'Penality Type',
		'code': '9'
	}):
		doc = frappe.get_doc({
			'doctype': 'Penality Type',
			'description': 'خفض الدرجة الوظيفية للدرجة الادنى دون المساس بالاجر',
			'code': '9'
		})
		doc.insert()

	if not frappe.db.exists({
		'doctype': 'Penality Type',
		'code': '10'
	}):
		doc = frappe.get_doc({
			'doctype': 'Penality Type',
			'description': 'الفصل بعد العرض على مجلس الادارة',
			'code': '10'
		})
		doc.insert()

	if not frappe.db.exists({
		'doctype': 'Penality Type',
		'code': '11'
	}):
		doc = frappe.get_doc({
			'doctype': 'Penality Type',
			'description': 'الفصل وفقا لاحكام القانون',
			'code': '11'
		})
		doc.insert()