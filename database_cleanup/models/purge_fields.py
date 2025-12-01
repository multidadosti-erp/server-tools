# Copyright 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import _, api, models, fields
from odoo.exceptions import UserError
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from ..identifier_adapter import IdentifierAdapter


class CleanupPurgeLineField(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.field'
    _description = 'Purge fields'

    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.field', 'Purge Wizard', readonly=True
    )
    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field',
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        related="field_id.model_id",
        string="Model",
        store=True,
    )
    model_name = fields.Char(
        related="model_id.model",
        string="Model Technical Name",
        store=True,
    )

    @api.multi
    def purge(self):
        """
        Unlink fields upon manual confirmation.
        """
        context_flags = {
            MODULE_UNINSTALL_FLAG: True,
            'purge': True,
        }
        self.logger.info('Purging field entries:')
        for rec in self._get_target_lines():
            if rec.purged or not rec.field_id:
                continue
            try:
                self.logger.info(' - %s.%s', rec.model_name, rec.field_id.name)
                field_id = rec.with_context(**context_flags).field_id
                model = self.env[rec.model_name]
                table_name = model._table
                column_name = field_id.name
                force_drop = False
                # FIX: on unlink, odoo will not DROP the SQL column even if exists if the
                # store attribute is set to False.
                if not field_id.store and model._auto:
                    force_drop = True
                # Odoo will internally drop the SQL column
                field_id.unlink()
                if force_drop:
                    self._drop_column(table_name, column_name)
                rec.safe_write({'purged': True, 'last_error': False})
                self.env.cr.commit()  # pylint: disable=invalid-commit
            except Exception as err:  # pragma: no cover - defensive logging
                self.env.cr.rollback()
                rec.safe_write({'last_error': str(err)})
                self.logger.exception(
                    'Failed to purge field line %s.%s',
                    rec.model_name,
                    rec.field_id.name if rec.field_id else rec.id,
                )
        return True

    def _drop_column(self, table, column):
        # Use code from `purge_columns.py::purge()`
        # Check whether the column actually still exists.
        # Inheritance such as stock.picking.in from stock.picking
        # can lead to double attempts at removal
        self.env.cr.execute(
            'SELECT count(attname) FROM pg_attribute '
            'WHERE attrelid = '
            '( SELECT oid FROM pg_class WHERE relname = %s ) '
            'AND attname = %s', (table, column)
        )
        if not self.env.cr.fetchone()[0]:
            return
        self.logger.info('Dropping column %s from table %s', column, table)
        self.env.cr.execute(
            'ALTER TABLE %s DROP COLUMN %s',
            (IdentifierAdapter(table), IdentifierAdapter(column))
        )
        # Commit happens right after each purge line


class CleanupPurgeWizardField(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.field'
    _description = 'Purge fields'

    @api.model
    def find(self):
        """
        Search for fields not technically mapped to a model.
        """
        res = []
        ignored_fields = models.MAGIC_COLUMNS + [
            "display_name", models.BaseModel.CONCURRENCY_CHECK_FIELD
        ]
        domain = [('state', '=', 'base')]
        for field_id in self.env['ir.model.fields'].search(domain):
            if field_id.name in ignored_fields:
                continue
            model = self.env[field_id.model_id.model]
            if field_id.name not in model._fields.keys():
                res.append(
                    (0, 0, {
                        'name': field_id.name,
                        'field_id': field_id.id,
                    })
                )
        if not res:
            raise UserError(_('No orphaned fields found'))
        return res

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.field', 'wizard_id', 'Fields to purge'
    )
