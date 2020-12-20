# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime, timedelta


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

        {
            'fieldname': "insurance_salary",
            'label': _("Insurance Salary"),
            'fieldtype': "float",
            "width": 150
        },
        {
            'fieldname': "employee_share",
            'label': _("Employee Share"),
            'fieldtype': "float",
            "width": 150
        },

        {
            'fieldname': "company_share",
            'label': _("Company Share"),
            'fieldtype': "float",
            "width": 150
        }
        ,

        {
            'fieldname': "year",
            'label': _("Year"),
            'fieldtype': "data",
            "width": 150
        }
        ,

        {
            'fieldname': "month",
            'label': _("Month"),
            'fieldtype': "data",
            "width": 150
        }
    ]
    return columns


def getdata(filters):
    conditions = " and e.company = %(company)s"
    if  filters.get("department"):
        conditions += " and e.department = %(department)s"
    if  filters.get("employee"):
        conditions += " and e.name = %(employee)s"

    monthes_conditions = " and company = %(company)s "
    monthes_conditions += " and year = %(year)s "
    if filters.get("month"):
        monthes_conditions += " and name = %(month)s "
    payroll_monthes = frappe.db.sql("""
                select * from `tabPayroll Month` where 1 = 1 
                {monthes_conditions} 
                """.format(monthes_conditions = monthes_conditions),filters , as_dict=1)
    result = []
    for row in payroll_monthes:
        owner_percent = (frappe.db.get_single_value("Social Insurance Settings", 'owner_percent')  or 0  )/100
        employee_percent = (frappe.db.get_single_value("Social Insurance Settings", 'employee_percent' )or 0  )/100
        company_percent = (frappe.db.get_single_value("Social Insurance Settings", 'company_percent') or 0  )/100

        sql = """	
             select e.name as employee , e.employee_name, e.department ,e.designation,
       ifnull(insurance_salary,0)  as insurance_salary ,
        ifnull(is_owner,0) as is_owner ,
        case when is_owner = 1 then (ifnull( insurance_salary , 0) * {owner_percent}) else (ifnull( insurance_salary , 0) * {employee_percent})  end as employee_share ,
        (ifnull( insurance_salary , 0) * {company_percent})  as company_share
        , '{month}' as month ,
         '{year}' as year 
        from `tabEmployee Social Insurance Data`
        inner join tabEmployee e on e.name = `tabEmployee Social Insurance Data`.employee
        where `tabEmployee Social Insurance Data`.docstatus = 1 and date(`tabEmployee Social Insurance Data`.employee_strat_insurance_date) <= date('{end_date}')
        {conditions}
        				""".format( year=row.year , month = row.name, conditions=conditions, end_date=row.end_date  , company_percent =company_percent, owner_percent =owner_percent , employee_percent =employee_percent)
        data = frappe.db.sql(sql,filters,as_dict=1)
        # frappe.msgprint(str(sql))
        # frappe.msgprint(str(data))
        result.extend(data)

    return result




@frappe.whitelist()
def get_attendance_years():
    year = datetime.today().year
    year_list = [str(x) for x in range(2019, year + 2)]
    year_list.reverse()
    return "\n".join(year_list)


def calculate_Tax(row):
    total_taxable_amount = row.tax_pool
    has_disability, is_consultant = row.has_disability, row.is_consultant
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
    total_tax = total_tax * (row.total_month or 0)
    row.tax_amount = total_tax
    if row.tax_amount > row.tax_value:
        # Debit
        row.debit_tax = row.tax_amount - row.tax_value
    else:
        row.credit_tax = row.tax_value - row.tax_amount

    return row



