from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
        'fieldname': 'invoice_due',

        'transactions': [
			{
				'label': _('Operation Sales Invoice'),
				'items': ['Operation Sales Invoice']
			}
		]
	}
