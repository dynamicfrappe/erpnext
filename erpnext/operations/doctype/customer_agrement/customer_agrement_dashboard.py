from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
        'fieldname': 'agreement',

        'transactions': [
			{
				'label': _('Operations Invoice Dues'),
				'items': ['Operations Invoice Dues']
			}
		]
	}
