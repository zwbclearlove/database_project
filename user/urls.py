from django.urls import path
from user.views import *

app_name = 'user'
urlpatterns = [
    path('',index),
    path('index/',index,name='index'),
    path('sign_up/',register,name='register'),
    path('login/',login,name='login'),
    path('logout/',exit,name='logout'),
    path('user_info/',user_info,name='user_info'),
    path('user_update/',user_update,name='user_update'),
    path('add_address/',add_address,name='add_address'),
    path('address_update/<int:add_id>',address_update,name='address_update'),
    path('address_delete/<int:add_id>',address_delete,name='address_delete'),
    path('product_list/',product_list,name='product_list'),
    path('product/<int:pid>/',product,name='product'),
    path('cart/',cart,name='cart'),
    path('footprint/',footprint,name='footprint'),
    path('favorite/',favorite,name='favorite'),
    path('order/<int:order_id>/',order,name='order'),
    path('order_list/<int:status>/',order_list,name='order_list'),
    path('add_to_cart/<int:pid>/',add_to_cart,name='add_to_cart'),
    path('add_to_favorite/<int:pid>/',add_to_favorite,name='add_to_favorite'),
    path('delete_cart_item/<int:pid>/',delete_cart_item,name='delete_cart_item'),
    path('cancel_favorite/<int:pid>/',cancel_favorite,name='cancel_favorite'),
    path('checkout/',gen_order,name='checkout'),
    path('place_order_success/',place_order_success,name='place_order_success'),
    path('order/<str:order_id>/',order,name='order'),
    path('comment/<int:pid>/',comment,name='comment'),
]