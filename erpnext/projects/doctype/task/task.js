// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.projects");

frappe.ui.form.on("Task", {
	setup: function (frm) {
		frm.set_query("project", function () {
			return {
				query: "erpnext.projects.doctype.task.task.get_project"
			}
		});

		frm.make_methods = {
			'Timesheet': () => frappe.model.open_mapped_doc({
				method: 'erpnext.projects.doctype.task.task.make_timesheet',
				frm: frm
			})
		}
	},

	onload: function (frm) {
		frm.set_query("task", "depends_on", function () {
			let filters = {
				name: ["!=", frm.doc.name]
			};
			if (frm.doc.project) filters["project"] = frm.doc.project;
			return {
				filters: filters
			};
		})
	},

	refresh: function (frm) {
		frm.set_query("parent_task", { "is_group": 1 });
	},

	is_group: function (frm) {
		frappe.call({
			method: "erpnext.projects.doctype.task.task.check_if_child_exists",
			args: {
				name: frm.doc.name
			},
			callback: function (r) {
				if (r.message.length > 0) {
					frappe.msgprint(__(`Cannot convert it to non-group. The following child Tasks exist: ${r.message.join(", ")}.`));
					frm.reload_doc();
				}
			}
		})
	},
	assigned:function(frm){

	if(frm.doc.project){
		var project = frm.doc.project
		frm.set_query("assigned_to" , function(frm) {
			return {
				query:"erpnext.projects.doctype.task.task.get_project_employee",
				filters: {
					"project" : project

				}
			}
		})
	}

	},


project:function(frm){

	if(frm.doc.assigned){
		var project = frm.doc.project
		frm.set_query("assigned_to" , function(frm) {
			return {
				query:"erpnext.projects.doctype.task.task.get_project_employee",
				filters: {
					"project" : project

				}
			}
		})
	}

	},
	validate: function (frm) {
		frm.doc.project && frappe.model.remove_from_locals("Project",
			frm.doc.project);
	}
});
