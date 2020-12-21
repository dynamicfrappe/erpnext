# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
 
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import pdfkit 
style_method= u""" 
	<style>
	    *{
	      font-family: sans-serif;

	    }
	.flex-container {
	  display: flex;
	}

	.flex-container > div {
	  margin-right: 100px;
	  padding: 2px;
	  
	}

	table, td, th {
	  border: 1px solid black;
	  text-align: center;
	}

	table {
	  width: 100%;
	  border-collapse: collapse;
	}
	</style> """


header = u""" 

<head> <meta charset="utf-8"> </head>
<div id="dleft" style="width:100%;margin-top: 0px;padding: 0px" dir="rtl">
		    <div style="float:right;">
		        <p style="float:right;margin-top: 1px">الهيئه القوميه للتامين الاجتماعي</p><br>
		     
		        <p style="float:right;margin-top: 1px">منطقه/{{ doc.region}}</p><br>
		        <p style="float:right;margin-right: 1px;margin-top: -7px">مكتب/{{ doc.insurance_office}}</p>
		    </div>
		    
		    <div style="float:left;margin-top: 1px">
		        <p>نموزج رقم (9) قرار وزاري رقم (00) لسنه 0000</p><br>
		        <p> رقم المنشاة: <span style="border: 1px black solid;padding: 2px;padding-right:20px;padding-left: 20px ">{{doc.insurance_number}}</span></p>
		    </div>
		</div>
		 <br>
		 <br>
		 <br>
		 



		"""
content = u""" 
<div style="width: 100%" dir="rtl">
   <div>
    <p style="display: inline;margin-right: 20px">اسم المنشاه/ {{ doc.organization_name }}</p>
    <p style="display: inline;margin-right: 100px">المالك /المدير المسئول:{{ doc.responsible_owner }}</p>
    <p style="display: inline;margin-right: 100px">الشكل القانوني للمنشاة:{{ doc.organizationlegalform}}</p>
   </div>

    <div class="flex-container" dir="rtl" >
  <div style="margin-right: 10px">عنوان المنشاة/{{doc.address}}</div>
  <div style="margin-right: 100px;"> الشياخه/القريه:---------</div>
  <div style="margin-right: 100px;">القسم/المركز:------------</div>

</div> 

 <div class="flex-container" dir="rtl" >
  <div style="margin-right: 10px">نسبه تامين المرض:------------</div>
  <div> تاريخ بدا النسبه: &nbsp;&nbsp; / &nbsp;&nbsp; / </div>
  <div> نسبه تامين الاصابه:------------</div>
   <div>تاريخ بدا النسبه : &nbsp;&nbsp; /&nbsp;&nbsp;  / </div>
</div> 

 <div class="flex-container" dir="rtl" >
  <div style="margin-right: 10px">تاريخ التوقف /الاستمرار : &nbsp;&nbsp;/&nbsp;&nbsp;/</div>
  <div style="margin-right: 5px;"> سبب التوقف :-------------</div>
   <div style="margin-right: 5px;">بدا النشاط :--------------</div>
   <div>رقم التسجيل الضريبي للمنشاة:--------------</div>
</div> 

</div>"""
class InsuranceOrganization(Document):
	def get_print(self):
		file_name = "test_beshoy.html"
		file_ = open(file_name , 'w')
		file_.write(str(style_method) + str(header) + str(content))
		file_.close()
		test = str(style_method) + str(header) + str(content)
		options = {
 'page-size': 'A4',
 'orientation':'landscape',
 'margin-top': '0.75in',
 'margin-right': '0.75in',
 'margin-bottom': '0.75in',
 'margin-left': '0.75in',
 'encoding': "UTF-8",
 'no-outline': None,

 } 
		pdfkit.from_string(test , 'out.pdf' ,options=options) 
		
		return (str(style_method) + str(header) + str(content))





@frappe.whitelist()
def get_jinja_data(doc):
	return frappe.db.sql("""select  ROW_NUMBER() OVER(ORDER BY name ASC) AS count , `tabEmployee Social Insurance Data`.* from `tabEmployee Social Insurance Data` where employee_strat_insurance_date < DATE_SUB(CURDATE(),INTERVAL 1 YEAR)  order by insurancenumber Asc""",as_dict=True)










