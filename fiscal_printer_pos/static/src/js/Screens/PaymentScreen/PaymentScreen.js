odoo.define('fiscal_printer.FPPaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const FPPaymentScreen = (PaymentScreen) => 
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
            }
            async validateOrder(isForceValidate) {
                if (!this.currentOrder.partner) {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Please select the Customer'),
                        body: this.env._t(
                            'You need to select the customer.'
                        ),
                    });
                    if (confirmed) {
                        await this.selectPartner();
                    }
                    return;
                }
                return await super.validateOrder(isForceValidate);
            }
        }

    Registries.Component.extend(PaymentScreen, FPPaymentScreen);

    return FPPaymentScreen;

})