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
    path('add_product/', add_product, name='add_product'),
    path('product_list/', product_list, name='product_list'),
    path('products/', products, name='products'),
    path('product/<int:pid>/', product, name='product'),
    path('update_product/<int:pid>/', update_product, name='update_product'),
    path('product_state_change/<str:state>/', change_product_state, name='product_state_change'),

]