// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Operation Monthly Invoicing", {
  refresh: function (frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__("Create Invoice"), function () {
        frm.events.create_invoice(frm);
      });
    }
  },
  onload: function (frm) {
    frm.set_query("employee", "monthly_details_data", function (doc, cdt, cdn) {
      return {
        filters: {
          outsource: 1,
          status: "Active",
          company: doc.company,
        },
      };
    });
    frm.set_query("debit_to", function (doc, cdt, cdn) {
      return {
        filters: {
          account_type: "Receivable",
          company: doc.company,
        },
      };
    });
    frm.set_query("income_account", function (doc, cdt, cdn) {
      return {
        filters: {
          company: doc.company,
        },
      };
    });
  },

  create_invoice: function (frm) {
    let selected_rows = frm
      .get_field("monthly_details_data")
      .grid.get_selected_children();
    if (selected_rows.length == 0) {
      frappe.throw(__("please Select Rows to Invoice"));
      return;
    }
    frappe.call({
      method: "create_invoice",
      doc: frm.doc,
      args: {
        selected_rows: selected_rows,
      },
      callback: function (r) {
        frm.refresh_fields();
        frm.refresh();
      },
    });
  },

  Calculate_totals: function (frm, cdt, cdn) {
    var d = locals[cdt][cdn];

    if (!d.gross_salary) d.gross_salary = 0;
    if (!d.social_insurance) d.social_insurance = 0;
    if (!d.laptop) d.laptop = 0;
    if (!d.ohs_courses) d.ohs_courses = 0;
    if (!d.medical_insurance) d.medical_insurance = 0;
    if (!d.mobile_package) d.mobile_package = 0;
    if (!d.ohs_tools) d.ohs_tools = 0;

    d.total =
      d.gross_salary +
      d.social_insurance +
      d.laptop +
      d.ohs_courses +
      d.medical_insurance +
      d.mobile_package +
      d.ohs_tools;
    frm.events.Calculate_all_totals(frm);
  },

  Calculate_all_totals: function (frm) {
    frm.doc.total = 0;
    frm.doc.monthly_details_data.forEach(function (element) {
      frm.doc.total += element.total;
    });
    refresh_field("total");
  },
});

frappe.ui.form.on("Monthly Details", {
  employee: function (frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    if (d.employee) {
      frappe.call({
        method: "frappe.client.get",
        args: {
          doctype: "Employee",
          name: d.employee,
        },
        callback: function (r) {
          //Default Payable Account
          if (r.message) {
            if (
              !r.message.outsource ||
              r.message.status != "Active" ||
              r.message.company != frm.doc.company
            )
              d.employee = "";
            frm.refresh_fields();
          }
        },
      });
    }
  },
  gross_salary: function (frm, cdt, cdn) {
    frm.events.Calculate_totals(frm, cdt, cdn);
    frm.refresh_fields();
  },
  social_insurance: function (frm, cdt, cdn) {
    frm.events.Calculate_totals(frm, cdt, cdn);
    frm.refresh_fields();
  },
  laptop: function (frm, cdt, cdn) {
    frm.events.Calculate_totals(frm, cdt, cdn);
    frm.refresh_fields();
  },
  ohs_courses: function (frm, cdt, cdn) {
    frm.events.Calculate_totals(frm, cdt, cdn);
    frm.refresh_fields();
  },
  medical_insurance: function (frm, cdt, cdn) {
    frm.events.Calculate_totals(frm, cdt, cdn);
    frm.refresh_fields();
  },
  mobile_package: function (frm, cdt, cdn) {
    frm.events.Calculate_totals(frm, cdt, cdn);
    frm.refresh_fields();
  },
  ohs_tools: function (frm, cdt, cdn) {
    frm.events.Calculate_totals(frm, cdt, cdn);
    frm.refresh_fields();
  },
});
