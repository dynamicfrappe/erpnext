// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings["Purchase Invoice"] = {
  add_fields: [
    "supplier",
    "supplier_name",
    "base_grand_total",
    "outstanding_amount",
    "due_date",
    "company",
    "currency",
    "is_return",
    "release_date",
    "on_hold",
    "Created_since",
  ],
  onload: function (doc) {
    // triggers once before the list is loaded
    //  frappe.call({
    //       method: "erpnext.accounts.doctype.purchase_invoice.purchase_invoice.update_created_since",
    //       args :{
    //       },callback(r){
    //
    //       }
    //   });
  },
  prepare_data: function () {},
  refresh: function (doclist) {
    // doclist.data.forEach((a)=>{
    // 	a.Created_since = 150;
    // });
  },
  get_indicator: function (doc) {
    doc.Created_since = "150";
    if (
      flt(doc.outstanding_amount) <= 0 &&
      doc.docstatus == 1 &&
      doc.status == "Debit Note Issued"
    ) {
      return [__("Debit Note Issued"), "darkgrey", "outstanding_amount,<=,0"];
    } else if (flt(doc.outstanding_amount) > 0 && doc.docstatus == 1) {
      if (cint(doc.on_hold) && !doc.release_date) {
        return [__("On Hold"), "darkgrey"];
      } else if (
        cint(doc.on_hold) &&
        doc.release_date &&
        frappe.datetime.get_diff(doc.release_date, frappe.datetime.nowdate()) >
          0
      ) {
        return [__("Temporarily on Hold"), "darkgrey"];
      } else if (frappe.datetime.get_diff(doc.due_date) < 0) {
        return [
          __("Overdue"),
          "red",
          "outstanding_amount,>,0|due_date,<,Today",
        ];
      } else {
        return [
          __("Unpaid"),
          "orange",
          "outstanding_amount,>,0|due_date,>=,Today",
        ];
      }
    } else if (cint(doc.is_return)) {
      return [__("Return"), "darkgrey", "is_return,=,Yes"];
    } else if (flt(doc.outstanding_amount) == 0 && doc.docstatus == 1) {
      return [__("Paid"), "green", "outstanding_amount,=,0"];
    }
  },
};
