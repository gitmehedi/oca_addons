# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    parent_id = fields.Many2one('purchase.requisition', string='Merged Into', readonly=True)
    child_ids = fields.One2many('purchase.requisition','parent_id','Children')


    @api.multi
    def send_mail_to_all_quotations(self):
        template_id = self.env.ref('purchase.email_template_edi_purchase')
        if template_id:
            for rfq in self.purchase_ids:
                if rfq.partner_id.email:
                    values = template_id.generate_email(rfq.id)
                    values['email_to'] = rfq.partner_id.email
                    values['email_from'] = self.env.user.email
                    mail = self.env['mail.mail'].create(values)
                    attachment_ids = []
                    # create attachments
                    for attachment in values['attachments']:
                        attachment_data = {
                            'name': attachment[0],
                            'datas_fname': attachment[0],
                            'datas': attachment[1],
                            'res_model': 'mail.message',
                            'res_id': mail.mail_message_id.id,
                        }
                        attachment_ids.append(self.env['ir.attachment'].create(attachment_data).id)
                    if attachment_ids:
                        mail.write({'attachment_ids': [(6, 0, attachment_ids)]})
                    # send mail
                    mail.send()
                    # change status of RFQ
                    rfq.state = 'sent'
        return True
