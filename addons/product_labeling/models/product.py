import logging

from odoo import api, fields, models
from  odoo.service.server import _logger

# _logger = logging.getLogger(__name__)


class Product(models.Model):
    _name = 'product.product'
    _description = 'Product records'

    name = fields.Char(string='Наименование товара', required=True)
    description = fields.Text(string='Описание товара', required=True)


class Status(models.Model):
    _name = 'product.status'
    _description = 'Status'

    name = fields.Char(string='Статус')


class Warehouse(models.Model):
    _name = 'product.warehouse'
    _description = 'Склад'

    name = fields.Char('Название склада')


class ExpensesReceipts(models.Model):
    _name = 'product.expenses_receipts'
    _description = 'Затраты'

    name = fields.Char(string='Тип статьи затрат/приходов')


class MarkedProductExpensesReceipts(models.Model):
    _name = 'product.marked_product_expenses_receipts'
    _description = 'Затраты/приходы'

    expenses_id = fields.Many2one(
        'product.expenses_receipts',
        string='Тип статьи затрат/приходов',
        required=True
    )
    act_id = fields.Many2one('product.act')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref('base.RUB')
    )
    value = fields.Monetary(string='Значение', required=True)


class MarkedProduct(models.Model):
    _name = 'product.marked_product'
    _description = 'Маркированный товар'

    # act_ids = fields.One2many(comodel_name='product.act', inverse_name='marked_product_id')
    act_ids = fields.Many2many(
        'product.act',
        relation='marked_product_act_rel',
        column1='akt_id',
        column2='marked_product_id',
        string='Акты'
    )
    expenses_receipts_ids = fields.One2many(
        comodel_name='product.marked_product_expenses_receipts',
        inverse_name='act_id',
        string='Затраты/приходы',
        compute='_compute_expenses_receipts',
        readonly=True,
    )
    total_amount = fields.Monetary(string='Прибыль', compute='_compute_total_amount', readonly=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.ref('base.RUB'), readonly=True) # todo

    def _compute_expenses_receipts(self):
        for marked_product in self:
            marked_product.expenses_receipts_ids = self.env[
                'product.marked_product_expenses_receipts'].search(
                [('act_id', 'in', marked_product.act_ids.ids)]
            )

    # @api.depends('expenses_receipts_ids')
    def _compute_total_amount(self):
        for marked_product in self:
            p = marked_product.expenses_receipts_ids.mapped('value')
            marked_product.total_amount = sum(p)

    product_id = fields.Many2one('product.product')
    warehouse_id = fields.Many2one('product.warehouse')
    status_id = fields.Many2one('product.status')

    name = fields.Char(
        'Маркированный продукт',
        compute='_compute_name',
        readonly=True,
        store=False
    )

    def _compute_name(self):
        for record in self:
            record.name = f'{record.product_id.name} #{record.id}'


class ProductAct(models.Model):
    _name = 'product.act'
    _description = 'Акты'

    name = fields.Char('Название', default=lambda self: self._get_default_value())
    product_id = fields.Many2one('product.product', string='Продукт')
    # marked_product_id = fields.Many2one(
    #     'product.marked_product',
    #     string='Маркированный продукт'
    # )
    marked_product_ids = fields.Many2many(
        'product.marked_product',
        relation='marked_product_act_rel',
        column1='marked_product_id',
        column2='akt_id',
        string='Маркированный продукт'
    )
    warehouse_from_id = fields.Many2one(
        'product.warehouse',
        string='Применить для товаров со склада'
    )
    warehouse_to_id = fields.Many2one(
        'product.warehouse',
        string='Назначить новый склад',
        required=True
    )
    status_id = fields.Many2one('product.status', required=True, string='Статус')

    expenses_ids = fields.One2many(
        comodel_name='product.marked_product_expenses_receipts',
        inverse_name='act_id',
        string='Затраты/приходы',
    )
    amount = fields.Integer('Количество', default=1, required=True)
    status = fields.Char(
        '_compute_status',
        default=lambda self: self.status_id.name,  # todo
        readonly=True,
        store=False
    )

    current_date = fields.Date(
        string='Текущая дата',
        default=fields.Date.context_today,
        readonly=True,
        store=False
    )
    is_carried_out = fields.Boolean('Проведен')

    def _get_default_value(self):
        sequence = self.env['ir.sequence'].next_by_code('product.act') or 'Fallback Value'
        return sequence

    @api.onchange('status_id')
    def _compute_status(self):
        self.status = self.status_id.name

    def carry_out_an_act(self):
        marked_product_env = self.env['product.marked_product']

        for rec in self:
            if rec.status_id.name.lower() == 'покупка':
                values = {
                    'product_id': self.product_id.id,
                    'warehouse_id': self.warehouse_to_id.id,
                    'status_id': self.status_id.id,
                    'act_ids': [rec.id]
                }
                marked_product_env.create([values for _ in range(rec.amount)])
            else:
                rec.marked_product_ids.write({
                    'warehouse_id': rec.warehouse_to_id.id,
                    'status_id': rec.status_id.id
                })

            rec.write({'is_carried_out': True})
