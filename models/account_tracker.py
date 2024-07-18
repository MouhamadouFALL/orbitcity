# -*- coding: utf -*-
from odoo import api, models, fields, _


class Tracker(models.Model):
    _name = "account.tracker"
    _description = "Account Follow-up"
    _rec_name = "name"

    company_id = fields.Many2one("res.company", "Company Name",
                                 default=lambda self: self.env["res.company"]._company_default_get("account.tracker"))
    name = fields.Char(related="company_id.name", string="Name", readonly=True)
    # tracker_line = fields.One2many("account.tracker.line", "tracker_id", string="Follow up")

    _sql_constraints = [('company_uniq', 'unique(company_id)', 'Only one follow-up per company is allowed')]


