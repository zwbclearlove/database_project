import hashlib

from django.core.paginator import Paginator
from django.shortcuts import render, redirect,get_object_or_404
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, redirect
from user.models import User,Address,OrderItem,Order,Cart,CartItem,Favorite
from shop.models import ProductType,Product,Shop,Comment

# Create your views here.
def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result

def register(request):
    result = {"status":"error","data":""}
    response = render(request,"user/sign_up.html",locals())
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password1 = request.POST.get("password1")
        email = request.POST.get("email")
        nickname = request.POST.get("nickname")
        user = User.objects.filter(username=username).first()
        if user:
            result["data"] = "用户名已存在"
            response = render(request, "user/sign_up.html", locals())
            return response
        if password1 != password:
            result["data"] = "两次密码不匹配"
            response = render(request, "user/sign_up.html", locals())
            return response
        user = User()
        user.username = username
        user.password = setPassword(password)
        user.email = email
        user.nickname = nickname
        user.save()
        return HttpResponseRedirect('/login/')
    return response

def login(request):
    result = {"status":"error","data":""}

    response = render(request,"user/login.html",locals())
    response.set_cookie("user_login_from","legitimate")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            user = User.objects.filter(username=username).first()
            if user:
                web_password = setPassword(password)

                cookies = request.COOKIES.get("user_login_from")
                print(web_password," ",user.password)
                if web_password == user.password and cookies == "legitimate":
                    result["status"] = "success"
                    result["data"] = "登录成功"
                    response = HttpResponseRedirect('/index/',locals())
                    response.set_cookie("user_username", user.username)
                    response.set_cookie("user_userId", user.id)
                    request.session["user_username"] = user.username

                    return response
                else:
                    result["data"] = "密码错误"
                    response = render(request, "user/login.html", locals())
            else:
                result["data"] = "用户名不存在"
                response = render(request, "user/login.html", locals())
        else:
            result["data"] = "用户名和密码不能为空"
            response = render(request, "user/login.html", locals())

    return response


def loginValid(fun):
    def inner(request,*args,**kwargs):
        c_user = request.COOKIES.get("user_username")
        s_user = request.session.get("user_username")
        if c_user and s_user and c_user == s_user:
            return fun(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/login/")
    return inner

#@loginValid
def index(request):
    product_type_list = ProductType.objects.all()
    return render(request,"user/index0.html",locals())

def exit(request):
    response = HttpResponseRedirect("/login/")
    for key in request.COOKIES:
        response.delete_cookie(key)
    del request.session["user_username"]
    # 跳转到登录
    return response

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
    if request.method == "POST":
        address = request.POST.get("address")
        receiver = request.POST.get('receiver')
        receiver_phone = request.POST.get('phone')
        post_num = request.POST.get('post_num')

        add = Address()
        add.address = address
        add.receiver = receiver
        add.receive_phone = receiver_phone
        add.postNumber = post_num
        add.user_id = user
        add.save()
        return HttpResponseRedirect('/user_info/')
    return render(request, "user/address_add.html",locals())

def address_update(request,add_id):
    """
    address = models.TextField(verbose_name="收货地址")
    receiver = models.CharField(max_length=32, verbose_name="收货人")
    receive_phone = models.CharField(max_length=32, verbose_name="联系电话")
    postNumber = models.CharField(max_length=32, verbose_name="邮编")
    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="用户ID")
    """
    add = Address.objects.get(id=add_id)
    if request.method == "POST":
        address = request.POST.get("address")
        receiver = request.POST.get('receiver')
        receiver_phone = request.POST.get('phone')
        post_num = request.POST.get('post_num')

        add.address = address
        add.receiver = receiver
        add.receive_phone = receiver_phone
        add.postNumber = post_num
        add.save()
        return HttpResponseRedirect('/user_info/')
    return render(request, "user/address_update.html",locals())

def address_delete(request,add_id):
    add = Address.objects.get(id=add_id)
    add.delete()
    return HttpResponseRedirect('/user_info/')

def product_list(request):
    keywords = request.GET.get("keywords","")
    page_num = request.GET.get("page_num",1)
    if keywords:
        plist = Product.objects.filter(name__contains=keywords)
    else:
        plist = Product.objects.all()
    paginator = Paginator(plist,8)
    page = paginator.page(int(page_num))
    page_range = paginator.page_range
    return render(request,"user/product_list.html",locals())

def product(request,pid):
    product = Product.objects.get(id=pid)
    comment_list = Comment.objects.filter(product=product)
    for comment in comment_list:
        user = User.objects.get(id=comment.user_id)
        comment.nickname = user.nickname
    user_id = request.COOKIES.get('user_userId')
    favorite = Favorite.objects.filter(user_id=user_id,product_id=pid).first()
    if favorite:
        favorited = True
    else:
        favorited = False
    return render(request,"user/product.html",locals())

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
    return  HttpResponseRedirect('/cart/')

def generate_order_id(user_id,shop_id):
    date = timezone.datetime.now()
    return str(date) + str(user_id) + str(shop_id)

def cart(request):
    user_id = request.COOKIES.get("user_userId")
    user = User.objects.get(id=user_id)
    cart_item_list = CartItem.objects.filter(cart_user=user)
    for ci in cart_item_list:
        pro = Product.objects.get(id=ci.product_id)
        ci.image = pro.image
    total_price = sum([ci.total_price for ci in cart_item_list])
    if request.method == "POST":
        return HttpResponseRedirect('/checkout/')



    return render(request,"user/cart.html",locals())

def gen_order(request):
    user_id = request.COOKIES.get("user_userId")
    user = User.objects.get(id=user_id)
    cart_item_list = CartItem.objects.filter(cart_user=user)
    address_list = Address.objects.filter(user_id=user)
    order_list = {}
    total_price = sum([ci.total_price for ci in cart_item_list])
    for ci in cart_item_list:
        shop_name = Shop.objects.get(id=ci.shop_id)
        pro = Product.objects.get(id=ci.product_id)
        ci.image = pro.image
        if order_list.get(shop_name):
            order_list.get(shop_name).append(ci)
        else:
            order_list[shop_name] = [ci]
    order_number = len(order_list)
    product_number = len(cart_item_list)
    if request.method == "POST":
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
            new_order.order_address = Address.objects.filter(user_id=user).first()
            new_order.order_date = timezone.now()
            new_order.order_status = 0 # 已下单
            new_order.save()
            for ci in pro_list:
                oi = OrderItem()
                oi.order = new_order
                oi.product_id = ci.product_id
                oi.shop_id = ci.shop_id
                oi.product_name = ci.product_name
                oi.product_number = ci.product_number
                oi.product_price = ci.product_price
                oi.total_price = ci.total_price
                oi.save()
            CartItem.objects.filter(cart_user=user).delete()
        return render(request,'user/place_order_success.html',{'order_list': order_id_list})

    return render(request,"user/checkout.html",locals())
def order(request,order_id):
    order = Order.objects.get(id=order_id)
    order_item_list = OrderItem.objects.filter(order=order)

    return render(request,"user/order.html",locals())

def set_order_status(request,order_id,status):
    corder = Order.objects.get(id=order_id)
    corder.order_status = status
    corder.save()
    return render(request,"user/order_list.html",locals())

def order_list(request,status=5):
    user_id = request.COOKIES.get("user_userId")
    user = User.objects.get(id=user_id)
    if status == 5:
        orders = Order.objects.filter(order_user=user).order_by('-order_date')
    else:
        orders = Order.objects.filter(order_user=user,order_status=status).order_by('-order_date')

    for o in orders:
        shop = Shop.objects.get(id=o.order_shop)
        o.shop_name = shop.shopName
        o.item_list = OrderItem.objects.filter(order=o)
        for pro in o.item_list:
            prod = Product.objects.get(id=pro.product_id)
            pro.image = prod.image
            pro.desc = prod.description
    return render(request,"user/order_list.html",locals())

def place_order_success(request):

    return render(request,'user/place_order_success.html',locals())

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

    messages.add_message(request,messages.SUCCESS,'评论程坤',extra_tags='success')

    return HttpResponseRedirect('/product/%s/'%pid)

def favorite(request):
    user_id = request.COOKIES.get('user_userId')
    favorites = Favorite.objects.filter(user_id=user_id)
    for fav in favorites:
        pro = Product.objects.get(id=fav.product_id)
        fav.image = pro.image
    return render(request,'user/favorite.html',locals())

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

def footprint(request):

    return render(request,'user/footprint.html',locals())

