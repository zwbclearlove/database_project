from django.db import models
from django.utils import timezone

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=32, verbose_name="用户名")
    password = models.CharField(max_length=32, verbose_name="密码")
    nickname = models.CharField(max_length=16, verbose_name="昵称", null=True, blank=True)
    phoneNumber = models.CharField(max_length=16, verbose_name="手机号码", null=True, blank=True)
    email = models.EmailField(verbose_name="邮箱", null=True, blank=True)
    avatar = models.ImageField(upload_to="shop/images", verbose_name="头像", null=True, blank=True)

    address = models.CharField(max_length=32,verbose_name="地址",null=True,blank=True)
    creditCard = models.CharField(max_length=32,verbose_name="银行卡号",null=True,blank=True)

    def __str__(self):
        return self.username

class ShopType(models.Model):
    shopType = models.CharField(max_length=32, verbose_name="店铺类型")
    description = models.TextField(verbose_name="详细信息")

    def __str__(self):
        return self.shopType

class Shop(models.Model):
    shopName = models.CharField(max_length=32, verbose_name="店铺名称")
    address = models.CharField(max_length=32, verbose_name="地址")
    description = models.TextField(verbose_name="描述")
    avatar = models.ImageField(upload_to="shop/images", verbose_name="logo")
    phoneNumber = models.CharField(max_length=32, verbose_name="联系电话")

    userId = models.IntegerField(verbose_name="店主")
    type = models.ManyToManyField(to=ShopType, verbose_name="店铺类型")
    def __str__(self):
        return self.shopName

class ProductType(models.Model):
    product_type = models.CharField(max_length=32, verbose_name="商品类型")
    description = models.TextField(verbose_name="详细信息")
    picture = models.ImageField(upload_to="shop/images",verbose_name="首页展示图")

    def __str__(self):
        return self.product_type

class Product(models.Model):
    name = models.CharField(max_length=32, verbose_name="商品名称")
    price = models.FloatField(verbose_name="商品价格")
    image = models.ImageField(upload_to="shop/images", verbose_name="商品图片")
    stock = models.IntegerField(verbose_name="库存")
    sales = models.IntegerField(verbose_name="销量", default=0)
    description = models.TextField(verbose_name="商品描述")
    createdDate = models.DateField(verbose_name="上架时间")
    product_type = models.ForeignKey(to=ProductType,on_delete=models.CASCADE,verbose_name="商品类型",default=1)
    shopId = models.ForeignKey(to=Shop, on_delete=models.CASCADE, verbose_name="商品店铺", null=True)
    on_sale = models.IntegerField(verbose_name="状态",default=0)
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    address = models.ImageField(upload_to="shop/images", verbose_name="图片地址")
    description = models.TextField(verbose_name="图片描述")
    productId = models.ForeignKey(to=Product,on_delete=models.CASCADE, verbose_name="商品id")

class Comment(models.Model):
    user_id = models.IntegerField(verbose_name="发布用户")
    product = models.ForeignKey(to=Product,on_delete=models.CASCADE,verbose_name="所属产品")
    content = models.TextField(verbose_name="评论内容")
    score = models.IntegerField(verbose_name="评分")
    create_time = models.DateTimeField(verbose_name="发布时间")

    def __str__(self):
        return self.content

class Message(models.Model):
    content = models.TextField(verbose_name="消息内容")
    message_type = models.IntegerField(verbose_name="消息类型")
    # 1- shop-to-user 2- user-to-shop
    message_time = models.DateTimeField(verbose_name="生成时间",default=timezone.now())
    from_id = models.IntegerField(verbose_name="发送者")
    to_id = models.IntegerField(verbose_name="接收人")
    have_read = models.BooleanField(verbose_name="已读",default=False)

    def __str__(self):
        return self.content

class Follow(models.Model):
    follow_time = models.DateTimeField(verbose_name="关注时间")
    user_id = models.IntegerField(verbose_name="关注者")
    shop = models.ForeignKey(to=Shop,on_delete=models.CASCADE,verbose_name="关注店铺")
    def __str__(self):
        return self.shop.shopName

class Coupon(models.Model):
    create_time = models.DateTimeField(default=timezone.now(),verbose_name="创建时间")
    product = models.ForeignKey(to=Product,on_delete=models.CASCADE,verbose_name="所属商品")
    end_time = models.DateTimeField(default=timezone.now(),verbose_name="截止时间")
    discount = models.FloatField(verbose_name="优惠金额")

    def __str__(self):
        return str(self.product)





















