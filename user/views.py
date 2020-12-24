import hashlib
import json
import random

from django.core.paginator import Paginator
from django.shortcuts import render, redirect,get_object_or_404
from django.template import RequestContext
from django.core import serializers
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, HttpResponseRedirect, redirect
from user.models import User,Address,OrderItem,Order,CartItem,Favorite,FootPrint
from shop.models import ProductType,Product,Shop,Comment,Follow,Message,Coupon

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
    return "用户" + mac_str

@csrf_exempt
def register(request):
    result = {"status":"error","data":""}
    response = render(request,"user/sign_up.html",locals())
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password1 = request.POST.get("password_confirm")
        email = request.POST.get("email")
        if not (username and password and password1 and email):
            result["data"] = "信息不能为空"
            response = JsonResponse({"data":result})
            return response
        user = User.objects.filter(username=username).first()

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

    response = render(request,"user/login.html",{'result': json.dumps(result)})
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
                    response.set_cookie("user_username", user.username)
                    response.set_cookie("user_userId", user.id)

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
        c_user = request.COOKIES.get("user_username")
        if c_user:
            return fun(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/login/")
    return inner

#@loginValid
def index(request):
    product_type_list = ProductType.objects.all()
    best_sales = Product.objects.all().order_by('-sales')[:8]
    product_list1 = Product.objects.all().order_by('-createdDate')[:6]
    product_list2 = Product.objects.all().order_by('price')[:6]
    return render(request,"user/index.html",locals())

def exit(request):
    response = HttpResponseRedirect("/login/")
    for key in request.COOKIES:
        response.delete_cookie(key)
    #del request.session["user_username"]
    # 跳转到登录
    return response

@loginValid
def user_info(request):
    user_id = request.COOKIES.get("user_userId")
    user = User.objects.filter(id=user_id).first()
    address_list = Address.objects.filter(user_id=user)
    order_list = Order.objects.filter(order_user=user)
    return render(request,"user/user_info.html",locals())

def user_update(request):
    user_id = request.COOKIES.get("user_userId")
    user = User.objects.filter(id=user_id).first()
    if request.method == "POST":
        nickname = request.POST.get("nickname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("contact_address")
        image = request.FILES.get("avatar")

        user.nickname = nickname
        user.email = email
        user.phone = phone
        user.contact_address = address
        if image:
            user.avatar = image
        user.save()
        return HttpResponseRedirect("/user_info/")
    return render(request, "user/user_update.html",locals())

@csrf_exempt
def user_avatar_update(request):
    user_id = request.COOKIES.get("user_userId")
    user = User.objects.filter(id=user_id).first()
    if request.method == "POST":
        image = request.FILES.get("image")
        print(image)
        if image:
            user.avatar = image
            messages.add_message(request,messages.SUCCESS,'头像修改成功',extra_tags='success')
        user.save()

        return HttpResponseRedirect('/user_info/')
    show_image = user.avatar
    return render(request,'image_update.html',locals())

@csrf_exempt
def user_info_update(request):
    user_id = request.COOKIES.get("user_userId")
    user = User.objects.filter(id=user_id).first()
    if request.method == "POST":
        nickname = request.POST.get("nickname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        user.nickname = nickname
        user.email = email
        user.phone = phone
        user.save()
        messages.add_message(request,messages.SUCCESS,'个人信息修改成功',extra_tags='success')

        return  JsonResponse({"status":"success"})
    return  JsonResponse({"status":"error"})


@csrf_exempt
def user_password_update(request):
    user_id = request.COOKIES.get("user_userId")
    user = User.objects.filter(id=user_id).first()
    data = ""
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        current_password = setPassword(current_password)
        new_password = request.POST.get("new_password")
        new_password_confirm = request.POST.get("new_password_confirm")

        if not (current_password and new_password and new_password_confirm) :
            data = '信息不能为空'
            return  JsonResponse({"status":"error",'data':data})
        if current_password != user.password:
            data = '当前密码输入错误'
            return  JsonResponse({"status":"error",'data':data})
        if new_password != new_password_confirm:
            data = '确认密码输入错误'
            return  JsonResponse({"status":"error",'data':data})
        user.password = setPassword(new_password)
        user.save()
        messages.add_message(request,messages.SUCCESS,'密码修改成功',extra_tags='success')

        return  JsonResponse({"status":"success",'data':data})
    return  JsonResponse({"status":"error",'data':data})


def user_coupon(request):
    user_id = request.COOKIES.get("user_userId")
    follows = Follow.objects.filter(user_id=user_id)
    coupons = []
    product_names = {}
    shop_names = {}
    for follow in follows:
        coupon = Coupon.objects.filter(product__shopId_id=follow.shop.id)
        for c in coupon:
            product_names[c.product.id] = c.product.name
            shop_names[c.product_id] = c.product.shopId.shopName
            coupons.append(c)
    cps = serializers.serialize('json',coupons)
    pns = json.dumps(product_names)
    sns = json.dumps(shop_names)
    return render(request, "user/user_coupon.html",{
        'coupons':mark_safe(cps),
        'product_names':mark_safe(pns),
        'shop_names':mark_safe(sns)
    })

def user_address(request):
    user_id = request.COOKIES.get("user_userId")
    user = User.objects.filter(id=user_id).first()
    address_list = Address.objects.filter(user_id=user)
    adds = serializers.serialize('json',address_list)
    return render(request,"user/user_address.html",{
        'address_list' : mark_safe(adds)
    })

@csrf_exempt
def add_address(request):
    user_id = request.COOKIES.get("user_userId")
    user = User.objects.filter(id=user_id).first()
    '''
    address = models.TextField(verbose_name="收货地址")
    receiver = models.CharField(max_length=32, verbose_name="收货人")
    receive_phone = models.CharField(max_length=32, verbose_name="联系电话")
    postNumber = models.CharField(max_length=32, verbose_name="邮编")
    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="用户ID")
    '''
    if request.is_ajax():
        address = request.POST.get("address")
        receiver = request.POST.get('receiver')
        receiver_phone = request.POST.get('phone')
        #post_num = request.POST.get('post_num')

        add = Address()
        add.address = address
        add.receiver = receiver
        add.receive_phone = receiver_phone
        add.postNumber = "100000"
        add.user_id = user
        add.save()
        messages.add_message(request,messages.SUCCESS,'地址添加成功',extra_tags='success')
        return JsonResponse({"status":"success"})
    return JsonResponse({"status":"error"})

@csrf_exempt
def address_update(request,add_id):
    """
    address = models.TextField(verbose_name="收货地址")
    receiver = models.CharField(max_length=32, verbose_name="收货人")
    receive_phone = models.CharField(max_length=32, verbose_name="联系电话")
    postNumber = models.CharField(max_length=32, verbose_name="邮编")
    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="用户ID")
    """

    print('hello')
    add = Address.objects.get(id=add_id)
    if request.is_ajax():
        print('ajax request')
        address = request.POST.get("address")
        receiver = request.POST.get('receiver')
        receiver_phone = request.POST.get('phone')
        #post_num = request.POST.get('post_num')

        add.address = address
        add.receiver = receiver
        add.receive_phone = receiver_phone
        #add.postNumber = post_num
        add.save()
        messages.add_message(request,messages.SUCCESS,'地址修改成功',extra_tags='success')
        return JsonResponse({"status":"success"})
    return JsonResponse({"status":"error"})

def address_delete(request,add_id):
    add = Address.objects.get(id=add_id)
    add.delete()
    messages.add_message(request,messages.SUCCESS,'地址删除成功',extra_tags='success')
    return HttpResponseRedirect('/user_address/')

def product_list(request, type_id=0):
    if type_id != 0 :
        current_product_type = ProductType.objects.get(id=type_id)
    else :
        current_product_type = False
    keyword = request.GET.get("keyword","")
    if keyword:
        plist = Product.objects.filter(name__contains=keyword)
    else:
        plist = Product.objects.all()
    if type_id != 0 :
        plist = plist.filter(product_type_id=type_id)
    products = serializers.serialize('json',plist)
    return render(request,"user/product_list.html",{
        "product_list":mark_safe(products),
        "keyword": mark_safe('"'+keyword+'"'),
        'current_product_type' : current_product_type,
    })

def product(request,pid):
    product = Product.objects.get(id=pid)
    comment_name_list = {}
    comment_image_list = {}
    comment_list = Comment.objects.filter(product=product)
    for comment in comment_list:
        user = User.objects.get(id=comment.user_id)
        comment_name_list[comment.user_id] = user.nickname
        comment_image_list[comment.user_id] = str(user.avatar)
    user_id = request.COOKIES.get('user_userId')
    if user_id :
        new_foot_print = FootPrint()
        new_foot_print.user_id = user_id
        new_foot_print.product_id = pid
        new_foot_print.create_time = timezone.now()
        new_foot_print.save()
    favorite = Favorite.objects.filter(user_id=user_id,product_id=pid).first()
    if favorite:
        favorited = True
    else:
        favorited = False
    follow = Follow.objects.filter(user_id=user_id,shop=product.shopId).first()
    if follow:
        shop_followed = True
    else:
        shop_followed = False
    coupon = Coupon.objects.filter(product_id=pid).first()
    if coupon:
        on_sale = True
        product.on_sale_price = product.price - coupon.discount
    else:
        on_sale = False
    return render(request,"user/product.html",{
        'favorited' : favorited,
        'shop_followed' : shop_followed,
        'on_sale' : on_sale,
        'product' : product,
        'comment_list': mark_safe(serializers.serialize('json',comment_list)),
        'comment_name_list': mark_safe(json.dumps(comment_name_list)),
        'comment_image_list' : mark_safe(json.dumps(comment_image_list)),

    })

def add_to_cart(request,pid):
    print("add to cart")
    user_id = request.COOKIES.get('user_userId')
    user = User.objects.get(id=user_id)
    cart_item = CartItem.objects.filter(cart_user=user,product_id=pid).first()
    if cart_item:
        print("exist")
        cart_item.product_number += 1
        cart_item.total_price += cart_item.product_price
        cart_item.save()
    else:
        print('not exist')
        cart_item = CartItem()
        cart_item.cart_user = user
        current_product = Product.objects.get(id=pid)
        cart_item.product_id = pid
        cart_item.product_name = current_product.name
        cart_item.product_number = 1
        cart_item.shop_id = current_product.shopId.id
        cart_item.product_name = current_product.name
        cart_item.product_price = current_product.price
        cart_item.total_price = current_product.price
        cart_item.save()
    messages.add_message(request,messages.SUCCESS,'已添加到购物车',extra_tags='success')
    return  HttpResponseRedirect('/product/%s'%pid)

def delete_cart_item(request,pid):
    print("delete cart item")
    user_id = request.COOKIES.get('user_userId')
    user = User.objects.get(id=user_id)
    cart_item = CartItem.objects.filter(cart_user=user,product_id=pid).first()
    if cart_item.product_number > 1:
        print("exist")
        cart_item.product_number -= 1
        cart_item.total_price -= cart_item.product_price
        cart_item.save()
    else:
        cart_item.delete()
    messages.add_message(request,messages.SUCCESS,'已经移出购物车',extra_tags='success')
    return  HttpResponseRedirect('/cart/')

def get_random_str():
    send = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    mac_str = ''
    for i in range(10):
        mac_str += random.choice(send)
    return mac_str

def generate_order_id(user_id,shop_id):
    date = timezone.datetime.now()
    return str(date.strftime('%y%m%d')) + get_random_str()


@loginValid
def cart(request):
    user_id = request.COOKIES.get("user_userId")
    user = User.objects.get(id=user_id)
    cart_item_list = CartItem.objects.filter(cart_user=user)
    cart_item_image_list = {}
    for ci in cart_item_list:
        pro = Product.objects.get(id=ci.product_id)
        cart_item_image_list[ci.product_id] = str(pro.image)

    total_price = sum([ci.total_price for ci in cart_item_list])
    if request.method == "POST":
        return HttpResponseRedirect('/checkout/')

    cart_items = serializers.serialize('json',cart_item_list)
    cart_item_images = json.dumps(cart_item_image_list)
    return render(request,"user/cart.html",{
        'total_price':total_price,
        'cart_items':mark_safe(cart_items),
        'cart_item_images': mark_safe(cart_item_images)
                                                 })
cart_rec = {}

@csrf_exempt
def process_cart_info(request):
    global cart_rec
    if request.is_ajax():
        item_list = request.POST
        print(item_list)
        cart_rec = {}
        i = 0
        for k in item_list:
            if i == 0:
                key = int(item_list[k])
            else:
                cart_rec[key] = int(item_list[k])
            i = 1 - i
        print(cart_rec)
        user_id = request.COOKIES.get("user_userId")
        user = User.objects.get(id=user_id)
        cart_item_list = CartItem.objects.filter(cart_user=user)
        for i in cart_item_list:
            if i.product_id in cart_rec.keys():
                i.product_number = cart_rec[i.product_id]
                i.total_price = i.product_price * i.product_number
                i.save()
            else:
                i.delete()
        cart_item_list = CartItem.objects.filter(cart_user=user)
        print(cart_item_list)
        return JsonResponse({"status":"success","data":"yes"})
    return JsonResponse({"status":"error","data":"no"})

@csrf_exempt
def gen_order(request):
    global cart_rec
    print("gen_order")
    print(cart_rec)
    user_id = request.COOKIES.get("user_userId")
    user = User.objects.get(id=user_id)
    cart_item_list = CartItem.objects.filter(cart_user=user)
    address_list = Address.objects.filter(user_id=user)
    order_list = {}

    for ci in cart_item_list:
        shop_name = Shop.objects.get(id=ci.shop_id)
        pro = Product.objects.get(id=ci.product_id)
        ci.image = pro.image
        ci.desc = pro.description
        coupon = Coupon.objects.filter(product_id=ci.product_id).first()
        if coupon:
            ci.discount = coupon.discount
            ci.distp = (ci.product_price - ci.discount) * ci.product_number
        else:
            ci.distp = ci.total_price
        if order_list.get(shop_name):
            order_list.get(shop_name).append(ci)
        else:
            order_list[shop_name] = [ci]
    total_price = sum([ci.distp for ci in cart_item_list])
    order_number = len(order_list)
    product_number = len(cart_item_list)
    if request.is_ajax():
        address = request.POST.get("address_id")
        order_id_list = []
        print(order_list)
        for k,v in order_list.items():
            new_order = Order()
            pro_list = v
            order_id = generate_order_id(user_id,k)
            new_order.order_id = order_id
            order_id_list.append(order_id)
            new_order.order_user = user
            new_order.order_shop = pro_list[0].shop_id
            new_order.order_price = sum([pro.product_price for pro in pro_list])
            new_order.order_address = Address.objects.filter(id=address).first()
            new_order.order_date = timezone.now()
            new_order.order_status = 0 # 已下单
            new_order.save()
            for ci in pro_list:
                coupon = Coupon.objects.filter(product_id=ci.product_id).first()
                oi = OrderItem()
                oi.order = new_order
                oi.product_id = ci.product_id
                oi.shop_id = ci.shop_id
                oi.product_name = ci.product_name
                oi.product_number = ci.product_number
                if coupon :
                    oi.product_price = ci.product_price - coupon.discount
                else :
                    oi.product_price = ci.product_price
                oi.total_price = oi.product_number * oi.product_price
                oi.save()
                cp = Product.objects.get(id=ci.product_id)
                cp.sales += ci.product_number
                cp.save()
            new_message = Message()
            new_message.message_type = 2
            new_message.message_time = timezone.now()
            new_message.from_id = new_order.order_user.id
            new_message.to_id = new_order.order_shop
            new_message.content = "有用户下单了"
            new_message.save()
            CartItem.objects.filter(cart_user=user).delete()
        #return render(request,'user/place_order_success.html',{'order_list': order_id_list})
            return JsonResponse({'status':'success'})

    adds = serializers.serialize('json',address_list)

    return render(request,"user/checkout.html",{
        'addresses':mark_safe(adds),
        'order_list':order_list,
        'product_number':product_number,
        'total_price':total_price
    })

def order(request,order_id):
    order = Order.objects.get(id=order_id)
    order_item_list = OrderItem.objects.filter(order=order)

    return render(request,"user/order.html",locals())

#收货
def receive_product(request,order_id):
    corder = Order.objects.get(id=order_id)
    corder.order_status = 2
    corder.save()
    new_message = Message()
    new_message.message_type = 2
    new_message.message_time = timezone.now()
    new_message.from_id = corder.order_user.id
    new_message.to_id = corder.order_shop
    new_message.content = "卖家已经收货"
    new_message.save()
    referer = request.META.get("HTTP_REFERER")
    return  HttpResponseRedirect(referer)

#完成订单
def finish_order(request,order_id):
    corder = Order.objects.get(id=order_id)
    corder.order_status = 3
    corder.save()
    referer = request.META.get("HTTP_REFERER")
    return  HttpResponseRedirect(referer)

##催促商家发货
def urge_shipment(request, order_id):
    order = Order.objects.get(id=order_id)
    new_message = Message()
    new_message.message_type = 2
    new_message.from_id = order.order_user.id
    new_message.to_id = order.order_shop
    new_message.message_time = timezone.now()
    new_message.content = "有用户在催促您发货"
    new_message.save()
    referer = request.META.get("HTTP_REFERER")
    return  HttpResponseRedirect(referer)

def set_order_status(request,order_id,status):
    corder = Order.objects.get(id=order_id)
    old_status = corder.order_status
    corder.order_status = status
    corder.save()
    if old_status == 0 and status == 1:
        new_message = Message()
        new_message.message_type = 1
        new_message.message_time = timezone.now()
        new_message.from_id = corder.order_shop
        new_message.to_id = corder.order_user.id
        new_message.content = "您的订单已经发货"
        new_message.save()
    elif old_status == 1 and status == 2:
        new_message = Message()
        new_message.message_type = 2
        new_message.message_time = timezone.now()
        new_message.from_id = corder.order_user.id
        new_message.to_id = corder.order_shop
        new_message.content = "卖家已经收货"
        new_message.save()
    elif old_status == 2 and status == 3:
        new_message = Message()
        new_message.message_type = 1
        new_message.message_time = timezone.now()
        new_message.from_id = corder.order_shop
        new_message.to_id = corder.order_user.id
        new_message.content = "您有一个订单需要评价"
        new_message.save()

    return render(request,"user/order_list.html",locals())

@loginValid
def order_list(request):
    user_id = request.COOKIES.get("user_userId")
    user = User.objects.get(id=user_id)
    orders = Order.objects.filter(order_user=user).order_by('-order_date')
    order_pro_list = {}
    shop_name_list = {}
    pro_desc_list = {}
    pro_image_list = {}

    for o in orders:
        shop = Shop.objects.get(id=o.order_shop)
        shop_name_list[shop.id] = shop.shopName
        o.shop_name = shop.shopName
        o.item_list = OrderItem.objects.filter(order=o)
        pro_list = []
        for pro in o.item_list:
            prod = Product.objects.get(id=pro.product_id)
            pro_image_list[pro.product_id] = str(prod.image)
            pro_desc_list[pro.product_id] = prod.description
            pro_list.append(pro)
        pro_list = serializers.serialize('json',pro_list)
        order_pro_list[o.id] = pro_list


    orders = serializers.serialize('json',orders)
    opl = json.dumps(order_pro_list)
    snl = json.dumps(shop_name_list)
    pdl = json.dumps(pro_desc_list)
    pil = json.dumps(pro_image_list)
    return render(request,"user/order_list.html",{
        'orders': mark_safe(orders),
        'order_pro_list' : mark_safe(opl),
        'shop_name_list':mark_safe(snl),
        'pro_desc_list':mark_safe(pdl),
        'pro_image_list' : mark_safe(pil)
    })

def place_order_success(request):

    return render(request,'user/place_order_success.html',locals())

@csrf_exempt
@loginValid
def comment(request, pid):
    user_id = request.COOKIES.get('user_userId')
    product = get_object_or_404(Product,id=pid)
    content = request.POST.get('content')
    score = request.POST.get('score')
    comment = Comment()
    comment.content = content
    comment.score = score
    comment.user_id = user_id
    comment.product = product
    comment.create_time = timezone.now()

    comment.save()

    messages.add_message(request,messages.SUCCESS,'评论成功',extra_tags='success')

    return JsonResponse({'status':'success'})

@loginValid
def favorite(request):
    user_id = request.COOKIES.get('user_userId')
    favorites = Favorite.objects.filter(user_id=user_id)
    fav_images = {}
    for fav in favorites:
        pro = Product.objects.get(id=fav.product_id)
        fav_images[fav.product_id] = str(pro.image)
    favs = serializers.serialize('json',favorites)
    fis = json.dumps(fav_images)
    return render(request,'user/favorite.html',{
        'favorites' : mark_safe(favs),
        'fav_images' : mark_safe(fis),
    })

@loginValid
def add_to_favorite(request,pid):
    user_id = request.COOKIES.get('user_userId')
    product = Product.objects.get(id=pid)
    favorite = Favorite.objects.filter(user_id=user_id,product_id=pid).first()
    if favorite:
        messages.add_message(request,messages.ERROR,'添加失败',extra_tags='error')
        return  HttpResponseRedirect('/product/%s'%pid)
    else:
        favorite = Favorite()
        favorite.user_id = user_id
        favorite.product_id = product.id
        favorite.create_time = timezone.now()
        favorite.save()
        messages.add_message(request,messages.SUCCESS,'添加成功',extra_tags='success')
        return  HttpResponseRedirect('/product/%s'%pid)

def cancel_favorite(request,pid):
    user_id = request.COOKIES.get('user_userId')
    favorite = Favorite.objects.filter(user_id=user_id,product_id=pid).first()
    favorite.delete()
    messages.add_message(request,messages.SUCCESS,'取消成功',extra_tags='success')
    referer = request.META.get("HTTP_REFERER")
    return  HttpResponseRedirect(referer)

@loginValid
def footprint(request):
    user_id = request.COOKIES.get('user_userId')
    footprints = FootPrint.objects.filter(user_id=user_id).order_by('-create_time')[:24]
    print(footprints)
    for fp in footprints:
        pro = Product.objects.get(id=fp.product_id)
        fp.image = pro.image
    return render(request,'user/footprint.html',locals())

def shop_info(request, sid):
    current_shop = Shop.objects.filter(id=sid).first()
    products = Product.objects.filter(shopId=current_shop)
    return render(request,'user/shop_info.html',locals())

@loginValid
def follow_shop(request, sid):
    user_id = request.COOKIES.get('user_userId')
    new_follow = Follow()
    new_follow.user_id = user_id
    shop = Shop.objects.get(id=sid)
    new_follow.shop = shop
    new_follow.follow_time = timezone.now()
    new_follow.save()
    messages.add_message(request,messages.SUCCESS,'关注'+shop.shopName+'成功',extra_tags='success')
    referer = request.META.get("HTTP_REFERER")
    return  HttpResponseRedirect(referer)

def cancel_follow(request, sid):
    user_id = request.COOKIES.get('user_userId')
    cur_follow = Follow.objects.filter(user_id=user_id,shop_id=sid)
    cur_follow.delete()
    messages.add_message(request,messages.SUCCESS,'取消关注成功',extra_tags='success')
    referer = request.META.get("HTTP_REFERER")
    return  HttpResponseRedirect(referer)

@loginValid
def message_list(request):
    user_id = request.COOKIES.get('user_userId')
    user_message_list = Message.objects.filter(message_type=1,to_id=user_id).order_by('-message_time')
    shop_name_dict = {}
    shop_image_dict = {}
    for message in user_message_list:
        shop_id = message.from_id
        shop = Shop.objects.get(id=shop_id)
        shop_name_dict[shop_id] = shop.shopName
        shop_image_dict[shop_id] = str(shop.avatar)
    uml = serializers.serialize('json', user_message_list)
    return render(request,'user/message_list.html',{
        'message_list' : mark_safe(uml),
        'shop_names' : mark_safe(json.dumps(shop_name_dict)),
        'shop_images' : mark_safe(json.dumps(shop_image_dict)),
    })

