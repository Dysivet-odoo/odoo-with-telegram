from odoo import fields, models


class Estate_property_tag(models.Model):
    _name = "estate.property.tag"
    _description = "estate property tag"

    _sql_constraints = [('name_unique',
                         'unique(name)',
                         'Choose another name - it has to be unique!')]
    _order = "name"
    name = fields.Char(string="Name", size=20, required=True)
    color = fields.Integer('Color')