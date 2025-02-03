odoo.define('pos_default_customer.pos_default_customer', function(require) {
    "use strict";

    const {Order} = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    // models.load_fields("res.partner", "ced_rif")
    const FPPosOrder = (Order) => class FPPosOrder extends Order {
        constructor(obj, options) {
            super(...arguments);

            var customer = this.pos.config.default_customer_id;

            if (customer) {
                this.set_partner(this.pos.db.get_partner_by_id(customer[0]));
            }
        }
        async _processData(loadedData) {
            await super._processData(...arguments);
            console.log("*****************************")
            console.log(loadedData)

        }
        fiscal_auto_print() {
            return this.pos.config.fiscal_auto_print;
        }
        async FPPrintChanges(){
            var printers = this.pos.printers;
            const cashier = this.pos.get_cashier()
            let data = ''
            for(var i = 0; i < printers.length; i++){
                var changes = this.computeChanges(printers[i].config.product_categories_ids);
                if ( changes['new'].length > 0 || changes['cancelled'].length > 0){
                    data += (QWeb.render('OrderChangeReceipt',{changes:changes, widget:this})) 
                    + `<strong>Mesero</strong>: ${cashier.name}`
                    + '<br/><br/><br/><br/><br/><br/>';
                }
            }
            return data;
        }
    }

    Registries.Model.extend(Order, FPPosOrder);
    // var _super_order = Order.prototype;
    // models.Order = models.Order.extend({
    //     // Set default customer on pos screen
    //     initialize: function() {
    //         _super_order.initialize.apply(this, arguments);

    //         var customer = this.pos.config.default_customer_id;

    //         if (customer) {
    //             this.set_client(this.pos.db.get_partner_by_id(customer[0]));
    //         }
    //     },
    //     fiscal_auto_print: function() {
    //         return this.pos.config.fiscal_auto_print;
    //     }
    // });
});
