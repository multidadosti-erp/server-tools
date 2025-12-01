# Copyright 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CleanupPurgeLineMenu(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.menu'

    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.menu', 'Purge Wizard', readonly=True)
    menu_id = fields.Many2one('ir.ui.menu', 'Menu entry')

    @api.multi
    def purge(self):
        """Unlink menu entries upon manual confirmation."""
        for line in self._get_target_lines():
            if line.purged or not line.menu_id:
                continue
            try:
                self.logger.info('Purging menu entry: %s', line.name)
                line.menu_id.unlink()
                line.safe_write({'purged': True, 'last_error': False})
                self.env.cr.commit()  # pylint: disable=invalid-commit
            except Exception as err:  # pragma: no cover - defensive logging
                self.env.cr.rollback()
                line.safe_write({'last_error': str(err)})
                self.logger.exception(
                    'Failed to purge menu entry %s', line.name or line.id
                )
        return True


class CleanupPurgeWizardMenu(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.menu'
    _description = 'Purge menus'

    @api.model
    def find(self):
        """
        Search for models that cannot be instantiated.
        """
        res = []
        for menu in self.env['ir.ui.menu'].with_context(active_test=False)\
                .search([('action', '!=', False)]):
            if menu.action.type != 'ir.actions.act_window':
                continue
            if (menu.action.res_model and menu.action.res_model not in
                self.env) or \
                    (menu.action.src_model and menu.action.src_model not in
                        self.env):
                res.append((0, 0, {
                    'name': menu.complete_name,
                    'menu_id': menu.id,
                }))
        if not res:
            raise UserError(_('No dangling menu entries found'))
        return res

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.menu', 'wizard_id', 'Menus to purge')
