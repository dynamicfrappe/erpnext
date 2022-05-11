// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shift Assignment", {
  refresh: function (frm) {
    if (frm.doc.docstatus == 1) {
      frm
        .add_custom_button(__("Create Inner Shift"), function () {
          frm.events.create_inner_shift(frm);
        })
        .addClass("btn-primary");
    }
  },
  create_inner_shift: function (frm) {
    var d = new frappe.ui.Dialog({
      title: __("Post for Employees"),
      fields: [
        {
          fieldname: "shift",
          fieldtype: "Link",
          options: "Shift Type",
          reqd: 1,
          label: __("Shift Type"),
        },
        {
          fieldname: "from_date",
          fieldtype: "Date",
          label: __("Start Date"),
          reqd: 1,
        },
        {
          fieldname: "to_date",
          fieldtype: "Date",
          label: __("End Date"),
          reqd: 1,
        },
      ],
      primary_action: function () {
        var data = d.get_values();
        data.doc = frm.doc.name;
        frappe.call({
          method:
            "dynamicerp.dynamic_hr.doctype.shift_assignment.shift_assignment.create_inner_shift_assignment",
          args: data,
          freeze: true,
          callback: function (r) {
            d.hide();
          },
        });
      },
      primary_action_label: __("Create"),
    });

    d.show();
  },
});
