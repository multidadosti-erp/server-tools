.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

Limpeza de banco de dados
=========================

Limpe seu banco de dados Odoo dos restos de modulos, modelos, colunas e
tabelas deixados por modulos desinstalados (antes da versao 7.0) ou por
uma atualizacao artesanal para uma nova versao principal do Odoo.

Atencao! Este modulo pode ser perigoso e *facilmente* destruir a integridade
dos seus dados. Nao use se voce nao domina os detalhes tecnicos do modelo
de dados do Odoo de *todos* os modulos que ja foram instalados em seu banco
de dados, e nao elimine nenhum modulo, modelo, coluna ou tabela sem saber
exatamente o que esta fazendo.

Uso
===

Apos instalar o modulo, va em Menu Configuracoes -> Tecnico -> Limpeza do
Banco de Dados. Este menu esta disponivel apenas para membros do grupo
*Direitos de Acesso*. Passe pelos registros de modulos, modelos, colunas e
tabelas (nesta ordem) para identificar dados orfaos em seu banco. Voce pode
excluir entrada por entrada ou eliminar tudo de uma vez (somente se estiver
*realmente* seguro).

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Experimente no Runbot
    :target: https://runbot.odoo-community.org/runbot/149/11.0

Rastreamento de bugs
====================

Os bugs sao acompanhados em `GitHub Issues <https://github.com/OCA/database_cleanup/issues>`_.
Em caso de problemas, verifique se a situacao ja foi relatada. Se voce a
identificou primeiro, ajude com um feedback detalhado.

Creditos
========

Imagens
-------

* Odoo Community Association: `Icone <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contribuidores
--------------

* Stefan Rijnhart <stefan@opener.amsterdam>
* Holger Brunn <hbrunn@therp.nl>
* Andrea Stirpe

Nao entre em contato diretamente com os contribuidores sobre duvidas ou
problemas referentes a este addon. Use a `lista de e-mails da comunidade <mailto:community@mail.odoo.com>`_
ou a `lista especializada apropriada <https://odoo-community.org/groups>`_ para obter ajuda,
e o rastreador de bugs citado em `Rastreamento de bugs`_ para questoes tecnicas.

Mantenedor
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

Este modulo e mantido pela OCA.

A OCA, ou Odoo Community Association, e uma organizacao sem fins lucrativos
cuja missao e apoiar o desenvolvimento colaborativo de recursos para o Odoo
e promover seu uso generalizado.

Para contribuir com este modulo, acesse https://odoo-community.org.
