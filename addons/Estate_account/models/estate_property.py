from odoo import models
from odoo import Command


class EstateProperty(models.Model):
    _inherit = "estate.test"

    def action_sold(self):
        res = super().action_sold()

        for record in self:
            # record.buyer_id можно вглубь заходить
            # record.buyer_id.id возвращает id
            self.env["account.move"].create({
                "partner_id": record.buyer_id.id,
                "move_type": "out_invoice",
                'invoice_line_ids': [
                    Command.create({
                        "name": record.name,
                        "quantity": 1.0,
                        "price_unit": 0.06 * record.selling_price
                    }),
                    Command.create({
                        "name": "Administrative fees",
                        "quantity": 1.0,
                        "price_unit": 100.0
                    }),
                ]
            })
        return res