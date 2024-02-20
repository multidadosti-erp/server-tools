# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'SQL Export Mail',
    'version': '12.0.1.1.0',
    'category': 'Generic Modules',
    'summary': 'Send csv file generated by sql query by mail.',
    'author':
        "Akretion,GRAP,Odoo Community Association (OCA)",
    'maintainers': ['legalsylvain', 'florian-dacosta'],
    'website': 'https://github.com/OCA/server-tools',
    'depends': [
        'sql_export',
        'mail',
    ],
    'license': 'AGPL-3',
    'data': [
        'views/sql_export_view.xml',
        'mail_template.xml',
    ],
    'installable': False,
}
