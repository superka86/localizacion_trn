odoo.define("fiscal_printer_pos.PartnerDetailsEdit", function (require) {
    "use strict";

    const PartnerDetailsEdit = require("point_of_sale.PartnerDetailsEdit");
    const Registries = require("point_of_sale.Registries");

    const { useState } = owl;


    const FPPartnerDetailsEdit = (PartnerDetailsEdit) => class extends PartnerDetailsEdit {
        constructor() {
            super(...arguments)
        }
        setup() {
            super.setup()
            const partner = this.props.partner;
            console.log(partner)
            console.log(this.changes)
            this.changes = useState({
                ...this.changes,
                ced_rif: partner.ced_rif || ""
            })
            console.log(this.changes)
        }
    };

    Registries.Component.extend(PartnerDetailsEdit, FPPartnerDetailsEdit);
    return FPPartnerDetailsEdit;
})