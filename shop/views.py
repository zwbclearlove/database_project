import hashlib
import json
import random

from datetime import timedelta
from django.core import serializers
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from pyecharts.faker import Faker
from pyecharts.globals import ThemeType
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse,HttpResponse
from django.shortcuts import render, HttpResponseRedirect, redirect
from user.models import Order
from shop.models import User,Shop,ShopType,Product,ProductType,Comment,Coupon,Follow,Message
from user.models import OrderItem,Favorite


from pyecharts import options as opts
from pyecharts.charts import Bar, Pie, Line


# Create your views here.

def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result

def get_random_nickname():
    send = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    mac_str = ''
    for i in range(10):
        mac_str += random.choice(send)
    return "商户" + mac_str

@csrf_exempt
def sign_up(request):
    result = {"status":"error","data":""}
    response = render(request,"shop/sign_up.html",locals())
    if request.is_ajax():
        username = request.POST.get("username")
        password = request.POST.get("password")
        password1 = request.POST.get("confirm_password")
        email = request.POST.get("email")
        if not (username and password and password1 and email):
            result["data"] = "信息不能为空"
            response = JsonResponse({"data":result})
            return response
        user = User.objects.filter(username=username).first()
        print(user)
        if user:
            result["data"] = "用户名已存在"
            response = JsonResponse({"data":result})
            return response
        if password1 != password:
            result["data"] = "两次密码不匹配"
            response = JsonResponse({"data":result})
            return response
        user = User()
        user.username = username
        user.password = setPassword(password)
        user.email = email
        user.nickname = get_random_nickname()
        user.save()
        result["status"] = "success"
        response = JsonResponse({"data":result})
        return response
    return response

@csrf_exempt
def login(request):
    result = {"status":"error","data":"?"}

    response = render(request,"shop/login.html",{'result': json.dumps(result)})
    response.set_cookie("user_login_from","legitimate")
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        print(username,password)
        if username and password:
            user = User.objects.filter(username=username).first()
            if user:
                web_password = setPassword(password)

                cookies = request.COOKIES.get("user_login_from")
                if web_password == user.password:
                    result["status"] = "success"
                    result["data"] = "登录成功"
                    response = JsonResponse({"data":result})
                    response.set_cookie("shop_username", user.username)
                    response.set_cookie("shop_userId", user.id)
                    shop = Shop.objects.filter(userId=user.id).first()
                    if shop:
                        response.set_cookie("shop_registered",shop.id)
                    else:
                        response.set_cookie("shop_registered","")
                        result["status"] = "no_shop"
                        response = JsonResponse({"data":result})
                    return response
                else:
                    result["data"] = "密码错误"
                    response = JsonResponse({"data":result})
                    return response
            else:
                result["data"] = "用户名不存在"
                response = JsonResponse({"data":result})
                return response
        else:
            result["data"] = "用户名和密码不能为空"
            response = JsonResponse({"data":result})
            return response

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


def index(request):
    userId = request.COOKIES.get("shop_userId")
    if userId:
        userId = int(userId)
    else:
        userId = -1
    # 通过用户查询店铺是否存在（店铺和用户通过用户的id进行关联）
    shop = Shop.objects.filter(userId=userId).first()
    return render(request,"shop/index_new.html",{"shop":shop})

def exit(request):
    response = HttpResponseRedirect("/shop/login/")
    for key in request.COOKIES:
        response.delete_cookie(key)

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
        type1 = post_data.get("type")
        logo = request.FILES.get("avatar")

        shop = Shop()
        shop.shopName = shopName
        shop.address = address
        shop.description = description
        shop.phoneNumber = phone
        shop.userId = user_id
        shop.avatar = logo
        st = ShopType.objects.get(shopType=type1)
        shop.type = st
        shop.save()
        response = HttpResponseRedirect("/shop/index/")
        response.set_cookie("shop_registered",shop.id)
        return response

    return render(request,"shop/shop_register.html",locals())

def shop_logo_update(request):
    shopId = request.COOKIES.get("shop_registered")
    shop = Shop.objects.get(id=shopId)
    if request.method == "POST":
        image = request.FILES.get("image")
        if image:
            shop.avatar = image
            messages.add_message(request,messages.SUCCESS,'logo修改成功',extra_tags='success')
        shop.save()

        return HttpResponseRedirect('/shop/index/')
    show_image = shop.avatar
    return render(request,'image_update.html',locals())

#update shop info
@csrf_exempt
def shop_update(request):
    shopId = request.COOKIES.get("shop_registered")
    shop = Shop.objects.get(id=shopId)
    if request.is_ajax():
        post_data = request.POST
        shopName = post_data.get("name")
        address = post_data.get("address")
        description = post_data.get("description")
        phone = post_data.get("phoneNumber")

        shop.shopName = shopName
        shop.address = address
        shop.description = description
        shop.phoneNumber = phone
        shop.save()
        messages.add_message(request,messages.SUCCESS,'信息修改成功',extra_tags='success')
        return JsonResponse({"status":"success"})

    return JsonResponse({"status":"error"})

#add a new product for current shop
@csrf_exempt
def add_product(request):
    if request.is_ajax():
        postdata = request.POST
        name = postdata.get("name")
        price = postdata.get("price")
        description = postdata.get("description")
        stock = postdata.get("stock")
        type = postdata.get('product_type')
        #image = request.FILES.get("image")

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
        #if image:
            #product.image = image
        #else :
        product.image = 'shop/images/no_image.png'
        product.product_type = ProductType.objects.get(product_type=type)
        product.save()
        messages.add_message(request,messages.SUCCESS,'商品添加成功',extra_tags='success')
        return JsonResponse({"status":"success"})

    return  JsonResponse({"status":"error"})

#get all products from current shop
def product_list(request):
    pt_list = ProductType.objects.all()
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
    return render(request,"shop/product_list1.html",locals())

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
    return render(request,"shop/product_list1.html",locals())

# show product info
def product(request, pid):
    product = Product.objects.filter(id=pid).first()
    comments = Comment.objects.filter(product_id=product.id).order_by('-create_time')
    from user.models import User
    for comment in comments:
        user = User.objects.get(id=comment.user_id)
        comment.image = user.avatar
        comment.username = user.username
    return render(request,"shop/product.html",locals())

def update_product_image(request,pid):
    product = Product.objects.get(id=pid)
    if request.method == "POST":
        image = request.FILES.get("image")
        if image:
            product.image = image
            messages.add_message(request,messages.SUCCESS,'商品图片修改成功',extra_tags='success')
        product.save()

        return HttpResponseRedirect('/shop/product/'+str(pid)+'/')
    show_image = product.image
    return render(request,'image_update.html',locals())

#update product info
@csrf_exempt
def update_product(request, pid):
    p = Product.objects.filter(id=pid).first()
    if request.method == "POST":
        postdata = request.POST
        name = postdata.get("name")
        price = postdata.get("price")
        description = postdata.get("description")
        stock = postdata.get("stock")

        p.name = name
        p.price = price
        p.description = description
        p.stock = stock
        p.save()
        messages.add_message(request,messages.SUCCESS,'商品信息修改成功',extra_tags='success')
        return JsonResponse({'status':'success'})
    return JsonResponse({'status':'error'})

#change product state
def change_product_state(request,state):
    print('商品状态更改')
    if state == "up":
        state_num = 1
    else:
        state_num = 0
    id = request.GET.get("id")
    print(state,id)
    referer = request.META.get("HTTP_REFERER")
    if id:
        product = Product.objects.filter(id=id).first()
        if state == "delete":
            print("delete",id)
            product.delete()
            messages.add_message(request,messages.SUCCESS,'商品删除成功',extra_tags='success')
        else:
            product.on_sale = state_num
            product.save()
            messages.add_message(request,messages.SUCCESS,'状态已经变更',extra_tags='success')
    return HttpResponseRedirect(referer)

def order_list(request):
    user_id = request.COOKIES.get("shop_userId")
    shop = Shop.objects.get(userId=user_id)
    orders = Order.objects.filter(order_shop=shop.id).order_by('-order_date')

    for o in orders:
        o.item_list = OrderItem.objects.filter(order=o)
        pro_list = []
        for pro in o.item_list:
            prod = Product.objects.get(id=pro.product_id)
            pro.image = prod.image
            pro.desc = prod.description


    return render(request,"shop/order_list.html",locals())

@csrf_exempt
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
        messages.add_message(request,messages.SUCCESS,'商品类型添加成功',extra_tags='success')
        return JsonResponse({'status':'success'})
    return JsonResponse({'status':'error'})

def ptype_delete(request, ptid):
    ptype = ProductType.objects.get(id=ptid)
    ptype.delete()
    messages.add_message(request,messages.SUCCESS,'商品类型删除成功',extra_tags='success')
    return HttpResponseRedirect('/shop/product_types/')

@csrf_exempt
def coupon_add(request,pid):
    print('add coupom')
    if request.is_ajax():
        postdata = request.POST
        discount = postdata.get('discount')

        new_coupon = Coupon()
        new_coupon.create_time = timezone.now()
        new_coupon.discount = discount
        new_coupon.product_id = pid
        new_coupon.save()

        favs = Favorite.objects.filter(product_id=pid)
        shop_id = request.COOKIES.get('shop_userId')
        for fav in favs:
            new_message = Message()
            new_message.message_time = timezone.now()
            new_message.message_type = 1
            new_message.from_id = shop_id
            new_message.to_id = fav.user_id
            new_message.content = "您收藏的一款商品降价了"
            new_message.save()
            messages.add_message(request,messages.SUCCESS,'优惠券发布成功',extra_tags='success')
        return JsonResponse({'status':'success'})
    return JsonResponse({'status':'error'})

def coupon_delete(request, cid):
    coupon = Coupon.objects.get(id=cid)
    coupon.delete()
    messages.add_message(request,messages.SUCCESS,'优惠券删除成功',extra_tags='success')
    return HttpResponseRedirect('/shop/coupons/')

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
    user_message_list = Message.objects.filter(message_type=2,to_id=shop_id).order_by('-message_time')[:20]
    from user.models import User
    for me in user_message_list:
        user = User.objects.get(id=me.from_id)
        me.image = user.avatar
        me.name = user.nickname
    return render(request,'shop/messages.html',locals())

def coupons(request):
    shop_id = request.COOKIES.get('shop_registered')
    coupon_list = Coupon.objects.filter(product__shopId_id=shop_id)
    print(coupon_list)
    return render(request,'shop/coupons.html',locals())

def product_types(request):
    pt_list = ProductType.objects.all()
    for pt in pt_list:
        plist = Product.objects.filter(product_type=pt)
        pt.num = len(plist)
    return render(request,'shop/product_types.html',locals())


def extra_info(request,type=0):
    if type == 1:
        shop_id = request.COOKIES.get('shop_registered')
        plist = Product.objects.filter(shopId_id=shop_id).order_by('-sales')
        name_list = []
        sale_list = []
        if len(plist) <= 10:
            for p in plist:
                name_list.append(p.name)
                sale_list.append(p.sales)
        else:
            for i in range(0,9):
                name_list.append(plist.first().name)
                sale_list.append(plist.first().sales)
                plist = plist.exclude(id=plist.first().id)
            sale = 0
            for i in plist:
                sale += i.sales
            name_list.append('其他')
            sale_list.append(sale)
        c = (
            Pie()
            .add("", [list(z) for z in zip(name_list, sale_list)])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="商品销量展示"),
                legend_opts=opts.LegendOpts(type_="scroll",pos_top="20%", pos_left="80%", orient="vertical"),

                toolbox_opts=opts.ToolboxOpts(is_show=True,pos_top="top",pos_left="right",),
            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
            .render("./templates/shop/sales.html")
        )
        return render(request,'shop/sales.html',locals())
    if type == 2:
        shop_list = Shop.objects.all()
        shop_name = []
        shop_earnings = []
        for shop in shop_list:
            shop_name.append(shop.shopName)
            oil = OrderItem.objects.filter(shop_id=shop.id)
            shop_earnings.append(int(sum([oi.total_price for oi in oil])))
        c = (
        Bar({"theme": ThemeType.MACARONS})
        .add_xaxis(shop_name)
        .add_yaxis("销售额", shop_earnings)
        .set_global_opts(
            title_opts={"text": "店铺销售额汇总"},
            toolbox_opts=opts.ToolboxOpts(is_show=True,pos_top="top",pos_left="right",),
        )
        .render("./templates/shop/earning.html")
        )
        return render(request,'shop/earning.html',locals())
    if type == 3:
        x_data = []
        y_earning = []
        y_follows = []
        shop_id = request.COOKIES.get('shop_registered')
        oil = OrderItem.objects.filter(shop_id=shop_id)

        fl = Follow.objects.filter(shop_id=shop_id)
        cdate = timezone.now()
        for i in range(0,7):
            date_now = (cdate - timedelta(days=i))
            print(date_now.day)
            x_data.append(date_now.strftime('%y-%m-%d'))
            oil1 = []
            for oi in oil :
                if oi.order.order_date.day == date_now.day:
                    oil1.append(oi)
                    print(oi.order.order_date.day)
            y_earning.append(int(sum([oi.total_price for oi in oil1])))
            print(oil1)
            fl1 = []
            for f in fl:
                if f.follow_time.day == date_now.day:
                    fl1.append(f)
            print(fl1)
            y_follows.append(len(fl1))
        x_data.reverse()
        y_earning.reverse()
        y_follows.reverse()
        (
            Line(init_opts=opts.InitOpts(width="1400px", height="700px"))
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(
                series_name="销售额变化",
                y_axis=y_earning,
                linestyle_opts=opts.LineStyleOpts(width=2),
            )
            .add_yaxis(
                series_name="关注人数变化", y_axis=y_follows, linestyle_opts=opts.LineStyleOpts(width=2)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="店铺信息变化"),
                toolbox_opts=opts.ToolboxOpts(is_show=True,pos_top="top",pos_left="right",),
            )
            .render("./templates/shop/info_change.html")
        )
        return render(request,'shop/info_change.html',locals())
    return render(request,'shop/extra_info.html',locals())




