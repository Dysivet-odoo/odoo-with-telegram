{
    'name': 'Estate',
    'version': '0.8',
    'application': True,
    'depends': [
        'base_setup'
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/estate_property_offer_view.xml',
        'views/estate_property_tag_view.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
        'views/estate_test_views.xml',
        'views/res_users_view.xml',
        'views/estate_menus.xml',
    ]
}