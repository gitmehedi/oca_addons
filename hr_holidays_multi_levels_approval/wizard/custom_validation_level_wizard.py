from odoo import api, fields, models, _

class CustomValidationLevelWizard(models.TransientModel):
    _name = 'custom.validation.level.wizard'

    validation_level = fields.Integer(string='Validation Level',default=lambda self: self.env.context.get('level'))

    @api.multi
    def save_record(self):
        form_id = self.env.context.get('active_id')
        emp_form_pool = self.env['hr.employee'].search([('id', '=', form_id)])
        emp_form_pool.write({'validation_level': self.validation_level})

        for approver in emp_form_pool.holidays_approvers:
            approver.unlink()

        approver = emp_form_pool.parent_id
        sequence = 1
        pool_emp_approver_objs = self.env['hr.employee.holidays.approver']

        while sequence <= emp_form_pool.validation_level:
            if sequence == emp_form_pool.validation_level:
                model_data_pool = self.env['ir.model.data'].search([('module','=','hr_holidays'),('name','=','group_hr_holidays_user')], limit=1)
                record_id = model_data_pool.res_id
                holiday_officer_group = self.env['res.groups'].search([('id','=',record_id)])
                if holiday_officer_group and holiday_officer_group.users:
                    pool_emp_obj = self.env['hr.employee'].search([('user_id', 'in', holiday_officer_group.users.ids)])
                    emp_approver = (pool_emp_obj - emp_form_pool)[0]
                    pool_emp_approver_objs.create(
                        {'employee': emp_form_pool.id, 'approver': emp_approver.id, 'sequence': sequence})
                sequence = sequence + 1
            elif approver:
                pool_emp_approver_objs.create(
                    {'employee': emp_form_pool.id, 'approver': approver.id, 'sequence': sequence})
                approver = approver.parent_id
                sequence = sequence + 1
            else:
                sequence = sequence + 1
        return {'type': 'ir.actions.act_window_close'}