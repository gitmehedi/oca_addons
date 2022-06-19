# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    def _create_resource_leave(self):
        """On leave creation, trigger the recomputation of the involved
        records."""
        res = super(HrHolidays, self)._create_resource_leave()
        self._check_theoretical_hours()
        return res

    def _remove_resource_leave(self):
        """On leave cancellation, trigger the recomputation of the involved
        records."""
        res = super(HrHolidays, self)._remove_resource_leave()
        self._check_theoretical_hours()
        return res

    def _check_theoretical_hours(self):
        """Recomputes all the theoretical hours that corresponds to the
        interval of dates and employee of the leaves.

        :param: self: Leave recordset.
        """
        to_recompute = self.env['hr.attendance']
        for record in self.filtered(lambda x: x.date_from and x.date_to):
            dt_from = record.date_from
            dt_to = record.date_to
            from_datetime = fields.Datetime.from_string(dt_from).replace(
                hour=0, minute=0, second=0, microsecond=0,
            )
            to_datetime = fields.Datetime.from_string(dt_to).replace(
                hour=23, minute=59, second=59, microsecond=99999,
            )
            to_recompute |= self.env['hr.attendance'].search([
                ('employee_id', '=', record.employee_id.id),
                ('check_in', '>=', fields.Datetime.to_string(from_datetime)),
                ('check_in', '<=', fields.Datetime.to_string(to_datetime)),
            ])
        to_recompute._compute_theoretical_hours()
