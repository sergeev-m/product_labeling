# -*- coding: utf-8 -*-
{
    'name': "product_labeling",
    'summary': "Short (1 phrase/line) summary of the module's purpose",
    'description': """
        Long description of module's purpose
    """,
    'author': "Mikhail",
    'website': "https://github.com/sergeev-m/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/product.xml',
        # 'views/views.xml'
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
