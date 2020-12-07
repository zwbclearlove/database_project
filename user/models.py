from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=32, verbose_name="用户名")
    nickname = models.CharField(max_length=32, verbose_name="昵称")
    password = models.CharField(max_length=32, verbose_name="密码")
    email = models.EmailField(verbose_name="邮箱")
    avatar = models.ImageField(upload_to="user/images", verbose_name="头像",null=True,blank=True)
    phone = models.CharField(max_length=32, verbose_name="联系电话",null=True,blank=True)
    contact_address = models.TextField(verbose_name="联系地址",null=True,blank=True)

    def __str__(self):
        return self.username

class Address(models.Model):
    address = models.TextField(verbose_name="收货地址")
    receiver = models.CharField(max_length=32, verbose_name="收货人")
    receive_phone = models.CharField(max_length=32, verbose_name="联系电话")
    postNumber = models.CharField(max_length=32, verbose_name="邮编")
    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="用户ID")
    def __str__(self):
        return self.address

class Order(models.Model):
    order_id = models.CharField(max_length=64, verbose_name="订单编号")
    order_user = models.ForeignKey(to=User,on_delete=models.CASCADE,verbose_name="订单用户")
    order_shop = models.IntegerField(verbose_name="店铺id")
    order_address = models.ForeignKey(to=Address,on_delete=models.CASCADE,verbose_name="收货地址")
    order_status = models.IntegerField(verbose_name="订单状态")
    # 0-未发货 1-已发货 2-已收货 3-已完成
    order_price = models.FloatField(verbose_name="订单总额")
    order_date = models.DateTimeField(verbose_name="下单时间")
    def __str__(self):
        return self.order_id

class OrderItem(models.Model):
    order = models.ForeignKey(to=Order,on_delete=models.CASCADE,verbose_name="所属订单")
    product_id = models.IntegerField(verbose_name="商品id")
    product_name = models.CharField(max_length=32,verbose_name="商品名称")
    product_price = models.FloatField(verbose_name="商品价格")
    product_number = models.IntegerField(verbose_name="商品数量")
    total_price = models.FloatField(verbose_name="商品总价")
    shop_id = models.IntegerField(verbose_name="店铺id")
    def __str__(self):
        return str(self.order)

class Cart(models.Model):
    cart_user = models.ForeignKey(to=User,on_delete=models.CASCADE,verbose_name="订单用户")
    def __str__(self):
        return self.cart_user

class CartItem(models.Model):
    cart_user = models.ForeignKey(to=User,on_delete=models.CASCADE,verbose_name="所属用户")
    product_id = models.IntegerField(verbose_name="商品id")
    product_name = models.CharField(max_length=32,verbose_name="商品名称")
    product_price = models.FloatField(verbose_name="商品价格")
    product_number = models.IntegerField(verbose_name="商品数量")
    total_price = models.FloatField(verbose_name="商品总价")
    shop_id = models.IntegerField(verbose_name="店铺id")
    def __str__(self):
        return self.cart_user.username + ' ' + self.product_name + ' ' + str(self.product_number)

class Favorite(models.Model):
    user_id = models.IntegerField(verbose_name='所属用户')
    product_id = models.IntegerField(verbose_name='所属商品')
    create_time = models.DateTimeField(verbose_name='添加时间')

class FootPrint(models.Model):
    user_id = models.IntegerField(verbose_name='所属用户')
    product_id = models.IntegerField(verbose_name='所属商品')
    create_time = models.DateTimeField(verbose_name='访问时间')





