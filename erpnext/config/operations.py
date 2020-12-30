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
          "name": "Assets Return",
          "onboard": 1
        },
        {
          "type": "doctype",
          "name": "Custody request",
          "onboard": 1
        },
        {
                                        "type": "report",
                                        "name": "Assts Movement Report",
          "label" : "Custudy Movement",
                                        "doctype": "Asset",
                                        "is_query_report": True,
                                },

      ]
    },
    {
      "label": _("Training"),
      "items": [
        {
          "type": "doctype",
          "name": "Training Program"
        },
        {
          "type": "doctype",
          "name": "Training Event"
        },
        {
          "type": "doctype",
          "name": "Training Result"
        },
        {
          "type": "doctype",
          "name": "Training Feedback"
        },
      ]
    },
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
      "label": _("Projects"),
      "icon": "fa fa-star",
      "items": [
        {
          "type": "doctype",
          "name": "Project",
          "description": _("Project master."),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Task",
          "route": "#List/Task",
          "description": _("Project activity / task."),
          "onboard": 1,
        },
        {
          "type": "report",
          "route": "#List/Task/Gantt",
          "doctype": "Task",
          "name": "Gantt Chart",
          "description": _("Gantt chart of all tasks."),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Project Template",
          "description": _("Make project from a template."),
        },
        {
          "type": "doctype",
          "name": "Project Type",
          "description": _("Define Project type."),
        },
        {
          "type": "doctype",
          "name": "Project Update",
          "description": _("Project Update."),
          "dependencies": ["Project"],
        },
       
      ]
    },
   {
      "label":_("Operation Monthly"),
      "icon": "fa fa-table",
      "items":[
        {
          "type": "doctype",
          "name": "Operation Monthly Invoicing",
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
