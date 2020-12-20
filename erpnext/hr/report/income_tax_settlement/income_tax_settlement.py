# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime,timedelta


def execute(filters=None):
    columns, data = [], []
    columns = getColumns(filters)
    data = getdata(filters)
    return columns, data


def getColumns(filters):
    columns = [
        {
            'fieldname': "employee",
            'label': _("Employee"),
            'fieldtype': "Link",
            'options': "Employee",
            "width": 100
        },
        {
            'fieldname': "employee_name",
            'label': _("Name"),
            'fieldtype': "Data",
            "width": 150
        },
        {
            'fieldname': "designation",
            'label': _("Designation"),
            'fieldtype': "Data",
            "width": 100
        },
        {
            'fieldname': "department",
            'label': _("Department"),
            'fieldtype': "Department",
            "width": 100
        },
        # {
        #     'fieldname': "is_consultant",
        #     'label': _("Is Conultant"),
        #     'fieldtype': "check",
        #     "width": 100
        # },
        # {
        #     'fieldname': "has_disability",
        #     'label': _("Has Disability"),
        #     'fieldtype': "check",
        #     "width": 100
        # },
        {
            'fieldname': "tax_pool",
            'label': _("Total Net Income"),
            'fieldtype': "float",
            "width": 150
        },
        {
            'fieldname': "tax_value",
            'label': _("Total Paid Tax"),
            'fieldtype': "float",
            "width": 150
        },

        {
            'fieldname': "tax_amount",
            'label': _("Actual Tax Amount"),
            'fieldtype': "float",
            "width": 150
        },

        {
            'fieldname': "total_month",
            'label': _("Total Working Monthes"),
            'fieldtype': "float",
            "width": 175
        },
        {
            'fieldname': "credit_tax",
            'label': _("Employee Credit Tax"),
            'fieldtype': "float",
            "width": 150
        },
        {
            'fieldname': "debit_tax",
            'label': _("Employee Debit Tax"),
            'fieldtype': "float",
            "width": 150
        }
    ]
    return columns


def getdata(filters):
    conditions = ""
    if filters.get("company"):
        conditions = " and  E.`company` =%(company)s"

        if filters.get("employee"):
            conditions += " and E.name = %(employee)s"
        if filters.get("year"):
            conditions += " and month.year  = %(year)s"
        if filters.get("department"):
            conditions += " and E.department = %(department)s"
        sql = """
					SELECT
                           slip.employee,
                           E.employee_name,
                           E.designation,
                           E.department,
                           ifnull(E.is_consultant , 0) as is_consultant,
                           ifnull(E.has_disability , 0) as has_disability,
                           SUM(slip.tax_pool) as tax_pool,
                           SUM(slip.tax_value) as tax_value,
                           count(distinct slip.month) as total_month ,
                           0 as tax_amount,
                           0 as credit_tax,
                           0 as debit_tax
                    
                    from `tabMonthly Salary Slip` slip
                        Inner join tabEmployee E
                            on E.name = slip.employee
                        Inner join `tabPayroll Month` month
                            on month.name = slip.month
                    where slip.docstatus = 1
                    {conditions}
                    group by slip.employee


			""".format(conditions=conditions)
        # frappe.msgprint(str(sql))
        results = frappe.db.sql(sql, filters, as_dict=1)
        return 	 [calculate_Tax(row = row ) for row in results]



@frappe.whitelist()
def get_attendance_years():
        year = datetime.today().year
        year_list = [str(x) for x in range(2019 ,year+2)]
        year_list.reverse()
        return "\n".join(year_list)


def calculate_Tax(row):
    total_taxable_amount  = row.tax_pool
    has_disability, is_consultant = row.has_disability , row.is_consultant
    total_tax = 0
    hr_settings = frappe.get_single("HR Settings")
    Tax_Sc = hr_settings.income_tax_salary_component or None
    personal_exemption_value = hr_settings.personal_exemption_value or 0
    disability_exemption_value = hr_settings.disability_exemption_value or 0

    if is_consultant:
        consultant_percent = hr_settings.consultant_percent
        total_tax = total_taxable_amount * consultant_percent / 100
    else:

        if has_disability:
            personal_exemption_value += disability_exemption_value

        tax_layers = hr_settings.tax_layers or None

        if Tax_Sc and tax_layers:
            total_taxable_amount = total_taxable_amount / (row.total_month or 1)
            if total_taxable_amount and total_taxable_amount > 0:
                total_taxable_amount_yearly = (total_taxable_amount * 12) - personal_exemption_value
                total_tax = 0
                perviuos_limit = 0
                total_taxable_amount_yearly = float(int(total_taxable_amount_yearly / 10) * 10)
                for i in tax_layers:
                    if i.limit < total_taxable_amount_yearly:
                        total_tax += (i.limit - perviuos_limit) * (i.tax_percent / 100)
                        perviuos_limit = i.limit


                    else:
                        total_taxable_amount_yearly -= perviuos_limit
                        total_tax += total_taxable_amount_yearly * (i.tax_percent / 100)
                        break;
                total_tax = total_tax / 12


    if total_tax < 0:
        total_tax = 0
    total_tax =  total_tax * (row.total_month or 0)
    row.tax_amount = total_tax
    if row.tax_amount > row.tax_value :
        # Debit
        row.debit_tax = row.tax_amount - row.tax_value
    else:
        row.credit_tax = row.tax_value - row.tax_amount

    return row



