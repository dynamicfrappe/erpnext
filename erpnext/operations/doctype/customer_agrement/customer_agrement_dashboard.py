from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
        'fieldname': 'customer_agreement',
		'non_standard_fieldnames': {
				'Operations Invoice Dues': 'agreement',
				'Operation Sales Invoice': 'customer_agreement',
			},
        'transactions': [
			{
				'label': _('Operations Invoice'),
				'items': ['Operations Invoice Dues','Operation Sales Invoice']
			}
		]
	}
