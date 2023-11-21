import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError
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
    amount = fields.Integer('Количество товара')

    @api.constrains('amount')
    def _check_amount_positive(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError('Количество товара должно быть больше нуля.')  # todo

    def _compute_expenses_receipts(self):
        for marked_product in self:
            marked_product.expenses_receipts_ids = self.env[
                'product.marked_product_expenses_receipts'].search(
                [('act_id', 'in', marked_product.act_ids.ids)]
            )

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

    def copy(self, default=None):
        if default is None:
            default = {}
        new_record = super().copy(default)

        act_mapping = {}

        # for act in self.act_ids:
        #     new_act = act.copy({'marked_product_ids': [(4, new_record.id)]})
        #     act_mapping[act.id] = new_act.id

        # new_act_ids = [(6, 0, list(act_mapping.values()))]
        # new_record.write({'act_ids': new_act_ids})


        # for related_record in self.act_ids:
        #     related_record.copy({'marked_product_id': new_record.id})

        act_ids = [(4, act.id) for act in self.act_ids]

        # act_mapping = {}
        #
        # for act in self.act_ids:
        #     new_act = act.copy({'marked_product_ids': new_record.id})
        #     act_mapping[act.id] = new_act.id
        #
        # new_act_ids = [(6, 0, list(act_mapping.values()))]
        new_record.write({'act_ids': act_ids})



        # for act in self.act_ids:
        #     new_act = act.copy({'marked_product_id': new_record.id})
        #     id_mapping[act.id] = new_act.id

        # new_act_ids = [(6, 0, list(act_mapping.values()))]
        # new_record.write({'act_ids': new_act_ids})

        # for act in self.act_ids:
        #     new_act = act.copy()
        #     id_mapping[act.id] = new_act.id

        # new_act_ids = [(4, i.id) for i in self.act_ids]
        # new_record.write({'act_ids': new_act_ids})
        #
        # # act_ids = [act.id for act in self.act_ids]
        # # new_record.write({'act_ids': new_act_ids})
        #
        return new_record


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
        string='Применить для товаров со склада',
        default=lambda self: self.marked_product_ids.warehouse_id.id or None
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
                    'product_id': rec.product_id.id,
                    'warehouse_id': rec.warehouse_to_id.id,
                    'status_id': rec.status_id.id,
                    'amount': rec.amount,
                    'act_ids': [rec.id]
                }
                marked_product_id = marked_product_env.create(values)
                rec.write({'marked_product_ids': marked_product_id})

            else:
                for product in rec.marked_product_ids:
                    old_amount = product.amount
                    values = {
                        'warehouse_id': rec.warehouse_to_id.id,
                        'status_id': rec.status_id.id,
                        'amount': rec.amount,
                        'act_ids': [(4, rec.id, 0)]
                    }

                    if not old_amount - rec.amount:
                        if rec.status_id.name.lower() == 'продажа':
                            values['amount'] = 0
                        product.write(values)

                    else:
                        if rec.status_id.name.lower() == 'продажа':
                            values['amount'] = 0
                        product.write({'amount': old_amount - rec.amount})


                        new_marked = product.copy(values)
                        # rec.write({'marked_product_ids': [(6, 0, [new_marked.id])]})
                        rec.write({'marked_product_ids': [(3, product.id)]})

            rec.write({'is_carried_out': True})
