from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateTest(models.Model):
    _name = "estate.test"
    _description = "My Test Estate Model"

    _sql_constraints = [('check_expected_price', 'CHECK(expected_price > 0)',
                         'Expected price should be strictly positive'),
                        ('check_selling_price', 'CHECK(selling_price >= 0)',
                         'Selling price should be positive')]
    _order = "id desc"

    name = fields.Char(string="Name", size=20, required=True)  # VARCHAR
    # Можна зробити store=True зберегти в базі даних так як compute не зберігаються
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode", size=15)
    date_availability = fields.Date(string="Data availability",
                                    default=lambda self: fields.Date.today() + relativedelta(months=3),
                                    copy=False, required=True)  # copy писати перед required
    expected_price = fields.Float(string="Expected price")
    selling_price = fields.Float(string="Selling price", copy=False, readonly=True)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living area")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden area")
    garden_orientation = fields.Selection(
        string='Type',
        selection=[("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")],
        help="Type is used to separate North, South, East, West"
    )
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(
        string='State',
        selection=[("new", "New"), ("offer received", "Offer Received"), ("offer accepted", "Offer Accepted"),
                   ("sold", "Sold"), ("canceled", "Canceled")],
        default="new",
        copy=False,
        required=True,
        help="Type is used to separate New, Offer Received, Offer Accepted, Sold, Canceled"
    )
    # partner_id = fields.Many2one("res.partner", string="Partner")
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    salesman_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offer")

    total_area = fields.Integer(string="Total Area", compute="_compute_area")
    best_price = fields.Float(string="Best Offer", compute="_compute_price")

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_canceled_property(self):
        for record in self:
            if record.state != 'new' and record.state != 'canceled':
                raise UserError("Only new or canceled properties can be deleted")


    @api.depends("living_area", "garden_area")  # Вход
    def _compute_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_price(self):
        for record in self:
            list_prices = record.mapped("offer_ids.price")
            if list_prices:
                record.best_price = max(list_prices)
            else:
                record.best_price = 0

    @api.onchange("garden")
    def _onchange(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = None

    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if not float_is_zero(record.selling_price, precision_rounding=0.01):
                if float_compare(record.selling_price, 0.9 * record.expected_price, precision_rounding=0.01) < 0:
                    raise ValidationError("The selling price must be at least 90% of thr expected price")

    def action_sold(self):
        error = False
        for record in self:
            if record.state != "canceled":
                record.state = "sold"
            else:
                error = True
        if error:
            raise UserError("Canceled properties cannot be sold")
        else:
            return True

    def action_cancel(self):
        error = False
        for record in self:
            if record.state != "sold":
                record.state = "canceled"
            else:
                error = True
        if error:
            raise UserError("Sold properties cannot be canceled")
        else:
            return True

    def set_offer_received(self):
        for record in self:
            if record.state == 'new':
                record.state = 'offer received'