from django.contrib import admin
from .models import User,Shop,ShopType,Product,ProductType,ProductImage,Comment,Follow,Coupon,Message
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['username','password','nickname','phoneNumber','email',
                    'avatar','address','creditCard']


admin.site.register(User)
admin.site.register(Shop)
admin.site.register(ShopType)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductType)
admin.site.register(Comment)
admin.site.register(Follow)
admin.site.register(Coupon)
admin.site.register(Message)