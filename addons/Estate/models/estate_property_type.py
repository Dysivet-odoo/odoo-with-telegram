from odoo import fields, models, api

class Estate_property_type(models.Model):
    _name = "estate.property.type"
    _description = "estate property"

    _sql_constraints = [('name_unique',
                         'unique(name)',
                         'Choose another name - it has to be unique!')]

    _order = "name"

    name = fields.Char(string="Name", size=20)
    property_ids = fields.One2many("estate.test", "property_type_id", string="Properties")
    sequence = fields.Integer("Sequence", default=1, help="Used to order types.")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id",string="Offers")
    offer_count = fields.Integer(string="Offer Count", compute="_compute_offer_count")

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            #record.offer_count = len(record.mapped("offer_ids.price"))
            #record.offer_count = self.env['estate.property.offer'].search_count([('property_id.property_type_id','=',record.id)])
            record.offer_count = self.env['estate.property.offer'].search_count(
                [('property_type_id', '=', record.id)])