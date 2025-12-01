# Copyright 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.modules.module import get_module_path
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG


class IrModelData(models.Model):
    _inherit = 'ir.model.data'

    @api.model
    def _module_data_uninstall(self, modules_to_remove):
        """this function crashes for xmlids on undefined models or fields
        referring to undefined models"""
        for this in self.search([('module', 'in', modules_to_remove)]):
            if this.model == 'ir.model.fields':
                field = self.env[this.model].with_context(
                    **{MODULE_UNINSTALL_FLAG: True}).browse(this.res_id)
                if not field.exists() or field.model not in self.env:
                    this.unlink()
                    continue
            if this.model not in self.env:
                this.unlink()
        return super(IrModelData, self)._module_data_uninstall(
            modules_to_remove)


class CleanupPurgeLineModule(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.module'

    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.module', 'Purge Wizard', readonly=True)

    @api.multi
    def purge(self):
        """
        Uninstall modules upon manual confirmation, then reload
        the database.
        """
        module_model = self.env['ir.module.module']
        for line in self._get_target_lines():
            if line.purged:
                continue
            try:
                modules = module_model.search([
                    ('name', '=', line.name)
                ])
                if not modules:
                    line.safe_write({'purged': True, 'last_error': False})
                    self.env.cr.commit()  # pylint: disable=invalid-commit
                    continue
                self.logger.info('Purging module %s', ', '.join(modules.mapped('name')))
                modules.filtered(
                    lambda x: x.state == 'to install'
                ).write({'state': 'uninstalled'})
                modules.filtered(
                    lambda x: x.state in ('to upgrade', 'to remove')
                ).write({'state': 'installed'})
                modules.filtered(
                    lambda x: x.state == 'installed' and x.name != 'base'
                ).button_immediate_uninstall()
                modules.refresh()
                modules.filtered(
                    lambda x: x.state not in (
                        'installed', 'to upgrade', 'to remove', 'to install')
                ).unlink()
                line.safe_write({'purged': True, 'last_error': False})
                self.env.cr.commit()  # pylint: disable=invalid-commit
            except Exception as err:  # pragma: no cover - defensive logging
                self.env.cr.rollback()
                line.safe_write({'last_error': str(err)})
                self.logger.exception(
                    'Failed to purge module %s', line.name or line.id
                )
        return True


class CleanupPurgeWizardModule(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.module'
    _description = 'Purge modules'

    @api.model
    def find(self):
        res = []
        purge_lines = self.env['cleanup.purge.line.module']
        IrModule = self.env['ir.module.module']
        for module in IrModule.search(
                [
                    ('to_buy', '=', False),
                    ('name', '!=', 'studio_customization')
                ]
        ):
            if get_module_path(module.name, display_warning=False):
                continue
            if module.state == 'uninstalled':
                purge_lines += self.env['cleanup.purge.line.module'].create({
                    'name': module.name,
                })
                continue
            res.append((0, 0, {'name': module.name}))

        purge_lines.purge()

        if not res:
            raise UserError(_('No modules found to purge'))
        return res

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.module', 'wizard_id', 'Modules to purge')
