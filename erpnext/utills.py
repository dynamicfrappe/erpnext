import frappe
import datetime
from frappe.utils import date_diff
def AdditionalSalaries(employee,month):
    result=frappe.db.sql("select type,amount as 'Amount' from `tabAdditional Salary` where employee='{}' and month(payroll_date)='{}'".format(employee,month),as_dict=1)
    return result








def get_leave_with_type_leave_without_pay(employee , strat,end):
	count = frappe.db.sql(""" SELECT (total_leave_days) FROM `tabLeave Application` WHERE employee = '%s' 
		and from_date >= '%s' and to_date <= '%s'"""%(employee,strat,end) )



def check_leave_without_pay_in_deference_monthes(employee , strat,end):
	#if application In the end of the month 
	count = frappe.db.sql(""" SELECT (total_leave_days),  end_date FROM `tabLeave Application` WHERE employee = '%s' 
		and from_date >= '%s' and to_date >= '%s' """%(employee,strat,end) )
	count_date =  date_diff(end , count[0][1] )
	return(count_date)




