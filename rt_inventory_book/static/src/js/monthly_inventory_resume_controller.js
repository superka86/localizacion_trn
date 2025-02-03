odoo.define('tdv_inventory_book.MonthlyInventoryReportController', function (require) {
    'use strict';

    var ListView = require('web.ListView');
    var ListController = require('web.ListController');
    var viewRegistry = require('web.view_registry');

    var MonthlyInventoryReportListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: ListController.extend({
                buttons_template: 'MonthlyInventoryReport.Buttons',
                init: function (...args) {
                    return this._super.apply(this, arguments);
                },
                renderButtons: function ($node) {
                    this._super.apply(this, arguments);
                    this.$buttons.on('click', '.o_generate_report', this._onOpenWizard.bind(this));
                },
                _onOpenWizard: function () {
                    this.do_action({
                        res_model: 'tdv.monthly.resume.wizard',
                        views: [[false, 'form']],
                        target: 'new',
                        type: 'ir.actions.act_window'
                    });
                }
            }),
        }),
    });
    viewRegistry.add('monthly_inventory_resume', MonthlyInventoryReportListView)

    return MonthlyInventoryReportListView;
})