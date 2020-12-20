# shop system 接口声明

## 前台

### URL

|              URL               |      name:user      |               description                |         发送数据          | 接收数据 |
| :----------------------------: | :-----------------: | :--------------------------------------: | :-----------------------: | :------: |
|             index/             |        index        |                   主页                   |                           |          |
|            sign_up/            |      register       |                 注册页面                 | result.status result.data |          |
|             login/             |        login        |                 登陆页面                 |                           |          |
|            logout/             |       logout        |                   注销                   |                           |          |
|           user_info/           |      user_info      |               显示个人信息               |                           |          |
|          user_update/          |     user_update     |               个人信息更改               |                           |          |
|          add_address/          |     add_address     |               添加收货地址               |                           |          |
| address_update/\<int:add_id\>/ |   address_update    |             收货地址信息更改             |                           |          |
| address_delete/\<int:add_id\>/ |   address_delete    |               删除收货地址               |                           |          |
|         product_list/          |    product_list     |               显示商品列表               |                           |          |
|      product/\<int:pid\>/      |       product       |               显示商品信息               |                           |          |
|             cart/              |        cart         |                购物车详情                |                           |          |
|           footprint/           |      foorprint      |                 浏览历史                 |                           |          |
|           favorite/            |      favorite       |                  收藏夹                  |                           |          |
|    order/\<int:order_id\>/     |        order        |                 订单信息                 |                           |          |
|   order_list/\<int:status\>/   |     order_list      | 显示当前用户的订单列表，status为订单状态 |                           |          |
|    add_to_cart/\<int:pid\>/    |     add_to_cart     |            将某商品加入购物车            |                           |          |
|  add_to_favorite/\<int:pid\>/  |   add_to_favorite   |            将某商品加入收藏夹            |                           |          |
| delete_cart_item/\<int:pid\>/  |  delete_cart_item   |            删除购物车中的商品            |                           |          |
|  cancel_favorite/\<int:pid\>/  |   cancel_favorite   |                 取消收藏                 |                           |          |
|           checkout/            |      checkout       |     更改确认订单信息（确定收货地址）     |                           |          |
|      place_order_success/      | place_order_success |                 下单成功                 |                           |          |
|      comment/\<int:pid\>/      |       comment       |            生成对某商品的评论            |                           |          |

