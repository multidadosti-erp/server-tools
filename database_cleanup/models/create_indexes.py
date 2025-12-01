# Copyright 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from ..identifier_adapter import IdentifierAdapter
from odoo import api, fields, models


class CreateIndexesLine(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.create_indexes.line'

    purged = fields.Boolean('Created')
    wizard_id = fields.Many2one('cleanup.create_indexes.wizard')
    field_id = fields.Many2one('ir.model.fields', required=True)

    @api.multi
    def purge(self):
        for line in self._get_target_lines():
            if line.purged or not line.field_id:
                continue
            try:
                field = line.field_id
                model = self.env[field.model]
                name = '%s_%s_index' % (model._table, field.name)
                self.env.cr.execute(
                    'create index %s ON %s (%s)',
                    (
                        IdentifierAdapter(name, quote=False),
                        IdentifierAdapter(model._table),
                        IdentifierAdapter(field.name),
                    ),
                )
                self.env.cr.execute(
                    'analyze %s', (IdentifierAdapter(model._table),)
                )
                line.safe_write({'purged': True, 'last_error': False})
                self.env.cr.commit()  # pylint: disable=invalid-commit
            except Exception as err:  # pragma: no cover - defensive logging
                self.env.cr.rollback()
                line.safe_write({'last_error': str(err)})
                self.logger.exception(
                    'Failed to create index for %s', line.name or line.id
                )
        return True


class CreateIndexesWizard(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.create_indexes.wizard'
    _description = 'Create indexes'

    purge_line_ids = fields.One2many(
        'cleanup.create_indexes.line', 'wizard_id',
    )

    @api.multi
    def find(self):
        res = list()
        for field in self.env['ir.model.fields'].search([
                ('index', '=', True),
        ]):
            if field.model not in self.env.registry:
                continue
            model = self.env[field.model]
            name = '%s_%s_index' % (model._table, field.name)
            self.env.cr.execute(
                'select indexname from pg_indexes '
                'where indexname=%s and tablename=%s',
                (name, model._table)
            )
            if self.env.cr.rowcount:
                continue

            self.env.cr.execute(
                'select a.attname '
                'from pg_attribute a '
                'join pg_class c on a.attrelid=c.oid '
                'join pg_tables t on t.tablename=c.relname '
                'where attname=%s and c.relname=%s',
                (field.name, model._table,)
            )
            if not self.env.cr.rowcount:
                continue

            res.append((0, 0, {
                'name': '%s.%s' % (field.model, field.name),
                'field_id': field.id,
            }))
        return res
