import hashlib

from django.core.paginator import Paginator
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, redirect
from shop.models import User,Shop,ShopType,Product,ProductType,Comment,Coupon,Follow,Message
from user.models import Order

# Create your views here.


def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result

def sign_up(request):
    result = {"status":"error","data":""}
    response = render(request,"shop/sign_up.html",locals())
    if request.method == "POST":
        username = request.POST.get("username")
        nickname = request.POST.get("nickname")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        if username and password:
            user = User()
            user.username = username
            user1 = User.objects.filter(username=username).first()
            if user1:
                result["data"] = "用户名已经存在"
                response = render(request, "shop/sign_up.html", locals())
                return response
            if password != password2:
                result["data"] = "两次输入的密码不相同"
                response = render(request, "shop/sign_up.html", locals())
                return response
            user.password = setPassword(password)
            user.nickname = nickname
            user.save()
            result["status"] = "success"
            result["data"] = "注册成功"
            return HttpResponseRedirect("/shop/login/")
        else:
            result["data"] = "用户名和密码不能为空"
            response = render(request, "shop/sign_up.html", locals())
    return response

def login(request):
    result = {"status":"error","data":""}

    response = render(request,"shop/login.html",locals())
    response.set_cookie("login_from","legitimate")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember = request.POST.get("remember")
        if username and password:
            user = User.objects.filter(username=username).first()
            if user:
                web_password = setPassword(password)

                cookies = request.COOKIES.get("login_from")
                if web_password == user.password and cookies == "legitimate":
                    result["status"] = "success"
                    result["data"] = "登录成功"
                    response = HttpResponseRedirect('/shop/index/',locals())
                    response.set_cookie("shop_username", user.username)
                    response.set_cookie("shop_userId", user.id)
                    request.session["shop_username"] = user.username

                    shop = Shop.objects.filter(userId=user.id).first()
                    if shop:
                        response.set_cookie("shop_registered",shop.id)
                    else:
                        response.set_cookie("shop_registered","")
                    return response
                else:
                    result["data"] = "密码错误"
                    response = render(request, "shop/login.html", locals())
            else:
                result["data"] = "用户名不存在"
                response = render(request, "shop/login.html", locals())
        else:
            result["data"] = "用户名和密码不能为空"
            response = render(request, "shop/login.html", locals())

    return response

def loginValid(fun):
    def inner(request,*args,**kwargs):
        # 获取成功登录后的cookie和session
        c_user = request.COOKIES.get("shop_username")
        s_user = request.session.get("shop_username")
        # 如果cookie和session都存在并且值都相同
        if c_user and s_user and c_user == s_user:
            # 通过c_user查询数据库
            user = User.objects.filter(username=c_user).first()
            # 如果有这个用户，则返回函数，这里只index
            if user:
                return fun(request,*args,**kwargs)
        # 否则重定向到登录页面
        return HttpResponseRedirect("/shop/login/")
    return inner

@loginValid
def index(request):
    userId = request.COOKIES.get("shop_userId")
    if userId:
        userId = int(userId)
    else:
        userId = -1
    # 通过用户查询店铺是否存在（店铺和用户通过用户的id进行关联）
    shop = Shop.objects.filter(userId=userId).first()
    return render(request,"shop/index.html",{"shop":shop})

def exit(request):
    response = HttpResponseRedirect("/shop/login/")
    for key in request.COOKIES:
        response.delete_cookie(key)
    del request.session["shop_username"]
    # 跳转到登录
    return response

#register a shop
def shop_register(request):
    type_list = ShopType.objects.all()
    if request.method == "POST":
        post_data = request.POST
        shopName = post_data.get("name")
        address = post_data.get("address")
        description = post_data.get("description")
        phone = post_data.get("phoneNumber")
        user_id = int(request.COOKIES.get("shop_userId"))
        type_lst = post_data.getlist("type")
        logo = request.FILES.get("avatar")

        shop = Shop()
        shop.shopName = shopName
        shop.address = address
        shop.description = description
        shop.phoneNumber = phone
        shop.userId = user_id
        shop.avatar = logo
        shop.save()
        for i in type_lst:
            st = ShopType.objects.get(id=i)
            shop.type.add(st)
        shop.save()
        response = HttpResponseRedirect("/shop/index/")
        response.set_cookie("shop_registered",shop.id)
        return response

    return render(request,"shop/shop_register.html",locals())

#update shop info
def shop_update(request):
    type_list = ShopType.objects.all()
    shopId = request.COOKIES.get("shop_registered")
    shop = Shop.objects.get(id=shopId)
    if request.method == "POST":
        post_data = request.POST
        shopName = post_data.get("name")
        address = post_data.get("address")
        description = post_data.get("description")
        phone = post_data.get("phoneNumber")
        user_id = int(request.COOKIES.get("shop_userId"))
        type_lst = post_data.getlist("type")
        logo = request.FILES.get("avatar")

        shop.shopName = shopName
        shop.address = address
        shop.description = description
        shop.phoneNumber = phone
        shop.userId = user_id
        if logo:
            shop.avatar = logo
        shop.save()
        for i in type_lst:
            st = ShopType.objects.get(id=i)
            shop.type.add(st)
        shop.save()
        return HttpResponseRedirect("/shop/index/")

    return render(request,"shop/shop_update.html",locals())

#add a new product for current shop
def add_product(request):
    if request.method == "POST":
        postdata = request.POST
        name = postdata.get("name")
        price = postdata.get("price")
        description = postdata.get("description")
        stock = postdata.get("stock")
        image = request.FILES.get("image")

        date = timezone.now()
        user_id = int(request.COOKIES.get("shop_userId"))
        shop = Shop.objects.filter(userId=user_id).first()
        product = Product()
        product.name = name
        product.price = price
        product.description = description
        product.stock = stock
        product.createdDate = date
        product.shopId = shop
        if image:
            product.image = image
        else :
            product.image = 'shop/images/no_image.png'
        product.save()
        return HttpResponseRedirect("/shop/index/")

    return render(request,"shop/add_product.html",locals())

#get all products from current shop
def product_list(request):
    keywords = request.GET.get("keywords","")
    page_num = request.GET.get("page_num",1)
    shop_registered = int(request.COOKIES.get("shop_registered"))
    shop = Shop.objects.filter(id=shop_registered).first()
    if keywords:
        plist = Product.objects.filter(shopId=shop,name__contains=keywords)
    else:
        plist = Product.objects.filter(shopId=shop)
    paginator = Paginator(plist,10)
    page = paginator.page(int(page_num))
    page_range = paginator.page_range
    return render(request,"shop/product_list.html",locals())

#get all products
def products(request):
    keywords = request.GET.get("keywords","")
    page_num = request.GET.get("page_num",1)
    if keywords:
        plist = Product.objects.filter(name__contains=keywords)
    else:
        plist = Product.objects.all()
    paginator = Paginator(plist,3)
    page = paginator.page(int(page_num))
    page_range = paginator.page_range
    return render(request,"shop/product_list.html",locals())

# show product info
def product(request, pid):
    p = Product.objects.filter(id=pid).first()
    return render(request,"shop/product.html",locals())

#update product info
def update_product(request, pid):
    p = Product.objects.filter(id=pid).first()
    if request.method == "POST":
        postdata = request.POST
        name = postdata.get("name")
        price = postdata.get("price")
        description = postdata.get("description")
        stock = postdata.get("stock")
        image = request.FILES.get("image")
        date = postdata.get("createdDate")

        p.name = name
        p.price = price
        p.description = description
        p.stock = stock
        p.createdDate = date
        if image:
            p.image = image
        p.save()
        return HttpResponseRedirect('/shop/product/%s'%pid)
    return render(request,"shop/update_product.html",locals())

#change product state
def change_product_state(request,state):
    if state == "up":
        state_num = 1
    else:
        state_num = 0
    id = request.GET.get("id")
    referer = request.META.get("HTTP_REFERER")
    if id:
        product = Product.objects.filter(id=id).first()
        if state == "delete":
            product.delete()
        else:
            product.on_sale = state_num
            product.save()
    return HttpResponseRedirect(referer)

def ptype_add(request):
    if request.method == "POST":
        postdata = request.POST
        name = postdata.get("name")
        description = postdata.get("description")
        image = request.FILES.get("image")

        ptype = ProductType()
        ptype.product_type = name
        ptype.description = description
        ptype.picture = image
        ptype.save()
        return HttpResponseRedirect("/shop/index/")
    return render(request,"shop/ptype_add.html")

def ptype_delete(request, ptid):
    ptype = ProductType.objects.get(id=ptid)
    ptype.delete()
    return HttpResponseRedirect('/shop/index/')

def coupon_add(request):
    if request.method == 'POST':
        postdata = request.POST
        end_time = postdata.get('end_time')
        product_id = postdata.get('product_id')
        discount = postdata.get('discount')

        new_coupon = Coupon()
        new_coupon.create_time = timezone.now()
        new_coupon.end_time = end_time
        new_coupon.discount = discount
        new_coupon.product_id = product_id
        new_coupon.save()

        shop_id = request.COOKIES.get('shop_userId')
        follower_list = Follow.objects.filter(shop_id=shop_id)
        for follower in follower_list:
            new_message = Message()
            new_message.message_time = timezone.now()
            new_message.message_type = 1
            new_message.from_id = shop_id
            new_message.to_id = follower.user_id
            new_message.content = "您关注的商店有一款商品降价了"
            new_message.save()
        return HttpResponseRedirect("/shop/index/")
    return render(request,"shop/coupon_add.html")

def coupon_delete(request, cid):
    coupon = Coupon.objects.get(id=cid)
    coupon.delete()
    return HttpResponseRedirect('/shop/index/')

def comment_delete(request,cid):
    current_comment = Comment.objects.get(id=cid)
    current_comment.delete()
    messages.add_message(request,messages.SUCCESS,'评论删除成功',extra_tags='success')
    referer = request.META.get("HTTP_REFERER")
    return  HttpResponseRedirect(referer)

#发货
def ship_product(request,order_id):
    corder = Order.objects.get(id=order_id)
    corder.order_status = 1
    corder.save()
    new_message = Message()
    new_message.message_type = 1
    new_message.message_time = timezone.now()
    new_message.from_id = corder.order_shop
    new_message.to_id = corder.order_user.id
    new_message.content = "您的订单已经发货"
    new_message.save()
    referer = request.META.get("HTTP_REFERER")
    return  HttpResponseRedirect(referer)


#提醒用户评价
def urge_comment(request,order_id):
    corder = Order.objects.get(id=order_id)
    new_message = Message()
    new_message.message_type = 1
    new_message.message_time = timezone.now()
    new_message.from_id = corder.order_shop
    new_message.to_id = corder.order_user.id
    new_message.content = "您有一个订单需要评价"
    new_message.save()
    referer = request.META.get("HTTP_REFERER")
    return  HttpResponseRedirect(referer)

def message_list(request):
    shop_id = request.COOKIES.get('shop_registered')
    user_message_list = Message.objects.filter(message_type=2,to_id=shop_id).order_by('-message_time')
    return render(request,'shop/message_list.html',locals())






