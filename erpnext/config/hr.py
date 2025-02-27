from __future__ import unicode_literals
from frappe import _

def get_data():

    return [
        {
            "label": _("Employee"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Employee",
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Employment Type",
                },
                {
                    "type": "doctype",
                    "name": "Branch",
                },
                {
                    "type": "doctype",
                    "name": "Department",
                },
                {
                    "type": "doctype",
                    "name": "Designation",
                },
                {
                    "type": "doctype",
                    "name": "Employee Grade",
                },
                {
                    "type": "doctype",
                    "name": "Employee Contract",
                },
                {
                    "type": "doctype",
                    "name": "Employee Contract Type",
                },
                {
                    "type": "doctype",
                    "name": "Employee Group",
                    "dependencies": ["Employee"]
                },
                {
                    "type": "doctype",
                    "name": "Employee Health Insurance"
                },
                {
                    "type": "doctype",
                    "name": "Employee Document"
                },
                {
                    "type": "doctype",
                    "name": "Employee document type"
                },
                {
                    "label": "Document Designation Templates",
                    "type": "doctype",

                    "name": "Employee Designation Templates"
                },
                {
                    "type": "doctype",
                    "name": "Employee Documents Notification"
                },

            ]
        },
        {
            "label": _("Attendance"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Employee Attendance Tool",
                    "hide_count": True,
                    "onboard": 1,
                    "dependencies": ["Employee"]
                },
                {
                    "type": "doctype",
                    "name": "Attendance Rule"
                },
                {
                    "type": "doctype",
                    "name": "Attendance",
                    "onboard": 1,
                    "dependencies": ["Employee"]
                },
                {
                    "type": "doctype",
                    "name": "Attendance Request",
                    "dependencies": ["Employee"]
                },
                {
                    "type": "doctype",
                    "name": "Upload Attendance",
                    "hide_count": True,
                    "dependencies": ["Employee"]
                },
                {
                    "type": "doctype",
                    "name": "Employee Checkin",
                    "hide_count": True,
                    "dependencies": ["Employee"]
                },
                {
                    "type": "doctype",
                    "name": "Device",
                    "hide_count": True,
                    "dependencies": ["Employee"]
                },
                {
                    "type": "doctype",
                    "name": "Device Log",
                    "hide_count": True,
                    "dependencies": ["Device"]
                },
                {
                    "type": "doctype",
                    "name": "Employee Attendance Logs",
                    "hide_count": True,
                    "dependencies": ["Device Log"]
                },
                {
                    "type": "doctype",
                    "name": "Attendance Calculation",
                    "hide_count": True,
                    "dependencies": ["Device Log"]
                },
                {
                    "label": "Monthly Attendance Sheet Details",
                    "type": "report",
                    "is_query_report": True,
                    "name": "Attendance Sheet",
                    "doctype": "Employee Attendance Logs"
                },
                {
                    "label": "Monthly Attendance Sheet",
                    "type": "report",
                    "is_query_report": True,
                    "name": "Monthly Attendance Sheet",
                    "doctype": "Attendance"
                },
            ]
        },
        {
            "label": _("Business Trips And Mission"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Business Trip"
                },
                {
                    "type": "doctype",
                    "name": "Mission",
                    "dependencies": ["Mission Destination"]
                },
                {
                    "type": "doctype",
                    "name": "Mission Destination"
                },
                {
                    "type": "doctype",
                    "name": "Permission",
                    "dependencies": ["Permission Type"]

                },
                {
                    "type": "doctype",
                    "name": "Permission Type"
                }

            ]
        }
        # ,
        # {
        #  "label":_("New PayRoll "),
        #  "items": [
        #  		{
        # 			"type": "doctype",
        # 			"name": "Payroll Month"
        #
        # 		},
        # 		 {
        # 			"type": "doctype",
        # 			"name": "Multi Payroll"
        # 		},
        # 		{
        # 			"type": "doctype",
        # 			"name": "Salary Structure Type",
        # 		},
        #
        # 		{
        # 			"type": "doctype",
        # 			"name": "Multi salary structure"
        # 		},
        # 		{
        # 			"type": "doctype",
        # 			"name": "Monthly Salary Slip",
        # 			"dependencies": ["Permission Type"]
        #
        # 		},
        #
        #
        #  ]
        # }
        ,
        {
            "label": _("Employee Penalties"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Employee Penality"
                },
                {
                    "type": "doctype",
                    "name": "Penality Type"
                },
                {
                    "type": "doctype",
                    "name": "Warnings",
                    "dependencies": ["Warnings Types"]
                },
                {
                    "type": "doctype",
                    "name": "Warnings Types"
                },
                {
                    "type": "doctype",
                    "name": "Violations",
                    "dependencies": ["Penality Type"]

                }

            ]
        }
        ,
        {
            "label": _("Leaves"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Leave Application",
                    "dependencies": ["Employee"]
                },
                {
                    "type": "doctype",
                    "name": "Leave Allocation",
                    "dependencies": ["Employee"]
                },
                {
                    "type": "doctype",
                    "name": "Leave Policy",
                    "dependencies": ["Leave Type"]
                },
                {
                    "type": "doctype",
                    "name": "Leave Period",
                    "dependencies": ["Employee"]
                },
                {
                    "type": "doctype",
                    "name": "Leave Type",
                },
                {
                    "type": "doctype",
                    "name": "Holiday List",
                },
                {
                    "type": "doctype",
                    "name": "Compensatory Leave Request",
                    "dependencies": ["Employee"]
                },
                {
                    "type": "doctype",
                    "name": "Leave Encashment",
                    "dependencies": ["Employee"]
                },
                {
                    "type": "doctype",
                    "name": "Leave Block List",
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Employee Leave Balance",
                    "doctype": "Leave Application"
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Leave Ledger Entry",
                    "doctype": "Leave Ledger Entry"
                },
            ]
        },
        # {
        #     "label": _("Payroll"),
        #     "items": [
        #         {
        #             "type": "doctype",
        #             "name": "Salary Structure",
        #             "onboard": 1,
        #         }, {
        #             "type": "doctype",
        #             "name": "Salary Structure Type",
        #             "onboard": 1,
        #         },
        #         {
        #             "type": "doctype",
        #             "name": "Multi salary structure",
        #             "onboard": 1,
        #             "dependencies": ["Salary Structure", "Employee", "Salary Structure Type"],
        #         },
        #         {
        #             "type": "doctype",
        #             "name": "Multi Payroll",
        #             "onboard": 1,
        #         },
        #         {
        #             "type": "doctype",
        #             "name": "Monthly Salary Slip",
        #             "onboard": 1,
        #         },
        #         {
        #             "type": "doctype",
        #             "name": "Payroll Month",
        #         },
        #         # {
        #         # 	"type": "doctype",
        #         # 	"name": "Income Tax Slab",
        #         # },
        #         {
        #             "type": "doctype",
        #             "name": "Salary Component",
        #         },
        #         {
        #             "type": "doctype",
        #             "name": "Additional Salary",
        #         },
        #         # {
        #         # 	"type": "doctype",
        #         # 	"name": "Retention Bonus",
        #         # 	"dependencies": ["Employee"]
        #         # },
        #         # {
        #         # 	"type": "doctype",
        #         # 	"name": "Employee Incentive",
        #         # 	"dependencies": ["Employee"]
        #         # },
        #         # {
        #         # 	"type": "report",
        #         # 	"is_query_report": True,
        #         # 	"name": "Salary Register",
        #         # 	"doctype": "Salary Slip"
        #         # },
        #     ]
        # },
        # {
        #     "label": _("Employee Benefits"),
        #     "items": [
        #         {
        #             "type": "doctype",
        #             "name": "Employee Tax Exemption Declaration",
        #             "dependencies": ["Employee"]
        #         },
        #         {
        #             "type": "doctype",
        #             "name": "Employee Tax Exemption Proof Submission",
        #             "dependencies": ["Employee"]
        #         },
        #         {
        #             "type": "doctype",
        #             "name": "Employee Other Income",
        #         },
        #         {
        #             "type": "doctype",
        #             "name": "Employee Benefit Application",
        #             "dependencies": ["Employee"]
        #         },
        #         {
        #             "type": "doctype",
        #             "name": "Employee Benefit Claim",
        #             "dependencies": ["Employee"]
        #         },
        #         {
        #             "type": "doctype",
        #             "name": "Employee Tax Exemption Category",
        #             "dependencies": ["Employee"]
        #         },
        #         {
        #             "type": "doctype",
        #             "name": "Employee Tax Exemption Sub Category",
        #             "dependencies": ["Employee"]
        #         },
        #     ]
        # },
        {
            "label": _("Employee Lifecycle"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Employee Onboarding",
                    "dependencies": ["Job Applicant"],
                },
                {
                    "type": "doctype",
                    "name": "Employee Skill Map",
                    "dependencies": ["Employee"],
                },
                {
                    "type": "doctype",
                    "name": "Employee Promotion",
                    "dependencies": ["Employee"],
                },
                {
                    "type": "doctype",
                    "name": "Employee Transfer",
                    "dependencies": ["Employee"],
                },
                {
                    "type": "doctype",
                    "name": "Employee Separation",
                    "dependencies": ["Employee"],
                },
                {
                    "type": "doctype",
                    "name": "Employee Onboarding Template",
                    "dependencies": ["Employee"]
                },
                {
                    "type": "doctype",
                    "name": "Employee Separation Template",
                    "dependencies": ["Employee"]
                },
            ]
        },
        {
            "label": _("Recruitment"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Job Opening",
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Job Applicant",
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Job Offer",
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Staffing Plan",
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
            "label": _("Performance"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Appraisal",
                },
                {
                    "type": "doctype",
                    "name": "Appraisal Template",
                },
                {
                    "type": "doctype",
                    "name": "Energy Point Rule",
                },
                {
                    "type": "doctype",
                    "name": "Energy Point Log",
                },
                {
                    "type": "link",
                    "doctype": "Energy Point Log",
                    "label": _("Energy Point Leaderboard"),
                    "route": "#social/users"
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
                    "name": "Employee Advance",
                    "dependencies": ["Employee"]
                },
            ]
        },
        {
            "label": _("Loans"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Loan Application",
                    "dependencies": ["Employee"]
                },
                {
                    "type": "doctype",
                    "name": "Loan"
                },
                {
                    "type": "doctype",
                    "name": "Loan Type",
                },
            ]
        },
        {
            "label": _("Shift Management"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Shift Type",
                },
                {
                    "type": "doctype",
                    "name": "Shift Request",
                },
                {
                    "type": "doctype",
                    "name": "Shift Assignment",
                },
            ]
        },
        {
            "label": _("Social Insurance"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Insurance Office",
                },
                {
                    "type": "doctype",
                    "name": "Insurance Organization",
                },
                {
                    "type": "doctype",
                    "name": "Job insurance codes",
                },
                {
                    "type": "doctype",
                    "name": "Employee Social Insurance Data",
                },
                {
                    "type": "doctype",
                    "name": "Social Insurance Settings",
                },
                {
                    "type": "doctype",
                    "name": "Government",
                },
            ]
        },
        {
            "label": _("Medical Insurance"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Medical Insurance Document",
                },
                {
                    "type": "doctype",
                    "name": "Employee Medical Insurance Document",
                },

            ]
        },
        {
            "label": _("Fleet Management"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Vehicle"
                },
                {
                    "type": "doctype",
                    "name": "Vehicle Log"
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Vehicle Expenses",
                    "doctype": "Vehicle"
                },
            ]
        },
        {
            "label": _("Settings"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "HR Settings",
                },
                {
                    "type": "doctype",
                    "name": "Medical Insurance Document",
                },
                {
                    "type": "doctype",
                    "name": "Daily Work Summary Group"
                },
                {
                    "type": "page",
                    "name": "team-updates",
                    "label": _("Team Updates")
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
                    "name": "Employee Birthday",
                    "doctype": "Employee"
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Employees working on a holiday",
                    "doctype": "Employee"
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Department Analytics",
                    "doctype": "Employee"
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Employee Documents Report",
                    "doctype": "Employee Document"
                }, {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Income Tax Settlement"
                }, {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Social Insurance Value",
                    "doctype": "Employee Social Insurance Data"
                }
            ]
        },
    ]

