from django.urls import path
from shop.views import *

app_name = 'shop'
urlpatterns = [
    path('',index),
    path('sign_up/',sign_up, name='sign_up'),
    path('login/',login, name='login'),
    path('logout/',exit, name='logout'),
    path('index/',index, name='index'),
    path('shop_register/', shop_register, name='shop_register'),
    path('shop_update/', shop_update, name='shop_update'),
    path('shop_logo_update/', shop_logo_update, name='shop_logo_update'),
    path('add_product/', add_product, name='add_product'),
    path('product_list/', product_list, name='product_list'),
    path('products/', products, name='products'),
    path('product/<int:pid>/', product, name='product'),
    path('update_product/<int:pid>/', update_product, name='update_product'),
    path('update_product_image/<int:pid>/',update_product_image),    path('product_state_change/<str:state>/', change_product_state, name='product_state_change'),
    path('order_list/',order_list,name='order_list'),
    path('ship_product/<int:order_id>/',ship_product),
    path('urge_comment/<int:order_id>/',urge_comment),
    path('coupons/',coupons,name='coupons'),
    path('coupon_add/<int:pid>/',coupon_add,name='coupon_add'),
    path('coupon_delete/<int:cid>/',coupon_delete),
    path('product_types/',product_types),
    path('ptype_delete/<int:ptid>/',ptype_delete),
    path('ptype_add/',ptype_add),
    path('messages/',message_list),
    path('extrainfo/',extra_info),
    path('extrainfo/<int:type>/',extra_info),
    path('comment_delete/<int:cid>/',comment_delete),
]