import random
import urllib2
import json
import collections
import decimal
import time
import xlwt
from collections import OrderedDict
from django.db.models import Sum
from collections import OrderedDict
from collections import Counter
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import datetime
from django import template
from datetime import timedelta
from .models import (Admin_User, Branch, City, Item_Category, Item_Subcategory,
                     Item, Membership, User, Partner, PartnerMenu, Coupons,
                     CouponInfo, ForOrdernumber, AllOrder, PromotionImage,
                     PromotionVideo, Customer, Offer, OfferMenu, OrderSource,
                     PaymentMode, DeliveryCharge, RestrictedAreas, Waiter,
                     CounterTable, CounterOrder, CounterOrdernumber, Expense,
                     ExpenseCollection, PayDeliveryBoy, CollectiontoDelboy,
                     InventoryItem, InventoryDependency, InventoryPurchase,
                     DelBoyCurrentLocation, DelBoyLocationReport, ForDelBoyTripNumber,
                     DelBoyUpdatedTrips, DueCreditInfo, NewsAndEvent, PerItemRateList,
                     LaundryPlans, PickupDropSlots, AppCarousel)


def checkout(request):
    paymentmodes = PaymentMode.objects.all()
    today = datetime.datetime.now()
    context = {'paymentmodes': paymentmodes}
    if 'user' in request.session:
        phone = request.session['user']['phone']
        userstored = User.objects.get(phone=phone)
        user = {}
        user['name'] = userstored.full_name
        user['email'] = userstored.email
        user['phone'] = phone
        user['e_wallet'] = float(userstored.e_wallet)
        user['credit_limit'] = float(userstored.credit_limit)
        if userstored.address is not None:
            user['address'] = userstored.address
        request.session['user'] = user
    if 'offer' in request.session:
        try:
            offer = Offer.objects.get(offer_name=request.session['offer'], is_active=True,
                start_time__lte=datetime.datetime.time(today),
                end_time__gte=datetime.datetime.time(today))
        except Offer.DoesNotExist:
            del request.session['offer']
            return HttpResponseRedirect("/")
    return render(request,'app/infoincheckout.html', context)


from string import Template
from ccavutil import encrypt,decrypt
from ccavResponseHandler import res

accessCode = 'AVNF07CL92BF82FNFB'   
workingKey = 'F06C47C78E0542A1CBDAABC6D0E99634'


def foodpanda_catalog(request):
    # di is a dictionary of items
    di = OrderedDict()
    for c in Item_Category.objects.order_by('item_category'):
        di[c] = OrderedDict()
    for s in Item_Subcategory.objects.order_by('subcategory_name'):
        if s not in di[s.belongs_to_category]:
            di[s.belongs_to_category][s] = OrderedDict()
    for i in Item.objects.filter(active_on_website=True).order_by('item_name'):
        if i.item_code not in di[i.item_category][i.item_subcategory]:
            di[i.item_category][i.item_subcategory][i.item_code] = []
        di[i.item_category][i.item_subcategory][i.item_code].append(i)
    context = {'catalog': di}
    xml = render_to_string('app/foodpanda_catalog.xml', context)
    return HttpResponse(xml)


def index(request):
    if 'orderplaced' in request.session:
        del request.session['orderplaced']
    today = datetime.datetime.now()
    if 'user' in request.session:
        phone = request.session['user']['phone']
        userstored = User.objects.get(phone=phone)
        user = {}
        user['name'] = userstored.full_name
        user['email'] = userstored.email
        user['phone'] = phone
        user['e_wallet'] = float(userstored.e_wallet)
        user['credit_limit'] = float(userstored.credit_limit)
        if userstored.address is not None:
            user['address'] = userstored.address
        request.session['user'] = user
    offer_count = Offer.objects.filter(
        is_active=True, offer_date=datetime.datetime.date(today), start_time__lte=datetime.datetime.time(today),
        end_time__gte=datetime.datetime.time(today)).count()
    if 'cart' in request.session and offer_count:
        del request.session['cart']
    if 'offer' in request.session:
        del request.session['offer']
    if 'carthasoffer' in request.session:
        if 'cart' in request.session:
            del request.session['cart']
        del request.session['carthasoffer']
    if 'partner' not in request.session:
        # ci is a dictionary of category and subcategory
        ci = OrderedDict()
        for category in Item_Category.objects.order_by('item_category'):
            ci[category] = []
        for subcategory in Item_Subcategory.objects.order_by('subcategory_name'):
            if subcategory not in ci[subcategory.belongs_to_category]:
                ci[subcategory.belongs_to_category].append(subcategory)
        # print ci
        # di is a dictionary of items
        di = OrderedDict()
        for c in Item_Category.objects.order_by('item_category'):
            di[c] = OrderedDict()
        for s in Item_Subcategory.objects.order_by('subcategory_name'):
            if s not in di[s.belongs_to_category]:
                di[s.belongs_to_category][s] = OrderedDict()
        for i in Item.objects.filter(active_on_website=True).order_by('item_name'):
            if i.item_code not in di[i.item_category][i.item_subcategory]:
                di[i.item_category][i.item_subcategory][i.item_code] = []
            di[i.item_category][i.item_subcategory][i.item_code].append(i)
    else:
        partner = Partner.objects.get(
            loginid=request.session['partner']['loginid'])
        item_categories = Item_Category.objects.distinct().filter(
            item__partnermenu__partner=partner.id)
        item_subcategories = Item_Subcategory.objects.distinct().filter(
            item__partnermenu__partner=partner.id)
        # ci is a dictionary of category and subcategory
        ci = OrderedDict()
        for category in item_categories.order_by('item_category'):
            ci[category] = []
        for subcategory in item_subcategories.order_by('subcategory_name'):
            if subcategory not in ci[subcategory.belongs_to_category]:
                ci[subcategory.belongs_to_category].append(subcategory)
        # print ci
        # di is a dictionary of items
        di = OrderedDict()
        for c in item_categories.order_by('item_category'):
            di[c] = OrderedDict()
        for s in item_subcategories.order_by('subcategory_name'):
            if s not in di[s.belongs_to_category]:
                di[s.belongs_to_category][s] = OrderedDict()
        for i in PartnerMenu.objects.filter(partner=partner):
            if i.item.item_code not in di[i.item.item_category][i.item.item_subcategory]:
                di[i.item.item_category][i.item.item_subcategory][i.item.item_code] = []
            di[i.item.item_category][i.item.item_subcategory][i.item.item_code].append(i)
    promotion_image = PromotionImage.objects.all()
    promotion_video = PromotionVideo.objects.all()
    paymentmodes = PaymentMode.objects.all()
    booking_offer = Offer.objects.filter(
        is_active=True, applicable_on='Booking',
        offer_date=datetime.datetime.date(today),
        end_time__gte=datetime.datetime.time(today))
    delivery_offer = Offer.objects.filter(
        is_active=True, applicable_on='Delivery',
        offer_date__gte=datetime.datetime.date(today))
    offers = booking_offer | delivery_offer
    orders = AllOrder.objects.exclude(order_status="cancelled")
    del_date = datetime.datetime.date(timezone.now())
    orders = orders.filter(expected_at__startswith=del_date)
    orders = orders.exclude(ordered_items="")
    items = []
    for order in orders:
        d = json.loads(order.ordered_items)
        for i in d.keys():
            if type(d[i]) == dict:
                for j in d[i].keys():
                    if type(d[i][j]) == dict:
                        items.append(d[i][j])
    ordered_items = []
    for item in items:
        item_name = item["name"]+"-"+item["subname"]
        ordered_items.append(item_name)
    ordered_items_final = {}
    for item in ordered_items:
        if item in ordered_items_final.keys():
            continue
        else:
            ordered_items_final[item] = ordered_items.count(item)
    all_sorted = sorted(ordered_items_final, key=ordered_items_final.__getitem__)
    top_10_trending = all_sorted[:10]
    news_event_list = NewsAndEvent.objects.all()
    context = {'items': di, 'category_dict': ci,
               'promotion_image': promotion_image,
               'promotion_video': promotion_video, 'news_event_list': news_event_list,
               'offers': offers, "paymentmodes": paymentmodes, "top_10_trending": top_10_trending}
    return render(request, 'app/index.html', context)


def offerindex(request, offer_id, offer_day):
    today = datetime.datetime.now()
    try:
        offer = Offer.objects.get(id=offer_id,offer_date=datetime.datetime.date(today),
            start_time__lte=datetime.datetime.time(today),end_time__gte=datetime.datetime.time(today))
    except Offer.DoesNotExist:
        return HttpResponseRedirect("/")
    if 'cart' in request.session:
        del request.session['cart']
    item_categories = Item_Category.objects.distinct().filter(
        item__offermenu__offer=offer_id, item__offermenu__daytime=offer_day).order_by('item_category')
    item_subcategories = Item_Subcategory.objects.distinct().filter(
        item__offermenu__offer=offer_id, item__offermenu__daytime=offer_day).order_by('subcategory_name')
    # ci is a dictionary of category and subcategory
    ci = OrderedDict()
    for category in item_categories:
        ci[category] = []
    for subcategory in item_subcategories:
        if subcategory not in ci[subcategory.belongs_to_category]:
            ci[subcategory.belongs_to_category].append(subcategory)
    # di is a dictionary of items
    di = OrderedDict()
    for c in item_categories:
        di[c] = OrderedDict()
    for s in item_subcategories:
        if s not in di[s.belongs_to_category]:
            di[s.belongs_to_category][s] = OrderedDict()
    request.session['offer_day_full'] = offer_day
    offer_day_string = str(offer_day)
    values = offer_day_string.split('_')
    offer_day_day = values[0]
    offer_day_time = values[1]
    request.session['offer'] = offer.offer_name
    request.session['offer_coupon'] = offer.are_coupon_applied
    request.session['offer_day'] = offer_day_day
    request.session['offer_time'] = offer_day_time
    request.session['offer_payment_mode'] = offer.payment_mode
    for i in OfferMenu.objects.filter(offer=offer, daytime=offer_day).order_by('item'):
        if i.item.item_code not in di[i.item.item_category][i.item.item_subcategory]:
            di[i.item.item_category][i.item.item_subcategory][i.item.item_code] = []
        di[i.item.item_category][i.item.item_subcategory][i.item.item_code].append(i)
    promotion_image = PromotionImage.objects.all()
    promotion_video = PromotionVideo.objects.all()
    paymentmodes = PaymentMode.objects.all()
    context = {'category_dict': ci, 'items': di,
               'promotion_image': promotion_image,
               'promotion_video': promotion_video,
               'offer': offer, "paymentmodes": paymentmodes}
    return render(request, 'app/offerindex.html', context)


def clearsession(request):
    if 'partner' in request.session:
        request.session.flush()
        return HttpResponseRedirect("/partnerloginpage/")
    if 'admin' in request.session:
        request.session.flush()
        return HttpResponseRedirect("/adminloginpage/")
    request.session.flush()
    return HttpResponseRedirect("/")


def adminloginpage(request):
    return render(request, 'app/adminloginpage.html')


def myadmin_neworder(request):
    if 'admin' not in request.session:
        return HttpResponseRedirect("/adminloginpage/")
    order_source = OrderSource.objects.all()
    paymentmodes = PaymentMode.objects.all()
    restrictareas = RestrictedAreas.objects.all()
    return render(
        request, 'app/myadmin_neworder.html',
        {'order_source': order_source, 'paymentmodes': paymentmodes,
         'restrictareas': restrictareas})


def partnerloginpage(request):
    return render(request, 'app/partnerloginpage.html')


def checkoutpage(request):
    return render(request, 'app/checkoutpage.html')


def contactus(request):
    return render(request, 'app/contactus.html')


def team(request):
    return render(request, 'app/team.html')


def currenttracking(request):
    currentlocations = DelBoyCurrentLocation.objects.all()
    return render(request, 'app/currenttracking.html', {'currentlocations': currentlocations})


def apply_for_credit(request):
    return render(request, 'app/apply_for_credit.html')


def order_cancel_confirm_page(request, order_number):
    return render(request, 'app/order_cancel_confirm_page.html',
        {'order_number': order_number})


def reopen_coupon(coupon_number):
    coupon = CouponInfo.objects.get(coupon_number=coupon_number)
    coupon.blocked = True
    coupon.save()


def order_cancel_by_customer(request, order_number):
    order = AllOrder.objects.get(order_number=order_number)
    diff = order.expected_at - timezone.now()
    diff_minutes = diff.seconds / 60
    if order.expected_at > timezone.now():
        try:
            coupon = CouponInfo.objects.get(order_number=order_number)
        except CouponInfo.DoesNotExist:
            coupon = False
        if (order.expected_at.date() == order.placed_at.date()):
            if diff_minutes > 30:
                order.order_status = 'cancelled'
                order.save()
                if coupon:
                    reopen_coupon(coupon.coupon_number)
                return render(request, 'app/order_sucessfully_cancel.html')
        else:
            if diff_minutes > 180:
                order.order_status = 'cancelled'
                order.save()
                if coupon:
                    reopen_coupon(coupon.coupon_number)
                return render(request, 'app/order_sucessfully_cancel.html')
    return render(request, 'app/order_not_cancelled.html')


def adminlogin(request):
    username = request.POST['username']
    password = request.POST['password']
    try:
        user = Admin_User.objects.get(loginid=username)
        if user.password == password:
            admin = {}
            admin['loginid'] = user.loginid
            admin['role'] = user.roles
            admin['name'] = user.first_name + ' ' + user.last_name
            admin['branch'] = user.branch.branch
            request.session['admin'] = admin
            if not user.roles == 'deliveryboy':
                if user.roles == 'billinguser':
                    return HttpResponseRedirect("/myadmin/counterorder/")
                else:
                    return HttpResponseRedirect("/myadmin/")
            else:
                request.session['loginnotallow'] = "true"
                return HttpResponseRedirect("/adminloginpage/")
        else:
            return HttpResponseRedirect("/adminloginpage/")
    except Admin_User.DoesNotExist:
        return HttpResponseRedirect("/adminloginpage/")


def partnerlogin(request):
    loginid = request.POST['loginid']
    password = request.POST['password']
    try:
        partner_stored = Partner.objects.get(loginid=loginid)
        if partner_stored.password == password:
            partner = {}
            partner['loginid'] = loginid
            partner['name'] = partner_stored.name
            partner['address'] = partner_stored.address
            partner['e_wallet'] = float(partner_stored.e_wallet)
            partner['my_counter'] = float(partner_stored.my_counter)
            partner['credit_limit'] = float(partner_stored.credit_limit)
            request.session['partner'] = partner
            return HttpResponseRedirect("/")
        else:
            return HttpResponseRedirect("/partnerloginpage/")
    except Partner.DoesNotExist:
        return HttpResponseRedirect("/partnerloginpage/")


def myadmin(request):
    if 'admin' not in request.session:
        return HttpResponseRedirect("/adminloginpage/")
    loginid = request.session['admin']['loginid']
    admin_user = Admin_User.objects.get(loginid=loginid)
    if admin_user.roles == 'branchuser':
        allorders = AllOrder.objects.filter(branch_assigned=admin_user.branch)
    else:
        allorders = AllOrder.objects.all()
    # allorders = allorders.exclude(delivery_type='Table')
    today = datetime.datetime.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today = today.replace(hour=23, minute=59, second=59, microsecond=0)
    active_orders = allorders.filter(
        paid_at=None, expected_at__lte=today,
        expected_at__gt=today_start).exclude(
        order_status="cancelled").order_by('expected_at')
    active_orders = active_orders.exclude(order_status="dispatched")
    orders_completed = allorders.filter(
        paid_at__lte=today, paid_at__gt=today_start).exclude(
        delivered_at=None).order_by('order_number')
    cancelled_orders = allorders.filter(
        order_status="cancelled", placed_at__lte=today,
        placed_at__gte=today_start).order_by('order_number')
    forthcoming_orders = allorders.filter(
        paid_at=None, expected_at__gt=today).exclude(
        order_status="cancelled").order_by('expected_at')
    exception_orders = allorders.filter(
        paid_at=None, expected_at__lt=today_start).exclude(
        order_status="cancelled").order_by('expected_at')
    dispatched_orders = allorders.filter(
        order_status="dispatched", paid_at=None).exclude(
        order_status="cancelled").order_by('expected_at')
    branches = Branch.objects.all()
    deliveryboys = Admin_User.objects.filter(roles='deliveryboy')
    paymentmodes = PaymentMode.objects.all()
    today_orders = {}
    orders = AllOrder.objects.filter(
        placed_at__lte=today, placed_at__gte=today_start)
    today_orders['booked'] = orders.filter(order_status="just placed").count()
    today_orders['assigned'] = orders.filter(
        order_status="assigned to branch").count()
    today_orders['accepted'] = orders.filter(order_status="accepted").count()
    today_orders['dispatched'] = orders.filter(
        order_status="dispatched").count()
    today_orders['delivered'] = orders.filter(order_status="delivered").count()
    today_orders['cancelled'] = orders.filter(order_status="cancelled").count()
    today_orders['onlinepayment'] = orders.filter(
        payment_mode="Online Pay").count()
    today_orders['cod'] = orders.filter(payment_mode="Cash on Delivery").count()
    today_orders['paid'] = orders.exclude(paid_at=None).count()
    return render(
        request, 'app/myadmin.html',
        {"active_orders": active_orders, "branches": branches,
         "deliveryboys": deliveryboys, "orders_completed": orders_completed,
         'cancelled_orders': cancelled_orders,
         'forthcoming_orders': forthcoming_orders,
         'exception_orders': exception_orders,
         'dispatched_orders': dispatched_orders,
         'today_orders': today_orders, "paymentmodes": paymentmodes})


@csrf_exempt
def updatedashboard(request):
    if 'admin' not in request.session:
        return HttpResponseRedirect("/adminloginpage/")
    loginid = request.session['admin']['loginid']
    admin_user = Admin_User.objects.get(loginid=loginid)
    if admin_user.roles == 'branchuser':
        allorders = AllOrder.objects.filter(branch_assigned=admin_user.branch)
    else:
        allorders = AllOrder.objects.all()
    # allorders = allorders.exclude(delivery_type='Table')
    today = datetime.datetime.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today = today.replace(hour=23, minute=59, second=59, microsecond=0)
    active_orders = allorders.filter(
        paid_at=None, expected_at__lte=today,
        expected_at__gt=today_start).exclude(
        order_status="cancelled").order_by('expected_at')
    active_orders = active_orders.exclude(order_status="dispatched")
    orders_completed = allorders.filter(
        paid_at__lte=today, paid_at__gt=today_start).exclude(
        delivered_at=None).order_by('order_number')
    cancelled_orders = allorders.filter(
        order_status="cancelled", placed_at__lte=today,
        placed_at__gte=today_start).order_by('order_number')
    forthcoming_orders = allorders.filter(
        paid_at=None, expected_at__gt=today).exclude(
        order_status="cancelled").order_by('expected_at')
    exception_orders = allorders.filter(
        paid_at=None, expected_at__lt=today_start).exclude(
        order_status="cancelled").order_by('expected_at')
    dispatched_orders = allorders.filter(
        order_status="dispatched", paid_at=None).exclude(
        order_status="cancelled").order_by('expected_at')
    branches = Branch.objects.all()
    deliveryboys = Admin_User.objects.filter(roles='deliveryboy')
    paymentmodes = PaymentMode.objects.all()
    html = render_to_string(
        'app/updatedashboard.html',
        {"active_orders": active_orders, "branches": branches,
         "deliveryboys": deliveryboys, "orders_completed": orders_completed,
         "cancelled_orders": cancelled_orders,
         "forthcoming_orders": forthcoming_orders,
         "exception_orders": exception_orders,
         'dispatched_orders': dispatched_orders,
         "paymentmodes": paymentmodes},
        RequestContext(request))
    return HttpResponse(html)


def applicationsetup(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    return render(request, 'app/applicationsetup.html')


# ======================Admin panel Check Online Order ====================
def checkonlineorderpage(request):
    return render(request, 'app/checkonlineorder.html')


def checkonlineorder(request):
    order_number = request.POST['order_number']
    url = request.POST['url']
    try:
        if 'orderdoesnotexist' in request.session:
            request.session.pop('orderdoesnotexist')
        order = AllOrder.objects.get(order_number=order_number)
        request.session['cart'] = json.loads(order.ordered_items)
        return render(request, 'app/onlineorderdetail.html', {'order': order})
    except AllOrder.DoesNotExist:
        request.session['orderdoesnotexist'] = 'true'
        return HttpResponseRedirect(url)


# ======================== Application Setup admin ============================
def applicationsetup_admin(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    alladmins = Admin_User.objects.all()
    return render(
        request, 'app/applicationsetup_admin.html', {'admins': alladmins})


def adduserpage(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    cities = City.objects.all()
    branches = Branch.objects.all()
    return render(request, 'app/adduserpage.html',
                  {'cities': cities, "branches": branches})


def edituserpage(request, loginid):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    cities = City.objects.all()
    branches = Branch.objects.all()
    admin_user = Admin_User.objects.get(loginid=loginid)
    return render(
        request, 'app/edituserpage.html',
        {'cities': cities, "branches": branches, "admin_user": admin_user})


def createuser(request):
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    loginid = request.POST['loginid']
    email = request.POST['email']
    mobile = request.POST['mobile']
    gender = request.POST['gender']
    password = request.POST['password']
    address = request.POST['address']
    city = City.objects.get(city=request.POST['city'])
    branch = Branch.objects.get(branch=request.POST['branch'])
    company = request.POST['company']
    dateofbirth = request.POST['dateofbirth']
    checks1 = request.POST.get('checks1', False)
    checks2 = request.POST.get('checks2', False)
    role = request.POST['optionsRadios']
    try:
        user = Admin_User.objects.get(loginid=loginid)
    except Admin_User.DoesNotExist:
        Admin_User.objects.create(
            first_name=first_name, last_name=last_name, loginid=loginid,
            email=email, mobile=mobile, gender=gender, password=password,
            address=address, city=city, branch=branch, company=company,
            roles=role, dateofbirth=dateofbirth, is_login_enable=checks2,
            is_attendance_enable=checks1, is_active=True)
    return HttpResponseRedirect("/myadmin/applicationsetup/admin/")


def edituser(request, db_loginid):
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    loginid = request.POST['loginid']
    email = request.POST['email']
    mobile = request.POST['mobile']
    gender = request.POST['gender']
    password = request.POST['password']
    address = request.POST['address']
    city = City.objects.get(city=request.POST['city'])
    branch = Branch.objects.get(branch=request.POST['branch'])
    company = request.POST['company']
    dateofbirth = request.POST['dateofbirth']
    checks1 = request.POST.get('checks1', False)
    checks2 = request.POST.get('checks2', False)
    role = request.POST['optionsRadios']
    Admin_User.objects.filter(loginid=db_loginid).update(
        first_name=first_name, last_name=last_name, loginid=loginid,
        email=email, mobile=mobile, gender=gender, password=password,
        address=address, city=city, branch=branch, company=company,
        roles=role, dateofbirth=dateofbirth, is_login_enable=checks2,
        is_attendance_enable=checks1, is_active=True)
    return HttpResponseRedirect("/myadmin/applicationsetup/admin/")


# ======================= Application Setup customer ==========================
def applicationsetup_customer(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    customer_list = Customer.objects.all()
    paginator = Paginator(customer_list, 200)
    page = request.GET.get('page')
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        customers = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        customers = paginator.page(paginator.num_pages)
    return render(
        request, 'app/applicationsetup_customer.html', {'customers': customers})


def addcustomerpage(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    return render(request, 'app/addcustomerpage.html')


def createcustomer(request):
    name = request.POST['name']
    mobile = request.POST['mobile']
    orders = request.POST['orders']
    address = request.POST['address']
    Customer.objects.create(
        customer_name=name, customer_number=mobile,
        order_number=orders, customer_address=address,
        isblocked=False)
    return HttpResponseRedirect("/myadmin/applicationsetup/customer/")


def edit_customer_info(request):
    url = request.POST['url']
    name = request.POST['name']
    number = request.POST['number']
    orders = request.POST['order_number']
    address = request.POST['address']
    isblocked = request.POST.get('is_blocked', False)
    customer_id = request.POST['customer_id']
    Customer.objects.filter(id=customer_id).update(
        customer_name=name, customer_number=number,
        order_number=orders, customer_address=address,
        isblocked=isblocked)
    return HttpResponseRedirect(url)


def export_customers_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Customers.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Customers')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Customer Name', 'Number', 'Address', 'Blocked', 'Orders',]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Customer.objects.all().values_list(
        'customer_name', 'customer_number', 'customer_address',
        'isblocked', 'order_number')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


# ====================== Application Setup Menu ==============================
def applicationsetup_menu(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    items = Item.objects.all()
    return render(request, 'app/applicationsetup_menu.html', {'items': items})


def additempage(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    item_categories = Item_Category.objects.all()
    item_subcategories = Item_Subcategory.objects.all()
    return render(request, 'app/additem.html',
                  {'items': item_categories,
                   'item_subcategories': item_subcategories})


def createitem(request):
    item_name = request.POST['item_name']
    item_subname = request.POST['item_subname']
    item_code = request.POST['item_code']
    price = request.POST['price']
    serves = request.POST['serves']
    del_time = request.POST.get('del_time', "Immediate")
    advance_pay = request.POST.get('advance_pay', "N.A.")
    discount = request.POST['discount']
    item_description = request.POST['item_description']
    isactive = request.POST.get('isactive', False)
    active_on_website = request.POST.get('active_on_website', False)
    active_on_app = request.POST.get('active_on_app', False)
    active_on_callcenter = request.POST.get('active_on_call_center', False)
    active_on_counter = request.POST.get('active_on_counter', False)
    active_on_outside = request.POST.get('active_on_outside', False)
    item_type = request.POST['item_type']
    image = request.POST['image']
    item_category = Item_Category.objects.get(
        item_category=request.POST['item_category'])
    item_subcategory = Item_Subcategory.objects.get(
        subcategory_name=request.POST['item_subcategory'])
    image = request.POST['image']
    if image:
        Item.objects.create(
            image=image, item_name=item_name, item_subname=item_subname,
            item_code=item_code, price=price, serves=serves, del_time=del_time,
            advance_pay=advance_pay, discount=discount,
            item_description=item_description, item_category=item_category,
            item_subcategory=item_subcategory, is_active=isactive,
            active_on_website=active_on_website, active_on_app=active_on_app,
            active_on_callcenter=active_on_callcenter, active_on_counter=active_on_counter,
            active_on_outside=active_on_outside, item_type=item_type)
    else:
        Item.objects.create(
            item_name=item_name, item_subname=item_subname,
            item_code=item_code, price=price, serves=serves, del_time=del_time,
            advance_pay=advance_pay, discount=discount,
            item_description=item_description, item_category=item_category,
            item_subcategory=item_subcategory, is_active=isactive,
            active_on_website=active_on_website, active_on_app=active_on_app,
            active_on_callcenter=active_on_callcenter, active_on_counter=active_on_counter,
            active_on_outside=active_on_outside, item_type=item_type)
    return HttpResponseRedirect("/myadmin/applicationsetup/menu/")


def edititempage(request, item_id):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    item_categories = Item_Category.objects.all()
    item_subcategories = Item_Subcategory.objects.all()
    item = Item.objects.get(id=item_id)
    return render(
        request, 'app/edititempage.html',
        {'items': item_categories, "item": item,
         'item_subcategories': item_subcategories})


def edititem(request, item_id):
    item_name = request.POST['item_name']
    item_subname = request.POST['item_subname']
    item_code = request.POST['item_code']
    price = request.POST['price']
    serves = request.POST['serves']
    del_time = request.POST.get('del_time', "Immediate")
    advance_pay = request.POST.get('advance_pay', "N.A.")
    discount = request.POST['discount']
    item_description = request.POST['item_description']
    isactive = request.POST.get('isactive', False)
    active_on_website = request.POST.get('active_on_website', False)
    active_on_app = request.POST.get('active_on_app', False)
    active_on_callcenter = request.POST.get('active_on_call_center', False)
    active_on_counter = request.POST.get('active_on_counter', False)
    active_on_outside = request.POST.get('active_on_outside', False)
    item_type = request.POST['item_type']
    item_category = Item_Category.objects.get(
        item_category=request.POST['item_category'])
    item_subcategory = Item_Subcategory.objects.get(
        subcategory_name=request.POST['item_subcategory'])
    image = request.POST['image']
    Item.objects.filter(id=item_id).update(
        image=image, item_name=item_name, item_subname=item_subname,
        item_code=item_code, price=price, serves=serves, del_time=del_time,
        advance_pay=advance_pay, discount=discount,
        item_description=item_description, item_category=item_category,
        item_subcategory=item_subcategory, is_active=isactive,
        active_on_website=active_on_website, active_on_app=active_on_app,
        active_on_callcenter=active_on_callcenter, active_on_counter=active_on_counter,
        active_on_outside=active_on_outside, item_type=item_type)
    return HttpResponseRedirect("/myadmin/applicationsetup/menu/")


def deleteitem(request, item_id):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    item = Item.objects.get(id=item_id)
    item.delete()
    return HttpResponseRedirect("/myadmin/applicationsetup/menu/")


def manage_images_description(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    if 'nosuchitem' in request.session:
        del request.session['nosuchitem']
    if 'yesupdated' in request.session:
        del request.session['yesupdated']
    if request.method == "POST":
        item_code = request.POST['item_code']
        image = request.POST['image']
        description = request.POST['description']
        allitems = Item.objects.filter(item_code=item_code)
        if allitems.count():
            for anitem in allitems:
                anitem.image = image
                anitem.item_description = description
                anitem.save()
            request.session['yesupdated'] = 'True'
        else:
            request.session['nosuchitem'] = 'True'
    return render(request, 'app/manage_images_description.html')


def manage_app_carousel(request):
    if 'imagecodeexists' in request.session:
        del request.session['imagecodeexists']
    if request.method == "POST":
        image_code = request.POST['image_code']
        try:
            AppCarousel.objects.get(image_code=image_code)
            request.session['imagecodeexists'] = 'True'
        except AppCarousel.DoesNotExist:
            image_url = request.POST['image_url']
            AppCarousel.objects.create(image_code=image_code,image_url=image_url)
    allcarousels = AppCarousel.objects.all()
    return render(request, 'app/manage_app_carousel.html', {'allcarousels':allcarousels})


def delete_app_carousel(request, image_code):
    carousel = AppCarousel.objects.get(image_code=image_code)
    carousel.delete()
    return HttpResponseRedirect("/myadmin/manage_app_carousel")


# ================ Application Setup Item Categories =========================
def applicationsetup_item_category(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    items = Item_Category.objects.all()
    return render(
        request, 'app/applicationsetup_item_category.html', {'items': items})


def additemcategorypage(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    return render(request, 'app/additemcategory.html')


def createitemcategory(request):
    item_category = request.POST['item_category']
    description = request.POST['description']
    isactive = request.POST.get('isactive', False)
    ishomedisplay = request.POST.get('ishomedisplay', False)
    image = request.POST['image']
    try:
        item = Item_Category.objects.get(item_category=item_category)
    except Item_Category.DoesNotExist:
        if image:
            Item_Category.objects.create(
                item_category=item_category, description=description, is_active=isactive,
                is_home_display=ishomedisplay, image=image)
        else:
            Item_Category.objects.create(
                item_category=item_category, description=description, is_active=isactive,
                is_home_display=ishomedisplay)
    return HttpResponseRedirect("/myadmin/applicationsetup/itemcategory/")


def edititemcategorypage(request, item_category_id):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    item_category = Item_Category.objects.get(id=item_category_id)
    return render(
        request, 'app/edititemcategorypage.html',
        {"item_category": item_category})


def edititemcategory(request, item_category_id):
    item_category = request.POST['item_category']
    description = request.POST['description']
    isactive = request.POST.get('isactive', False)
    ishomedisplay = request.POST.get('ishomedisplay', False)
    image = request.POST['image']
    Item_Category.objects.filter(id=item_category_id).update(
        item_category=item_category, description=description, is_active=isactive,
        is_home_display=ishomedisplay, image=image)
    return HttpResponseRedirect("/myadmin/applicationsetup/itemcategory/")


def deleteitemcategory(request, item_category_id):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    item_category = Item_Category.objects.get(id=item_category_id)
    item_category.delete()
    return HttpResponseRedirect("/myadmin/applicationsetup/itemcategory/")


def manageitemsubcategory(request, item_category_id):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    category = Item_Category.objects.get(id=item_category_id)
    subcategories = Item_Subcategory.objects.filter(
        belongs_to_category=category)
    return render(
        request, 'app/manage_itemsubcategory.html',
        {'category': category, 'subcategories': subcategories})


def createsubcategory(request, item_category_id):
    url = request.POST['url']
    subcategory_name = request.POST['subcategory']
    category_name = request.POST['category']
    category = Item_Category.objects.get(item_category=category_name)
    try:
        subcategory = Item_Subcategory.objects.get(
            subcategory_name=subcategory_name, belongs_to_category=category)
    except Item_Subcategory.DoesNotExist:
        Item_Subcategory.objects.create(
            subcategory_name=subcategory_name,
            belongs_to_category=category)
    return HttpResponseRedirect(url)


def deletesubcategory(request, subcategory_id, category_id):
    subcategory = Item_Subcategory.objects.get(id=subcategory_id)
    subcategory.delete()
    return HttpResponseRedirect(
        '/myadmin/manageitemsubcategory/' + category_id + '/')


# =================== Application Setup Membership ===========================
def applicationsetup_membership(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    memberships = Membership.objects.all()
    return render(request, 'app/applicationsetup_membership.html',
                  {'memberships': memberships})


def addmembershippage(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    return render(request, 'app/addmembershippage.html')


def createmembership(request):
    membership_id = request.POST['membership_id']
    membership_name = request.POST['membership_name']
    discount = request.POST['discount']
    checks1 = request.POST.get('checks1', False)
    try:
        membership = Membership.objects.get(membership_name=membership_name)
    except Membership.DoesNotExist:
        Membership.objects.create(
            membership_id=membership_id,
            membership_name=membership_name,
            discount=discount,
            is_active=checks1)
    return HttpResponseRedirect("/myadmin/applicationsetup/membership/")


def editmembershippage(request, membership_id):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    membership = Membership.objects.get(membership_id=membership_id)
    return render(
        request, 'app/editmembershippage.html', {'membership': membership})


def editmembership(request, db_membership_id):
    membership_id = request.POST['membership_id']
    membership_name = request.POST['membership_name']
    discount = request.POST['discount']
    checks1 = request.POST.get('checks1', False)
    Membership.objects.filter(membership_id=db_membership_id).update(
        membership_id=membership_id,
        membership_name=membership_name,
        discount=discount,
        is_active=checks1)
    return HttpResponseRedirect("/myadmin/applicationsetup/membership/")


def deletemembership(request, membership_id):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    membership = Membership.objects.get(membership_id=membership_id)
    membership.delete()
    return HttpResponseRedirect("/myadmin/applicationsetup/membership/")


# ================== Application Setup Online Users ==========================
def applicationsetup_online_users(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    users = User.objects.all()
    if 'phone' in request.POST and request.POST['phone'] != "":
        phone = request.POST['phone']
        users = users.filter(phone=phone)
    if 'name' in request.POST and request.POST['name'] != "":
        name = request.POST['name']
        users = users.filter(full_name=name)
    return render(
        request, 'app/applicationsetup_online_users.html', {'users': users})


def addonlineuserpage(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    cities = City.objects.all()
    branches = Branch.objects.all()
    membership_types = Membership.objects.all()
    return render(request, 'app/addonlineuserpage.html',
                  {"cities": cities,
                   "branches": branches,
                   "membership_types": membership_types})


def createonlineuser(request):
    url = request.POST['url']
    full_name = request.POST['name']
    phone = request.POST['phone']
    password = request.POST['password']
    email = request.POST['email']
    gender = request.POST['gender']
    address = request.POST['address']
    city = City.objects.get(city=request.POST['city'])
    company = request.POST['company']
    block_user = request.POST.get('checks1', False)
    credit_limit = request.POST['credit_limit']
    # otp = request.POST['otp']
    membership_type = Membership.objects.get(
        membership_name=request.POST['membership_type'])
    e_wallet = request.POST['e_wallet']
    dateofbirth = request.POST['dateofbirth']
    branch = Branch.objects.get(branch=request.POST['branch'])
    try:
        user = User.objects.get(phone=phone)
        request.session['mobileexistsalready'] = "true"
        return HttpResponseRedirect(url)
    except User.DoesNotExist:
        User.objects.create(
            full_name=full_name, phone=phone, password=password,
            email=email, gender=gender, address=address,
            city=city, company=company, block_user=block_user,
            credit_limit=credit_limit,
            membership_type=membership_type, e_wallet=e_wallet,
            date_of_birth=dateofbirth, branch=branch)
    return HttpResponseRedirect("/myadmin/applicationsetup/online_users/")


def editonlineuserpage(request, phone):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    cities = City.objects.all()
    branches = Branch.objects.all()
    membership_types = Membership.objects.all()
    user = User.objects.get(phone=phone)
    return render(request, 'app/editonlineuserpage.html',
                  {"cities": cities,
                   "branches": branches,
                   "membership_types": membership_types,
                   "user": user})


def editonlineuser(request, db_phone):
    full_name = request.POST['name']
    phone = request.POST['phone']
    password = request.POST['password']
    email = request.POST['email']
    gender = request.POST['gender']
    address = request.POST['address']
    city = City.objects.get(city=request.POST['city'])
    company = request.POST['company']
    block_user = request.POST.get('checks1', False)
    credit_limit = request.POST['credit_limit']
    # otp = request.POST['otp']
    membership_type = Membership.objects.get(
        membership_name=request.POST['membership_type'])
    e_wallet = request.POST['e_wallet']
    dateofbirth = request.POST['dateofbirth']
    branch = Branch.objects.get(branch=request.POST['branch'])
    User.objects.filter(phone=db_phone).update(
        full_name=full_name, phone=phone, password=password,
        email=email, gender=gender, address=address,
        city=city, company=company, block_user=block_user,
        credit_limit=credit_limit,
        membership_type=membership_type, e_wallet=e_wallet,
        date_of_birth=dateofbirth, branch=branch)
    return HttpResponseRedirect("/myadmin/applicationsetup/online_users/")


def export_onlineusers_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Online_Users.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Full Name', 'Phone', 'Password', 'Email', 
               'Gender', 'Address', 'City', 'Company', 'Blocked',
               'Credit Limit', 'Membership Type', 'E-Wallet',
               'Date of Birth', 'Branch']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = User.objects.all().values_list(
        'full_name', 'phone', 'password', 'email', 'gender', 'address',
        'city', 'company', 'block_user', 'credit_limit', 'membership_type',
        'e_wallet', 'date_of_birth', 'branch')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


# ==================== Application Setup Partner =============================
def applicationsetup_partner(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    partners = Partner.objects.all()
    return render(
        request, 'app/applicationsetup_partner.html', {'partners': partners})


def addpartnerpage(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    cities = City.objects.all()
    membership_types = Membership.objects.all()
    return render(request, 'app/addpartnerpage.html',
                  {"cities": cities,
                   "membership_types": membership_types})


def editpartnerpage(request, partner_loginid):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    cities = City.objects.all()
    membership_types = Membership.objects.all()
    partner = Partner.objects.get(loginid=partner_loginid)
    return render(request, 'app/editpartnerpage.html',
                  {'cities': cities, "partner": partner,
                   "membership_types": membership_types})


def createpartner(request):
    url = request.POST['url']
    name = request.POST['name']
    loginid = request.POST['loginid']
    password = request.POST['password']
    email = request.POST['email']
    mobile = request.POST['mobile']
    address = request.POST['address']
    city = City.objects.get(city=request.POST['city'])
    partner_name = request.POST['partner_name']
    owner_number = request.POST['owner_number']
    contact_number = request.POST['contact_number']
    service_tax_number = request.POST['service_tax_number']
    vat_number = request.POST['vat_number']
    logo_link = request.POST['logo_link']
    vat_percent = request.POST['vat_percent']
    service_charge_percent = request.POST['service_charge_percent']
    service_tax_percent = request.POST['service_tax_percent']
    e_wallet = request.POST['e_wallet']
    my_counter = request.POST['my_counter']
    credit_limit = request.POST['credit_limit']
    otp_required = request.POST.get('otp_required', False)
    membership_type = Membership.objects.get(
        membership_name=request.POST['membership_type'])
    try:
        partner = Partner.objects.get(loginid=loginid)
        request.session['partnerloginidexistsalready'] = 'true'
        return HttpResponseRedirect(url)
    except Partner.DoesNotExist:
        Partner.objects.create(
            name=name, loginid=loginid, password=password, email=email,
            mobile=mobile, address=address, city=city,
            partner_name=partner_name, owner_number=owner_number,
            contact_number=contact_number, vat_number=vat_number,
            service_tax_number=service_tax_number, logo_link=logo_link,
            vat_percent=vat_percent, e_wallet=e_wallet,
            service_charge_percent=service_charge_percent,
            service_tax_percent=service_tax_percent, my_counter=my_counter,
            credit_limit=credit_limit, otp_required=otp_required,
            membership_type=membership_type)
        return HttpResponseRedirect("/myadmin/applicationsetup/partner/")


def editpartner(request, db_partner_loginid):
    name = request.POST['name']
    loginid = request.POST['loginid']
    password = request.POST['password']
    email = request.POST['email']
    mobile = request.POST['mobile']
    address = request.POST['address']
    city = City.objects.get(city=request.POST['city'])
    partner_name = request.POST['partner_name']
    owner_number = request.POST['owner_number']
    contact_number = request.POST['contact_number']
    service_tax_number = request.POST['service_tax_number']
    vat_number = request.POST['vat_number']
    logo_link = request.POST['logo_link']
    vat_percent = request.POST['vat_percent']
    service_charge_percent = request.POST['service_charge_percent']
    service_tax_percent = request.POST['service_tax_percent']
    e_wallet = request.POST['e_wallet']
    my_counter = request.POST['my_counter']
    credit_limit = request.POST['credit_limit']
    otp_required = request.POST.get('otp_required', False)
    membership_type = Membership.objects.get(
        membership_name=request.POST['membership_type'])
    Partner.objects.filter(loginid=db_partner_loginid).update(
        name=name, loginid=loginid, password=password, email=email,
        mobile=mobile, address=address, city=city,
        partner_name=partner_name, owner_number=owner_number,
        contact_number=contact_number, vat_number=vat_number,
        service_tax_number=service_tax_number, logo_link=logo_link,
        vat_percent=vat_percent, e_wallet=e_wallet,
        service_charge_percent=service_charge_percent,
        service_tax_percent=service_tax_percent, my_counter=my_counter,
        credit_limit=credit_limit, otp_required=otp_required,
        membership_type=membership_type)
    return HttpResponseRedirect("/myadmin/applicationsetup/partner/")


def deletepartner(request, partner_id):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    partner = Partner.objects.get(id=partner_id)
    partner.delete()
    return HttpResponseRedirect("/myadmin/applicationsetup/partner/")


def applicationsetup_partnermenu(request, partner_loginid):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    item_categories = Item_Category.objects.all()
    items = Item.objects.all()
    partner = Partner.objects.get(loginid=partner_loginid)
    partner_items = PartnerMenu.objects.filter(partner=partner)
    return render(
        request, 'app/applicationsetup_partnermenu.html',
        {'items': items, 'partner_items': partner_items,
         'item_categories': item_categories, 'partner': partner})


def createpartneritem(request, partner_loginid):
    item_name = request.POST['item_name']
    item_subname = request.POST['item_subname']
    expected_price = request.POST['expected_price']
    item = Item.objects.get(item_name=item_name, item_subname=item_subname)
    partner = Partner.objects.get(loginid=partner_loginid)
    try:
        partner_item = PartnerMenu.objects.get(item=item, partner=partner)
    except PartnerMenu.DoesNotExist:
        PartnerMenu.objects.create(
            item=item, partner=partner,
            expected_price=expected_price)
    return HttpResponseRedirect(
        '/myadmin/applicationsetup/partnermenu/' + partner.loginid + '/')


def deletepartneritem(request, item_id):
    item = PartnerMenu.objects.get(id=item_id)
    partner = Partner.objects.get(loginid=item.partner.loginid)
    item.delete()
    return HttpResponseRedirect(
        '/myadmin/applicationsetup/partnermenu/' + partner.loginid + '/')


def partnermenuajaxreload(request):
    item_category = request.GET['item_category']
    item_type = request.GET['item_type']
    item_name = request.GET['item_name']
    item_subname = request.GET['item_subname']
    partner_id = request.GET['partner_id']
    item_categories = Item_Category.objects.all()
    partner = Partner.objects.get(id=partner_id)
    current_price = ''
    if (item_category and item_type and item_name and item_subname) or (item_category and item_name and item_subname):
        category_selected = Item_Category.objects.get(
            item_category=item_category)
        items = Item.objects.filter(
            item_name=item_name, item_subname=item_subname)
        current_price = items[0].price
    if (item_category and item_type and item_name) or (item_category and item_name):
        category_selected = Item_Category.objects.get(
            item_category=item_category)
        items = Item.objects.filter(
            item_category=category_selected, item_type=item_type,
            item_name=item_name)
    if item_category and item_type:
        category_selected = Item_Category.objects.get(
            item_category=item_category)
        items = Item.objects.filter(
            item_category=category_selected, item_type=item_type)
    if item_category:
        category_selected = Item_Category.objects.get(
            item_category=item_category)
        items = Item.objects.filter(item_category=category_selected)
    data = {'item_categories': item_categories, 'items': items,
            'partner': partner, 'item_category': item_category,
            'item_type': item_type, 'item_name': item_name,
            'item_subname': item_subname, 'current_price': current_price}
    html = render_to_string('app/partnermenuajaxreload.html', data,
                            RequestContext(request))
    return HttpResponse(html)


# =================== Application Setup Coupons ==============================
def applicationsetup_coupans(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    coupons = Coupons.objects.all()
    return render(
        request, 'app/applicationsetup_coupans.html', {'coupons': coupons})


def addcouponpage(request):
    return render(request, 'app/addcouponpage.html')


def store_couponinfo(num_of_coupons, prefix, suffix, start_from, start_date,
                     end_date, discount_type, discount_value):
    coupon_start = int(start_from)
    num_of_coupons = int(num_of_coupons)
    coupon_end = coupon_start + num_of_coupons * num_of_coupons
    coupons = random.sample(range(coupon_start, coupon_end), num_of_coupons)
    for coupon in coupons:
        coupon_number = prefix + str(coupon) + suffix
        CouponInfo.objects.create(
            coupon_number=coupon_number, prefix=prefix, suffix=suffix,
            start_from=start_from, start_date=start_date, end_date=end_date,
            discount_type=discount_type, discount_amount=discount_value,
            blocked=True)


def createcoupons(request):
    url = request.POST['url']
    num_of_coupons = request.POST['num_of_coupons']
    prefix = request.POST['prefix']
    suffix = request.POST['suffix']
    start_from = request.POST['start_from']
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']
    discount_type = request.POST['discount_type']
    discount_value = request.POST['discount_value']
    is_active = request.POST.get('is_active', False)
    try:
        coupons = Coupons.objects.get(prefix=prefix, suffix=suffix)
        request.session['coupontypeexistalready'] = "true"
        return HttpResponseRedirect(url)
    except Coupons.DoesNotExist:
        Coupons.objects.create(
            num_of_coupons=num_of_coupons, prefix=prefix, suffix=suffix,
            start_from=start_from, start_date=start_date, end_date=end_date,
            discount_type=discount_type, discount_value=discount_value,
            is_active=is_active)
        store_couponinfo(
            num_of_coupons, prefix, suffix, start_from,
            start_date, end_date, discount_type, discount_value)
    return HttpResponseRedirect("/myadmin/applicationsetup/coupons/")


def editcouponspage(request, coupons_id):
    coupon = Coupons.objects.get(id=coupons_id)
    return render(request, 'app/editcouponspage.html', {'coupon': coupon})


def edit_couponinfo(prefix, suffix, start_date, end_date):
    CouponInfo.objects.filter(prefix=prefix, suffix=suffix).update(
        start_date=start_date, end_date=end_date)


def editcoupons(request, coupons_id):
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']
    is_active = request.POST.get('is_active', False)
    Coupons.objects.filter(id=coupons_id).update(
        start_date=start_date, end_date=end_date, is_active=is_active)
    coupon = Coupons.objects.get(id=coupons_id)
    edit_couponinfo(coupon.prefix, coupon.suffix, start_date, end_date)
    return HttpResponseRedirect("/myadmin/applicationsetup/coupons/")


def deletecoupons(request, coupons_id):
    coupons = Coupons.objects.get(id=coupons_id)
    coupons.delete()
    return HttpResponseRedirect('/myadmin/applicationsetup/coupons/')


def couponinfo(request, prefix, suffix):
    coupons = CouponInfo.objects.filter(prefix=prefix, suffix=suffix)
    return render(request, 'app/couponinfo.html', {"coupons": coupons})


def unblockcoupon(request, coupon_number):
    coupon = CouponInfo.objects.get(coupon_number=coupon_number)
    coupon.blocked = True
    prefix = coupon.prefix
    suffix = coupon.suffix
    coupon.save()
    return HttpResponseRedirect(
        '/myadmin/couponinfo/' + prefix + '/' + suffix + '/')


# ================ Application Setup Manage Promotion =======================
def applicationsetup_managepromotion(request):
    promotionimage = PromotionImage.objects.all()
    promotionvideo = PromotionVideo.objects.all()
    return render(
        request, 'app/applicationsetup_manage_promotion.html',
        {'promotionimage': promotionimage, 'promotionvideo': promotionvideo})


def promotionvideo(request):
    video = request.POST['video1']
    try:
        video_url = PromotionVideo.objects.get(id=1)
        video_url.video = video
        video_url.save()
        # PromotionVideo.objects.filter(id=1).update(video=video)
    except PromotionVideo.DoesNotExist:
        PromotionVideo.objects.create(video=video)
    return HttpResponseRedirect('/myadmin/applicationsetup/managepromotion/')


def addpromotionimage(request):
    image_url = request.POST['image']
    PromotionImage.objects.create(
        image_url=image_url)
    return HttpResponseRedirect('/myadmin/applicationsetup/managepromotion/')


def deletepromotionimage(request, image_id):
    image_url = PromotionImage.objects.get(id=image_id)
    image_url.delete()
    return HttpResponseRedirect('/myadmin/applicationsetup/managepromotion/')


# ===================== Application Setup Offers =============================
def applicationsetup_offers(request):
    offers = Offer.objects.all()
    return render(
        request, 'app/applicationsetup_offers.html', {'offers': offers})


def addofferpage(request):
    return render(request, 'app/addofferpage.html')


def createoffer(request):
    url = request.POST['url']
    offer_name = request.POST['offer_name']
    offer_image = request.POST['offer_image']
    applicable_on = request.POST['applicable_on']
    offer_date = request.POST['offer_date']
    start_time = request.POST['start_time']
    end_time = request.POST['end_time']
    description = request.POST['description']
    sunday = request.POST.get('sunday', 'false')
    monday = request.POST.get('monday', 'false')
    tuesday = request.POST.get('tuesday', 'false')
    wednesday = request.POST.get('wednesday', 'false')
    thursday = request.POST.get('thursday', 'false')
    friday = request.POST.get('friday', 'false')
    saturday = request.POST.get('saturday', 'false')
    delivery_days = [sunday, monday, tuesday, wednesday, thursday, friday, saturday]
    cod = request.POST.get('cod', 'false')
    online = request.POST.get('online', 'false')
    smd = request.POST.get('smd', 'false')
    credit = request.POST.get('credit', 'false')
    payment_mode = [cod, online, smd, credit]
    is_active = request.POST.get('is_active', False)
    is_default_membership_applied = request.POST.get('is_default_membership_applied', False)
    are_coupon_applied = request.POST.get('are_coupon_applied', False)
    try:
        offer = Offer.objects.get(offer_name=offer_name)
        request.session['offerexistalready'] = "true"
        return HttpResponseRedirect(url)
    except Offer.DoesNotExist:
        Offer.objects.create(
            offer_name=offer_name, offer_image=offer_image,
            applicable_on=applicable_on, offer_date=offer_date,
            start_time=start_time, end_time=end_time,
            description=description, delivery_days=delivery_days,
            payment_mode=payment_mode, is_active=is_active,
            is_default_membership_applied=is_default_membership_applied,
            are_coupon_applied=are_coupon_applied)
    return HttpResponseRedirect("/myadmin/applicationsetup/offers/")


def editofferpage(request, offer_id):
    offer = Offer.objects.get(id=offer_id)
    return render(request, 'app/editofferpage.html', {'offer': offer})


def editoffer(request, offer_id):
    offer_name = request.POST['offer_name']
    offer_image = request.POST['offer_image']
    applicable_on = request.POST['applicable_on']
    offer_date = request.POST['offer_date']
    start_time = request.POST['start_time']
    end_time = request.POST['end_time']
    description = request.POST['description']
    sunday = request.POST.get('sunday', 'false')
    monday = request.POST.get('monday', 'false')
    tuesday = request.POST.get('tuesday', 'false')
    wednesday = request.POST.get('wednesday', 'false')
    thursday = request.POST.get('thursday', 'false')
    friday = request.POST.get('friday', 'false')
    saturday = request.POST.get('saturday', 'false')
    delivery_days = [sunday, monday, tuesday, wednesday, thursday, friday, saturday]
    cod = request.POST.get('cod', 'false')
    online = request.POST.get('online', 'false')
    smd = request.POST.get('smd', 'false')
    credit = request.POST.get('credit', 'false')
    payment_mode = [cod, online, smd, credit]
    is_active = request.POST.get('is_active', False)
    is_default_membership_applied = request.POST.get('is_default_membership_applied', False)
    are_coupon_applied = request.POST.get('are_coupon_applied', False)
    Offer.objects.filter(id=offer_id).update(
        offer_name=offer_name, offer_image=offer_image,
        applicable_on=applicable_on, offer_date=offer_date,
        start_time=start_time, end_time=end_time,
        description=description, delivery_days=delivery_days,
        payment_mode=payment_mode, is_active=is_active,
        is_default_membership_applied=is_default_membership_applied,
        are_coupon_applied=are_coupon_applied)
    return HttpResponseRedirect("/myadmin/applicationsetup/offers/")


def deleteoffer(request, offer_id):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    offer = Offer.objects.get(id=offer_id)
    offer.delete()
    return HttpResponseRedirect("/myadmin/applicationsetup/offers/")


def applicationsetup_offermenu(request, offer_id):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    item_categories = Item_Category.objects.all()
    items = Item.objects.all()
    offer = Offer.objects.get(id=offer_id)
    offer_items = OfferMenu.objects.filter(offer=offer)
    return render(
        request, 'app/applicationsetup_offermenu.html',
        {'items': items, 'offer_items': offer_items,
         'item_categories': item_categories, 'offer': offer})


def createofferitem(request, offer_id):
    date = request.POST['date']
    daytime = request.POST.get('daytime', False)
    item_name = request.POST['item_name']
    item_subname = request.POST['item_subname']
    discount_percent = request.POST['discount_percent']
    item = Item.objects.get(item_name=item_name, item_subname=item_subname)
    offer = Offer.objects.get(id=offer_id)
    try:
        offer_item = OfferMenu.objects.get(date=date, daytime=daytime, item=item, offer=offer)
    except OfferMenu.DoesNotExist:
        OfferMenu.objects.create(
            date = date, daytime=daytime, item=item, offer=offer,
            discount_percent=discount_percent)
    return HttpResponseRedirect(
        '/myadmin/applicationsetup/offermenu/' + str(offer.id) + '/')


def deleteofferitem(request, item_id):
    item = OfferMenu.objects.get(id=item_id)
    offer = Offer.objects.get(id=item.offer.id)
    item.delete()
    return HttpResponseRedirect(
        '/myadmin/applicationsetup/offermenu/' + str(offer.id) + '/')


def offermenuajaxreload(request):
    item_category = request.GET['item_category']
    item_type = request.GET['item_type']
    item_name = request.GET['item_name']
    item_subname = request.GET['item_subname']
    offer_id = request.GET['offer_id']
    item_categories = Item_Category.objects.all()
    offer = Offer.objects.get(id=offer_id)
    current_price = ''
    if item_category:
        category_selected = Item_Category.objects.get(
            item_category=item_category)
        items = Item.objects.filter(item_category=category_selected)
        if item_category and item_name:
            category_selected = Item_Category.objects.get(
                item_category=item_category)
            items = Item.objects.filter(
                item_category=category_selected, item_name=item_name)
            if item_category and item_name and item_subname:
                category_selected = Item_Category.objects.get(
                    item_category=item_category)
                items = Item.objects.filter(
                    item_name=item_name, item_subname=item_subname)
                current_price = items[0].price
    # if item_category and item_name and item_subname:
    #     category_selected = Item_Category.objects.get(
    #         item_category=item_category)
    #     items = Item.objects.filter(
    #         item_name=item_name, item_subname=item_subname)
    #     current_price = items[0].price
    # if item_category and item_name:
    #     category_selected = Item_Category.objects.get(
    #         item_category=item_category)
    #     items = Item.objects.filter(
    #         item_category=category_selected, item_name=item_name)
    # if item_category and item_type:
    #     category_selected = Item_Category.objects.get(
    #         item_category=item_category)
    #     items = Item.objects.filter(
    #         item_category=category_selected, item_type=item_type)
    # if item_category:
    #     category_selected = Item_Category.objects.get(
    #         item_category=item_category)
    #     items = Item.objects.filter(item_category=category_selected)
    data = {'item_categories': item_categories, 'items': items,
            'offer': offer, 'item_category': item_category,
            'item_type': item_type, 'item_name': item_name,
            'item_subname': item_subname, 'current_price': current_price}
    html = render_to_string('app/offermenuajaxreload.html', data,
                            RequestContext(request))
    return HttpResponse(html)


@csrf_exempt
def get_offerdata(request):
	offer_id = request.POST['offer_id']
	offer = Offer.objects.get(id=offer_id)
	html = render_to_string('app/offer_detail.html', {"offer": offer})
	return HttpResponse(html)


# ===================== Application order source =============================
def ordersource(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    order_source = OrderSource.objects.all()
    return render(
        request, 'app/applicationsetup_ordersource.html',
        {'order_source': order_source})


def addordersource(request):
    source = request.POST['order_source']
    url = request.POST['url']
    try:
        source = OrderSource.objects.get(source=source)
    except OrderSource.DoesNotExist:
        OrderSource.objects.create(source=source)
    return HttpResponseRedirect(url)


def deleteordersource(request, source_id):
    source = OrderSource.objects.get(id=source_id)
    source.delete()
    return HttpResponseRedirect("/myadmin/applicationsetup/ordersource/")


# ===================== Application restricted area ===========================
def restrictedareas(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    rareas = RestrictedAreas.objects.all()
    return render(
        request, 'app/applicationsetup_restrictedareas.html',
        {'rareas': rareas})


def addrestrictedarea(request):
    area = request.POST['area']
    url = request.POST['url']
    try:
        rarea = RestrictedAreas.objects.get(restricted_areas=area)
    except RestrictedAreas.DoesNotExist:
        RestrictedAreas.objects.create(restricted_areas=area)
    return HttpResponseRedirect(url)


def removerestrictedarea(request, area_id):
    area = RestrictedAreas.objects.get(id=area_id)
    area.delete()
    return HttpResponseRedirect("/myadmin/applicationsetup/restrictedareas/")


# =================== Applicationsetup manage waiters ========================
def managewaiter(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    waiters = Waiter.objects.all()
    branch_list = Branch.objects.all()
    return render(
        request, 'app/applicationsetup_waiter.html',
        {'waiters': waiters, 'branch_list': branch_list})


def addnewwaiter(request):
    name = request.POST['name']
    userid = request.POST['userid']
    password = request.POST['password']
    branch = request.POST['branch']
    url = request.POST['url']
    try:
        waiter = Waiter.objects.get(userid=userid)
    except Waiter.DoesNotExist:
        Waiter.objects.create(
            name=name, userid=userid, password=password, branch_name=branch)
    return HttpResponseRedirect(url)


def removewaiter(request, waiter_id):
    waiter = Waiter.objects.get(id=waiter_id)
    waiter.delete()
    return HttpResponseRedirect("/myadmin/applicationsetup/managewaiter/")


# ==================== Applicationsetup manage Tables ========================
def managetables(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    tables = CounterTable.objects.all()
    branches = Branch.objects.all()
    waiter_list = Waiter.objects.all()
    return render(
        request, 'app/applicationsetup_table.html',
        {'tables': tables, 'branches': branches, 'waiter_list': waiter_list})


def addnewtable(request):
    url = request.POST['url']
    branch_name = request.POST['branch_name']
    table_number = request.POST['table_number']
    table_name = request.POST['table_name']
    waiter = Waiter.objects.get(id=request.POST['waiter'])
    max_occupy = request.POST['max_occupy']
    is_active = request.POST.get('is_active', False)
    try:
        table = CounterTable.objects.get(branch_name=branch_name,table_number=table_number)
    except CounterTable.DoesNotExist:
        CounterTable.objects.create(branch_name=branch_name,
            table_number=table_number, table_name=table_name,
            waiter=waiter, max_occupy=max_occupy,
            is_active=is_active, order_number="")
    return HttpResponseRedirect(url)


def edittable(request):
    url = request.POST['url']
    table_id = request.POST['table_id']
    branch_name = request.POST['branch_name']
    table_number = request.POST['table_number']
    table_name = request.POST['table_name']
    waiter = Waiter.objects.get(id=request.POST['waiter'])
    max_occupy = request.POST['max_occupy']
    is_active = request.POST.get('is_active', False)
    CounterTable.objects.filter(id=table_id).update(
        branch_name=branch_name, table_number=table_number,
        table_name=table_name, waiter=waiter,
        max_occupy=max_occupy, is_active=is_active)
    return HttpResponseRedirect(url)


def removetable(request, table_id):
    table = CounterTable.objects.get(id=table_id)
    table.delete()
    return HttpResponseRedirect('/myadmin/applicationsetup/managetables/')


# ======================Applicationsetup manage News And Event===========================
def  manage_news_and_events(request):
    if 'admin' not in request.session or request.session['admin']['role'] != 'admin':
        return HttpResponseRedirect("/adminloginpage/")
    news_event_list = NewsAndEvent.objects.all()
    return render(
        request, 'app/applicationsetup_news_event.html',
        {'news_event_list': news_event_list})


def add_news_event(request):
    url = request.POST['url']
    title = request.POST['title']
    image_url = request.POST['image_url']
    description = request.POST['description']
    try:
        news = NewsAndEvent.objects.get(title=title)
    except NewsAndEvent.DoesNotExist:
        NewsAndEvent.objects.create(title=title,
            image_url=image_url, description=description)
    return HttpResponseRedirect(url)

def delete_news_and_event(request, news_event_id):
    news_object = NewsAndEvent.objects.get(id=news_event_id)
    news_object.delete()
    return HttpResponseRedirect('/myadmin/applicationsetup/manage_news_and_events/')


def edit_news_event(request):
    url = request.POST['url']
    news_id = request.POST['news_id'] 
    title = request.POST['title']
    image_url = request.POST['image_url']
    description = request.POST['description']
    NewsAndEvent.objects.filter(id=news_id).update(title=title,
        image_url=image_url, description=description)
    return HttpResponseRedirect(url)


# ===========================================================================
@csrf_exempt
def additemtocart(request):
    item_code = request.POST['item_code']
    item_subname = request.POST['item_subname']
    # import pdb; pdb.set_trace()
    if 'cart' not in request.session:
        request.session['cart'] = {"totalcost": 0, "grandtotal": 0, "totalcost_actual": 0, "grandtotal_actual": 0}
    cart = request.session['cart']
    if 'ewallet' in request.session:
        if 'offer' in request.session:
            grandtotal = float(cart['grandtotal_actual'])
            grandtotal += float(request.session['ewallet'])
            cart['grandtotal_actual'] = float(grandtotal)
        else:
            grandtotal = float(cart['grandtotal'])
            grandtotal += float(request.session['ewallet'])
            cart['grandtotal'] = float(grandtotal)
        request.session.pop('ewallet')
    item = Item.objects.get(item_code=item_code, item_subname=item_subname)
    if 'partner' in request.session:
        loginid = request.session['partner']['loginid']
        partner = Partner.objects.get(loginid=loginid)
        item = PartnerMenu.objects.get(item=item, partner=partner)
        item_code = str(item.item.item_code)
        if item_code not in cart:
            cart[item_code] = {"name": item.item.item_name}
        thisitem = cart[item_code]
        if item_subname not in thisitem:
            thisitem[item_subname] = {
                "price": item.expected_price, "name": item.item.item_name,
                "discount": item.item.discount, "quantity": 0,
                "subname": item.item.item_subname}
        thisitem[item_subname]['quantity'] += 1
        cart['totalcost'] += int(item.expected_price)
    elif 'offer' in request.session:
        request.session['carthasoffer'] = "True"
        offer_name = request.session['offer']
        offer = Offer.objects.get(offer_name=offer_name)
        item = OfferMenu.objects.get(item=item, offer=offer, daytime=request.session['offer_day_full'])
        item_code = str(item.item.item_code)
        if item_code not in cart:
            cart[item_code] = {"name": item.item.item_name}
        thisitem = cart[item_code]
        if item_subname not in thisitem:
            thisitem[item_subname] = {
                "price": item.get_discount_price(), "price_actual": int(item.item.price),
                "name": item.item.item_name, "discount": item.item.discount, "quantity": 0,
                "subname": item.item.item_subname}
        thisitem[item_subname]['quantity'] += 1
        cart['totalcost'] += int(item.get_discount_price())
        cart['totalcost_actual'] += int(item.item.price)
    else:
        item_code = str(item.item_code)
        if item_code not in cart:
            cart[item_code] = {"name": item.item_name}
        thisitem = cart[item_code]
        if item_subname not in thisitem:
            thisitem[item_subname] = {
                "price": item.price, "name": item.item_name,
                "discount": item.discount, "quantity": 0,
                "subname": item.item_subname}
        thisitem[item_subname]['quantity'] += 1
        cart['totalcost'] += int(item.price)
    cart['grandtotal'] = float(1.05 * float(cart['totalcost']))
    cart['grandtotal_actual'] = float(0.05 * float(cart['totalcost_actual'])) + cart['totalcost']
    cart[item_code] = thisitem
    newcart = {}
    for k in sorted(cart):
        newcart[k] = cart[k]
    request.session['cart'] = newcart
    return JsonResponse({"status": "success"})


@csrf_exempt
def subtractitemtocart(request):
    item_code = request.POST['item_code']
    item_subname = request.POST['item_subname']
    if 'cart' not in request.session or item_code not in request.session['cart'] or item_subname not in request.session['cart'][item_code]:
        return JsonResponse({"noobject": "whyudodis"})
    cart = request.session['cart']
    thisitem = cart[item_code]
    initem = thisitem[item_subname]
    initem['quantity'] -= 1
    thisitem[item_subname] = initem
    cart[item_code] = thisitem
    if initem['quantity'] <= 0:
        thisitem.pop(item_subname)
    if len(thisitem) == 1:
        cart.pop(item_code)
    item = Item.objects.get(item_code=item_code, item_subname=item_subname)
    if 'offer' in request.session:
        offer_name = request.session['offer']
        offer = Offer.objects.get(offer_name=offer_name)
        item = OfferMenu.objects.get(item=item, offer=offer, daytime=request.session['offer_day_full'])
        cart['totalcost'] -= int(item.get_discount_price())
        cart['totalcost_actual'] -= int(item.item.price)
    elif 'partner' in request.session:
        loginid = request.session['partner']['loginid']
        partner = Partner.objects.get(loginid=loginid)
        item = PartnerMenu.objects.get(item=item, partner=partner)
        cart['totalcost'] -= int(item.expected_price)
    else:
        cart['totalcost'] -= int(item.price)
    cart['grandtotal'] = float(1.05 * float(cart['totalcost']))
    cart['grandtotal_actual'] = float(0.05 * float(cart['totalcost_actual'])) + cart['totalcost']
    newcart = {}
    if len(cart) != 2:
        for k in sorted(cart):
            newcart[k] = cart[k]
        request.session['cart'] = newcart
    else:
        request.session.pop('cart')
    if cart['totalcost'] == 0:
        del request.session['cart']
    return JsonResponse({"status": "success"})


def cartajaxreload(request):
    data = {}
    if 'coupon' in request.session:
        try:
            coupon = CouponInfo.objects.get(coupon_number=request.session['coupon'])
            primary_coupon = Coupons.objects.get(
                prefix=coupon.prefix, suffix=coupon.suffix)
            if ((coupon.blocked == True) and (primary_coupon.is_active == True) and (coupon.end_date >= datetime.datetime.now().date())):
                grandtotal = request.session['cart']['grandtotal']
                grandtotal = float(grandtotal)
                if coupon.discount_type == 'Rs':
                    grandtotal -= coupon.discount_amount
                    if grandtotal < 0:
                        grandtotal = 0
                    request.session['coupon_discount'] = "Rs " + str(coupon.discount_amount)
                else:
                    grandtotal -= float((grandtotal * coupon.discount_amount) / 100)
                    request.session['coupon_discount'] = str(coupon.discount_amount) + "%"
                request.session['cart']['grandtotal'] = str(grandtotal)
                request.session['coupon'] = coupon_code
                return JsonResponse({"status": 201})
            else:
                request.session["couponinvalid"] = "true"
        except:
            request.session["couponinvalid"] = "true"
    if 'cart' in request.session:
        cart = request.session['cart']
        newcart = {}
        for k in sorted(cart):
            newcart[k] = cart[k]
        data['cart'] = newcart
    html = render_to_string('app/cartinindex.html', {"data": data})
    return HttpResponse(html)


def checkoutcartajaxreload(request):
    data = {}
    if 'offer' not in request.session:
        today = datetime.datetime.now()
        offers = Offer.objects.filter(
            is_active=True, applicable_on='Booking',
            offer_date=datetime.datetime.date(today), start_time__lte=datetime.datetime.time(today),
            end_time__gte=datetime.datetime.time(today))
        data['offers'] = offers
        html = render_to_string(
            'app/cartincheckout.html', {"data": data, "offers": offers}, RequestContext(request))
    else:
        data['offers'] = False
        html = render_to_string(
            'app/cartincheckout.html', {"data": data}, RequestContext(request))
    return HttpResponse(html)


def infoajaxreload(request):
    paymentmodes = PaymentMode.objects.all()
    html = render_to_string(
        'app/infoincheckout.html', {"paymentmodes": paymentmodes}, RequestContext(request))
    return HttpResponse(html)


def multiply(value, arg):
    return value * arg


# ============================login|signup and user related views===============================
@csrf_exempt
def signup(request):
    url = request.POST['url']
    name = request.POST['name']
    phone = request.POST['phone']
    email = request.POST['email']
    password = request.POST['password']
    gender = request.POST['gender']
    if len(password) < 6:
        request.session['passwordlessthansix'] = "true"
        return HttpResponseRedirect(url)
    if len(phone) != 10:
        request.session['phonenotequaltoten'] = "true"
        return HttpResponseRedirect(url)
    try:
        user = User.objects.get(phone=phone)
        request.session['mobileexistsalready'] = "true"
        return HttpResponseRedirect(url)
    except User.DoesNotExist:
        user = {}
        user['name'] = name
        user['phone'] = phone
        user['email'] = email
        user['password'] = password
        user['gender'] = gender
        user['otp'] = str(random.randint(100000, 999999))
        otp = user['otp']
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(phone)
        messagesendurl += "&message=lhd%20signup%20OTP%3A%20"
        messagesendurl += otp
        messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
        request.session['usersignup'] = user
        request.session['onetimesorry'] = "true"
        return HttpResponseRedirect(url)


@csrf_exempt
def phoneforgotpassword(request):
    url = request.POST['url']
    phone = request.POST['phone']
    try:
        user = User.objects.get(phone=phone)
        user = {}
        user['phone'] = phone
        user['otp'] = str(random.randint(100000, 999999))
        otp = user['otp']
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(phone)
        messagesendurl += "&message=lhd%20forgot%20password%20OTP%3A%20"
        messagesendurl += otp
        messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
        request.session['userforgot'] = user
        request.session['onetimesorryforgot'] = 'true'
        return HttpResponseRedirect(url)
    except:
        request.session['mobiledoesnotexistforgot'] = 'true'
        return HttpResponseRedirect(url)


@csrf_exempt
def login(request):
    url = request.POST['url']
    phone = request.POST['phone']
    password = request.POST['password']
    try:
        userstored = User.objects.get(phone=phone)
        if password == userstored.password:
            if userstored.block_user is False:
                user = {}
                user['name'] = userstored.full_name
                user['email'] = userstored.email
                user['phone'] = phone
                user['e_wallet'] = float(userstored.e_wallet)
                user['credit_limit'] = float(userstored.credit_limit)
                if userstored.address is not None:
                    user['address'] = userstored.address
                request.session['user'] = user
            else:
                request.session['userisblocked'] = 'true'
        else:
            request.session['userinvaild'] = "true"
    except:
        request.session['userinvaild'] = "true"
    return HttpResponseRedirect(url)


def removeerrors(request):
    if 'userinvaild' in request.session:
        request.session.pop('userinvaild')
    if 'mobileexistsalready' in request.session:
        request.session.pop('mobileexistsalready')
    if 'otpinvalid' in request.session:
        request.session.pop('otpinvalid')
    if 'differentrest' in request.session:
        request.session.pop('differentrest')
    if 'previousrest' in request.session:
        request.session.pop('previousrest')
    if 'mobiledoesnotexistforgot' in request.session:
        request.session.pop('mobiledoesnotexistforgot')
    if 'onetimesorryforgot' in request.session:
        request.session.pop('onetimesorryforgot')
    if 'otpinvalidforgot' in request.session:
        request.session.pop('otpinvalidforgot')
    if 'passwordlessthansix' in request.session:
        request.session.pop('passwordlessthansix')
    if 'phonenotequaltoten' in request.session:
        request.session.pop('phonenotequaltoten')
    if 'partnerinvalid' in request.session:
        request.session.pop('partnerinvalid')
    if 'couponinvalid' in request.session:
        request.session.pop('couponinvalid')
    if 'loginnotallow' in request.session:
        request.session.pop('loginnotallow')
    if 'offerexistalready' in request.session:
        request.session.pop('offerexistalready')
    if 'userisblocked' in request.session:
        request.session.pop('userisblocked')
    if 'orderplaced' in request.session:
        request.session.pop('orderplaced')
    if 'insufficientcreditamount' in request.session:
        request.session.pop('insufficientcreditamount')
    return HttpResponse("Awesome")


def removeonetimesorry(request):
    if 'onetimesorry' in request.session:
        request.session.pop('onetimesorry')
    return HttpResponse("Awesome")


def removeoffererror(request):
    if 'offer' in request.session:
        request.session.pop('offer')
    if 'offer_coupon' in request.session:
        request.session.pop('offer_coupon')
    return HttpResponse("Awesome")


@csrf_exempt
def otpverify(request):
    url = request.POST['url']
    otpgot = request.POST['otp']
    if 'usersignup' not in request.session:
        return HttpResponseRedirect(url)
    else:
        usersignup = request.session['usersignup']
        otpstored = usersignup['otp']
        if otpgot != otpstored:
            request.session['otpinvalid'] = "true"
            return HttpResponseRedirect(url)
        else:
            name = usersignup['name']
            phone = usersignup['phone']
            email = usersignup['email']
            password = usersignup['password']
            gender = usersignup['gender']
            request.session.pop('usersignup')
            usersignup.pop('password')
            request.session['user'] = usersignup
            User.objects.create(
                full_name=name, phone=phone, email=email,
                password=password, gender=gender)
            return HttpResponseRedirect(url)


@csrf_exempt
def otpverifyforgot(request):
    url = request.POST['url']
    otp = request.POST['otp']
    password = request.POST['password']
    if 'userforgot' not in request.session:
        return HttpResponseRedirect(url)
    else:
        userforgot = request.session['userforgot']
        otpstored = userforgot['otp']
        phone = userforgot['phone']
        if otp != otpstored:
            request.session['otpinvalidforgot'] = "true"
            return HttpResponseRedirect(url)
        else:
            user = User.objects.get(phone=phone)
            user.password = password
            user.save()
            userst = {}
            userst['phone'] = phone
            userst['email'] = user.email
            userst['name'] = user.full_name
            request.session['user'] = userst
            return HttpResponseRedirect(url)


def userslhdindia(request):
    if 'user' not in request.session:
        return HttpResponseRedirect("/")
    cities = City.objects.all()
    branches = Branch.objects.all()
    membership_types = Membership.objects.all()
    user = User.objects.get(phone=request.session['user']['phone'])
    orders = AllOrder.objects.filter(customer_mobile=request.session['user']['phone'])
    return render(request, 'app/userslhdindia.html',
                  {"cities": cities,
                   "branches": branches,
                   "membership_types": membership_types,
                   "user": user, "orders": orders})


def edituserslhdindia(request, db_phone):
    address = request.POST['address']
    company = request.POST['company']
    dateofbirth = request.POST['dateofbirth']
    User.objects.filter(phone=db_phone).update(
        address=address,company=company,
        date_of_birth=dateofbirth)
    return HttpResponseRedirect("/userslhdindia/")


def addmoneytowallet(request):
    if 'user' not in request.session:
        return HttpResponseRedirect("/")
    if 'cart' in request.session:
        del request.session['cart']
    user = User.objects.get(phone=request.session['user']['phone'])
    orders = AllOrder.objects.filter(customer_mobile=request.session['user']['phone'])
    return render(request, 'app/addmoneytowallet.html', {"user": user})


# ========================= order views ====================================
def placeorder(request):
    today = datetime.datetime.now()
    if 'offer' in request.session:
        try:
            offer = Offer.objects.get(offer_name=request.session['offer'], is_active=True,
                start_time__lte=datetime.datetime.time(today),
                end_time__gte=datetime.datetime.time(today))
        except Offer.DoesNotExist:
            del request.session['offer']
            del request.session['cart']
            return HttpResponseRedirect("/oopsofferover")
    if 'partner' in request.session:
        user = Partner.objects.get(loginid=request.session['partner']['loginid'])
        customer_name = user.name
        customer_mobile = user.mobile
    else:
        user = User.objects.get(phone=request.session['user']['phone'])
        customer_name = user.full_name
        customer_mobile = user.phone
    ordernumberitem = ForOrdernumber.objects.get(pk=1)
    order_number = ordernumberitem.number
    if 'order_number' in request.session:
        del request.session['order_number']
    request.session['order_number'] = order_number
    ordernumberitem.number += 1
    ordernumberitem.save()
    if 'addamount' in request.POST:
        order_status = "just placed"
        onlinepay_status = "pending"
        offer_from_web = "False"
        branch_assigned = ""
        placed_at = datetime.datetime.now()
        expected_at = placed_at + datetime.timedelta(0, 300)
        no_of_people = 'not applicable'
        accepted_by = ""
        dispatched_by = ""
        dispatched_with = ""
        payment_mode = "Online Pay"
        delivery_type = "Home Deliverly"
        source = "Web"
        address = ""
        special_comment = " E-wallet refill request"
        ordered_items = ""
        subtotal = request.POST['addamount']
        ewallet = 0
        coupon_applied = ""
        discount_percent = '0'
        vat_percent = '0'
        service_charge_percent = '0'
        service_tax_percent = '0'
        grand_total = subtotal
        AllOrder.objects.create(
        order_number=order_number, order_status=order_status, onlinepay_status=onlinepay_status,
        offer_from_web=offer_from_web, branch_assigned=branch_assigned,
        placed_at=placed_at, expected_at=expected_at,
        no_of_people=no_of_people, accepted_by=accepted_by,
        dispatched_by=dispatched_by, dispatched_with=dispatched_with,
        payment_mode=payment_mode, delivery_type=delivery_type,
        customer_name=customer_name, customer_mobile=customer_mobile,
        source=source, address=address, special_comment=special_comment,
        ordered_items=ordered_items, subtotal=subtotal, e_wallet=ewallet,
        coupon_applied=coupon_applied, discount_percent=discount_percent,
        vat_percent=vat_percent, service_charge_percent=service_charge_percent,
        service_tax_percent=service_tax_percent, grand_total=grand_total)
        p_merchant_id = "80351"
        p_order_id = str(order_number)
        p_currency = "INR"
        subtotal = grand_total
        p_amount = str(grand_total)
        p_redirect_url = "http://www.lhdindia.com/online_payment_successfull/"  #to be changed
        p_cancel_url = "http://www.lhdindia.com/online_payment_cancel/"    #to be changed
        p_language = "EN"
        p_billing_name = str(user.full_name)
        p_billing_address = str(user.address)
        p_billing_city = str(user.city)
        p_billing_state = "Madhya Pradesh"
        p_billing_zip = "462023"
        p_billing_country = "India"
        p_billing_tel = str(user.phone)
        p_billing_email = str(user.email)
        p_delivery_name = str(user.full_name)
        p_delivery_address = str(user.address)
        p_delivery_city = str(user.city)
        p_delivery_state = "Madhya Pradesh"
        p_delivery_zip = ""
        p_delivery_country = "India"
        p_delivery_tel = str(user.phone)
        p_merchant_param1 = ""
        p_merchant_param2 = ""
        p_merchant_param3 = ""
        p_merchant_param4 = ""
        p_merchant_param5 = ""
        p_promo_code = ""
        p_customer_identifier = ""

        

        merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+'billing_email='+p_billing_email+'&'+'delivery_name='+p_delivery_name+'&'+'delivery_address='+p_delivery_address+'&'+'delivery_city='+p_delivery_city+'&'+'delivery_state='+p_delivery_state+'&'+'delivery_zip='+p_delivery_zip+'&'+'delivery_country='+p_delivery_country+'&'+'delivery_tel='+p_delivery_tel+'&'+'merchant_param1='+p_merchant_param1+'&'+'merchant_param2='+p_merchant_param2+'&'+'merchant_param3='+p_merchant_param3+'&'+'merchant_param4='+p_merchant_param4+'&'+'merchant_param5='+p_merchant_param5+'&'+'promo_code='+p_promo_code+'&'+'customer_identifier='+p_customer_identifier+'&'
        
        encryption = encrypt(merchant_data,workingKey)

        html = '''\
    <html>
    <head>
        <title>Sub-merchant checkout page</title>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
    </head>
    <body>
    <form id="nonseamless" method="post" name="redirect" action="https://secure.ccavenue.com/transaction/transaction.do?command=initiateTransaction" > 
            <input type="hidden" id="encRequest" name="encRequest" value=$encReq>
            <input type="hidden" name="access_code" id="access_code" value=$xscode>
            <script language='javascript'>document.redirect.submit();</script>
    </form>    
    </body>
    </html>
    '''
        fin = Template(html).safe_substitute(encReq=encryption,xscode=accessCode)
        return HttpResponse(fin)
    #######################END OF ADD MONEY TO WALLET##########################    
    cart = request.session['cart']
    payment_mode = request.POST['paymentmode']
    if payment_mode== "Online Pay":
        # order_status = ""
        order_status = "just placed"
        onlinepay_status = 'pending'
    elif payment_mode== "ZUP Pay":
        order_status = "just placed"
        onlinepay_status = 'pending'
    elif payment_mode== "Paytm":
        order_status = "just placed"
        onlinepay_status = 'pending'
    elif payment_mode=="credit":
        order_status = "just placed"
        onlinepay_status = 'pending'
    else:
        order_status = "just placed"
        onlinepay_status = 'NA'
    branch_assigned = ""
    placed_at = datetime.datetime.now()
    accepted_by = ""
    dispatched_by = ""
    dispatched_with = ""
    
    delivery_type = request.POST['delivery_type']
    source = "Web"
    if 'offer' in request.session:
        offer_from_web = "True"
    else:
        offer_from_web = "False"
    special_comment = request.POST['comment']
    ordered_items = json.dumps(cart)
    if 'offer' in request.session:
        subtotal = cart['totalcost_actual']
    if 'offer' not in request.session:
        subtotal = cart['totalcost']
    address = user.address
    if delivery_type == "Home Delivery":
        if 'offer' in request.session:
            offer_day = request.session['offer_day']
            offer_time = request.session['offer_time']
            today_day = datetime.date.today()
            today_weekday = datetime.date.today().weekday()
            #generating offer placement date
            # if offer_day == 'Wednesday':
            #     offer_day_weekday = 2
            #     if (today_weekday - offer_day_weekday) > 0:
            #         days_ahead = today_weekday - offer_day_weekday + 1
            #     if (today_weekday - offer_day_weekday) < 0:
            #         days_ahead = offer_day_weekday - today_weekday
            #     offer_for_day = today_day + timedelta(days=days_ahead)
            if offer_day == 'Thursday':
                offer_day_weekday = 3
                if (today_weekday - offer_day_weekday) > 0:
                    days_ahead = 7 - (today_weekday - offer_day_weekday)
                if (today_weekday - offer_day_weekday) < 0:
                    days_ahead = offer_day_weekday - today_weekday
                offer_for_day = today_day + timedelta(days=days_ahead)
            if offer_day == 'Friday':
                offer_day_weekday = 4
                if (today_weekday - offer_day_weekday) > 0:
                    days_ahead = 7 - (today_weekday - offer_day_weekday)
                if (today_weekday - offer_day_weekday) < 0:
                    days_ahead = offer_day_weekday - today_weekday
                offer_for_day = today_day + timedelta(days=days_ahead)
            if offer_day == 'Saturday':
                offer_day_weekday = 5
                if (today_weekday - offer_day_weekday) > 0:
                    days_ahead = 7 - (today_weekday - offer_day_weekday)
                if (today_weekday - offer_day_weekday) < 0:
                    days_ahead = offer_day_weekday - today_weekday
                offer_for_day = today_day + timedelta(days=days_ahead)
            if offer_day == 'Sunday':
                offer_day_weekday = 6
                if (today_weekday - offer_day_weekday) > 0:
                    days_ahead = 7 - (today_weekday - offer_day_weekday)
                if (today_weekday - offer_day_weekday) < 0:
                    days_ahead = offer_day_weekday - today_weekday
                offer_for_day = today_day + timedelta(days=days_ahead)
            if offer_day == 'Monday':
                offer_day_weekday = 0
                if (today_weekday - offer_day_weekday) > 0:
                    days_ahead = 7 - (today_weekday - offer_day_weekday)
                if (today_weekday - offer_day_weekday) < 0:
                    days_ahead = offer_day_weekday - today_weekday
                offer_for_day = today_day + timedelta(days=days_ahead)
            if offer_day == 'Tuesday':
                offer_day_weekday = 1
                if (today_weekday - offer_day_weekday) > 0:
                    days_ahead = 7 - (today_weekday - offer_day_weekday)
                if (today_weekday - offer_day_weekday) < 0:
                    days_ahead = offer_day_weekday - today_weekday
                offer_for_day = today_day + timedelta(days=days_ahead)
            #generating offer placement time
            if offer_time == 'Lunch':
                offer_for_time = datetime.datetime(offer_for_day.year, offer_for_day.month, offer_for_day.day, 12, 00)
            if offer_time == 'Dinner':
                offer_for_time = datetime.datetime(offer_for_day.year, offer_for_day.month, offer_for_day.day, 18, 00)
            no_of_people = 'not applicable'
            service_tax_percent = "0"
            expected_at = offer_for_time
            street = request.POST['street']
            locality = request.POST['locality']
            city = request.POST['city']
            state = request.POST['state']
            zipcode = request.POST['zipcode']
            country = request.POST['country']
            address = street +', ' +locality+', '+city+', '+state+', '+country+', '+zipcode
            user.address = address
        else:
            no_of_people = 'not applicable'
            service_tax_percent = "0"
            expected_delivery = request.POST.get('deliverRadio')
            if expected_delivery == 'nownow':
                expected_at = placed_at + datetime.timedelta(0, 3000)
            else:
                expected_at = request.POST['expected_date_time']
            if 'partner' not in request.session:
                street = request.POST['street']
                locality = request.POST['locality']
                city = request.POST['city']
                state = request.POST['state']
                zipcode = request.POST['zipcode']
                country = request.POST['country']
                address = street +', ' +locality+', '+city+', '+state+', '+country+', '+zipcode
                user.address = address
            else:
                address = request.session['partner']['address']
    if delivery_type == "Branch Pickup":
        if 'offer' in request.session:
            offer_day = request.session['offer_day']
            offer_time = request.session['offer_time']
            today_day = datetime.date.today()
            today_weekday = datetime.date.today().weekday()
            #generating offer placement date
            # if offer_day == 'Wednesday':
            #     offer_day_weekday = 2
            #     if (today_weekday - offer_day_weekday) > 0:
            #         days_ahead = 7 - (today_weekday - offer_day_weekday)
            #     if (today_weekday - offer_day_weekday) < 0:
            #         days_ahead = offer_day_weekday - today_weekday
            #     offer_for_day = today_day + timedelta(days=days_ahead)
            if offer_day == 'Thursday':
                offer_day_weekday = 3
                if (today_weekday - offer_day_weekday) > 0:
                    days_ahead = 7 - (today_weekday - offer_day_weekday)
                if (today_weekday - offer_day_weekday) < 0:
                    days_ahead = offer_day_weekday - today_weekday
                offer_for_day = today_day + timedelta(days=days_ahead)
            if offer_day == 'Friday':
                offer_day_weekday = 4
                if (today_weekday - offer_day_weekday) > 0:
                    days_ahead = 7 - (today_weekday - offer_day_weekday)
                if (today_weekday - offer_day_weekday) < 0:
                    days_ahead = offer_day_weekday - today_weekday
                offer_for_day = today_day + timedelta(days=days_ahead)
            if offer_day == 'Saturday':
                offer_day_weekday = 5
                if (today_weekday - offer_day_weekday) > 0:
                    days_ahead = 7 - (today_weekday - offer_day_weekday)
                if (today_weekday - offer_day_weekday) < 0:
                    days_ahead = offer_day_weekday - today_weekday
                offer_for_day = today_day + timedelta(days=days_ahead)
            if offer_day == 'Sunday':
                offer_day_weekday = 6
                if (today_weekday - offer_day_weekday) > 0:
                    days_ahead = 7 - (today_weekday - offer_day_weekday)
                if (today_weekday - offer_day_weekday) < 0:
                    days_ahead = offer_day_weekday - today_weekday
                offer_for_day = today_day + timedelta(days=days_ahead)
            if offer_day == 'Monday':
                offer_day_weekday = 0
                if (today_weekday - offer_day_weekday) > 0:
                    days_ahead = 7 - (today_weekday - offer_day_weekday)
                if (today_weekday - offer_day_weekday) < 0:
                    days_ahead = offer_day_weekday - today_weekday
                offer_for_day = today_day + timedelta(days=days_ahead)
            if offer_day == 'Tuesday':
                offer_day_weekday = 1
                if (today_weekday - offer_day_weekday) > 0:
                    days_ahead = 7 - (today_weekday - offer_day_weekday)
                if (today_weekday - offer_day_weekday) < 0:
                    days_ahead = offer_day_weekday - today_weekday
                offer_for_day = today_day + timedelta(days=days_ahead)
            #generating offer placement time
            if offer_time == 'Lunch':
                offer_for_time = datetime.datetime(offer_for_day.year, offer_for_day.month, offer_for_day.day, 12, 00)
            if offer_time == 'Dinner':
                offer_for_time = datetime.datetime(offer_for_day.year, offer_for_day.month, offer_for_day.day, 18, 00)
            no_of_people = 'not applicable'
            service_tax_percent = "0"
            expected_at = offer_for_time
        else:
            no_of_people = 'not applicable'
            service_tax_percent = "0"
            expected_delivery = request.POST.get('deliverRadio')
            if expected_delivery == 'nownownow':
                expected_at = placed_at + datetime.timedelta(0, 3000)
                expected_at = expected_at.replace(microsecond=0)
            else:
                expected_at = request.POST['expected_date_time']
    if delivery_type == "Dining":
        expected_at = request.POST['expected_date_time']
        no_of_people = request.POST['no_of_people']
        service_tax_percent = '6'
    service_charge_percent = "0"
    vat_percent = "5"
    if 'coupon' in request.session:
        coupon_applied = request.session['coupon']
        coupon = CouponInfo.objects.get(coupon_number=coupon_applied)
        coupon.blocked = False
        coupon.order_number = order_number
        coupon.save()
        special_comment += " Coupon Number " + coupon_applied + " successfully applied"
        request.session.pop('coupon')
        if coupon.discount_type == 'persent':
            discount_percent = str(coupon.discount_amount)
        else:
            discount_percent = str((coupon.discount_amount * 100) / float(subtotal))
    else:
        coupon_applied = ""
        discount_percent = '0'
    intsub = int(subtotal)
    service_tax = (intsub * float(service_tax_percent)) / 100
    vat = (intsub * float(vat_percent)) / 100
    service_charge = (intsub * float(service_charge_percent)) / 100
    grand_total = float(intsub + service_tax + vat + service_charge)
    if 'ewallet' in request.session:
        if grand_total > user.e_wallet:
            user.e_wallet = 0
        else:
            user.e_wallet -= decimal.Decimal(grand_total)
        ewallet = float(request.session['ewallet'])
        request.session.pop('ewallet')
    else:
        ewallet = 0
    if 'offer' in request.session:
        offer_name = request.session['offer']
        offer = Offer.objects.get(offer_name=offer_name)
        discount_offer = offer.discount
        discount_percent = discount_offer
        discount = (intsub * float(discount_offer)) / 100
    if 'offer' not in request.session:
        discount = (intsub * float(discount_percent)) / 100
    if discount < (grand_total - ewallet):
        grand_total = float(grand_total - discount - ewallet)
    else:
        grand_total = 0
        grand_total = float(grand_total)
        discount_percent = '100'
    if 'offer' in request.session:
        special_comment += " Placed via Offer Menu"
    if 'partner' in request.session:
        special_comment += " Placed via Partner Menu"
    AllOrder.objects.create(
        order_number=order_number, order_status=order_status, onlinepay_status=onlinepay_status,
        offer_from_web=offer_from_web, branch_assigned=branch_assigned,
        placed_at=placed_at, expected_at=expected_at,
        no_of_people=no_of_people, accepted_by=accepted_by,
        dispatched_by=dispatched_by, dispatched_with=dispatched_with,
        payment_mode=payment_mode, delivery_type=delivery_type,
        customer_name=customer_name, customer_mobile=customer_mobile,
        source=source, address=address, special_comment=special_comment,
        ordered_items=ordered_items, subtotal=subtotal, e_wallet=ewallet,
        coupon_applied=coupon_applied, discount_percent=discount_percent,
        vat_percent=vat_percent, service_charge_percent=service_charge_percent,
        service_tax_percent=service_tax_percent, grand_total=grand_total)
    if decimal.Decimal(grand_total) < 0:
            grand_total = 0
    if 'offer' in request.session:
        offer_name = request.session['offer']
        offer = Offer.objects.get(offer_name=offer_name)
        if offer.is_default_membership_applied:
            membership_discount = (decimal.Decimal(grand_total) * user.membership_type.discount) / 100
            user.e_wallet += membership_discount
    else:
        membership_discount = (decimal.Decimal(grand_total) * user.membership_type.discount) / 100
        user.e_wallet += membership_discount
        if 'partner' in request.session:
            user.my_counter += decimal.Decimal(grand_total)
    user.save()
    if payment_mode == "credit":
        thisorder = AllOrder.objects.get(order_number=order_number)
        if 'user' in request.session:
            hisphone = request.session['user']['phone']
            thisuser = User.objects.get(phone=hisphone)
            if user.credit_limit < grand_total:
                thisorder.onlinepay_status = "insufficient"
                thisorder.save()
                return HttpResponseRedirect("/oopsinsufficientcredit/")
            else:
                thisorder.onlinepay_status = "verifying_otp"
                thisorder.save()
                request.session['orderplaced'] = order_number
                request.session['creditotp'] = str(random.randint(100000, 999999))
                otp = request.session['creditotp']
                messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
                messagesendurl += str(hisphone)
                messagesendurl += "&message=lhdindia%20credit%20verify%20OTP%3A%20"
                messagesendurl += otp
                messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
                req = urllib2.Request(messagesendurl)
                print urllib2.urlopen(req)
                return HttpResponseRedirect("/creditotpverify/")
        if 'partner' in request.session:
            loginid = request.session['partner']['loginid']
            thispartner = Partner.objects.get(loginid=loginid)
            if thispartner.credit_limit < grand_total:
                thisorder.onlinepay_status = "insufficient"
                thisorder.save()
                return HttpResponseRedirect("/oopsinsufficientcredit/")
            else:
                thisorder.onlinepay_status = "verifying_otp"
                thisorder.save()
                request.session['orderplaced'] = order_number
                request.session['creditotp'] = str(random.randint(100000, 999999))
                otp = request.session['creditotp']
                messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
                messagesendurl += str(thispartner.mobile)
                messagesendurl += "&message=lhdindia%20credit%20verify%20OTP%3A%20"
                messagesendurl += otp
                messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
                req = urllib2.Request(messagesendurl)
                print urllib2.urlopen(req)
                return HttpResponseRedirect("/creditotpverify/")
    request.session.pop('cart')
    # if 'partner' in request.session:
    #     request.session['partner']['e_wallet'] = float(user.e_wallet)
    #     request.session['partner']['credit_limit'] = float(user.credit_limit)
    #     request.session['partner']['my_counter'] = float(user.my_counter)
    # else:
    #     request.session['user']['e_wallet'] = float(user.e_wallet)
    #     request.session['user']['credit_limit'] = float(user.credit_limit)
    request.session['orderplaced'] = order_number
    if payment_mode=="Cash on Delivery":
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(customer_mobile)
        messagesendurl += "&message="
        messagesendurl += str(customer_name)
        messagesendurl += ",%20your%20order%20with%20lhdindia%20is%20placed%20"
        messagesendurl += "successfully.%0AAmount%20("
        messagesendurl += str(payment_mode)
        messagesendurl += "):%20" + str(grand_total)
        messagesendurl += "%0ADelivery%20Day%20and%20Time:%20"
        messagesendurl += str(expected_at)
        # messagesendurl += "%0AClick%20on%20below%20link%20to%20cancel%20order%0A"
        # messagesendurl += "www%2Elhdindia%2Ecom%2Fcacel_order_by_customer%2F"
        # messagesendurl += str(order_number)
        messagesendurl += "%2F&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
    if payment_mode=="Online Pay":
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(customer_mobile)
        messagesendurl += "&message="
        messagesendurl += str(customer_name)
        messagesendurl += ",%20Your%20order%20with%20lhdindia%20is%20pending%20"
        messagesendurl += ".%20Please%20complete%20online%20payment%20for%0AAmount%20("
        messagesendurl += str(payment_mode)
        messagesendurl += "):%20" + str(grand_total)
        messagesendurl += "%0ADelivery%20Day%20and%20Time:%20"
        messagesendurl += str(expected_at)
        # messagesendurl += "%0AClick%20on%20below%20link%20to%20cancel%20order%0A"
        # messagesendurl += "www%2Elhdindia%2Ecom%2Fcacel_order_by_customer%2F"
        # messagesendurl += str(order_number)
        messagesendurl += "%2F&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
    if payment_mode=="ZUP Pay":
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(customer_mobile)
        messagesendurl += "&message="
        messagesendurl += str(customer_name)
        messagesendurl += ",%20Your%20order%20with%20lhdindia%20is%20pending%20"
        messagesendurl += ".%20Please%20complete%20ZUP%20payment%20for%0AAmount%20("
        messagesendurl += str(payment_mode)
        messagesendurl += "):%20" + str(grand_total)
        messagesendurl += "%0ADelivery%20Day%20and%20Time:%20"
        messagesendurl += str(expected_at)
        messagesendurl += "%0AZUP%20Vendor%20Code%20is%201060.%20Download%20ZUP%20from%20Google%20Play."
        # messagesendurl += "%0AClick%20on%20below%20link%20to%20cancel%20order%0A"
        # messagesendurl += "www%2Elhdindia%2Ecom%2Fcacel_order_by_customer%2F"
        # messagesendurl += str(order_number)
        messagesendurl += "%2F&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
    if payment_mode=="Paytm":
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(customer_mobile)
        messagesendurl += "&message="
        messagesendurl += str(customer_name)
        messagesendurl += ",%20Your%20order%20with%20lhdindia%20is%20pending%20"
        messagesendurl += ".%20Please%20complete%20Paytm%20transaction%20for%0AAmount%20("
        messagesendurl += str(payment_mode)
        messagesendurl += "):%20" + str(grand_total)
        messagesendurl += "%0ADelivery%20Day%20and%20Time:%20"
        messagesendurl += str(expected_at)
        messagesendurl += "%0ATransfer%20amount%20using%20Paytm%20to%209826267746"
        # messagesendurl += "%0AClick%20on%20below%20link%20to%20cancel%20order%0A"
        # messagesendurl += "www%2Elhdindia%2Ecom%2Fcacel_order_by_customer%2F"
        # messagesendurl += str(order_number)
        messagesendurl += "%2F&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
    if payment_mode=="Online Pay":
        p_merchant_id = "80351"
        p_order_id = str(order_number)
        p_currency = "INR"
        subtotal = cart['totalcost']
        p_amount = str(grand_total)
        p_redirect_url = "http://www.lhdindia.com/online_payment_successfull/"  #to be changed
        p_cancel_url = "http://www.lhdindia.com/online_payment_cancel/"    #to be changed
        p_language = "EN"
        p_billing_name = str(user.full_name)
        p_billing_address = str(user.address)
        p_billing_city = str(user.city)
        p_billing_state = "Madhya Pradesh"
        p_billing_zip = "462023"
        p_billing_country = "India"
        p_billing_tel = str(user.phone)
        p_billing_email = str(user.email)
        p_delivery_name = str(user.full_name)
        p_delivery_address = str(user.address)
        p_delivery_city = str(user.city)
        p_delivery_state = "Madhya Pradesh"
        p_delivery_zip = ""
        p_delivery_country = "India"
        p_delivery_tel = str(user.phone)
        p_merchant_param1 = ""
        p_merchant_param2 = ""
        p_merchant_param3 = ""
        p_merchant_param4 = ""
        p_merchant_param5 = ""
        p_promo_code = ""
        p_customer_identifier = ""

        

        merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+'billing_email='+p_billing_email+'&'+'delivery_name='+p_delivery_name+'&'+'delivery_address='+p_delivery_address+'&'+'delivery_city='+p_delivery_city+'&'+'delivery_state='+p_delivery_state+'&'+'delivery_zip='+p_delivery_zip+'&'+'delivery_country='+p_delivery_country+'&'+'delivery_tel='+p_delivery_tel+'&'+'merchant_param1='+p_merchant_param1+'&'+'merchant_param2='+p_merchant_param2+'&'+'merchant_param3='+p_merchant_param3+'&'+'merchant_param4='+p_merchant_param4+'&'+'merchant_param5='+p_merchant_param5+'&'+'promo_code='+p_promo_code+'&'+'customer_identifier='+p_customer_identifier+'&'
        
        encryption = encrypt(merchant_data,workingKey)

        html = '''\
    <html>
    <head>
        <title>Sub-merchant checkout page</title>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
    </head>
    <body>
    <form id="nonseamless" method="post" name="redirect" action="https://secure.ccavenue.com/transaction/transaction.do?command=initiateTransaction" > 
            <input type="hidden" id="encRequest" name="encRequest" value=$encReq>
            <input type="hidden" name="access_code" id="access_code" value=$xscode>
            <script language='javascript'>document.redirect.submit();</script>
    </form>    
    </body>
    </html>
    '''
        fin = Template(html).safe_substitute(encReq=encryption,xscode=accessCode)
        return HttpResponse(fin)
        #return HttpResponseRedirect("/online_payment/")
    else :
        return HttpResponseRedirect("/confirmationafterplacement/")


@csrf_exempt
def confirmationafterplacement(request):
    if 'orderplaced' not in request.session:
        return HttpResponseRedirect("/")
    return render(request, 'app/confirmationafterplacement.html')


@csrf_exempt
def oopsonlinepayment(request):
    return render(request, 'app/oopsonlinepayment.html')


@csrf_exempt
def oopsinsufficientcredit(request):
    return render(request, 'app/oopsinsufficientcredit.html')


@csrf_exempt
def creditotpverify(request):
    if 'creditotp' not in request.session:
        return HttpResponseRedirect("/")
    return render(request, 'app/creditotpverify.html')


@csrf_exempt
def verifyingotp(request):
    if 'creditotpverify' not in request.POST:
        return HttpResponseRedirect("/")
    otp = request.POST['creditotpverify']
    if otp==request.session['creditotp']:
        thisorder = AllOrder.objects.get(order_number=request.session['orderplaced'])
        if 'user' in request.session:
            thisuser = User.objects.get(phone=thisorder.customer_mobile)
            credit_limit = float(thisuser.credit_limit)
            grand_total = float(thisorder.grand_total)
            credit_limit -= grand_total
            thisuser.credit_limit = credit_limit
            thisorder.onlinepay_status = "success"
            thisuser.save()
            grand_total = str(grand_total)
            DueCreditInfo.objects.create(order_number=request.session['orderplaced'],
                customer_mobile=thisuser.phone,amount_due=grand_total)
        if 'partner' in request.session:
            thispartner = Partner.objects.get(loginid=request.session['partner']['loginid'])
            credit_limit = float(thispartner.credit_limit)
            grand_total = float(thisorder.grand_total)
            credit_limit -= grand_total
            thispartner.credit_limit = credit_limit
            thisorder.onlinepay_status = "success"
            thispartner.save()
            grand_total = str(grand_total)
            DueCreditInfo.objects.create(order_number=request.session['orderplaced'],
                loginid=thispartner.loginid,amount_due=grand_total)
        thisorder.save()
        request.session.pop('cart')
        del request.session['creditotp']
        return HttpResponseRedirect("/confirmationafterplacement/")
    else:
        request.session['wrongcreditotp'] = "True"
        return HttpResponseRedirect("/creditotpverify/")


@csrf_exempt
def oopsofferover(request):
    return render(request, 'app/oopsofferover.html')


@csrf_exempt
def online_payment_successfull(request):
    encResp = request.POST["encResp"]
    order_number = request.POST["orderNo"]
    decResp = decrypt(encResp,workingKey)
    data=str(decResp).split('&')
    data2= data[3].split('=')
    order_status=str(data2[1])
    if order_status=="Success":
        order = AllOrder.objects.get(order_number=order_number)
        order.onlinepay_status= "success"
        if order.ordered_items=="":
            customer_mobile = order.customer_mobile
            user = User.objects.get(phone=customer_mobile)
            user.e_wallet += float(order.grand_total)
            user.save()
        order.save()
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(order.customer_mobile)
        messagesendurl += "&message="
        messagesendurl += str(order.customer_name)
        messagesendurl += ",%20Online%20payment%20for%20your%20order%20has%20been%20successfully%20received.%20Thanks%20for%20choosing%20lhdindia."
        messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
        return HttpResponseRedirect("/confirmationafterplacement/")
    else:
		order = AllOrder.objects.get(order_number=order_number)
		order.onlinepay_status= str(order_status)
		order.save()
		return HttpResponseRedirect("/oopsonlinepayment/")
		 

@csrf_exempt
def onlinepaycancel(request):
    order_number = request.session['order_number']
    order = AllOrder.objects.get(order_number=order_number)
    order.onlinepay_status="cancelled"
    order.save()
    return HttpResponseRedirect("/")


@csrf_exempt
def online_payment_cancel(request):
	# order=AllOrder.objects.get(customer_mobile=request.session['user']['phone'],order_status="")
	# order.order_status="cancel"
	return HttpResponseRedirect("/onlinepaycancel/")


def neworderplacing(request):
    customer_number = request.POST['mobile']
    customer_name = request.POST['name']
    address1 = request.POST['address1']
    try:
        address2 = request.POST['address2']
        try:
            address3 = request.POST['address3']
            customer_address = address1 + ';' + address2 + ';' + address3
        except:
            customer_address = address1 + ';' + address2
    except:
        customer_address = address1
    user = None
    try:
        user = Customer.objects.get(customer_number=customer_number)
    except:
        Customer.objects.create(
            customer_name=customer_name, customer_number=customer_number,
            customer_address=customer_address, isblocked=False,
            order_number="0")
    user = Customer.objects.get(customer_number=customer_number)
    user.customer_address = customer_address
    user.order_number = str(int(user.order_number) + 1)
    user.save()
    cart = {"totalcost": 0, "grandtotal": 0}
    ordernumberitem = ForOrdernumber.objects.get(pk=1)
    order_number = ordernumberitem.number
    ordernumberitem.number += 1
    ordernumberitem.save()
    order_status = "just placed"
    branch_assigned = ""
    placed_at = datetime.datetime.now()
    expected_datetime = request.POST['expecteddatetime']
    if expected_datetime == "":
        expected_at = placed_at + datetime.timedelta(0, 3000)
    else:
        expected_at = expected_datetime
    accepted_by = ""
    dispatched_by = ""
    dispatched_with = ""
    source = request.POST['source']
    delivery_type = request.POST['deltype']
    payment_mode = request.POST['payment_mode']
    if payment_mode == "Online Pay" and source == "Call Center":
        onlinepay_status = "SMS not sent"
    else:
        onlinepay_status = "NA"
    special_comment = ""
    refrence_number = request.POST['ref_number']
    alternate_mobile = request.POST['alt_mobile']
    if not refrence_number == "":
        special_comment += "Refrence Number: " + str(refrence_number)
    if not alternate_mobile == "":
        special_comment += " alternate mobile  " + str(alternate_mobile)
    customer_name = user.customer_name
    customer_mobile = user.customer_number
    orderaddress = request.POST['orderaddress']
    if orderaddress == '1':
        address = address1
    if orderaddress == '2':
        address = address2
    if orderaddress == '3':
        address = address3
    if delivery_type == 'Branch Pickup':
        address = 'Branch Pickup'
    ordered_items = json.dumps(cart)
    subtotal = cart['totalcost']
    coupon_applied = ""
    discount_percent = 0
    vat_percent = "5"
    service_charge_percent = "0"
    service_tax_percent = "0"
    intsub = float(subtotal)
    service_tax = (intsub * float(service_tax_percent)) / 100
    vat = (intsub * float(vat_percent)) / 100
    service_charge = (intsub * float(service_charge_percent)) / 100
    grand_total = float(intsub + service_tax + vat + service_charge)
    AllOrder.objects.create(
        order_number=order_number, order_status=order_status, onlinepay_status=onlinepay_status,
        branch_assigned=branch_assigned,
        placed_at=placed_at,
        expected_at=expected_at, accepted_by=accepted_by,
        dispatched_by=dispatched_by, dispatched_with=dispatched_with,
        payment_mode=payment_mode,
        delivery_type=delivery_type, customer_name=customer_name,
        customer_mobile=customer_mobile, source=source, address=address,
        special_comment=special_comment, ordered_items=ordered_items,
        subtotal=subtotal, coupon_applied=coupon_applied,
        discount_percent=discount_percent, vat_percent=vat_percent,
        service_charge_percent=service_charge_percent,
        service_tax_percent=service_tax_percent, grand_total=grand_total)
    messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
    messagesendurl += str(customer_mobile)
    messagesendurl += "&message=Dear%20"
    messagesendurl += str(customer_name)
    messagesendurl += ",%20thanks%20for%20choosing%20lhdindia%20(lazeez%20hakeem).%0A"
    messagesendurl += "Your%20order%20placement%20is%20being%20processed."
    messagesendurl += "%20You%20shall%20receive%20your%20order%20details%20shortly."
    # messagesendurl += "%0AClick%20on%20below%20link%20to%20cancel%20order%0A"
    # messagesendurl += "www%2Elhdindia%2Ecom%2Fcacel_order_by_customer%2F"
    # messagesendurl += str(order_number)
    messagesendurl += "%2F&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
    req = urllib2.Request(messagesendurl)
    print urllib2.urlopen(req)
    return HttpResponseRedirect("/myadmin/orderdetail/" + str(order_number) + "/")


def orderaddbranch(request, order_number):
    try:
        url = request.POST['url']
    except:
        url = ''
    branch = request.POST['branch']
    order = AllOrder.objects.get(order_number=order_number)
    order.branch_assigned = branch
    order.branch_assigned_at = datetime.datetime.now()
    order.order_status = "assigned to branch"
    order.save()
    if url == '/myadmin/orderdetail/' + order_number + '/':
        return HttpResponseRedirect('/myadmin/neworder/')
    return HttpResponseRedirect("/myadmin/")


@csrf_exempt
def orderaccepted(request, order_number):
    admin_name = request.session['admin']['name']
    order = AllOrder.objects.get(order_number=order_number)
    order.accepted_by = admin_name
    order.accepted_at = datetime.datetime.now()
    order.order_status = "accepted"
    if order.delivery_type == 'Branch Pickup':
        order.dispatched_with = "Branch Pickup"
    order.save()
    return HttpResponseRedirect("/myadmin/")


def ordercancelled(request, order_number):
    cancel_reason = request.POST['cancel_reason']
    order = AllOrder.objects.get(order_number=order_number)
    order.order_status = "cancelled"
    if order.special_comment.strip() != "":
        cancel_reason = ", " + cancel_reason.strip()
    else:
        cancel_reason = cancel_reason.strip()
    order.special_comment += cancel_reason
    order.save()
    try:
        coupon = CouponInfo.objects.get(order_number=order_number)
        reopen_coupon(coupon.coupon_number)
    except CouponInfo.DoesNotExist:
        print "coupan is not applied on this order"
    return HttpResponseRedirect("/myadmin/")


@csrf_exempt
def orderadddel(request, order_number):
    dels = request.POST['del']
    order = AllOrder.objects.get(order_number=order_number)
    order.dispatched_with = dels
    order.order_status = "dispatched"
    order.dispatched_at = datetime.datetime.now()
    order.save()
    messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
    messagesendurl += str(order.customer_mobile)
    messagesendurl += "&message=lhdindia%20Order%20No:%20"
    messagesendurl += str(order_number)
    messagesendurl += "%0AGrand%20Total:%20"
    messagesendurl += str(order.grand_total)
    messagesendurl += "%0APayment%20Mode:%20"
    if order.payment_mode == 'Cash on Delivery':
        messagesendurl += "Cash%20Payment%20to%20Delivery%20Boy"
    else:
        messagesendurl += "Payment%20Already%20Made"
    messagesendurl += "%0ADelivery%20Boy:%20"
    messagesendurl += str(order.dispatched_with)
    messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
    req = urllib2.Request(messagesendurl)
    print urllib2.urlopen(req)
    order_items = json.loads(order.ordered_items)
    for key1, value1 in order_items.iteritems():
        if key1 != 'totalcost' and key1 != 'grandtotal':
            for key2, value2 in value1.iteritems():
                if key2 != 'name':
                    item_code = value2['item_code']
                    subname = value2['subname']
                    qty = value2['quantity']
                    menu_item = Item.objects.get(
                        item_code=item_code, item_subname=subname)
                    dependency_items = InventoryDependency.objects.filter(
                        dependency_name=menu_item)
                    for item in dependency_items:
                        inventory_item = item.inventory_item
                        inventory_item.quantity -= (item.quantity * qty)
                        inventory_item.save()
                        alert_quantity = inventory_item.alert_quantity
                        if inventory_item.quantity <= alert_quantity:
                            messagesendurl = "https://control.msg91.com/api/"
                            messagesendurl += "sendhttp.php?authkey=96244"
                            messagesendurl += "AsR6Os06Hs562e546f&mobiles=91"
                            messagesendurl += str(inventory_item.alert_number)
                            messagesendurl += "&message=Hello%20admin,%0A"
                            messagesendurl += "Please%20pay%20attention,%20"
                            messagesendurl += str(inventory_item.item_name)
                            messagesendurl += "%20is%20coming%20to%20end."
                            messagesendurl += "&sender=LAZEEZ&route=4"
                            messagesendurl += "&country=0&campaign=signupweb"
                            req = urllib2.Request(messagesendurl)
                            print urllib2.urlopen(req)
    return JsonResponse({"status": "success"})


def orderdelivered(request, order_number):
    order = AllOrder.objects.get(order_number=order_number)
    order.delivered_at = timezone.now()
    if order.paid_at is None:
        order.paid_at = order.delivered_at
    order.order_status = "delivered"
    order.save()
    if order.payment_mode == 'Cash on Delivery' and order.delivery_type != 'Branch Pickup':
        date = datetime.datetime.date(order.delivered_at)
        first_name = (order.dispatched_with).split()[0]
        last_name = (order.dispatched_with).split()[1]
        mobile = (order.dispatched_with).split()[2]
        delivery_boy = Admin_User.objects.get(
            first_name=first_name, last_name=last_name, mobile=mobile)
        try:
            dboy_collection = CollectiontoDelboy.objects.get(
                date=date, delivery_boy=delivery_boy)
            dboy_collection.amount += float(order.grand_total)
            dboy_collection.save()
        except CollectiontoDelboy.DoesNotExist:
            amount = float(order.grand_total)
            CollectiontoDelboy.objects.create(
                date=date, delivery_boy=delivery_boy, amount=amount)
    if order.expected_at > order.delivered_at:
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey="
        messagesendurl += "96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(order.customer_mobile)
        messagesendurl += "&message=Dear%20"
        messagesendurl += str(order.customer_name)
        messagesendurl += ",%20Thanks%20for%20using%20lhdindia.%20It%20was%20"
        messagesendurl += "Pleasure%20serving%20you.%20we%20hope%20to%20see%20you%20soon."
        messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
    return HttpResponseRedirect("/myadmin/")


@csrf_exempt
def send_sms_at_counter(request):
    order_number = request.POST['order_number']
    customer_number = request.POST['customer_number']
    order = CounterOrder.objects.get(order_number=order_number)
    messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey="
    messagesendurl += "96244AsR6Os06Hs562e546f&mobiles=91"
    messagesendurl += str(customer_number)
    messagesendurl += "&message=Dear%20"
    messagesendurl += str(order.customer.customer_name)
    messagesendurl += ",%20use%20following%20url%20for%20online%20payment%20of%20order%20number%20"
    messagesendurl += str(order_number)
    messagesendurl += ",%20http://www.lhdindia.com/onlinepay_at_counter/"
    messagesendurl += str(order_number)
    messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
    req = urllib2.Request(messagesendurl)
    print urllib2.urlopen(req)
    return HttpResponseRedirect("/myadmin/counter")


def send_sms_at_callcenter(request, order_number):
    order = AllOrder.objects.get(order_number=order_number)
    order.onlinepay_status = "pending"
    order.save()
    messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey="
    messagesendurl += "96244AsR6Os06Hs562e546f&mobiles=91"
    messagesendurl += str(order.customer_mobile)
    messagesendurl += "&message=Dear%20"
    messagesendurl += str(order.customer_name)
    messagesendurl += ",%20use%20following%20url%20for%20online%20payment%20of%20order%20number%20"
    messagesendurl += str(order_number)
    messagesendurl += ",%20http://www.lhdindia.com/onlinepay_at_callcenter/"
    messagesendurl += str(order_number)
    messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
    req = urllib2.Request(messagesendurl)
    print urllib2.urlopen(req)
    return HttpResponseRedirect("/myadmin/orderdetail/" + order_number)


def cannot_pay_now(request):
    return render(request, 'app/cannot_pay_now.html')


def onlinepay_at_counter(request, order_number):
    order = CounterOrder.objects.get(order_number=order_number)
    if order.order_status == "completed":
        return render(request, 'app/cannot_pay_now.html')
    else:
        p_merchant_id = "80351"
        p_order_id = str(order_number)
        p_currency = "INR"
        subtotal = order.subtotal
        p_amount = str(order.grand_total)
        p_redirect_url = "http://www.lhdindia.com/counter_payment_successful/"  #to be changed
        p_cancel_url = "http://www.lhdindia.com/online_payment_cancel/"    #to be changed
        p_language = "EN"
        p_billing_name = str(order.customer.customer_name)
        p_billing_address = "NIL"
        p_billing_city = "Bhopal"
        p_billing_state = "Madhya Pradesh"
        p_billing_zip = "462023"
        p_billing_country = "India"
        p_billing_tel = str(order.customer.customer_number)
        p_billing_email = "husaintaheer@gmail.com"
        p_delivery_name = str(order.customer.customer_name)
        p_delivery_address = "NIL"
        p_delivery_city = "Bhopal"
        p_delivery_state = "Madhya Pradesh"
        p_delivery_zip = ""
        p_delivery_country = "India"
        p_delivery_tel = str(order.customer.customer_number)
        p_merchant_param1 = ""
        p_merchant_param2 = ""
        p_merchant_param3 = ""
        p_merchant_param4 = ""
        p_merchant_param5 = ""
        p_promo_code = ""
        p_customer_identifier = ""

        

        merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+'billing_email='+p_billing_email+'&'+'delivery_name='+p_delivery_name+'&'+'delivery_address='+p_delivery_address+'&'+'delivery_city='+p_delivery_city+'&'+'delivery_state='+p_delivery_state+'&'+'delivery_zip='+p_delivery_zip+'&'+'delivery_country='+p_delivery_country+'&'+'delivery_tel='+p_delivery_tel+'&'+'merchant_param1='+p_merchant_param1+'&'+'merchant_param2='+p_merchant_param2+'&'+'merchant_param3='+p_merchant_param3+'&'+'merchant_param4='+p_merchant_param4+'&'+'merchant_param5='+p_merchant_param5+'&'+'promo_code='+p_promo_code+'&'+'customer_identifier='+p_customer_identifier+'&'
        
        encryption = encrypt(merchant_data,workingKey)

        html = '''\
    <html>
    <head>
        <title>Sub-merchant checkout page</title>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
    </head>
    <body>
    <form id="nonseamless" method="post" name="redirect" action="https://secure.ccavenue.com/transaction/transaction.do?command=initiateTransaction" > 
            <input type="hidden" id="encRequest" name="encRequest" value=$encReq>
            <input type="hidden" name="access_code" id="access_code" value=$xscode>
            <script language='javascript'>document.redirect.submit();</script>
    </form>    
    </body>
    </html>
    '''
        fin = Template(html).safe_substitute(encReq=encryption,xscode=accessCode)
        return HttpResponse(fin)


def onlinepay_at_callcenter(request, order_number):
    order = AllOrder.objects.get(order_number=order_number)
    if order.order_status == "delivered" or order.payment_mode != "Online Pay":
        return render(request, 'app/cannot_pay_now.html')
    else:
        p_merchant_id = "80351"
        p_order_id = str(order_number)
        p_currency = "INR"
        subtotal = order.subtotal
        p_amount = str(order.grand_total)
        p_redirect_url = "http://www.lhdindia.com/callcenter_payment_successful/"  #to be changed
        p_cancel_url = "http://www.lhdindia.com/online_payment_cancel/"    #to be changed
        p_language = "EN"
        p_billing_name = str(order.customer_name)
        p_billing_address = "NIL"
        p_billing_city = "Bhopal"
        p_billing_state = "Madhya Pradesh"
        p_billing_zip = "462023"
        p_billing_country = "India"
        p_billing_tel = str(order.customer_mobile)
        p_billing_email = "husaintaheer@gmail.com"
        p_delivery_name = str(order.customer_name)
        p_delivery_address = "NIL"
        p_delivery_city = "Bhopal"
        p_delivery_state = "Madhya Pradesh"
        p_delivery_zip = ""
        p_delivery_country = "India"
        p_delivery_tel = str(order.customer_mobile)
        p_merchant_param1 = ""
        p_merchant_param2 = ""
        p_merchant_param3 = ""
        p_merchant_param4 = ""
        p_merchant_param5 = ""
        p_promo_code = ""
        p_customer_identifier = ""

        

        merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+'billing_email='+p_billing_email+'&'+'delivery_name='+p_delivery_name+'&'+'delivery_address='+p_delivery_address+'&'+'delivery_city='+p_delivery_city+'&'+'delivery_state='+p_delivery_state+'&'+'delivery_zip='+p_delivery_zip+'&'+'delivery_country='+p_delivery_country+'&'+'delivery_tel='+p_delivery_tel+'&'+'merchant_param1='+p_merchant_param1+'&'+'merchant_param2='+p_merchant_param2+'&'+'merchant_param3='+p_merchant_param3+'&'+'merchant_param4='+p_merchant_param4+'&'+'merchant_param5='+p_merchant_param5+'&'+'promo_code='+p_promo_code+'&'+'customer_identifier='+p_customer_identifier+'&'
        
        encryption = encrypt(merchant_data,workingKey)

        html = '''\
    <html>
    <head>
        <title>Sub-merchant checkout page</title>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
    </head>
    <body>
    <form id="nonseamless" method="post" name="redirect" action="https://secure.ccavenue.com/transaction/transaction.do?command=initiateTransaction" > 
            <input type="hidden" id="encRequest" name="encRequest" value=$encReq>
            <input type="hidden" name="access_code" id="access_code" value=$xscode>
            <script language='javascript'>document.redirect.submit();</script>
    </form>    
    </body>
    </html>
    '''
        fin = Template(html).safe_substitute(encReq=encryption,xscode=accessCode)
        return HttpResponse(fin)


@csrf_exempt
def counter_payment_successful(request):
    encResp = request.POST["encResp"]
    order_number = request.POST["orderNo"]
    decResp = decrypt(encResp,workingKey)
    data=str(decResp).split('&')
    data2= data[3].split('=')
    order_status=str(data2[1])
    order = CounterOrder.objects.get(order_number=order_number)
    if order_status=="Success":
        order_items = json.loads(order.ordered_items)
        for key1, value1 in order_items.iteritems():
            if key1 != 'totalcost' and key1 != 'grandtotal':
                for key2, value2 in value1.iteritems():
                    if key2 != 'name':
                        item_code = value2['item_code']
                        subname = value2['subname']
                        qty = value2['quantity']
                        menu_item = Item.objects.get(
                            item_code=item_code, item_subname=subname)
                        dependency_items = InventoryDependency.objects.filter(
                            dependency_name=menu_item)
                        for item in dependency_items:
                            inventory_item = item.inventory_item
                            inventory_item.quantity -= (item.quantity * qty)
                            inventory_item.save()
                            alert_quantity = inventory_item.alert_quantity
                            if inventory_item.quantity <= alert_quantity:
                                messagesendurl = "https://control.msg91.com/api/"
                                messagesendurl += "sendhttp.php?authkey=96244"
                                messagesendurl += "AsR6Os06Hs562e546f&mobiles=91"
                                messagesendurl += str(inventory_item.alert_number)
                                messagesendurl += "&message=Hello%20admin,%0A"
                                messagesendurl += "Please%20pay%20attention,%20"
                                messagesendurl += str(inventory_item.item_name)
                                messagesendurl += "%20is%20coming%20to%20end."
                                messagesendurl += "&sender=LAZEEZ&route=4"
                                messagesendurl += "&country=0&campaign=signupweb"
                                req = urllib2.Request(messagesendurl)
                                print urllib2.urlopen(req)
        order.order_status = "completed"
        table = order.table_no
        table.order_number = ""
        table.save()
        order.save()
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += "9977666541"
        messagesendurl += "&message="
        messagesendurl += str(order.customer.customer_name)
        messagesendurl += ",%20Online%20payment%20for%20your%20order%20has%20been%20successfully%20received.%20Thanks%20for%20choosing%20lhdindia."
        messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(order.customer.customer_number)
        messagesendurl += "&message=Dear%20"
        messagesendurl += str(order.customer.customer_name)
        messagesendurl += ",%20Online%20payment%20for%20your%20order%20has%20been%20successfully%20received.%20Thanks%20for%20choosing%20lhdindia."
        messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
        return HttpResponseRedirect("/")
    else:
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(order.customer.customer_mobile)
        messagesendurl += "&message="
        messagesendurl += str(order.customer.customer_name)
        messagesendurl += ",%20Online%20payment%20for%20your%20order%20is%20NOT%20successful."
        messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
        request.session['order_number'] = order_number
        return HttpResponseRedirect("/oopsonlinepayment/")


@csrf_exempt
def callcenter_payment_successful(request):
    encResp = request.POST["encResp"]
    order_number = request.POST["orderNo"]
    decResp = decrypt(encResp,workingKey)
    data=str(decResp).split('&')
    data2= data[3].split('=')
    order_status=str(data2[1])
    if order_status=="Success":
        order = AllOrder.objects.get(order_number=order_number)
        order.onlinepay_status= "success"
        order.save()
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(order.customer_mobile)
        messagesendurl += "&message="
        messagesendurl += str(order.customer_name)
        messagesendurl += ",%20Online%20payment%20for%20your%20order%20has%20been%20successfully%20received.%20Thanks%20for%20choosing%20lhdindia."
        messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += "9977666541"
        messagesendurl += "&message=Dear%20"
        messagesendurl += str(order.customer_name)
        messagesendurl += ",%20Online%20payment%20for%20your%20order%20has%20been%20successfully%20received.%20Thanks%20for%20choosing%20lhdindia."
        messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
        return HttpResponseRedirect("/")
    else:
        order = AllOrder.objects.get(order_number=order_number)
        order.onlinepay_status= str(order_status)
        order.save()
        return HttpResponseRedirect("/oopsonlinepayment/")


def counter_onlinepay_successful(request):
    return render(request, 'app/counter_onlinepay_successful.html')


def orderdetail(request, order_number):
    order = AllOrder.objects.get(order_number=order_number)
    deliveryboys = Admin_User.objects.filter(roles='deliveryboy')
    order_source = OrderSource.objects.all()
    paymentmodes = PaymentMode.objects.all()
    branches = Branch.objects.all()
    if order.ordered_items == "":
        ordered_items = ""
    else:
        d = json.loads(order.ordered_items)
        items = []
        for i in d.keys():
            if type(d[i]) == dict:
                for j in d[i].keys():
                    if type(d[i][j]) == dict:
                        if 'sno' not in d[i][j]:
                            t = datetime.datetime.now()
                            t = int(time.mktime(t.timetuple()))
                            d[i][j]['sno'] = t
                        items.append(d[i][j])
        ordered_items = sorted(items, key=lambda k: k['sno'])
    return render(request, 'app/orderdetail.html',
                  {"order": order, "deliveryboys": deliveryboys,
                   "order_source": order_source, "paymentmodes": paymentmodes,
                   "branches": branches, "ordered_items": ordered_items})


def myorderdetail(request, order_number):
    if 'user' not in request.session:
        return HttpResponseRedirect('/')
    order = AllOrder.objects.get(order_number=order_number, customer_mobile=request.session['user']['phone'])
    d = json.loads(order.ordered_items)
    items = []
    for i in d.keys():
        if type(d[i]) == dict:
            for j in d[i].keys():
                if type(d[i][j]) == dict:
                    if 'sno' not in d[i][j]:
                        t = datetime.datetime.now()
                        t = int(time.mktime(t.timetuple()))
                        d[i][j]['sno'] = t
                    items.append(d[i][j])
    ordered_items = sorted(items, key=lambda k: k['sno'])
    return render(request, 'app/myorderdetail.html',
                  {"order": order, "ordered_items": ordered_items})


def printorder(request, order_number):
    order = AllOrder.objects.get(order_number=order_number)
    customer_number = order.customer_mobile
    forlastdelboy = AllOrder.objects.filter(order_number__lt=order_number, customer_mobile=customer_number)
    forlastdelboy_list = list(forlastdelboy)
    if 'lastdelboy_info' in request.session:
        del request.session['lastdelboy_info']
    if len(forlastdelboy_list):
        lastdelboy_info = forlastdelboy_list[len(forlastdelboy_list)-1].dispatched_with
        request.session['lastdelboy_info'] = lastdelboy_info
    if len(order.ordered_items) == 2:
        request.session['cart'] = {"totalcost": 0, "grandtotal": 0}
    else:
        request.session['cart'] = json.loads(order.ordered_items)
    return render(request, 'app/printorder.html', {"order": order})


def editorder(request, order_number):
    order = AllOrder.objects.get(order_number=order_number)
    order.customer_name = request.POST['customer_name']
    order.address = request.POST['address']
    order.delivery_type = request.POST['delivery_type']
    order.expected_at = request.POST['delivery_date']
    order.source = request.POST['source']
    order.special_comment += request.POST['ref_number']
    if 'payment_mode' in request.POST:
        order.payment_mode = request.POST['payment_mode']
        if request.POST['payment_mode'] == 'Cash on Delivery':
            order.onlinepay_status = "NA"
        if request.POST['payment_mode'] == 'Online Pay':
            order.onlinepay_status = "pending"
    if 'onlinepay_status' in request.POST:
        order.onlinepay_status = request.POST['onlinepay_status']
    order.save()
    url = request.POST['url']
    return HttpResponseRedirect(url)


def updateallorder(order_number):
    order = AllOrder.objects.get(order_number=order_number)
    cart = json.loads(order.ordered_items)
    order.subtotal = cart['totalcost']
    discount_percent = order.discount_percent
    vat_percent = order.vat_percent
    service_charge_percent = order.service_charge_percent
    service_tax_percent = order.service_tax_percent
    ewallet = float(order.e_wallet)
    intsub = float(order.subtotal)
    if len(cart) == 2:
        intsub = 0
    service_tax = (intsub * float(service_tax_percent)) / 100
    vat = (intsub * float(vat_percent)) / 100
    service_charge = (intsub * float(service_charge_percent)) / 100
    discount = (intsub * float(discount_percent)) / 100
    order.grand_total = float(intsub + service_tax + vat + service_charge - discount - ewallet)
    order.save()


@csrf_exempt
def additemtoordercart(request):
    try:
        item_subname = request.POST['item_subname']
        item_code = request.POST['item_code']
        quantity = request.POST['item_quantity']
        order_number = request.POST['order_number']
        order = AllOrder.objects.get(order_number=order_number)
        cart = json.loads(order.ordered_items)
        item = Item.objects.get(item_code=item_code, item_subname=item_subname)
        item_code = str(item.item_code)
        if item_code not in cart:
            cart[item_code] = {"name": item.item_name}
        thisitem = cart[item_code]
        if item_subname not in thisitem:
            t = datetime.datetime.now()
            t = int(time.mktime(t.timetuple()))
            thisitem[item_subname] = {
                "price": item.price, "name": item.item_name,
                "discount": item.discount, "quantity": 0,
                "subname": item.item_subname, "sno": t, "item_code": item_code}
        thisitem[item_subname]['quantity'] += int(quantity)
        cart['totalcost'] += (int(item.price) * int(quantity))
        cart['grandtotal'] = float(1.05 * float(cart['totalcost']))
        cart[item_code] = thisitem
        order.ordered_items = json.dumps(cart)
        order.save()
        updateallorder(order_number)
    except:
        return JsonResponse({"status": "fail"})
    return JsonResponse({"status": "success"})


def updateordercart(request, order_number):
    order = AllOrder.objects.get(order_number=order_number)
    order.offer_from_web = ""
    order.save()
    d = json.loads(order.ordered_items)
    items = []
    for i in d.keys():
        if type(d[i]) == dict:
            for j in d[i].keys():
                if type(d[i][j]) == dict:
                    if 'sno' not in d[i][j]:
                        t = datetime.datetime.now()
                        t = int(time.mktime(t.timetuple()))
                        d[i][j]['sno'] = t
                    items.append(d[i][j])
    ordered_items = sorted(items, key=lambda k: k['sno'])
    html = render_to_string(
        'app/updateorderdetail.html',
        {"order": order, "ordered_items": ordered_items},
        RequestContext(request))
    return HttpResponse(html)


@csrf_exempt
def subtractitemtoordercart(request):
    item_code = request.POST['item_code']
    item_subname = request.POST['item_subname']
    item_quantity = request.POST['item_quantity']
    order_number = request.POST['order_number']
    item = Item.objects.get(item_code=item_code, item_subname=item_subname)
    order = AllOrder.objects.get(order_number=order_number)
    cart = json.loads(order.ordered_items)
    thisitem = cart[item_code]
    thisitem.pop(item_subname)
    cart[item_code] = thisitem
    if len(thisitem) == 1:
        cart.pop(item_code)
    cart['totalcost'] -= float(item.price) * int(item_quantity)
    cart['grandtotal'] = float(1.05 * (cart['totalcost']))
    order.ordered_items = json.dumps(cart)
    order.save()
    updateallorder(order_number)
    return JsonResponse({"status": "success"})


@csrf_exempt
def update_advance_pay(request):
    order_number = request.POST['order_number']
    advance_pay = request.POST['advance_pay']
    order = AllOrder.objects.get(order_number=order_number)
    send = {}
    try:
        order.advance_pay = advance_pay
        order.save()
        send['status'] = "success"
        send['balance_pay'] = order.balance_amount()
    except:
        send['status'] = "failed"
    return JsonResponse(send)


@csrf_exempt
def ajaxcheckcustomer(request):
    phone = request.POST['mobile']
    send = {}
    try:
        customer = Customer.objects.get(customer_number=phone)
        send['status'] = "pass"
        send['name'] = customer.customer_name
        send['mobile'] = customer.customer_number
        address = (customer.customer_address).split(';')
        send['address1'] = address[0]
        if len(address) > 1:
            if len(address) == 2:
                send['address2'] = address[1]
            else:
                send['address2'] = address[1]
                send['address3'] = address[2]
        send['no'] = str(int(customer.order_number) + 1)
    except:
        send['status'] = "fail"
    return JsonResponse(send)


@csrf_exempt
def ajaxcheckitem(request, keyword):
    counter_request = '/ajaxcheckitem_counter/' + str(keyword) + '/'
    outside_request = '/ajaxcheckitem_outside/' + str(keyword) + '/'
    callcenter_request = '/ajaxcheckitem_callcenter/' + str(keyword) + '/'
    send = []
    item_list1 = Item.objects.filter(item_name__icontains=keyword)
    item_list2 = Item.objects.filter(item_code__icontains=keyword)
    item_list = item_list1 | item_list2
    if request.path == counter_request:
        item_list = item_list.filter(active_on_counter=True)
    if request.path == outside_request:
        item_list = item_list.filter(active_on_outside=True)
    if request.path == callcenter_request:
        item_list = item_list.filter(active_on_callcenter=True)
    for item in item_list:
        item_json = {}
        item_json['item_code'] = item.item_code
        item_json['item_name'] = item.item_name
        item_json['item_subname'] = item.item_subname
        item_json['item_price'] = item.price
        send.append(item_json)
    return JsonResponse(json.dumps(send), safe=False)


@csrf_exempt
def updatediscountandtax(request):
    order_number = request.POST['order_number']
    special_comment = (request.POST['comment_text']).strip()
    discount_percent = request.POST['discount_percent']
    service_tax_percent = request.POST['service_tax_percent']
    vat_percent = request.POST['vat_percent']
    service_charge_percent = request.POST['service_charge_percent']
    distance_in_km = request.POST.get('distance_in_km', '')
    del_charge = DeliveryCharge.objects.all()
    del_charge = del_charge[0].delivery_charge
    # cart = request.session['cart']
    order = AllOrder.objects.get(order_number=order_number)
    order.special_comment = special_comment
    order.discount_percent = discount_percent
    order.service_tax_percent = service_tax_percent
    order.vat_percent = vat_percent
    order.service_charge_percent = service_charge_percent
    try:
        delivery_charge = float(distance_in_km) * float(del_charge)
    except:
        delivery_charge = float(order.delivery_charge)
    order.delivery_charge = delivery_charge
    # subtotal = cart['totalcost']
    subtotal = order.subtotal
    ewallet = float(order.e_wallet)
    intsub = float(subtotal)
    service_tax = (intsub * float(service_tax_percent)) / 100
    vat = (intsub * float(vat_percent)) / 100
    service_charge = (intsub * float(service_charge_percent)) / 100
    discount = (intsub * float(discount_percent)) / 100
    grand_total = intsub + service_tax + vat + service_charge + delivery_charge
    order.grand_total = float(grand_total - discount - ewallet)
    order.save()
    updatedorder = {}
    updatedorder['status'] = "success"
    updatedorder['discount_rs'] = order.discount_rs()
    updatedorder['service_tax_rs'] = order.service_tax_rs()
    updatedorder['vat_rs'] = order.vat_rs()
    updatedorder['service_charge_rs'] = order.service_charge_rs()
    updatedorder['delivery_charge'] = order.delivery_charge
    updatedorder['grand_total'] = order.grand_total
    return JsonResponse(updatedorder)


@csrf_exempt
def updatesubcategories(request):
    item_category = request.POST['item_category']
    category = Item_Category.objects.get(item_category=item_category)
    subcategories = Item_Subcategory.objects.filter(
        belongs_to_category=category)
    subcategory_list = []
    for subcategory in subcategories:
        subcategory_list.append(subcategory.subcategory_name)
    return JsonResponse(subcategory_list, safe=False)


@csrf_exempt
def applycoupon(request):
    coupon_code = request.POST['coupon_code']
    if 'coupon' not in request.session:
        try:
            coupon = CouponInfo.objects.get(coupon_number=coupon_code)
            primary_coupon = Coupons.objects.get(
                prefix=coupon.prefix, suffix=coupon.suffix)
            if ((coupon.blocked == True) and (primary_coupon.is_active == True) and (coupon.end_date >= datetime.datetime.now().date()) and (coupon.start_date <= datetime.datetime.now().date())):
                if 'offer' in request.session:
                    grandtotal = request.session['cart']['grandtotal_actual']
                else:
                    grandtotal = request.session['cart']['grandtotal']                
                grandtotal = float(grandtotal)
                if coupon.discount_type == 'Rs':
                    grandtotal -= coupon.discount_amount
                    if grandtotal < 0:
                        grandtotal = 0
                    request.session['coupon_discount'] = "Rs " + str(coupon.discount_amount)
                else:
                    grandtotal -= float((grandtotal * coupon.discount_amount) / 100)
                    request.session['coupon_discount'] = str(coupon.discount_amount) + "%"
                if 'offer' in request.session:
                    request.session['cart']['grandtotal_actual'] = float(grandtotal)
                else:
                    request.session['cart']['grandtotal'] = float(grandtotal)
                request.session['coupon'] = coupon_code
                return JsonResponse({"status": 201})
            else:
                request.session["couponinvalid"] = "true"
        except:
            request.session["couponinvalid"] = "true"
    return JsonResponse({"status": 400})


@csrf_exempt
def applyewallet(request):
    if 'ewallet' not in request.session:
        if 'user' in request.session:
            wallet_amount = float(request.session['user']['e_wallet'])
        else:
            wallet_amount = float(request.session['partner']['e_wallet'])
        grandtotal = float(request.session['cart']['grandtotal'])
        if 'offer' in request.session:
            grandtotal = float(request.session['cart']['grandtotal_actual'])
        if grandtotal > wallet_amount:
            request.session['ewallet'] = wallet_amount
            grandtotal -= wallet_amount
        else:
            request.session['ewallet'] = grandtotal
            grandtotal = 0.0
        request.session['cart']['grandtotal'] = float(grandtotal)
        if 'offer' in request.session:
            request.session['cart']['grandtotal_actual'] = float(grandtotal)
    return JsonResponse({"status": 400})


@csrf_exempt
def removewallet_amount(request):
    grandtotal = float(request.session['cart']['grandtotal'])
    if 'offer' in request.session:
        grandtotal = float(request.session['cart']['grandtotal_actual'])
    grandtotal += request.session['ewallet']
    request.session.pop('ewallet')
    if 'offer' in request.session:
        request.session['cart']['grandtotal_actual'] = float(grandtotal)
    else:
        request.session['cart']['grandtotal'] = float(grandtotal)
    return JsonResponse({"status": 400})


# ===================== Counter orders & Dashboard ===========================
def counter_total(value):
    if value is None:
        value = 0
    return value


def counter(request):
    if 'admin' not in request.session:
        return HttpResponseRedirect("/adminloginpage/")
    if 'branch_name' in request.POST:
        loginid = request.session['admin']['loginid']
        user = Admin_User.objects.get(loginid=loginid)
        del request.session['admin']
        admin = {}
        admin['loginid'] = user.loginid
        admin['role'] = user.roles
        admin['name'] = user.first_name + ' ' + user.last_name
        admin['branch'] = request.POST['branch_name']
        request.session['admin'] = admin
    branch_name = request.session['admin']['branch']
    tables = CounterTable.objects.exclude(is_active=False)
    tables = tables.filter(branch_name=branch_name)
    active_table = False
    if len(tables) > 0:
        active_table = True
        active_table_number = tables[0]
    counter_branch_order = CounterTable.objects.get(table_number=0,branch_name=branch_name)
    tables = tables.exclude(table_number=0)
    tables = tables.order_by('table_number')
    waiters = Waiter.objects.all()
    order = ''
    table = ''
    roundof_total = 0
    ordered_items = ''
    for t in tables:
        if t.order_number != '':
            table = t
            order = CounterOrder.objects.get(order_number=table.order_number)
            roundof_total = round(order.grand_total) - order.grand_total
            d = json.loads(order.ordered_items)
            items = []
            for i in d.keys():
                if type(d[i]) == dict:
                    for j in d[i].keys():
                        if type(d[i][j]) == dict:
                            if 'sno' not in d[i][j]:
                                t = datetime.datetime.now()
                                t = int(time.mktime(t.timetuple()))
                                d[i][j]['sno'] = t
                            items.append(d[i][j])
            ordered_items = sorted(items, key=lambda k: k['sno'])
            # item list for print qt functionality
            pqt_items = [item for item in items if item['pqt'] != 0]
            pqt_items = sorted(pqt_items, key=lambda k: k['sno'])
            break
    table_dropdown = CounterTable.objects.exclude(order_number="")
    deliveryboys = Admin_User.objects.filter(roles='deliveryboy',branch__branch=branch_name)
    paymentmodes = PaymentMode.objects.all()
    today = datetime.datetime.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today.replace(hour=23, minute=59, second=59, microsecond=0)
    today_date = timezone.now().date()
    today_expenses = Expense.objects.filter(date__startswith=today_date,branch_name=branch_name)
    today_expense_total = today_expenses.aggregate(Sum('amount'))
    today_collection = ExpenseCollection.objects.filter(
        date__startswith=today_date,branch_name=branch_name)
    today_collection_total = today_collection.aggregate(Sum('amount'))
    delboy_payments = PayDeliveryBoy.objects.filter(
        date__startswith=today_date,branch_name=branch_name)
    delboy_payment_total = delboy_payments.aggregate(Sum('amount'))
    payment_received = collections.OrderedDict()
    branch_pickup = AllOrder.objects.filter(
        delivery_type="Branch Pickup", placed_at__lte=today_end,
        placed_at__gte=today_start, payment_mode='Cash on Delivery',branch_assigned=branch_name)

    total_sum = 0.0
    if(len(branch_pickup) > 1):
        for i in range(0, len(branch_pickup)):
            total_sum += float(branch_pickup[i].grand_total)
    elif(len(branch_pickup) == 1):
        total_sum = float(branch_pickup[0].grand_total)
    for pmode in paymentmodes:
        pmode_list = CounterOrder.objects.filter(
            payment_mode=pmode, ordered_at__startswith=today_date, branch_name=branch_name)
        payment_received[pmode] = pmode_list.aggregate(Sum('grand_total'))
        if payment_received[pmode]['grand_total__sum'] is None:
            payment_received[pmode]['grand_total__sum'] = 0
    payment_received['Branch Pickup'] = {'grand_total__sum': total_sum}
    payment_sum = 0.0
    for key, value in payment_received.iteritems():
        payment_sum += float(value['grand_total__sum'])

    payment_received['total'] = {'grand_total__sum': payment_sum}
    branch_pickup_total = payment_received['Branch Pickup']['grand_total__sum']
    branch_pickup_call = AllOrder.objects.filter(
        delivery_type="Branch Pickup", placed_at__gte=today_start,
        placed_at__lte=today_end, source='callcenter',
        payment_mode='Cash on Delivery', branch_assigned=branch_name)
    total_sum_call = 0.0
    if(len(branch_pickup_call) != 0 and len(branch_pickup_call) > 1):
        for i in range(0, len(branch_pickup_call)):
            total_sum_call += float(branch_pickup_call[i].grand_total)
    elif(len(branch_pickup_call) != 0):
        total_sum_call = float(branch_pickup_call[0].grand_total)
    counterorders = CounterOrder.objects.filter(
        ordered_at__startswith=today_date, order_status='completed', branch_name=branch_name)
    # payment_received['total'] = counterorders.aggregate(Sum('grand_total'))
    # if len(counterorders) != 0 and len(branch_pickup) != 0:
    #     payment_received['total']['grand_total__sum'] += payment_received['Branch Pickup']['grand_total__sum']
    pmode = PaymentMode.objects.get(payment_mode='Cash on Delivery')
    cash_counterorder = counterorders.filter(payment_mode=pmode)
    counter_cash = cash_counterorder.aggregate(Sum('grand_total'))
    if len(cash_counterorder) != 0:
        counter_cash['grand_total__sum'] += total_sum_call
    else:
        counter_cash['grand_total__sum'] = total_sum_call
    sodexo_data = AllOrder.objects.filter(
        delivery_type='Home Deliverly', placed_at__gte=today_start, placed_at__lte=today_end,
        payment_mode='Sodexo Meal Passes', branch_assigned=branch_name)
    online_pay_data = AllOrder.objects.filter(
        delivery_type='Home Deliverly', placed_at__gte=today_start, placed_at__lte=today_end,
        payment_mode='Online Pay', branch_assigned=branch_name)
    credit_data = AllOrder.objects.filter(
        delivery_type='Home Deliverly', placed_at__gte=today_start, placed_at__lte=today_end,
        payment_mode='Credit', branch_assigned = branch_name)
    sodexo_total = 0.0
    online_total = 0.0
    credit_total = 0.0
    if(len(sodexo_data) != 0 and len(sodexo_data) > 1):
        for i in range(0, len(sodexo_data)):
            sodexo_total += float(sodexo_data[i].grand_total)
    elif(len(sodexo_data) != 0):
        sodexo_total = float(sodexo_data[0].grand_total)

    if(len(online_pay_data) != 0 and len(online_pay_data) > 1):
        for i in range(0, len(online_pay_data)):
            online_total += float(online_pay_data[i].grand_total)
    elif(len(online_pay_data) != 0):
        online_total = float(online_pay_data[0].grand_total)

    if(len(credit_data) != 0 and len(credit_data) > 1):
        for i in range(0, len(credit_data)):
            credit_total += float(credit_data[i].grand_total)
    elif(len(credit_data) != 0):
        credit_total = float(credit_data[0].grand_total)
    total_home_deliveries = sodexo_total + online_total + credit_total
    today_collection_dboy = CollectiontoDelboy.objects.filter(date=today_date)
    today_collection_dboy = today_collection_dboy.exclude(collected_at=None)
    del_received = today_collection_dboy.aggregate(Sum('amount'))
    total_countercash = 0.0
    total_countercash += counter_total(counter_cash['grand_total__sum'])
    total_countercash += payment_received['Branch Pickup']['grand_total__sum']
    total_countercash += counter_total(del_received['amount__sum'])
    total_countercash -= counter_total(today_expense_total['amount__sum'])
    total_countercash += counter_total(today_collection_total['amount__sum'])
    total_countercash -= counter_total(delboy_payment_total['amount__sum'])
    branches = Branch.objects.all()
    return render(request, 'app/counter.html',
                  {'tables': tables, 'order': order, 'table': table,
                   'ordered_items': ordered_items, 'branches': branches,
                   'counter_branch_order': counter_branch_order,
                   'waiters': waiters, 'paymentmodes': paymentmodes,
                   'table_dropdown': table_dropdown,
                   'deliveryboys': deliveryboys,
                   'today_expenses': today_expenses,
                   'today_collection': today_collection,
                   'delboy_payments': delboy_payments,
                   'payment_received': payment_received,
                   'branch_pickup_total': branch_pickup_total,
                   'today_expense_total': today_expense_total,
                   'today_collection_total': today_collection_total,
                   'delboy_payment_total': delboy_payment_total,
                   'counter_cash': counter_cash, 'del_received': del_received,
                   'total_countercash': total_countercash,
                   'sodexo_total': sodexo_total,
                   'online_total': online_total,
                   'credit_total': credit_total,
                   'total_home_deliveries': total_home_deliveries,
                   'active_table': active_table,
                   'active_table_number': active_table_number,
                   'roundof_total': roundof_total})


def tableorder(request):
    table_number = request.GET['table_number']
    branch_name = request.session['admin']['branch']
    table = CounterTable.objects.get(table_number=table_number, branch_name=branch_name)
    order = CounterOrder.objects.get(order_number=table.order_number)
    d = json.loads(order.ordered_items)
    items = []
    for i in d.keys():
        if type(d[i]) == dict:
            for j in d[i].keys():
                if type(d[i][j]) == dict:
                    if 'sno' not in d[i][j]:
                        t = datetime.datetime.now()
                        t = int(time.mktime(t.timetuple()))
                        d[i][j]['sno'] = t
                    items.append(d[i][j])
    ordered_items = sorted(items, key=lambda k: k['sno'])
    # item list for print qt functionality
    pqt_items = [item for item in items if item['pqt'] != 0]
    pqt_items = sorted(pqt_items, key=lambda k: k['sno'])
    tables = CounterTable.objects.exclude(is_active=False)
    tables = tables.filter(branch_name=branch_name)
    tables = tables.exclude(table_number=0)
    tables = tables.order_by('table_number')
    counter_branch_order = CounterTable.objects.get(table_number=0, branch_name=branch_name)
    waiters = Waiter.objects.all()
    paymentmodes = PaymentMode.objects.all()
    table_dropdown = CounterTable.objects.exclude(order_number="")
    roundof_total = round(order.grand_total) - order.grand_total
    html = render_to_string(
        'app/tableorder.html',
        {'order': order, 'table': table, 'ordered_items': ordered_items,
         'tables': tables, 'counter_branch_order': counter_branch_order,
         'pqt_items': pqt_items, 'waiters': waiters,
         'paymentmodes': paymentmodes, 'table_dropdown': table_dropdown,
         'roundof_total': roundof_total},
        RequestContext(request))
    return HttpResponse(html)


def countertableorder(request):
    table_number = request.GET['table_number']
    branch_name = request.session['admin']['branch']
    table = CounterTable.objects.get(table_number=table_number, branch_name=branch_name)
    order = CounterOrder.objects.get(order_number=table.order_number)
    d = json.loads(order.ordered_items)
    items = []
    for i in d.keys():
        if type(d[i]) == dict:
            for j in d[i].keys():
                if type(d[i][j]) == dict:
                    if 'sno' not in d[i][j]:
                        t = datetime.datetime.now()
                        t = int(time.mktime(t.timetuple()))
                        d[i][j]['sno'] = t
                    items.append(d[i][j])
    ordered_items = sorted(items, key=lambda k: k['sno'])
    # item list for print qt functionality
    pqt_items = [item for item in items if item['pqt'] != 0]
    pqt_items = sorted(pqt_items, key=lambda k: k['sno'])
    roundof_total = round(order.grand_total) - order.grand_total
    html = render_to_string(
        'app/branchcounter_order.html',
        {'order': order, 'table': table, 'ordered_items': ordered_items,
         'pqt_items': pqt_items,
         'roundof_total': roundof_total},
        RequestContext(request))
    return HttpResponse(html)


def orderinfo(request, order_number):
    order = CounterOrder.objects.get(order_number=order_number)
    d = json.loads(order.ordered_items)
    items = []
    for i in d.keys():
        if type(d[i]) == dict:
            for j in d[i].keys():
                if type(d[i][j]) == dict:
                    if 'sno' not in d[i][j]:
                        t = datetime.datetime.now()
                        t = int(time.mktime(t.timetuple()))
                        d[i][j]['sno'] = t
                    items.append(d[i][j])
    ordered_items = sorted(items, key=lambda k: k['sno'])
    html = render_to_string(
        'app/counterorderinfo.html',
        {'order': order, 'ordered_items': ordered_items},
        RequestContext(request))
    return HttpResponse(html)


@csrf_exempt
def placetableorder(request):
    branch_name = request.session['admin']['branch']
    table_number = request.POST['table_number']
    table = CounterTable.objects.get(table_number=table_number, branch_name=branch_name)
    cart = {"totalcost": 0, "grandtotal": 0}
    ordernumberitem = CounterOrdernumber.objects.get(pk=1)
    order_number = ordernumberitem.number
    ordernumberitem.number += 1
    ordernumberitem.save()
    ordered_at = timezone.now()
    table_no = table
    order_status = "active"
    ordered_items = json.dumps(cart)
    subtotal = cart['totalcost']
    discount_percent = 0
    vat_percent = "5"
    service_charge_percent = "0"
    if table_number == '0':
        service_tax_percent = "0"
    else:
        service_tax_percent = "6"
    intsub = float(subtotal)
    service_tax = (intsub * float(service_tax_percent)) / 100
    vat = (intsub * float(vat_percent)) / 100
    service_charge = (intsub * float(service_charge_percent)) / 100
    grand_total = float(intsub + service_tax + vat + service_charge)
    assigned_waiter = table.waiter
    assigned_at = timezone.now()
    CounterOrder.objects.create(
        order_number=order_number, ordered_at=ordered_at,
        ordered_items=ordered_items, branch_name=branch_name,
        table_no=table_no, order_status=order_status,
        assigned_waiter=assigned_waiter, assigned_at=assigned_at,
        discount_percent=discount_percent, vat_percent=vat_percent,
        service_charge_percent=service_charge_percent, subtotal=subtotal,
        service_tax_percent=service_tax_percent, grand_total=grand_total)
    table.order_number = order_number
    table.save()
    if table.table_number == 0:
        order = CounterOrder.objects.get(order_number=table.order_number)
        waiter = Waiter.objects.get(name="COUNTER BRANCH ORDER")
        order.assigned_waiter = waiter
        order.save()
    return JsonResponse({"status": "success"})


def finaltableorder(request, order_number):
    request_path = '/myadmin/finaltableorder/' + order_number + '/'
    request_path1 = '/myadmin_bcounter/finaltableorder/' + order_number + '/'
    order = CounterOrder.objects.get(order_number=order_number)
    order_items = json.loads(order.ordered_items)
    for key1, value1 in order_items.iteritems():
        if key1 != 'totalcost' and key1 != 'grandtotal':
            for key2, value2 in value1.iteritems():
                if key2 != 'name':
                    item_code = value2['item_code']
                    subname = value2['subname']
                    qty = value2['quantity']
                    menu_item = Item.objects.get(
                        item_code=item_code, item_subname=subname)
                    dependency_items = InventoryDependency.objects.filter(
                        dependency_name=menu_item)
                    for item in dependency_items:
                        inventory_item = item.inventory_item
                        inventory_item.quantity -= (item.quantity * qty)
                        inventory_item.save()
                        alert_quantity = inventory_item.alert_quantity
                        if inventory_item.quantity <= alert_quantity:
                            messagesendurl = "https://control.msg91.com/api/"
                            messagesendurl += "sendhttp.php?authkey=96244"
                            messagesendurl += "AsR6Os06Hs562e546f&mobiles=91"
                            messagesendurl += str(inventory_item.alert_number)
                            messagesendurl += "&message=Hello%20admin,%0A"
                            messagesendurl += "Please%20pay%20attention,%20"
                            messagesendurl += str(inventory_item.item_name)
                            messagesendurl += "%20is%20coming%20to%20end."
                            messagesendurl += "&sender=LAZEEZ&route=4"
                            messagesendurl += "&country=0&campaign=signupweb"
                            req = urllib2.Request(messagesendurl)
                            print urllib2.urlopen(req)
    order.order_status = "completed"
    table = order.table_no
    table.order_number = ""
    table.save()
    order.save()
    if request.path == request_path:
        return HttpResponseRedirect('/myadmin/counterdashboard/')
    if request.path == request_path1:
        return HttpResponseRedirect('/myadmin/counterorder/')
    return HttpResponseRedirect('/myadmin/counter/')


def updatecounterorder(order_number):
    order = CounterOrder.objects.get(order_number=order_number)
    cart = json.loads(order.ordered_items)
    order.subtotal = cart['totalcost']
    discount_percent = order.discount_percent
    vat_percent = order.vat_percent
    service_charge_percent = order.service_charge_percent
    service_tax_percent = order.service_tax_percent
    intsub = float(order.subtotal)
    if len(cart) == 2:
        intsub = 0
    service_tax = (intsub * float(service_tax_percent)) / 100
    vat = (intsub * float(vat_percent)) / 100
    service_charge = (intsub * float(service_charge_percent)) / 100
    discount = (intsub * float(discount_percent)) / 100
    order.grand_total = float(intsub + service_tax + vat + service_charge - discount)
    order.save()


@csrf_exempt
def additemtotableorder(request):
    try:
        item_subname = request.POST['item_subname']
        item_code = request.POST['item_code']
        quantity = request.POST['item_quantity']
        order_number = request.POST['order_number']
        order = CounterOrder.objects.get(order_number=order_number)
        cart = json.loads(order.ordered_items)
        item = Item.objects.get(item_code=item_code, item_subname=item_subname)
        item_code = str(item.item_code)
        if item_code not in cart:
            cart[item_code] = {"name": item.item_name}
        thisitem = cart[item_code]
        if item_subname not in thisitem:
            t = datetime.datetime.now()
            t = int(time.mktime(t.timetuple()))
            thisitem[item_subname] = {
                "price": item.price, "name": item.item_name,
                "discount": item.discount, "quantity": 0, "pqt": 0,
                "subname": item.item_subname, "sno": t, "item_code": item_code}
        thisitem[item_subname]['quantity'] += int(quantity)
        thisitem[item_subname]['pqt'] += int(quantity)
        cart['totalcost'] += (int(item.price) * int(quantity))
        cart['grandtotal'] = float(1.05 * float(cart['totalcost']))
        cart[item_code] = thisitem
        order.ordered_items = json.dumps(cart)
        order.save()
        updatecounterorder(order_number)
        order = CounterOrder.objects.get(order_number=order_number)
        d = json.loads(order.ordered_items)
        items = []
        for i in d.keys():
            if type(d[i]) == dict:
                for j in d[i].keys():
                    if type(d[i][j]) == dict:
                        if 'sno' not in d[i][j]:
                            t = datetime.datetime.now()
                            t = int(time.mktime(t.timetuple()))
                            d[i][j]['sno'] = t
                        items.append(d[i][j])
        ordered_items = sorted(items, key=lambda k: k['sno'])
        # item list for print qt functionality
        pqt_items = [x for x in items if x['pqt'] != 0]
        pqt_items = sorted(pqt_items, key=lambda k: k['sno'])
        table = order.table_no
        html = render_to_string(
            'app/item_description.html',
            {'order': order, 'table': table, 'ordered_items': ordered_items,
             'pqt_items': pqt_items}, RequestContext(request))
    except:
        return JsonResponse({"status": "fail"})
    return HttpResponse(html)


@csrf_exempt
def subtractitemtotableorder(request):
    item_code = request.POST['item_code']
    item_subname = request.POST['item_subname']
    item_quantity = request.POST['item_quantity']
    order_number = request.POST['order_number']
    item = Item.objects.get(item_code=item_code, item_subname=item_subname)
    order = CounterOrder.objects.get(order_number=order_number)
    cart = json.loads(order.ordered_items)
    thisitem = cart[item_code]
    thisitem[item_subname]['quantity'] = 0
    thisitem[item_subname]['pqt'] = 0
    # thisitem.pop(item_subname)
    cart[item_code] = thisitem
    if len(thisitem) == 1:
        cart.pop(item_code)
    cart['totalcost'] -= float(item.price) * int(item_quantity)
    cart['grandtotal'] = float(1.05 * (cart['totalcost']))
    order.ordered_items = json.dumps(cart)
    order.save()
    updatecounterorder(order_number)
    return JsonResponse({"status": "success"})


@csrf_exempt
def billprint(request, order_number):
    order = CounterOrder.objects.get(order_number=order_number)
    order.bill_print = timezone.now()
    payment_mode = PaymentMode.objects.get(payment_mode="Cash on Delivery")
    order.payment_mode = payment_mode
    order.save()
    return JsonResponse({"status": "success"})


def counterdashboard(request):
    branch_name = request.session['admin']['branch']
    branch = Branch.objects.get(branch=branch_name)
    waiters = Waiter.objects.filter(branch_name=branch)
    deliveryboys = Admin_User.objects.filter(roles='deliveryboy')
    paymentmodes = PaymentMode.objects.all()
    today = datetime.datetime.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today.replace(hour=23, minute=59, second=59, microsecond=0)
    today_orders = OrderedDict()
    orders = CounterOrder.objects.filter(
        ordered_at__lte=today_end, ordered_at__gte=today_start,branch_name=branch_name)
    today_orders['total'] = orders.count()
    paymentmodes = PaymentMode.objects.all()
    for p in paymentmodes:
        today_orders[p.payment_mode] = orders.filter(payment_mode=p,branch_name=branch_name).count()
    try:
        today_orders['Branch Order'] = orders.filter(
            table_no=CounterTable.objects.get(table_number=0,branch_name=branch_name)).count()
    except CounterTable.DoesNotExist:
        pass
    table_orders = []
    table_orders = CounterOrder.objects.filter(order_status="active",branch_name=branch_name)
    today_date = timezone.now().date()
    today_expenses = Expense.objects.filter(date__startswith=today_date,branch_name=branch_name)
    today_expense_total = today_expenses.aggregate(Sum('amount'))
    delboy_payments = PayDeliveryBoy.objects.filter(
        date__startswith=today_date,branch_name=branch_name)
    delboy_payment_total = delboy_payments.aggregate(Sum('amount'))
    payment_received = OrderedDict()
    branch_pickup = AllOrder.objects.filter(delivery_type="Branch Pickup",
                                            expected_at__lte=today_end,
                                            expected_at__gte=today_start,
                                            order_status='delivered',branch_assigned=branch_name)
    total_sum = 0
    for i in range(0, len(branch_pickup)):
            total_sum += float(branch_pickup[i].grand_total)
    for pmode in paymentmodes:
        pmode_list = CounterOrder.objects.filter(
            payment_mode=pmode, ordered_at__startswith=today_date, branch_name=branch_name)
        payment_received[pmode] = pmode_list.aggregate(Sum('grand_total'))
    payment_received['Branch Pickup'] = {'grand_total__sum': total_sum}
    payment_received['total'] = CounterOrder.objects.filter(
        ordered_at__startswith=today_date, branch_name=branch_name).aggregate(Sum('grand_total'))
    return render(request, 'app/counter_dashboard.html',
                  {'table_orders': table_orders, 'waiters': waiters,
                   'paymentmodes': paymentmodes, 'today_orders': today_orders,
                   'deliveryboys': deliveryboys,
                   'today_expenses': today_expenses,
                   'delboy_payments': delboy_payments,
                   'today_expense_total': today_expense_total,
                   'delboy_payment_total': delboy_payment_total})


def updatecounterdashboard(request):
    branch_name = request.session['admin']['branch']
    waiters = Waiter.objects.filter(branch_name=branch_name)
    paymentmodes = PaymentMode.objects.all()
    table_orders = []
    table_orders = CounterOrder.objects.filter(order_status="active",branch_name=branch_name)
    html = render_to_string(
        'app/updatecounterdashboard.html',
        {'table_orders': table_orders, 'waiters': waiters,
         'paymentmodes': paymentmodes},
        RequestContext(request))
    return HttpResponse(html)


@csrf_exempt
def select_table(request):
    table_number = request.POST['table_number']
    branch_name = request.session['admin']['branch']
    try:
        table = CounterTable.objects.get(branch_name=branch_name,table_number=table_number)
        return JsonResponse({"status": "success", "order_number": table.order_number})
    except:
        return JsonResponse({"status": "fail"})


@csrf_exempt
def assignwaiter(request):
    order_number = request.POST['order_number']
    waiter_userid = request.POST['waiter']
    print order_number, "==", waiter_userid
    order = CounterOrder.objects.get(order_number=order_number)
    waiter = Waiter.objects.get(userid=waiter_userid)
    order.assigned_waiter = waiter
    order.assigned_at = datetime.datetime.now()
    admin_loginid = request.session['admin']['loginid']
    admin = Admin_User.objects.get(loginid=admin_loginid)
    order.assigned_by = admin
    order.save()
    return JsonResponse({"status": "success"})


@csrf_exempt
def addcustomerinfo(request):
    order_number = request.POST['order_number']
    customer_name = request.POST['customer_name']
    customer_number = request.POST['customer_number']
    order = CounterOrder.objects.get(order_number=order_number)
    try:
        customer = Customer.objects.get(customer_number=customer_number)
    except:
        Customer.objects.create(
            customer_name=customer_name, customer_number=customer_number,
            customer_address='', isblocked=False,
            order_number="0")
        customer = Customer.objects.get(customer_number=customer_number)
    order.customer = customer
    order.save()
    customer.order_number = str(int(customer.order_number) + 1)
    customer.save()
    return JsonResponse({"status": "success"})


@csrf_exempt
def editdiscount_counter(request):
    order_number = request.POST['order_number']
    discount_percent = request.POST['discount_percent']
    if discount_percent == '':
        discount_percent = 0
    order = CounterOrder.objects.get(order_number=order_number)
    order.discount_percent = discount_percent
    subtotal = order.subtotal
    intsub = float(subtotal)
    service_tax = (intsub * float(order.service_tax_percent)) / 100
    vat = (intsub * float(order.vat_percent)) / 100
    service_charge = (intsub * float(order.service_charge_percent)) / 100
    discount = (intsub * float(discount_percent)) / 100
    grand_total = intsub + service_tax + vat + service_charge
    order.grand_total = float(grand_total - discount)
    order.save()
    updatedorder = {}
    updatedorder['status'] = "success"
    updatedorder['discount_rs'] = order.discount_rs()
    updatedorder['grand_total'] = order.grand_total
    return JsonResponse(updatedorder)


@csrf_exempt
def addpaymode(request):
    order_number = request.POST['order_number']
    pmode_id = request.POST['payment_mode']
    order = CounterOrder.objects.get(order_number=order_number)
    payment_mode = PaymentMode.objects.get(id=pmode_id)
    order.payment_mode = payment_mode
    table = order.table_no
    if table.table_number == 0:
        table.order_number = ""
        table.save()
    order.save()
    return JsonResponse({"status": "success"})


@csrf_exempt
def edit_advance_pay(request):
    order_number = request.POST['order_number']
    advance_pay = request.POST['advance_pay']
    order = CounterOrder.objects.get(order_number=order_number)
    send = {}
    try:
        order.advance_pay = advance_pay
        order.save()
        send['status'] = "success"
        send['advance_pay'] = order.advance_pay
        send['balance_pay'] = order.balance_pay()
    except:
        send['status'] = "failed"
    return JsonResponse(send)


def counterorderdetail(request, order_number):
    order = CounterOrder.objects.get(order_number=order_number)
    waiters = Waiter.objects.all()
    paymentmodes = PaymentMode.objects.all()
    branches = Branch.objects.all()
    d = json.loads(order.ordered_items)
    items = []
    for i in d.keys():
        if type(d[i]) == dict:
            for j in d[i].keys():
                if type(d[i][j]) == dict:
                    if 'sno' not in d[i][j]:
                        t = datetime.datetime.now()
                        t = int(time.mktime(t.timetuple()))
                        d[i][j]['sno'] = t
                    items.append(d[i][j])
    ordered_items = sorted(items, key=lambda k: k['sno'])
    return render(request, 'app/counterorderdetail.html',
                  {"order": order, "waiters": waiters,
                   "paymentmodes": paymentmodes,
                   "branches": branches, "ordered_items": ordered_items})


def printcounterorder(request, order_number):
    order = CounterOrder.objects.get(order_number=order_number)
    if order.customer is not None:
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(order.customer.customer_number)
        messagesendurl += "&message=Dear%20"
        messagesendurl += str(order.customer.customer_name)
        messagesendurl += ",%0AWe%20hope%20you%20had%20a%20satiating%20experience%20at%20Lazeez%20Hakeem.%20To%20bring%20to%20this%20experience%20to%20you%20doorstep%20via%20our%20Free%20Home%20Delivery%20anywhere%20in%20Bhopal,%20call:0755-4222227%200755-6222227"
        messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
    d = json.loads(order.ordered_items)
    items = []
    for i in d.keys():
        if type(d[i]) == dict:
            for j in d[i].keys():
                if type(d[i][j]) == dict:
                    if 'sno' not in d[i][j]:
                        t = datetime.datetime.now()
                        t = int(time.mktime(t.timetuple()))
                        d[i][j]['sno'] = t
                    items.append(d[i][j])
    ordered_items = sorted(items, key=lambda k: k['sno'])
    # if len(order.ordered_items) == 2:
    #     request.session['cart'] = {"totalcost": 0, "grandtotal": 0}
    # else:
    #     request.session['cart'] = json.loads(order.ordered_items)
    return render(request, 'app/printcounterorder.html',
                  {"order": order, 'ordered_items': ordered_items})


def editcounterorder(request, order_number):
    order = CounterOrder.objects.get(order_number=order_number)
    customer_name = request.POST['customer_name']
    customer_number = request.POST['customer_number']
    pmode = request.POST['payment_mode']
    payment_mode = PaymentMode.objects.get(payment_mode=pmode)
    try:
        customer = Customer.objects.get(customer_number=customer_number)
    except:
        Customer.objects.create(
            customer_name=customer_name, customer_number=customer_number,
            customer_address='', isblocked=False,
            order_number="0")
        customer = Customer.objects.get(customer_number=customer_number)
    order.customer = customer
    customer.order_number = str(int(customer.order_number) + 1)
    customer.save()
    order.payment_mode = payment_mode
    order.save()
    url = request.POST['url']
    return HttpResponseRedirect(url)


def updatecounterordercart(request, order_number):
    order = CounterOrder.objects.get(order_number=order_number)
    d = json.loads(order.ordered_items)
    items = []
    for i in d.keys():
        if type(d[i]) == dict:
            for j in d[i].keys():
                if type(d[i][j]) == dict:
                    if 'sno' not in d[i][j]:
                        t = datetime.datetime.now()
                        t = int(time.mktime(t.timetuple()))
                        d[i][j]['sno'] = t
                    items.append(d[i][j])
    ordered_items = sorted(items, key=lambda k: k['sno'])
    html = render_to_string(
        'app/updatecounterorderdetail.html',
        {"order": order, "ordered_items": ordered_items},
        RequestContext(request))
    return HttpResponse(html)


@csrf_exempt
def updatecdisandtax(request):
    order_number = request.POST['order_number']
    # special_comment = (request.POST['comment_text']).strip()
    discount_percent = request.POST['discount_percent']
    service_tax_percent = request.POST['service_tax_percent']
    vat_percent = request.POST['vat_percent']
    service_charge_percent = request.POST['service_charge_percent']
    order = CounterOrder.objects.get(order_number=order_number)
    # order.special_comment = special_comment
    order.discount_percent = discount_percent
    order.service_tax_percent = service_tax_percent
    order.vat_percent = vat_percent
    order.service_charge_percent = service_charge_percent
    subtotal = order.subtotal
    intsub = float(subtotal)
    service_tax = (intsub * float(service_tax_percent)) / 100
    vat = (intsub * float(vat_percent)) / 100
    service_charge = (intsub * float(service_charge_percent)) / 100
    discount = (intsub * float(discount_percent)) / 100
    grand_total = intsub + service_tax + vat + service_charge
    order.grand_total = float(grand_total - discount)
    order.save()
    updatedorder = {}
    updatedorder['status'] = "success"
    updatedorder['discount_rs'] = order.discount_rs()
    updatedorder['service_tax_rs'] = order.service_tax_rs()
    updatedorder['vat_rs'] = order.vat_rs()
    updatedorder['service_charge_rs'] = order.service_charge_rs()
    updatedorder['grand_total'] = order.grand_total
    return JsonResponse(updatedorder)


@csrf_exempt
def printqt(request):
    order_number = request.POST['order_number']
    order = CounterOrder.objects.get(order_number=order_number)
    d = json.loads(order.ordered_items)
    for i in d.keys():
        if type(d[i]) == dict:
            for j in d[i].keys():
                if type(d[i][j]) == dict:
                    d[i][j]['pqt'] = 0
    order.ordered_items = json.dumps(d)
    order.save()
    return JsonResponse({"status": "success"})


def counterorder(request):
    if 'admin' not in request.session:
        return HttpResponseRedirect("/adminloginpage/")
    branch_name = request.session['admin']['branch']
    order = ''
    table = CounterTable.objects.get(table_number=0,branch_name=branch_name)
    roundof_total = 0
    ordered_items = ''
    if table.order_number != '':
        order = CounterOrder.objects.get(order_number=table.order_number)
        roundof_total = round(order.grand_total) - order.grand_total
        d = json.loads(order.ordered_items)
        items = []
        for i in d.keys():
            if type(d[i]) == dict:
                for j in d[i].keys():
                    if type(d[i][j]) == dict:
                        if 'sno' not in d[i][j]:
                            t = datetime.datetime.now()
                            t = int(time.mktime(t.timetuple()))
                            d[i][j]['sno'] = t
                        items.append(d[i][j])
        ordered_items = sorted(items, key=lambda k: k['sno'])
        # item list for print qt functionality
        pqt_items = [item for item in items if item['pqt'] != 0]
        pqt_items = sorted(pqt_items, key=lambda k: k['sno'])
    return render(request, 'app/counterorder.html',
                  {'order': order, 'table': table,
                   'ordered_items': ordered_items,
                   'roundof_total': roundof_total})


def addtodayexpense(request):
    branch_name = request.session['admin']['branch']
    expense_for = request.POST['expense_for']
    amount = request.POST['amount']
    url = request.POST['url']
    date = timezone.now()
    Expense.objects.create(date=date, branch_name=branch_name,
        expense_for=expense_for, amount=amount)
    return HttpResponseRedirect(url)


def addtodayexpensecollection(request):
    collect_for = request.POST['collect_for']
    branch_name = request.session['admin']['branch']
    amount = request.POST['amount']
    url = request.POST['url']
    date = timezone.now()
    ExpenseCollection.objects.create(date=date, branch_name=branch_name,
        collection_for=collect_for, amount=amount)
    return HttpResponseRedirect(url)


@csrf_exempt
def removetodayexpense(request):
    branch_name = request.session['admin']['branch']
    expense_for = request.POST['expense_for']
    url = request.POST['url']
    amount = request.POST['amount']
    today = datetime.datetime.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today.replace(hour=23, minute=59, second=59, microsecond=0)
    exp = Expense.objects.get(date__lte=today_end, branch_name=branch_name,
        date__gte=today_start, expense_for=expense_for, amount=amount)
    exp.delete()
    return HttpResponseRedirect(url)


@csrf_exempt
def removetodaycollection(request):
    branch_name = request.session['admin']['branch']
    expense_for = request.POST['collection_for']
    url = request.POST['url']
    amount = request.POST['amount']
    today = datetime.datetime.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today.replace(hour=23, minute=59, second=59, microsecond=0)
    exp = ExpenseCollection.objects.get(
        date__lte=today_end, date__gte=today_start,
        collection_for=expense_for, amount=amount, branch_name=branch_name)
    exp.delete()
    return HttpResponseRedirect(url)


def paydeliveryboy(request):
    loginid = request.POST['delivery_boy']
    branch_name = request.session['admin']['branch']
    delivery_boy = Admin_User.objects.get(loginid=loginid)
    amount = request.POST['amount']
    url = request.POST['url']
    date = timezone.now()
    PayDeliveryBoy.objects.create(
        date=date, delivery_boy=delivery_boy, amount=amount, branch_name=branch_name)
    return HttpResponseRedirect(url)


@csrf_exempt
def removedelexp(request):
    loginid = request.POST['login_id']
    branch_name = request.session['admin']['branch']
    delivery_boy = Admin_User.objects.get(loginid=loginid)
    amount = request.POST['amount']
    url = request.POST['url']
    today = datetime.datetime.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today.replace(hour=23, minute=59, second=59, microsecond=0)
    exp = PayDeliveryBoy.objects.get(date__lte=today_end, date__gte=today_start, 
            delivery_boy=delivery_boy, amount=amount, branch_name=branch_name)
    exp.delete()
    return HttpResponseRedirect(url)


@csrf_exempt
def delboycollectiondata(request):
    del_date = request.POST.get('date')
    if del_date != "":
        del_date = datetime.datetime.strptime(del_date, "%Y-%m-%d").date()
    else:
        del_date = datetime.datetime.date(timezone.now())
    delboy_collection = CollectiontoDelboy.objects.filter(date=del_date)
    total_amount = delboy_collection.aggregate(Sum('amount'))
    delboy_collected = delboy_collection.exclude(collected_at=None)
    amount_collected = delboy_collected.aggregate(Sum('amount'))
    delboy_left = delboy_collection.filter(collected_at=None)
    amount_left = delboy_left.aggregate(Sum('amount'))
    html = render_to_string(
        'app/delboycollection.html',
        {'delboy_collection': delboy_collection, 'total_amount': total_amount,
         'amount_collected': amount_collected, 'amount_left': amount_left},
        RequestContext(request))
    return HttpResponse(html)


@csrf_exempt
def amountcollected(request):
    del_date = request.POST['date']
    if del_date != "":
        del_date = datetime.datetime.strptime(del_date, "%Y-%m-%d").date()
    else:
        del_date = datetime.datetime.date(timezone.now())
    collected_at = timezone.now()
    dboy_loginid = request.POST['del_boy']
    delivery_boy = Admin_User.objects.get(loginid=dboy_loginid)
    CollectiontoDelboy.objects.filter(
        date=del_date, delivery_boy=delivery_boy).update(
        collected_at=collected_at)
    return JsonResponse({"status": "success"})


# =======================Report section of admin panel=======================
def allreportpage(request):
    return render(request, 'app/allreportpage.html')


def datereportpage(request):
    deliveryboys = Admin_User.objects.filter(roles='deliveryboy')
    source_list = OrderSource.objects.all()
    paymentmodes = PaymentMode.objects.all()
    return render(request, 'app/datereportpage.html',
                  {"delv": deliveryboys, "source_list": source_list,
                   "paymentmodes": paymentmodes})


def singledayreportpage(request):
    deliveryboys = Admin_User.objects.filter(roles='deliveryboy')
    source_list = OrderSource.objects.all()
    paymentmodes = PaymentMode.objects.all()
    return render(request, 'app/singledayreportpage.html',
                  {"delv": deliveryboys, "source_list": source_list,
                   "paymentmodes": paymentmodes})


def menusellreportpage(request):
    deliveryboys = Admin_User.objects.filter(roles='deliveryboy')
    source_list = OrderSource.objects.all()
    paymentmodes = PaymentMode.objects.all()
    return render(request, 'app/menusellreportpage.html',
                  {"delv": deliveryboys, "source_list": source_list,
                   "paymentmodes": paymentmodes})


def deliveryboyreportpage(request):
    return render(request, 'app/deliveryboyreportpage.html')


def searchdatewise(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/datereport/")
    orderstatus = request.POST['orderstatus']
    ordersource = request.POST['ordersource']
    deliverytype = request.POST['deliverytype']
    paymentmode = request.POST['paymentmode']
    deliveryboy = request.POST['deliveryboy']
    sdate = request.POST.get('sdate')
    edate = request.POST.get('edate')
    orders = AllOrder.objects.exclude(order_status="cancelled")
    if sdate != "":
        sdate = datetime.datetime.strptime(sdate, "%Y-%m-%d").date()
        if edate != "":
            edate = datetime.datetime.strptime(edate, "%Y-%m-%d").date()
        else:
            edate = timezone.now()
        orders = orders.filter(delivered_at__range=(sdate, edate))
    if orderstatus != 'all':
        orders = orders.filter(order_status=orderstatus)
    if ordersource != 'all':
        orders = orders.filter(source=ordersource)
    if deliverytype != 'all':
        orders = orders.filter(delivery_type=deliverytype)
    if paymentmode != 'all':
        orders = orders.filter(payment_mode=paymentmode)
    if deliveryboy != 'all':
        orders = orders.filter(dispatched_with=deliveryboy)
    deliveryboys = Admin_User.objects.filter(roles='deliveryboy')
    source_list = OrderSource.objects.all()
    paymentmodes = PaymentMode.objects.all()
    totals = {"tot": 0, "gtot": 0, "disc": 0, "vat": 0, "ewallet": 0,
              "ser_tax": 0, "ser_charge": 0, "del_charge": 0}
    for ord in orders:
        totals['tot'] += float(ord.subtotal)
        totals['gtot'] += float(ord.grand_total)
        totals['ewallet'] += float(ord.e_wallet)
        totals['disc'] += ord.discount_rs()
        totals['vat'] += ord.vat_rs()
        totals['ser_tax'] += ord.service_tax_rs()
        totals['ser_charge'] += ord.service_charge_rs()
        totals['del_charge'] += float(ord.delivery_charge)
    return render(request, 'app/datereportpage.html',
                  {"delv": deliveryboys, "ords": orders, "total": totals,
                   "source_list": source_list, "paymentmodes": paymentmodes})


@csrf_exempt
def searchorder(request):
    order_number = request.POST['order_number']
    customer_name = request.POST['customer_name']
    customer_mobile = request.POST['customer_mobile']
    del_boy = request.POST['del_boy']
    payment_mode = request.POST['payment_mode']
    del_date = request.POST['del_date']
    deliveryboys = Admin_User.objects.filter(roles='deliveryboy')
    orders = AllOrder.objects.all()
    if del_date != "":
        del_date = datetime.datetime.strptime(del_date, "%Y-%m-%d").date()
        orders = orders.filter(delivered_at__startswith=del_date)
    if customer_name != "":
        orders = orders.filter(customer_name=customer_name)
    if customer_mobile != "":
        orders = orders.filter(customer_mobile=customer_mobile)
    if order_number != "":
        orders = orders.filter(order_number=order_number)
    if payment_mode != 'all':
        orders = orders.filter(payment_mode=payment_mode)
    if del_boy != 'all':
        orders = orders.filter(dispatched_with=del_boy)
    html = render_to_string(
        'app/dashboard_searchorder.html',
        {"ords": orders, "deliveryboys": deliveryboys}, RequestContext(request))
    return HttpResponse(html)


def searchdelboy(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/deliveryboyreport/")
    del_date = request.POST['delvery_date']
    orders = AllOrder.objects.exclude(order_status="cancelled")
    if del_date != "":
        del_date = datetime.datetime.strptime(del_date, "%Y-%m-%d").date()
    else:
        del_date = datetime.datetime.date(timezone.now())
    orders = orders.filter(delivered_at__startswith=del_date)
    paymentmodes = PaymentMode.objects.all()
    payment_order = {}
    payment_table = {}
    for pmode in paymentmodes:
        payment_order[pmode] = orders.filter(payment_mode=pmode.payment_mode)
        payment_table[pmode] = {}
        payment_table[pmode]['total'] = {
            "discount": 0, "vat": 0, "total_rs": 0,
            "ser_tax": 0, "ser_charge": 0, "ewallet": 0,
            "del_charge": 0, "gtot": 0, "order_count": 0}
    del_boys = Admin_User.objects.filter(roles='deliveryboy')

    for del_boy in del_boys:
        q = del_boy.first_name + ' ' + del_boy.last_name + ' ' + del_boy.mobile
        del_boy_order = {}
        for pmode, porders in payment_order.items():
            if porders:
                del_boy_order[pmode] = porders.filter(dispatched_with=q)
                if del_boy_order[pmode]:
                    payment_table[pmode][del_boy] = {
                        "discount": 0, "vat": 0, "total_rs": 0,
                        "ser_tax": 0, "ser_charge": 0, "ewallet": 0,
                        "del_charge": 0, "gtot": 0}
                    for ord in del_boy_order[pmode]:
                        payment_table[pmode][del_boy]['discount'] += ord.discount_rs()
                        payment_table[pmode][del_boy]['vat'] += ord.vat_rs()
                        payment_table[pmode][del_boy]['ser_tax'] += ord.service_tax_rs()
                        payment_table[pmode][del_boy]['ser_charge'] += ord.service_charge_rs()
                        payment_table[pmode][del_boy]['total_rs'] += float(ord.subtotal)
                        payment_table[pmode][del_boy]['ewallet'] += float(ord.e_wallet)
                        payment_table[pmode][del_boy]['del_charge'] += float(ord.delivery_charge)
                        payment_table[pmode][del_boy]['gtot'] += float(ord.grand_total)
                    payment_table[pmode][del_boy]['order_count'] = len(del_boy_order[pmode])
                    payment_del_boy = Counter(payment_table[pmode][del_boy])
                    payment_total = Counter(payment_table[pmode]['total'])
                    payment_newtotal = payment_total + payment_del_boy
                    payment_table[pmode]['total'] = dict(payment_newtotal)
    return render(request, 'app/deliveryboyreportpage.html',
                  {"payment_tables": payment_table})


def searchmenusell(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/menusellreport/")
    orderstatus = request.POST['orderstatus']
    del_date = request.POST.get('sdate')
    orders = AllOrder.objects.exclude(order_status="cancelled")
    if del_date != "":
        del_date = datetime.datetime.strptime(del_date, "%Y-%m-%d").date()
    else:
        del_date = datetime.datetime.date(timezone.now())
    orders = orders.filter(expected_at__year=del_date.year,
        expected_at__month=del_date.month,expected_at__day=del_date.day)
    if orderstatus != 'all':
        orders = orders.filter(order_status=orderstatus)
    items = []
    for order in orders:
        d = json.loads(order.ordered_items)
        for i in d.keys():
            if type(d[i]) == dict:
                for j in d[i].keys():
                    if type(d[i][j]) == dict:
                        items.append(d[i][j])
    ordered_items = []
    for item in items:
        item_name = item["name"]+"-"+item["subname"]
        for aquan in range(0,item["quantity"]):
            ordered_items.append(item_name)
    ordered_items_final = {}
    for item in ordered_items:
        if item in ordered_items_final.keys():
            continue
        else:
            ordered_items_final[item] = ordered_items.count(item)
    html = render_to_string(
        'app/menusellreportpage.html',
        {'ordered_items': ordered_items_final},
        RequestContext(request))
    return HttpResponse(html)


def searchsingleday(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/datereport/")
    orderstatus = request.POST['orderstatus']
    ordersource = request.POST['ordersource']
    deliverytype = request.POST['deliverytype']
    paymentmode = request.POST['paymentmode']
    deliveryboy = request.POST['deliveryboy']
    del_date = request.POST.get('sdate')
    orders = AllOrder.objects.exclude(order_status="cancelled")
    if del_date != "":
        del_date = datetime.datetime.strptime(del_date, "%Y-%m-%d").date()
    else:
        del_date = datetime.datetime.date(timezone.now())
    orders = orders.filter(delivered_at__startswith=del_date)
    if orderstatus != 'all':
        orders = orders.filter(order_status=orderstatus)
    if ordersource != 'all':
        orders = orders.filter(source=ordersource)
    if deliverytype != 'all':
        orders = orders.filter(delivery_type=deliverytype)
    if paymentmode != 'all':
        orders = orders.filter(payment_mode=paymentmode)
    if deliveryboy != 'all':
        orders = orders.filter(dispatched_with=deliveryboy)
    deliveryboys = Admin_User.objects.filter(roles='deliveryboy')
    source_list = OrderSource.objects.all()
    paymentmodes = PaymentMode.objects.all()
    totals = {"tot": 0, "gtot": 0, "disc": 0, "vat": 0, "ewallet": 0,
              "ser_tax": 0, "ser_charge": 0, "del_charge": 0}
    for ord in orders:
        totals['tot'] += float(ord.subtotal)
        totals['gtot'] += float(ord.grand_total)
        totals['ewallet'] += float(ord.e_wallet)
        totals['disc'] += ord.discount_rs()
        totals['vat'] += ord.vat_rs()
        totals['ser_tax'] += ord.service_tax_rs()
        totals['ser_charge'] += ord.service_charge_rs()
        totals['del_charge'] += float(ord.delivery_charge)
    return render(request, 'app/singledayreportpage.html',
                  {"delv": deliveryboys, "ords": orders, "total": totals,
                   "source_list": source_list, "paymentmodes": paymentmodes})


def singledayreportpage_counter(request):
    waiters = Waiter.objects.all()
    paymentmodes = PaymentMode.objects.all()
    return render(request, 'app/singledayreportpage_counter.html',
                  {"waiters": waiters, "paymentmodes": paymentmodes})


def searchsingleday_counter(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/datereport/")
    order_type = request.POST['order_type']
    paymentmode = request.POST['paymentmode']
    waiter_id = request.POST['waiter']
    order_date = request.POST.get('order_date')
    orders = CounterOrder.objects.all()
    if order_date != "":
        order_date = datetime.datetime.strptime(order_date, "%Y-%m-%d").date()
    else:
        order_date = datetime.datetime.date(timezone.now())
    orders = orders.filter(
        ordered_at__startswith=order_date, order_status='completed')
    if waiter_id != 'all':
        waiter = Waiter.objects.get(id=waiter_id)
        orders = orders.filter(assigned_waiter=waiter)
    if paymentmode != 'all':
        pmode = PaymentMode.objects.get(payment_mode=paymentmode)
        orders = orders.filter(payment_mode=pmode)
    if order_type != 'all':
        table = CounterTable.objects.get(table_number=0)
        if order_type == "branch_order":
            orders = orders.filter(table_no=table)
        else:
            orders = orders.exclude(table_no=table)
    waiters = Waiter.objects.all()
    paymentmodes = PaymentMode.objects.all()
    totals = {"tot": 0, "gtot": 0, "vat": 0,
              "ser_tax": 0, "ser_charge": 0, "dis": 0}
    for ord in orders:
        totals['tot'] += float(ord.subtotal)
        totals['gtot'] += float(ord.grand_total)
        totals['vat'] += ord.vat_rs()
        totals['dis'] += ord.discount_rs()
        totals['ser_tax'] += ord.service_tax_rs()
        totals['ser_charge'] += ord.service_charge_rs()
    return render(request, 'app/singledayreportpage_counter.html',
                  {"ords": orders, "total": totals,
                   "waiters": waiters, "paymentmodes": paymentmodes})


def counterexpense_report(request):
    return render(request, 'app/counterexpense_report.html')


def searchcounterexpense(request):
    date = request.POST.get('date')
    if date != "":
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    else:
        date = datetime.datetime.date(timezone.now())
    # expenses = Expense.objects.all()
    date_expense = Expense.objects.filter(date__startswith=date)
    date_expense_total = date_expense.aggregate(Sum('amount'))
    return render(request, 'app/counterexpense_report.html',
                  {'date_expense': date_expense,
                   'date_expense_total': date_expense_total})


def countercollection_report(request):
    return render(request, 'app/countercollection_report.html')


def searchcountercollection(request):
    date = request.POST.get('date')
    if date != "":
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    else:
        date = datetime.datetime.date(timezone.now())
    # expenses = Expense.objects.all()
    date_expense = ExpenseCollection.objects.filter(date__startswith=date)
    date_expense_total = date_expense.aggregate(Sum('amount'))
    return render(request, 'app/countercollection_report.html',
                  {'date_expense': date_expense,
                   'date_expense_total': date_expense_total})


def delboypayment_report(request):
    del_boys = Admin_User.objects.filter(roles='deliveryboy')
    return render(
        request, 'app/delboypayment_report.html', {'del_boys': del_boys})


def searchdelboypayment(request):
    date = request.POST.get('date')
    deliveryboy = request.POST['delboy']
    if date != "":
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    else:
        date = datetime.datetime.date(timezone.now())
    delboy_payments = PayDeliveryBoy.objects.filter(date__startswith=date)
    if deliveryboy != "all":
        del_boy = Admin_User.objects.get(loginid=deliveryboy)
        delboy_payments = delboy_payments.filter(delivery_boy=del_boy)
    delboy_payment_total = delboy_payments.aggregate(Sum('amount'))
    del_boys = Admin_User.objects.filter(roles='deliveryboy')
    return render(request, 'app/delboypayment_report.html',
                  {'delboy_payments': delboy_payments, 'del_boys': del_boys,
                   'delboy_payment_total': delboy_payment_total})


def duecreditinfo(request):
    if 'duecreditinfoerror' in request.session:
        del request.session['duecreditinfoerror']
    if 'phoneforcredit' in request.session:
        del request.session['phoneforcredit']
    if 'phone' in request.POST and request.POST['loginid']=="":
        phone = request.POST['phone']
        request.session['phoneforcredit'] = phone
        duecredits = DueCreditInfo.objects.filter(customer_mobile=phone,is_cleared=False)
        duecredits_total = duecredits.aggregate(Sum('amount_due'))
        return render(request, 'app/duecreditinfo.html',
            {'duecredits': duecredits, 'duecredits_total': duecredits_total})
    if 'loginid' in request.POST and request.POST['phone']=="" :
        pass
    if 'phone' in request.POST and 'loginid' in request.POST:
        if request.POST['phone']!="" and request.POST['loginid']!="":
            request.session['duecreditinfoerror'] = 'True'
    return render(request, 'app/duecreditinfo.html')


def clearduecredit(order_number):
    ordertoclear = DueCreditInfo.objects.get(order_number=order_number)
    ordertoclear.is_cleared = True
    ordertoclear.save()


@csrf_exempt
def clear_duecredits(request):
    order_list = request.POST.getlist('data[]')
    if order_list:
        for order_number in order_list:
            clearduecredit(order_number)
    phone = request.session['phoneforcredit']
    duecredits = DueCreditInfo.objects.filter(customer_mobile=phone,is_cleared=False)
    duecredits_total = duecredits.aggregate(Sum('amount_due'))
    return render(request, 'app/duecreditinfo.html',
        {'duecredits': duecredits, 'duecredits_total': duecredits_total})


# =======================Inventory Section Views =========================
def manage_inventry(request):
    inventory_items = InventoryItem.objects.all()
    return render(request, 'app/manage_inventry.html',
                  {'inventory_items': inventory_items})


def addinventoryitem(request):
    item_name = request.POST['item_name']
    quantity = 0
    alert_quantity = request.POST['alert_quantity']
    alert_number = request.POST['alert_number']
    alert_email = request.POST['alert_email']
    url = request.POST['url']
    try:
        item = InventoryItem.objects.get(item_name=item_name)
    except InventoryItem.DoesNotExist:
        InventoryItem.objects.create(
            item_name=item_name, quantity=quantity,
            alert_email=alert_email, alert_number=alert_number,
            alert_quantity=alert_quantity)
    return HttpResponseRedirect(url)


def removeinventory_item(request, item_id):
    item = InventoryItem.objects.get(id=item_id)
    item.delete()
    return HttpResponseRedirect('/myadmin/applicationsetup/manage_inventry/')


def manage_dependency(request, item_id):
    item = InventoryItem.objects.get(id=item_id)
    dependencies = InventoryDependency.objects.filter(inventory_item=item)
    return render(request, 'app/manage_dependency.html',
                  {'dependencies': dependencies, 'item': item})


def editinventoryitem(request):
    item_id = request.POST['item_id']
    item_name = request.POST['item_name']
    quantity = request.POST['quantity']
    alert_quantity = request.POST['alert_quantity']
    alert_number = request.POST['alert_number']
    alert_email = request.POST['alert_email']
    InventoryItem.objects.filter(id=item_id).update(
        item_name=item_name, quantity=quantity,
        alert_email=alert_email, alert_number=alert_number,
        alert_quantity=alert_quantity)
    return HttpResponseRedirect('/myadmin/applicationsetup/manage_inventry/')


def adddependency(request):
    item_name = request.POST['inventory_item']
    inventory_item = InventoryItem.objects.get(item_name=item_name)
    item_code = request.POST['item_code']
    item_subname = request.POST['item_subname']
    dependency_item = Item.objects.get(
        item_code=item_code, item_subname=item_subname)
    quantity = request.POST['quantity']
    try:
        item = InventoryDependency.objects.get(
            dependency_name=dependency_item, inventory_item=inventory_item)
    except InventoryDependency.DoesNotExist:
        InventoryDependency.objects.create(
            dependency_name=dependency_item, inventory_item=inventory_item,
            quantity=quantity)
    url = request.POST['url']
    return HttpResponseRedirect(url)


def editdependecyitem(request):
    dependency_id = request.POST['dependency_id']
    item = InventoryDependency.objects.get(id=dependency_id)
    inventory_id = item.inventory_item.id
    quantity = request.POST['quantity']
    InventoryDependency.objects.filter(id=dependency_id).update(
        quantity=quantity)
    url = '/myadmin/manage_dependency/' + str(inventory_id) + '/'
    return HttpResponseRedirect(url)


def removedependency(request, dependency_id):
    dependency_item = InventoryDependency.objects.get(id=dependency_id)
    dependency_item.delete()
    item_id = dependency_item.inventory_item.id
    url = "/myadmin/manage_dependency/" + str(item_id) + "/"
    return HttpResponseRedirect(url)


@csrf_exempt
def ajaxcheckinventoryitem(request, keyword):
    send = []
    item_list = InventoryItem.objects.filter(item_name__icontains=keyword)
    for item in item_list:
        item_json = {}
        item_json['item_name'] = item.item_name
        item_json['item_id'] = item.id
        send.append(item_json)
    return JsonResponse(json.dumps(send), safe=False)


def purchaseinventoryitem(request):
    # item_name = request.POST['item_name']
    url = request.POST['url']
    try:
        item_id = request.POST['item_id']
        quantity = request.POST['quantity']
        unit = request.POST['unit']
        amount = request.POST['amount']
        bill_no = request.POST['bill_number']
        if unit == "kg":
            quantity = float(quantity) * 1000
        item = InventoryItem.objects.get(id=item_id)
        date = timezone.now()
        if amount == "":
            amount = 0
        InventoryPurchase.objects.create(
            item_name=item, date=date,
            quantity=quantity, bill_no=bill_no,
            amount=amount)
        item.quantity += float(quantity)
        item.save()
    except:
        pass    
    return HttpResponseRedirect(url)

# =======================Advanced Counter Views =========================
@csrf_exempt
def android_get_menu(request):
    username = str(request.POST['username'])
    password = str(request.POST['password'])
    branch_name = str(request.POST['branch_name'])
    try:
        user = Waiter.objects.get(userid=username,branch_name=branch_name)
        if user.password == password:
            di = {}
            for c in Item_Category.objects.all():
                di[c.item_category] = {}
            print di
            for s in Item_Subcategory.objects.all():
                if s.subcategory_name not in di[s.belongs_to_category.item_category]:
                    di[s.belongs_to_category.item_category][s.subcategory_name] = {}
            print di
            for i in Item.objects.filter(active_on_counter=True):
                if i.item_code not in di[i.item_category.item_category][i.item_subcategory.subcategory_name]:
                    di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code] = []
                    di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code].append(i.item_name)
                    di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code].append(i.item_subname)
                    di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code].append(i.item_type)
                    di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code].append(i.price)
            print di
            return JsonResponse({'status': 'success', 'result': di})
        else:
            return JsonResponse({'status': 'failed', 'error': 'Wrong Password'})
    except Waiter.DoesNotExist:
        return JsonResponse({'status': 'failed', 'error': 'User does not exist.'})


@csrf_exempt
def android_get_active_tables(request):
    branch_name = str(request.POST['branch_name'])
    tables = CounterTable.objects.filter(is_active=True,branch_name=branch_name)
    tables = tables.exclude(table_number=0)
    tables = tables.exclude(order_number='')
    tables = tables.order_by('table_number')
    di = {}
    for c in tables:
        di[c.table_number] = {}
        di[c.table_number]["order_number"] = c.order_number
        counter_order = CounterOrder.objects.get(order_number=c.order_number)
        di[c.table_number]["cart"] = counter_order.ordered_items
        if not counter_order.bill_print:
            di[c.table_number]["Bill_print"] = "not_yet"
        else:
            di[c.table_number]["Bill_print"] = "done"
    return JsonResponse({'active_tables': di})


# ======================= Customer Android App Views =========================

@csrf_exempt
def appsignup(request):
    name = request.POST['name']
    email = request.POST['email']
    phone = request.POST['phone']
    password = request.POST['password']
    gender = request.POST['gender']
    try:
        userfromdb = User.objects.get(phone=phone)
        tosend = {"status": "mobilealreadyexists"}
        return JsonResponse(tosend)
    except User.DoesNotExist:
        otp = str(random.randint(100000, 999999))
        #OtpForApp.objects.create(mobile_number=phone, otp=otp)
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(phone)
        messagesendurl += '&message=LHDINDIA%20signup%20OTP%3A%20'
        messagesendurl += otp
        messagesendurl += '&sender=LAZEEZ&route=4&country=0&campaign=signupapp'
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
        tosend = {"status": "otpsent", "otp": otp}
        return JsonResponse(tosend)


@csrf_exempt
def appstoresignup(request):
    name = request.POST['name']
    email = request.POST['email']
    phone = request.POST['phone']
    password = request.POST['password']
    gender = request.POST['gender']
    User.objects.create(full_name=name, phone=phone, password=password, email=email, gender=gender)
    return JsonResponse({"status": "success"})


# @csrf_exempt
# def appcheckotp(request):
#     phone = request.POST['phone']
#     otp = request.POST['otp']
#     otpobject = OtpForApp.objects.get(mobile_number=phone)
#     otp_in_db = otpobject.otp
#     if otp == otp_in_db:
#         return JsonResponse({"status": "success"})
#     else:
#         return JsonResponse({"status": "failed"})


@csrf_exempt
def applogin(request):
    phone = request.POST['phone']
    password = request.POST['password']
    try:
        userfromdb = User.objects.get(phone=phone)
        if password == userfromdb.password:
            if userfromdb.block_user == True:
                return JsonResponse({"status": "blockedbyadmin"})
            else:
                useraddress = userfromdb.address
                usergender = userfromdb.gender
                userwallet = userfromdb.e_wallet
                userdob = userfromdb.date_of_birth
                useroccupation = userfromdb.company
                usercredit = userfromdb.credit_limit
                useremail = userfromdb.email
                usersname = userfromdb.full_name
                di = {}
                orders = AllOrder.objects.filter(customer_mobile=phone)
                orders = orders.exclude(order_status="delivered")
                orders = orders.exclude(order_status="cancelled")
                di["pending_orders"] = {}
                for order in orders:
                    di["pending_orders"][order.order_number] = {}
                    di["pending_orders"][order.order_number]["order_status"] = order.order_status
                    di["pending_orders"][order.order_number]["onlinepay_status"] = order.onlinepay_status
                    di["pending_orders"][order.order_number]["placed_at"] = str(order.placed_at)
                    di["pending_orders"][order.order_number]["expected_at"] = str(order.expected_at)
                    di["pending_orders"][order.order_number]["dispatched_at"] = str(order.dispatched_at)
                    di["pending_orders"][order.order_number]["dispatched_with"] = order.dispatched_with
                    di["pending_orders"][order.order_number]["payment_mode"] = order.payment_mode
                    di["pending_orders"][order.order_number]["source"] = order.source
                    di["pending_orders"][order.order_number]["special_comment"] = order.special_comment
                    di["pending_orders"][order.order_number]["coupon_applied"] = order.coupon_applied
                    di["pending_orders"][order.order_number]["discount_percent"] = order.discount_percent
                    di["pending_orders"][order.order_number]["vat_percent"] = order.vat_percent
                    di["pending_orders"][order.order_number]["service_tax_percent"] = order.service_tax_percent
                    di["pending_orders"][order.order_number]["delivery_charge"] = order.delivery_charge
                    di["pending_orders"][order.order_number]["grand_total"] = order.grand_total
                    di["pending_orders"][order.order_number]["ordered_items"] = order.ordered_items
                di["status"] = "success"
                di["useraddress"] = useraddress
                di["userwallet"] = userwallet
                di["usergender"] = usergender
                di["userdob"] = userdob
                di["useroccupation"] = useroccupation
                di["usercredit"] = usercredit
                di["useremail"] = useremail
                di["usersname"] = usersname
                return JsonResponse(di)
        else:
            return JsonResponse({"status": "wrongpassword"})
    except User.DoesNotExist:
        return JsonResponse({"status": "phonedoesnotexist"})


@csrf_exempt
def forgotpassword(request):
    phone = request.POST['phone']
    try:
        userfromdb = User.objects.get(phone=phone)
        otp = str(random.randint(100000, 999999))
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(phone)
        messagesendurl += '&message=LHDINDIA%20signup%20OTP%3A%20'
        messagesendurl += otp
        messagesendurl += '&sender=LAZEEZ&route=4&country=0&campaign=signupapp'
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
        tosend = {"status": "otpsent", "otp": otp}
        return JsonResponse(tosend)
        # try:
        #     otpobject = OtpForApp.objects.get(mobile_number=phone)
        #     otpobject.otp == otp
        #     otpobject.save()
        #     return JsonResponse({"status": "otpsent"})
        # except OtpForApp.DoesNotExist:
        #     OtpForApp.objects.create(mobile_number=phone, otp=otp)
        #     return JsonResponse({"status": "otpsent"})
    except User.DoesNotExist:
        return JsonResponse({"status": "mobiledoesnotexist"})


@csrf_exempt
def appchangepassword(request):
    phone = request.POST['phone']
    password = request.POST['password']
    try:
        userfromdb = User.objects.get(phone=phone)
        userfromdb.password = password
        userfromdb.save()
        return JsonResponse({"status": "passwordchanged"})
    except User.DoesNotExist:
        return JsonResponse({"status": "userdoesnotexist"})


@csrf_exempt
def getusermoreinfo(request):
    phone = request.POST['phone']
    userfromdb = User.objects.get(phone=phone)
    useraddress = userfromdb.address
    userwallet = userfromdb.e_wallet
    usercredit = userfromdb.credit_limit
    di = {}
    di["useraddress"] = useraddress
    di["userwallet"] = userwallet
    di["usercredit"] = usercredit
    return JsonResponse({'userinfo': di})


@csrf_exempt
def appgetmenu(request):
    di = {}
    di["appcarousel"] = {}
    for k in AppCarousel.objects.all():
        di["appcarousel"][k.image_code] = str(k.image_url)
    for c in Item_Category.objects.all():
        di[c.item_category] = {}
        di[c.item_category]["item_category_image"] = str(c.image)
        di[c.item_category]["item_category_description"] = str(c.description)
    print di
    for s in Item_Subcategory.objects.all():
        if s.subcategory_name not in di[s.belongs_to_category.item_category]:
            di[s.belongs_to_category.item_category][s.subcategory_name] = {}
    print di
    for i in Item.objects.filter(active_on_app=True):
        di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code] = {}
        for g in Item.objects.filter(active_on_app=True, item_code=i.item_code):
            di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code][g.item_subname] = []
            di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code][g.item_subname].append(g.item_name)
            di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code][g.item_subname].append(g.item_subname)
            di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code][g.item_subname].append(g.item_description)
            di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code][g.item_subname].append(g.item_type)
            di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code][g.item_subname].append(g.price)
            di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code][g.item_subname].append(g.serves)
            di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code][g.item_subname].append(g.del_time)
            di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code][g.item_subname].append(g.advance_pay)
            di[i.item_category.item_category][i.item_subcategory.subcategory_name][i.item_code][g.item_subname].append(g.image)
    print di
    return JsonResponse({'status': 'success', 'result': di})


@csrf_exempt
def appvalidatecoupon(request):
    coupon_code = request.POST['coupon_code']
    grandtotal = request.POST['grandtotal']
    coupon_response = {}
    try:
        coupon = CouponInfo.objects.get(coupon_number=coupon_code)
        primary_coupon = Coupons.objects.get(
            prefix=coupon.prefix, suffix=coupon.suffix)
        if ((coupon.blocked == True) and (primary_coupon.is_active == True) and (coupon.end_date >= datetime.datetime.now().date()) and (coupon.start_date <= datetime.datetime.now().date())):
            grandtotal = float(grandtotal)
            if coupon.discount_type == 'Rs':
                grandtotal -= coupon.discount_amount
                if grandtotal < 0:
                    grandtotal = 0
                coupon_response['grandtotal_new'] = grandtotal
                coupon_response['discount_type'] = 'Rs'
                coupon_response['discount_amount'] = str(coupon.discount_amount)
                coupon_response['coupon_applied'] = 'True'
            else:
                grandtotal -= float((grandtotal * coupon.discount_amount) / 100)
                coupon_response['grandtotal_new'] = grandtotal
                coupon_response['discount_type'] = '%'
                coupon_response['discount_amount'] = str(coupon.discount_amount)
                coupon_response['coupon_applied'] = 'True'
            return JsonResponse(coupon_response)
        else:
            coupon_response['coupon_applied'] = 'False'
    except:
        coupon_response['coupon_applied'] = 'False'
    return JsonResponse(coupon_response)



@csrf_exempt
def appgetrunningoffers(request):
    today = datetime.datetime.now()
    offers = Offer.objects.filter(
        is_active=True, applicable_on='Booking',
        offer_date=datetime.datetime.date(today), start_time__lte=datetime.datetime.time(today),
        end_time__gte=datetime.datetime.time(today))
    di = {}
    for offer in offers:
        di[offer.offer_name] = []
        di[offer.offer_name].append(offer.offer_image)
    return JsonResponse({'alloffers': di})


# ======================= Delivery Boy Android App Views =========================

@csrf_exempt
def deliveryapplogin(request):
    username = str(request.POST['username'])
    password = str(request.POST['password'])
    try:
        delivery_boy = Admin_User.objects.get(loginid=username)
        if password == delivery_boy.password:
            if delivery_boy.is_login_enable == False:
                return JsonResponse({"status": "login_disabled"})
            else:
                return JsonResponse({"status": "success", "first_name": delivery_boy.first_name,
                    "last_name": delivery_boy.last_name, "mobile": delivery_boy.mobile})
        else:
            return JsonResponse({"status": "wrong_password"})
    except Admin_User.DoesNotExist:
        return JsonResponse({"status": "delivery_boy_does_not_exist"})


@csrf_exempt
def deliveryappdispatchedorders(request):
    del_mob = str(request.POST['mobile'])
    try:
        delivery_boy = Admin_User.objects.get(mobile=del_mob, roles="deliveryboy")
    except Admin_User.DoesNotExist:
        return JsonResponse({"status": "delivery_boy_does_not_exist"})
    delivery_boy_string = delivery_boy.first_name + " " + delivery_boy.last_name + " " + delivery_boy.mobile
    dispatched_orders = AllOrder.objects.filter(order_status="dispatched",
        dispatched_with=delivery_boy_string)
    di = {}
    for order in dispatched_orders:
        di[order.order_number] = {}
        di[order.order_number]["customer_name"] = order.customer_name
        di[order.order_number]["customer_number"] = order.customer_mobile
        di[order.order_number]["customer_address"] = order.address
        di[order.order_number]["expected_at"] = order.expected_at
        di[order.order_number]["cart_info"] = order.ordered_items
        di[order.order_number]["payment_mode"] = order.payment_mode
        di[order.order_number]["grand_total"] = order.grand_total
    dispatched_orders = list(dispatched_orders)
    if len(dispatched_orders):
        return JsonResponse({"status": "success", "dispatched_orders": di})
    else:
        return JsonResponse({"status": "no_dispatched_orders_for_you"})


@csrf_exempt
def deliveryappmarkdelivered(request):
    order_number = str(request.POST['order_number'])
    order = AllOrder.objects.get(order_number=order_number)
    order.delivered_at = timezone.now()
    if order.paid_at is None:
        order.paid_at = order.delivered_at
    order.order_status = "delivered"
    order.save()
    messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey="
    messagesendurl += "96244AsR6Os06Hs562e546f&mobiles=91"
    messagesendurl += str(order.customer_mobile)
    messagesendurl += "&message=Dear%20"
    messagesendurl += str(order.customer_name)
    messagesendurl += ",%20Thanks%20for%20using%20lhdindia.%20It%20was%20"
    messagesendurl += "Pleasure%20serving%20you.%20we%20hope%20to%20see%20you%20soon."
    messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
    req = urllib2.Request(messagesendurl)
    print urllib2.urlopen(req)
    return JsonResponse({"status": "marked_delivered"})


@csrf_exempt
def deliveryappcompletedorders(request):
    del_mob = str(request.POST['mobile'])
    allorders = AllOrder.objects.all()
    today = datetime.datetime.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today = today.replace(hour=23, minute=59, second=59, microsecond=0)
    try:
        delivery_boy = Admin_User.objects.get(mobile=del_mob, roles="deliveryboy")
    except Admin_User.DoesNotExist:
        return JsonResponse({"status": "delivery_boy_does_not_exist"})
    delivery_boy_string = delivery_boy.first_name + " " + delivery_boy.last_name + " " + delivery_boy.mobile
    orders_completed = allorders.filter(
        paid_at__lte=today, paid_at__gt=today_start, dispatched_with=delivery_boy_string).exclude(
        delivered_at=None).order_by('order_number')
    cash_to_collect = 0.0
    di = {}
    for order in orders_completed:
        di[order.order_number] = {}
        di[order.order_number]["customer_name"] = order.customer_name
        di[order.order_number]["customer_number"] = order.customer_mobile
        di[order.order_number]["customer_address"] = order.address
        di[order.order_number]["expected_at"] = order.expected_at
        di[order.order_number]["cart_info"] = order.ordered_items
        di[order.order_number]["payment_mode"] = order.payment_mode
        di[order.order_number]["grand_total"] = order.grand_total
        if order.payment_mode=="Cash on Delivery":
            cash_to_collect += float(order.grand_total)
    number_of_orders = str(orders_completed.count())
    cash_to_collect = str(cash_to_collect)
    orders_completed = list(orders_completed)
    if len(orders_completed):
        return JsonResponse({"status": "success", "orders_completed": di,
            "cash_to_collect": cash_to_collect, "number_of_orders": number_of_orders})
    else:
        return JsonResponse({"status": "no_completed_orders_for_you"})


@csrf_exempt
def deliveryapporderdispatch(request):
    order_number = str(request.POST['order_number'])
    del_mob = str(request.POST['mobile'])
    order = AllOrder.objects.get(order_number=order_number)
    if order.dispatched_with != "":
        return JsonResponse({"status": "Order_Dispatched_Contact_Admin"})
    if order.order_status != "accepted":
        return JsonResponse({"status": "NOT_ALLOWED_PLEASE_CHECK"})
    delivery_boy = Admin_User.objects.get(mobile=del_mob, roles="deliveryboy")
    delivery_boy_string = delivery_boy.first_name + " " + delivery_boy.last_name + " " + delivery_boy.mobile
    order.dispatched_with = delivery_boy_string
    order.order_status = "dispatched"
    order.dispatched_at = datetime.datetime.now()
    order.save()
    messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
    messagesendurl += str(order.customer_mobile)
    messagesendurl += "&message=lhdindia%20Order%20No:%20"
    messagesendurl += str(order_number)
    messagesendurl += "%0AGrand%20Total:%20"
    messagesendurl += str(order.grand_total)
    messagesendurl += "%0APayment%20Mode:%20"
    if order.payment_mode == 'Cash on Delivery':
        messagesendurl += "Cash%20Payment%20to%20Delivery%20Boy"
    else:
        messagesendurl += "Payment%20Already%20Made"
    messagesendurl += "%0ADelivery%20Boy:%20"
    messagesendurl += str(order.dispatched_with)
    messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
    req = urllib2.Request(messagesendurl)
    print urllib2.urlopen(req)
    order_items = json.loads(order.ordered_items)
    for key1, value1 in order_items.iteritems():
        if key1 != 'totalcost' and key1 != 'grandtotal':
            for key2, value2 in value1.iteritems():
                if key2 != 'name':
                    item_code = value2['item_code']
                    subname = value2['subname']
                    qty = value2['quantity']
                    menu_item = Item.objects.get(
                        item_code=item_code, item_subname=subname)
                    dependency_items = InventoryDependency.objects.filter(
                        dependency_name=menu_item)
                    for item in dependency_items:
                        inventory_item = item.inventory_item
                        inventory_item.quantity -= (item.quantity * qty)
                        inventory_item.save()
                        alert_quantity = inventory_item.alert_quantity
                        if inventory_item.quantity <= alert_quantity:
                            messagesendurl = "https://control.msg91.com/api/"
                            messagesendurl += "sendhttp.php?authkey=96244"
                            messagesendurl += "AsR6Os06Hs562e546f&mobiles=91"
                            messagesendurl += str(inventory_item.alert_number)
                            messagesendurl += "&message=Hello%20admin,%0A"
                            messagesendurl += "Please%20pay%20attention,%20"
                            messagesendurl += str(inventory_item.item_name)
                            messagesendurl += "%20is%20coming%20to%20end."
                            messagesendurl += "&sender=LAZEEZ&route=4"
                            messagesendurl += "&country=0&campaign=signupweb"
                            req = urllib2.Request(messagesendurl)
                            print urllib2.urlopen(req)
    return JsonResponse({"status": "success"})


@csrf_exempt
def deliveryboytripupdates(request):
    del_mob = str(request.POST['mobile'])
    try:
        updated_trip_number = DelBoyUpdatedTrips.objects.get(delboy_mob=del_mob)
        tripnumberitem = ForDelBoyTripNumber.objects.get(pk=1)
        trip_number = tripnumberitem.number
        updated_trip_number.number = trip_number
        updated_trip_number.save()
        tripnumberitem.number += 1
        tripnumberitem.save()
        return JsonResponse({"status": "trip_number_updated"})
    except DelBoyUpdatedTrips.DoesNotExist:
        tripnumberitem = ForDelBoyTripNumber.objects.get(pk=1)
        trip_number = tripnumberitem.number
        tripnumberitem.number += 1
        tripnumberitem.save()
        DelBoyUpdatedTrips.objects.create(delboy_mob=del_mob,number=trip_number)
        return JsonResponse({"status": "new_created_and_trip_number_updated"})


@csrf_exempt
def deliveryappcatchlocation(request):
    del_mob = str(request.POST['mobile'])
    latitude = str(request.POST['latitude'])
    longitude = str(request.POST['longitude'])
    time_stamp_guy = str(datetime.datetime.now())
    try:
        delivery_boy = Admin_User.objects.get(mobile=del_mob, roles="deliveryboy")
    except Admin_User.DoesNotExist:
        return JsonResponse({"status": "delivery_boy_not_found"})
    delivery_boy_string = delivery_boy.first_name + " " + delivery_boy.last_name + " " + delivery_boy.mobile
    today_date = timezone.now().date()
    try:
        location_reports = DelBoyLocationReport.objects.get(delboy_mob=del_mob, date_of_entry=today_date)
        trip_number_item = DelBoyUpdatedTrips.objects.get(delboy_mob=del_mob)
        trip_number = str(trip_number_item.number)
        time_stamp_guy = str(datetime.datetime.now())
        coordinate_info = json.loads(location_reports.coordinate_info)
        if trip_number in coordinate_info.keys():
            coordinate_info_inside = coordinate_info[trip_number]
            coordinate_info_inside[time_stamp_guy] = {"latitude": latitude, "longitude": longitude}
            coordinate_info[trip_number] = coordinate_info_inside
            location_reports.coordinate_info = json.dumps(coordinate_info)
            location_reports.save()
        else:
            coordinate_info[trip_number] = {}
            coordinate_info_inside = coordinate_info[trip_number]
            coordinate_info_inside[time_stamp_guy] = {"latitude": latitude, "longitude": longitude}
            coordinate_info[trip_number] = coordinate_info_inside
            location_reports.coordinate_info = json.dumps(coordinate_info)
            location_reports.save()
        try:
            current_location = DelBoyCurrentLocation.objects.get(delboy_mob=del_mob)
            current_location.lastupdated_latitude = latitude
            current_location.lastupdated_longitude = longitude
            current_location.lastupdated_at = datetime.datetime.now()
            current_location.save()
        except DelBoyCurrentLocation.DoesNotExist:
            DelBoyCurrentLocation.objects.create(delboy_mob=del_mob, delboy_name=delivery_boy_string,
                lastupdated_latitude=latitude, lastupdated_longitude=longitude, 
                lastupdated_at=time_stamp_guy)
        return JsonResponse({"status": "updated_old"})
    except DelBoyLocationReport.DoesNotExist:
        trip_number_item = DelBoyUpdatedTrips.objects.get(delboy_mob=del_mob)
        trip_number = trip_number_item.number
        time_stamp_guy = datetime.datetime.now()
        trip_number = str(trip_number)
        time_stamp_guy = str(time_stamp_guy)
        coordinate_info = {}
        coordinate_info[trip_number] = {}
        coordinate_info[trip_number][time_stamp_guy] = {"latitude": latitude, "longitude": longitude}
        coordinate_info = json.dumps(coordinate_info)
        DelBoyLocationReport.objects.create(delboy_mob=del_mob, date_of_entry=today_date,
            delboy_name=delivery_boy_string, coordinate_info=coordinate_info)
        return JsonResponse({"status": "updated_new"})


#############Laundry Project Views############

def laundry_applicationsetup(request):
    return render(request, 'app/laundry_applicationsetup.html')


def laundry_setupratelist(request):
    if 'item_code_exists' in request.session:
        del request.session['item_code_exists']
    if request.method == "POST":
        item_code = request.POST['item_code']
        try:
            PerItemRateList.objects.get(item_code=item_code)
            items = PerItemRateList.objects.all()
            request.session['item_code_exists'] = 'True'
            return render(request, 'app/laundry_setupratelist.html', {'items': items})
        except PerItemRateList.DoesNotExist:
            item_name = request.POST['item_name']
            steam_iron_price = request.POST['steam_iron_price']
            wash_fold_price = request.POST['wash_fold_price']
            wash_iron_price = request.POST['wash_iron_price']
            dryclean_price = request.POST['dryclean_price']
            if 'is_express' in request.POST:
                is_express = True
            else:
                is_express = False
            PerItemRateList.objects.create(item_code=item_code, item_name=item_name, 
                steam_iron_price=steam_iron_price, wash_fold_price=wash_fold_price,
                wash_iron_price=wash_iron_price, dryclean_price=dryclean_price, 
                is_express=is_express)
    items = PerItemRateList.objects.all().order_by('item_code')
    return render(request, 'app/laundry_setupratelist.html', {'items': items})


def deleteratelistitem(request, item_code):
    item = PerItemRateList.objects.get(item_code=item_code)
    item.delete()
    return HttpResponseRedirect('/laundry/setupratelist/')


def laundry_setuplaundryplans(request):
    if 'plan_code_exists' in request.session:
        del request.session['plan_code_exists']
    if 'please_not_both' in request.session:
        del request.session['please_not_both']
    if request.method == "POST":
        plan_code = request.POST['plan_code']
        try:
            LaundryPlans.objects.get(plan_code=plan_code)
            plans = LaundryPlans.objects.all()
            request.session['plan_code_exists'] = 'True'
            return render(request, 'app/laundry_setuplaundryplans.html', {'plans': plans})
        except LaundryPlans.DoesNotExist:
            plan_name = request.POST['plan_name']
            lot_size = request.POST['lot_size']
            if lot_size == "":
                lot_size = "Not Applicable"
            pricing_per_kg = request.POST['pricing_per_kg']
            pricing_as_whole = request.POST['pricing_as_whole']
            if (pricing_per_kg == "" and pricing_as_whole == "") or (pricing_per_kg != "" and pricing_as_whole != ""):
                request.session['please_not_both'] = 'True'
                plans = LaundryPlans.objects.all()
                return render(request, 'app/laundry_setuplaundryplans.html', {'plans': plans})
            LaundryPlans.objects.create(plan_code=plan_code, plan_name=plan_name, 
                lot_size=lot_size, pricing_per_kg=pricing_per_kg, pricing_as_whole=pricing_as_whole)
    plans = LaundryPlans.objects.all().order_by('plan_code')
    return render(request, 'app/laundry_setuplaundryplans.html', {'plans': plans})


def deletelaundryplan(request, plan_code):
    plan = LaundryPlans.objects.get(plan_code=plan_code)
    plan.delete()
    return HttpResponseRedirect('/laundry/setuplaundryplans/')


def laundry_setuppickupdropslots(request):
    if 'slot_code_exists' in request.session:
        del request.session['slot_code_exists']
    if 'end_less_than_start' in request.session:
        del request.session['end_less_than_start']
    if request.method == "POST":
        slot_code = request.POST['slot_code']
        try:
            PickupDropSlots.objects.get(slot_code=slot_code)
            slots = PickupDropSlots.objects.all().order_by('slot_code')
            request.session['slot_code_exists'] = 'True'
            return render(request, 'app/laundry_setuppickupdropslots.html', {'slots': slots})
        except PickupDropSlots.DoesNotExist:
            pickup_or_drop = request.POST['pickup_or_drop']
            slot_begins_at = request.POST['slot_begins_at']
            slot_ends_at = request.POST['slot_ends_at']
            if slot_ends_at < slot_begins_at:
                request.session['end_less_than_start'] = 'True'
                slots = PickupDropSlots.objects.all().order_by('slot_code')
                return render(request, 'app/laundry_setuppickupdropslots.html', {'slots': slots})
            PickupDropSlots.objects.create(slot_code=slot_code, pickup_or_drop=pickup_or_drop,
                slot_begins_at=slot_begins_at, slot_ends_at=slot_ends_at)
    slots = PickupDropSlots.objects.all().order_by('slot_code')
    return render(request, 'app/laundry_setuppickupdropslots.html', {'slots': slots})


def deletepickupdropslot(request, slot_code):
    slot = PickupDropSlots.objects.get(slot_code=slot_code)
    slot.delete()
    return HttpResponseRedirect('/laundry/setuppickupdropslots/')


def laundry_index(request):
    laundryplans = LaundryPlans.objects.all()
    return render(request, 'app/laundry_index.html', {'laundryplans':laundryplans})


def laundry_loginsignup(request):
    if 'user' in request.session:
        return HttpResponseRedirect("/laundry/bookorder/")
    return render(request, 'app/laundry_loginsignup.html')


def laundry_bookorder(request):
    if 'user' not in request.session:
        return HttpResponseRedirect("/laundry/loginsignup/")
    laundryplans = LaundryPlans.objects.all()
    pickupslots = PickupDropSlots.objects.filter(pickup_or_drop="Pickup")
    dropslots = PickupDropSlots.objects.filter(pickup_or_drop="Drop")
    return render(request, 'app/laundry_bookorder.html', {'laundryplans':laundryplans,
        'pickupslots':pickupslots, 'dropslots':dropslots})


@csrf_exempt
def laundry_login(request):
    if 'userisblocked' in request.session:
        del request.session['userisblocked']
    if 'wrongpassword' in request.session:
        del request.session['wrongpassword']
    if 'userinvalid' in request.session:
        del request.session['userinvalid']
    if 'opensignuptab' in request.session:
        del request.session['opensignuptab']
    phone = request.POST['phone']
    password = request.POST['password']
    try:
        userstored = User.objects.get(phone=phone)
        if password == userstored.password:
            if userstored.block_user is False:
                user = {}
                user['name'] = userstored.full_name
                user['email'] = userstored.email
                user['phone'] = phone
                user['e_wallet'] = float(userstored.e_wallet)
                user['credit_limit'] = float(userstored.credit_limit)
                if userstored.address is not None:
                    user['address'] = userstored.address
                request.session['user'] = user
                return HttpResponseRedirect("/laundry/bookorder/")
            else:
                request.session['userisblocked'] = 'true'
        else:
            request.session['wrongpassword'] = "true"
    except:
        request.session['userinvalid'] = "true"
    return HttpResponseRedirect("/laundry/loginsignup/")


@csrf_exempt
def laundry_signup(request):
    if 'passwordlessthansix' in request.session:
        del request.session['passwordlessthansix']
    if 'phonenotequaltoten' in request.session:
        del request.session['phonenotequaltoten']
    if 'mobileexistsalready' in request.session:
        del request.session['mobileexistsalready']
    name = request.POST['name']
    phone = request.POST['phone']
    email = request.POST['email']
    password = request.POST['password']
    gender = request.POST['gender']
    if len(password) < 6:
        request.session['opensignuptab'] = "true"
        request.session['passwordlessthansix'] = "true"
        return HttpResponseRedirect("/laundry/loginsignup")
    if len(phone) != 10:
        request.session['opensignuptab'] = "true"
        request.session['phonenotequaltoten'] = "true"
        return HttpResponseRedirect("/laundry/loginsignup")
    try:
        user = User.objects.get(phone=phone)
        request.session['opensignuptab'] = "true"
        request.session['mobileexistsalready'] = "true"
        return HttpResponseRedirect("/laundry/loginsignup")
    except User.DoesNotExist:
        user = {}
        user['name'] = name
        user['phone'] = phone
        user['email'] = email
        user['password'] = password
        user['gender'] = gender
        user['otp'] = str(random.randint(100000, 999999))
        otp = user['otp']
        messagesendurl = "https://control.msg91.com/api/sendhttp.php?authkey=96244AsR6Os06Hs562e546f&mobiles=91"
        messagesendurl += str(phone)
        messagesendurl += "&message=lhd%20signup%20OTP%3A%20"
        messagesendurl += otp
        messagesendurl += "&sender=LAZEEZ&route=4&country=0&campaign=signupweb"
        req = urllib2.Request(messagesendurl)
        print urllib2.urlopen(req)
        request.session['usersignup'] = user
        request.session['onetimesorry'] = "true"
        return HttpResponseRedirect("/laundry/verifyotp")


def laundry_verifyotp(request):
    return render(request, 'app/laundry_verifyotp.html')


@csrf_exempt
def laundry_otpverify(request):
    if 'otpinvalid' in request.session:
        del request.session['otpinvalid']
    if 'passwordlessthansix' in request.session:
        del request.session['passwordlessthansix']
    if 'phonenotequaltoten' in request.session:
        del request.session['phonenotequaltoten']
    if 'mobileexistsalready' in request.session:
        del request.session['mobileexistsalready']
    if 'opensignuptab' in request.session:
        del request.session['opensignuptab']
    otpgot = request.POST['otp']
    if 'usersignup' not in request.session:
        return HttpResponseRedirect("/laundry/loginsignup")
    else:
        usersignup = request.session['usersignup']
        otpstored = usersignup['otp']
        if otpgot != otpstored:
            request.session['otpinvalid'] = "true"
            return HttpResponseRedirect("/laundry/verifyotp")
        else:
            name = usersignup['name']
            phone = usersignup['phone']
            email = usersignup['email']
            password = usersignup['password']
            gender = usersignup['gender']
            request.session.pop('usersignup')
            usersignup.pop('password')
            request.session['user'] = usersignup
            User.objects.create(
                full_name=name, phone=phone, email=email,
                password=password, gender=gender)
            return HttpResponseRedirect("/laundry/bookorder/")


def laundry_pricing(request):
    laundryplans = LaundryPlans.objects.all()
    peritemrates = PerItemRateList.objects.all()
    return render(request, 'app/laundry_pricing.html', {'laundryplans':laundryplans,
        'peritemrates': peritemrates})