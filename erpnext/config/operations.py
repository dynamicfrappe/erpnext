from __future__ import unicode_literals
import frappe
from frappe import _


def get_data():
  return [
    {
      "label":_("Custody"),
      "icon": "fa fa-table",
      "items":[
        {
          "type": "doctype",
          "name": "Employee Tools",
          "onboard": 1
        },
        {
          "type": "doctype",
          "name": "Delivery Note",
          "onboard": 1
        },
        

      ]
    },
    # {
    #   "label": _("Training"),
    #   "items": [
    #     {
    #       "type": "doctype",
    #       "name": "Training Program"
    #     },
    #     {
    #       "type": "doctype",
    #       "name": "Training Event"
    #     },
    #     {
    #       "type": "doctype",
    #       "name": "Training Result"
    #     },
    #     {
    #       "type": "doctype",
    #       "name": "Training Feedback"
    #     },
    #   ]
    # },
    {
      "label": _("Expense Claims"),
      "items": [
        {
          "type": "doctype",
          "name": "Expense Claim",
          "dependencies": ["Employee"]
        },
         {
          "type": "doctype",
          "name": "Request for expence claim",
          "dependencies": ["Employee"]
        },
        {
          "type": "doctype",
          "name": "Employee Advance",
          "dependencies": ["Employee"]
        },
        {
          "type": "doctype",
          "name": "benifits",
          "dependencies": ["Employee"]
        },
      ]
    },

   {
      "label":_("Operation Monthly"),
      "icon": "fa fa-table",
      "items":[
        {
          "type": "report",
          "name": "Operations Management",
          "onboard": 1
        },
        {
          "type": "doctype",
          "name": "Operations Settings",
          "onboard": 1
        }

      ]
    }
  ]