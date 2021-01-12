# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import sys
import os
from zk import ZK, const
from datetime import datetime
from datetime import timedelta

class Device(Document):
	def get_attendance(self):
		# frappe.msgprint(os.path)
		doc = self
		device_name = self.name1
		if doc:
			if doc.is_active:
				# create ZK instance
				last_log_date = None
				last_connection = datetime.now()
				last_error = None
				conn = None
				miniutes_period = 5
				# device = ZK('192.168.1.201', port=4370, timeout=5, password=0, force_udp=False, ommit_ping=False)
				device = ZK(ip=str(doc.ip), port=int(doc.port), timeout=5, password=int(doc.password), force_udp=False,
							ommit_ping=False)

				try:
					# connect to device
					conn = device.connect()
					# disable device, this method ensures no activity on the device while the process is run
					# conn.disable_device()
					# another commands will be here!
					# Example: Get All records
					attendances = device.get_attendance()

					records = []
					data_dict = list(map(lambda x: x.__dict__, attendances))
					if doc.last_log_date:
						records = [r for r in data_dict if
								   r['timestamp'] > datetime.strptime(doc.last_log_date, '%Y-%m-%d %H:%M:%S')]
					else:
						records = data_dict
					records_groupby_user_id = sorted(records, key=lambda i: int(i['user_id']))
					if records_groupby_user_id:
						old_user = ''
						old_timestamp = None
						user = '1'
						total = len(records_groupby_user_id)
						count = 1
						for record in records_groupby_user_id:
							frappe.publish_realtime('update_progress', {
								'progress': count,
								'total': total
							})
							count += 1
							user = record['user_id']
							if user != old_user:
								employee = frappe.db.get_value('Employee', {'attendance_device_id': record['user_id']},
															   ['name'], as_dict=1)
							if old_timestamp:
								period = record['timestamp'] - old_timestamp
								if user == old_user and period <= timedelta(minutes=miniutes_period):
									# frappe.msgprint("Continue" + str(record['timestamp']))
									continue

							if employee:

								log = frappe.get_doc({
									'doctype': 'Device Log',
									'employee': employee.name,
									'enroll_no': record['user_id'],
									'log_time': record['timestamp'],
									'log_type': record['status'],
									'punch': record['punch'],
									'parent': device_name,
									'parenttype': 'Device',
									'parentfield': 'device_logs',
									'device': device_name,
									'log_date': record['timestamp'].date()
								})
								log.save()
								# frappe.msgprint("log.inseet employee" )

								old_user = user
								old_timestamp = record['timestamp']
							else:
								log = frappe.get_doc({
									'doctype': 'Device Log',
									'enroll_no': record['user_id'],
									'log_time': record['timestamp'],
									'log_type': record['status'],
									'punch': record['punch'],
									'parent': device_name,
									'parenttype': 'Device',
									'parentfield': 'device_logs',
									'device': device_name,
									'log_date': record['timestamp'].date()
								})
								log.save()
								frappe.db.commit()
								# frappe.msgprint("log.inseet")


								old_user = user
								old_timestamp = record['timestamp']

						last = records[-1]
						last_log_date = last['timestamp']
					else:
						frappe.msgprint(_("No Data Found After {}".format(doc.last_log_date)) , indicator='blue')

					# Test Voice: Say Thank You
					# conn.test_voice()
				# re-enable device after all commands already executed
				# conn.enable_device()
				except Exception as e:
					frappe.msgprint("Process terminate : {}".format(e))
					last_error = e
				finally:
					if conn:
						conn.disconnect()
					# conn.enable_device()
					try:
						# document = frappe.get_doc('Device', device_name)
						if last_log_date:
							self.last_log_date = last_log_date
						if last_connection:
							self.last_connection = last_connection
						if last_error:
							self.last_error = last_error
						self.save()
					except:
						pass


@frappe.whitelist()
def map_employees():
	frappe.db.sql("""update `tabDevice Log` log set employee = (select name from `tabEmployee` where attendance_device_id = log.enroll_no)
	where employee is null """)

