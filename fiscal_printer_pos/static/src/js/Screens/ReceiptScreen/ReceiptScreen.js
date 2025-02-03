odoo.define('fiscal_printer.FPReceiptScreen', function (require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    const ajax = require('web.ajax')

    const FPReceiptScreen = (ReceiptScreen) => 
        class extends ReceiptScreen {
            constructor() {
                super(...arguments);
            }

            async willStart() {
                try {
                    await super.willStart();
                    if (this.currentOrder.fiscal_auto_print()) {
                        await this.printFiscalReceipt();
                    }
                } catch (e) {
                    console.error(e)
                }
            }

            async printFiscalReceipt() {
                try {
                    console.log({ 
                        as_json: this.currentOrder.export_as_JSON()
                    })
                    const { response } = await ajax.rpc("/fp3dv", {
                        as_json: this.currentOrder.export_as_JSON()
                    })
                    if (response.error) {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Error de conexion'),
                            body: this.env._t(response.message),
                        });
                    }
                } catch(e) {
                    console.log('ERROR!!!')
                    console.log(e)
                }
            }
        };


    Registries.Component.extend(ReceiptScreen, FPReceiptScreen);

    return FPReceiptScreen;
})