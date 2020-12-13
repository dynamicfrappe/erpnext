import frappe
import datetime
def AdditionalSalaries(employee,month):
    result=frappe.db.sql("select type,amount as 'Amount' from `tabAdditional Salary` where employee='{}' and month(payroll_date)='{}'".format(employee,month),as_dict=1)
    return result
