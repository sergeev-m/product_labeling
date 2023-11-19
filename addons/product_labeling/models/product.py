from odoo import api, fields, models, _


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
    marked_product_id = fields.Many2one('product.marked_product')
    akt_id = fields.Many2one('product.act')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref('base.RUB')
    )
    value = fields.Monetary(string='Значение')


class MarkedProduct(models.Model):
    _name = 'product.marked_product'
    _description = 'Маркированный товар'

    product_id = fields.Many2one('product.product')
    warehouse_id = fields.Many2one('product.warehouse')
    status_id = fields.Many2one('product.status')
    expenses_ids = fields.One2many(
        comodel_name='product.marked_product_expenses_receipts',
        inverse_name='marked_product_id',
        string='Затраты/приходы'
    )
    name = fields.Char(
        'Маркерованный продукт',
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

    product_id = fields.Many2one('product.product', string='Продукт')
    marked_product_id = fields.Many2one(
        'product.marked_product',
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
    status_id = fields.Many2one('product.status', required=True)

    expenses_ids = fields.One2many(
        comodel_name='product.marked_product_expenses_receipts',
        inverse_name='akt_id',
        string='Затраты/приходы',
    )
    amount = fields.Integer('Количество', required=True)
    status = fields.Char('_compute_status', readonly=True, store=False)
    sequence = fields.Integer(
        string='Порядковый номер',
        default=lambda self: self.env['ir.sequence'].next_by_code('product.act.id') or 1,
        readonly=True,
        copy=False,
        store=False
    )  # todo
    current_date = fields.Date(
        string='Текущая дата',
        default=fields.Date.context_today,
        readonly=True,
        store=False
    )
    is_carried_out = fields.Boolean('Проведен')

    @api.model
    def create(self, values):
        if values.get('id', _('New')) == _('New'):
            values['sequence'] = self.env['ir.sequence'].next_by_code('product.act') or 1
        return super(ProductAct, self).create(values)

    @api.onchange('status_id')
    def _compute_status(self):
        self.status = self.status_id.name

    def carry_out_an_act(self):
        marked_product_env = self.env['product.marked_product']
        marked_product_expenses_receipts = self.env['product.marked_product_expenses_receipts']

        for rec in self:
            if rec.status_id.name.lower() == 'покупка':
                values = {
                    'product_id': self.product_id.id,
                    'warehouse_id': self.warehouse_to_id.id,
                    'status_id': self.status_id.id
                }
                marked_product_id = marked_product_env.create([values for _ in range(rec.amount)])
                expenses = marked_product_expenses_receipts.search([('akt_id', '=', rec.id)])
                for row in expenses:
                    row.write({'marked_product_id': marked_product_id})

            else:
                rec.marked_product_id.write({
                    'warehouse_id': rec.warehouse_to_id.id,
                    'status_id': rec.status_id.id
                })

            rec.write({'is_carried_out': True})




    # @api.model
    # def create_expenses_receipts(self):
    #     expenses_receipts_data = {
    #         'product_id': self.product_id.id,
    #         'marked_product_id': self.marked_product_id.id,
    #         'akt_id': self.id,
    #         'currency_id': self.product_id.currency_id.id,
    #         'value': 100,
    #     }
    #
    #     expenses_receipts = self.env['product.marked_product_expenses_receipts'].create(
    #         expenses_receipts_data)
    #
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'reload',
    #     }

    # @api.depends('status_id')
    # def _compute_marked_product(self):
    #     for record in self:
    #         # Если status_id равен 'покупка', пытаемся взять marked_product_id из product.product
    #         # if record.status_id and record.status_id.name == 'покупка':
    #             # Вам нужно адаптировать этот код в соответствии с вашей логикой
    #         product_model = self.env['product.product']
    #         other_product = product_model.search([], limit=1)
    #         if other_product:
    #             record.marked_product_id = other_product.id


        # related_recordset = self.env["the.relation.obj"].search([("some", "condition","here")])
        # self.marked_product_id.ids = related_ids


