from odoo import api, fields, models, exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class Estate_property_offer(models.Model):
    _name = "estate.property.offer"
    _description = "estate property offer"

    _sql_constraints = [('positive_price', 'CHECK (price > 0)',
                         'Offer price should be strictly positive')]
    _order = "price desc"

    price = fields.Float(string='Price')
    status = fields.Selection(string='Status',
                              selection=[("accepted", "Accepted"), ("refused", "Refused")],
                              help="Type is used to separate Accepted, Refused", copy=False)
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.test", required=True)
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)

    validity = fields.Integer(string="Validity(days)",
                              compute="_compute_validity", inverse="_inverse_validity", default=7)
    date_deadline = fields.Date(string="Deadline", default=lambda self: fields.Date.today() + relativedelta(days=7))

    @api.model
    def create(self, vals):
        best_price_prop = self.env['estate.test'].browse(vals['property_id']).best_price
        if best_price_prop != 0 and best_price_prop > vals['price']:
            raise UserError("The offer must be higher than %f" % best_price_prop)
        self.env['estate.test'].browse(vals['property_id']).set_offer_received()
        return super(Estate_property_offer, self).create(vals)

    @api.depends("create_date", "date_deadline")  # Вход
    def _compute_validity(self):
        for record in self:
            if not record.create_date and record.date_deadline:
                record.validity = (record.date_deadline - fields.Date.today()).days
            elif record.create_date and record.date_deadline:
                record.validity = (record.date_deadline - fields.Date.to_date(record.create_date)).days

    @api.depends("create_date", "validity")
    def _inverse_validity(self):  # зпрацьовує коли зберігається модель estate.test
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + relativedelta(days=record.validity)
            elif not record.create_date:
                record.date_deadline = fields.Date.today() + relativedelta(days=record.validity)

    def action_accept(self):
        for record in self:
            is_offer_accepted = False
            for test in record.property_id.offer_ids:
                if test.status == "accepted":
                    is_offer_accepted = True
                    break
            if not is_offer_accepted:
                record.status = "accepted"
                record.property_id.buyer_id = record.partner_id
                record.property_id.selling_price = record.price
                record.property_id.state = "offer accepted"
            else:
                raise exceptions.UserError("One offer is already accepted")

    def action_refuse(self):
        for record in self:
            record.status = "refused"
