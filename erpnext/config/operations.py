from __future__ import unicode_literals
import frappe
from frappe import _


def get_data():
  return [
    {
      "label": _("Sales Pipeline"),
      "icon": "fa fa-star",
      "items": [
        {
          "type": "doctype",
          "name": "Lead",
          "description": _("Database of potential customers."),
          "onboard": 1,
        },
        
        
      ]
    },
    {
      "label": _("Reports"),
      "icon": "fa fa-list",
      "items": [
        {
          "type": "report",
          "is_query_report": True,
          "name": "Lead Details",
          "doctype": "Lead",
          "onboard": 1,
        },
       
      ]
    },
    {
      "label": _("Settings"),
      "icon": "fa fa-cog",
      "items": [
        {
          "type": "doctype",
          "label": _("Customer Group"),
          "name": "Customer Group",
          "icon": "fa fa-sitemap",
          "link": "Tree/Customer Group",
          "description": _("Manage Customer Group Tree."),
          "onboard": 1,
        },
       
      ]
    },
   
  ]
