# Copyright 2025 Multidadosti ERP
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, fields, models
from odoo.exceptions import UserError


LOGGER = logging.getLogger(__name__)


class CleanupFullCleanupWizard(models.TransientModel):
    _name = 'cleanup.full.cleanup.wizard'
    _description = 'Full cleanup wizard'

    log = fields.Text(
        string='Execution log',
        readonly=True,
        default=lambda self: _('Ready to run full cleanup.'),
    )

    def _get_cleanup_wizards(self):
        """Lista as wizards executadas na limpeza completa."""
        return [
            ('cleanup.purge.wizard.module', _('Modules')),
            ('cleanup.purge.wizard.model', _('Models')),
            ('cleanup.purge.wizard.field', _('Fields')),
            ('cleanup.purge.wizard.column', _('Columns')),
            ('cleanup.purge.wizard.table', _('Tables')),
            ('cleanup.purge.wizard.data', _('Data entries')),
            ('cleanup.purge.wizard.menu', _('Menu entries')),
            ('cleanup.create_indexes.wizard', _('Indexes')),
            ('cleanup.purge.wizard.property', _('Properties')),
        ]

    def action_run_full_cleanup(self):
        """Executa todas as rotinas de limpeza com tolerancia a falhas."""
        self.ensure_one()
        log_lines = []
        for model_name, label in self._get_cleanup_wizards():
            try:
                wizard = self.env[model_name].create({})
                wizard.purge_all()
                self.env.cr.commit()  # pylint: disable=invalid-commit
                log_lines.append(_('[OK] %s cleaned successfully.') % label)
            except UserError as err:
                self.env.cr.rollback()
                LOGGER.info('Full cleanup skipped %s: %s', model_name, err)
                log_lines.append(_('[SKIP] %s: %s') % (label, err.name or err))
            except Exception as err:  # pragma: no cover - defensive logging
                self.env.cr.rollback()
                LOGGER.exception('Full cleanup failed on %s', model_name)
                log_lines.append(_('[FAIL] %s: %s') % (label, err))
        if not log_lines:
            log_lines.append(_('Nothing to execute.'))
        self.log = '\n'.join(log_lines)
        view = self.env.ref('database_cleanup.view_full_cleanup_wizard')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Full cleanup'),
            'res_model': self._name,
            'view_mode': 'form',
            'view_id': view.id,
            'res_id': self.id,
            'target': 'new',
        }
