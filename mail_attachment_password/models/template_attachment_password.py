# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api

import base64
import PyPDF2

class MailTemplate(models.Model):
	_inherit = 'mail.template'

	is_report_protected = fields.Boolean(string="Is Password on Report?", default=False)
	report_password = fields.Char(string="Password", help="Set Password on pdf document.")

	@api.multi
	def generate_email(self, res_ids, fields=None):
		res= super(MailTemplate,self).generate_email(res_ids, fields=None)
		if self.is_report_protected and self.report_password:
			for key,value in res.values()[0].iteritems():
				if key=='attachments':
					password = str(self.report_password)
					name = value[0][0]
					bin_data = value[0][1]
					new_pdf = base64.b64decode(bin_data)
					new_file = open('/tmp/test.pdf','wb')
					new_file = new_file.write(new_pdf)
					pdffile = open('/tmp/test.pdf','rb')
					pdfreader = PyPDF2.PdfFileReader(pdffile)
					pdfwriter = PyPDF2.PdfFileWriter()

					for pagenum in range(pdfreader.numPages):
						pdfwriter.addPage(pdfreader.getPage(pagenum))

					pdfwriter.encrypt(password)
					resulltpdf = open('/tmp/'+str(value[0][0]),'wb')
					pdfwriter.write(resulltpdf)
					resulltpdf.close()
					with open('/tmp/'+str(value[0][0]), "rb") as pdf_file:
						encoded_string = base64.b64encode(pdf_file.read())
					res.values()[0]['attachments']=[(name,encoded_string)]
		return res





