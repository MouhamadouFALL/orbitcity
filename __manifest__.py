# -*- coding: utf-8 -*-
{
    'name': "CCBM SHOP",
    'summary': """ Management three Business: Order, Preorder and creditorder.""",
    'description': """
        Optimising sales flows by effectively managing three categories of transactional processes: 
        standard orders, pre-orders and credit orders.
    """,
    'author': "CCBM DEV",
    'license': "AGPL-3",
    'website': "https://ccbme.sn",
    'category': 'CCBM/',
    'version': '16.0.0',
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_crm', 'crm', 'account', 'purchase', 'stock'],

    # always loaded
    'data': [

        'security/orbit_security.xml',
        'security/ir.model.access.csv',

        # 'data/crm_stage_data.xml',
        # 'data/mail_template_data.xml',

        'wizard/preorder_advance_payment_wzd_view.xml',
        'wizard/crm_opportunity_to_quotation_orbit_views.xml',
        'wizard/crm_type_sale_for_quotation_views.xml',
        # 'wizard/sale_make_invoice_advance_inherited_views.xml',

        'views/res_partner_views.xml',
        'views/affiliate_views.xml',
        # 'views/crm_lead_views.xml',
        # 'views/payment_plan_views.xml',
        'views/product_product.xml',
        'views/sale_order_orbit_views.xml',
        'views/preorder_orbit_views.xml',
        'views/account_move_views.xml',
        
        # 'views/account_tracker_views.xml',
        # 'views/account_tracker_line_views.xml',
        # 'views/orbit_stage_views.xml',
        # 'views/sale_order_payment_plan_views.xml',
        # 'views/edit_account_move.xml',
        # 'views/plan_payment_tracker_line_view.xml',

        # ***************************** Menu ****************************
        'views/menu_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
}
