import datetime
from django.utils import timezone
from django.db import models
from multiselectfield import MultiSelectField
import datetime
from datetime import timedelta


class AppCarousel(models.Model):
    image_code = models.CharField(max_length=20, null=True)
    image_url = models.CharField(max_length=200)

    def __str__(self):
        return self.image_url


class City(models.Model):
    city = models.CharField(max_length=50)

    def __str__(self):
        return self.city


class RestrictedAreas(models.Model):
    restricted_areas = models.CharField(max_length=200)

    def __str__(self):
        return self.restricted_areas


class Branch(models.Model):
    branch = models.CharField(max_length=50)

    def __str__(self):
        return self.branch


class PaymentMode(models.Model):
    payment_mode = models.CharField(max_length=50)

    def __str__(self):
        return self.payment_mode


class DeliveryCharge(models.Model):
    delivery_charge = models.CharField(max_length=20)

    def __str__(self):
        return self.delivery_charge


class Admin_User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    loginid = models.CharField(max_length=50)
    password = models.CharField(max_length=80)
    email = models.CharField(max_length=50)
    roles = models.CharField(max_length=50)
    mobile = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    company = models.CharField(max_length=50)
    city = models.ForeignKey('City')
    branch = models.ForeignKey('Branch')
    address = models.TextField()
    dateofbirth = models.CharField(max_length=50)
    is_attendance_enable = models.BooleanField()
    is_login_enable = models.BooleanField()
    is_active = models.BooleanField()

    def __str__(self):
        return self.first_name + " " + self.last_name


class Item_Category(models.Model):
    item_category = models.CharField(max_length=50)
    is_home_display = models.BooleanField()
    description = models.CharField(max_length=100, null=True)
    is_active = models.BooleanField()
    image = models.CharField(max_length=250, default="http://delivery.lhdindia.com/Files/Image/LHD_NA.jpg")

    def __str__(self):
        return self.item_category


class Item_Subcategory(models.Model):
    subcategory_name = models.CharField(max_length=100)
    belongs_to_category = models.ForeignKey('Item_Category')

    def __str__(self):
        return self.subcategory_name


class Item(models.Model):
    item_name = models.CharField(max_length=50)
    item_subname = models.CharField(max_length=50)
    item_code = models.CharField(max_length=50)
    price = models.CharField(max_length=50)
    serves = models.CharField(max_length=50, default=0)
    del_time = models.CharField(max_length=50, default="Immediate")
    advance_pay = models.CharField(max_length=50, default="N.A.")
    discount = models.CharField(max_length=50)
    item_description = models.CharField(max_length=400)
    item_type = models.CharField(max_length=50)
    item_category = models.ForeignKey('Item_Category')
    item_subcategory = models.ForeignKey('Item_Subcategory')
    is_active = models.BooleanField()
    active_on_website = models.BooleanField(default=True)
    active_on_app = models.BooleanField(default=True)
    active_on_callcenter = models.BooleanField(default=True)
    active_on_counter = models.BooleanField(default=True)
    active_on_outside = models.BooleanField(default=True)
    image = models.CharField(max_length=250, default="http://delivery.lhdindia.com/Files/Image/LHD_NA.jpg")

    def __str__(self):
        return self.item_name + ' ' + self.item_subname


class Membership(models.Model):
    membership_id = models.IntegerField(primary_key=True)
    membership_name = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=4, decimal_places=2)
    is_active = models.BooleanField()

    def __str__(self):
        return self.membership_name


class User(models.Model):
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=80)
    email = models.CharField(max_length=50)
    gender = models.CharField(max_length=20)
    address = models.TextField(null=True)
    city = models.ForeignKey("City", null=True)
    company = models.CharField(max_length=50, default='Not Entered')
    block_user = models.BooleanField(default=False)
    credit_limit = models.DecimalField(
        max_digits=9, decimal_places=2, default=0.0)
    otp = models.IntegerField(default=0)
    membership_type = models.ForeignKey("Membership", default=1)
    e_wallet = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    date_of_birth = models.DateField(null=True)
    branch = models.ForeignKey("Branch", default=1)

    def __str__(self):
        return self.full_name


class Partner(models.Model):
    name = models.CharField(max_length=100)
    loginid = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    mobile = models.CharField(max_length=10)
    address = models.TextField()
    city = models.ForeignKey("City")
    partner_name = models.CharField(max_length=100)
    owner_number = models.CharField(max_length=10)
    contact_number = models.CharField(max_length=10)
    service_tax_number = models.CharField(max_length=50)
    vat_number = models.CharField(max_length=50)
    logo_link = models.URLField(max_length=200)
    vat_percent = models.DecimalField(max_digits=5, decimal_places=2)
    service_charge_percent = models.DecimalField(
        max_digits=5, decimal_places=2)
    service_tax_percent = models.DecimalField(max_digits=5, decimal_places=2)
    e_wallet = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0)
    my_counter = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0)
    credit_limit = models.IntegerField(default=0)
    otp_required = models.BooleanField(default=False)
    membership_type = models.ForeignKey("Membership", default=3)

    def __str__(self):
        return self.name


class PartnerMenu(models.Model):
    item = models.ForeignKey("Item")
    expected_price = models.CharField(max_length=20)
    partner = models.ForeignKey("Partner")

    def __str__(self):
        return self.item.item_name + ' ' + self.item.item_subname


class Coupons(models.Model):
    num_of_coupons = models.IntegerField()
    prefix = models.CharField(max_length=10)
    suffix = models.CharField(max_length=10)
    start_from = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    discount_type = models.CharField(max_length=10)
    discount_value = models.IntegerField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.num_of_coupons)


class CouponInfo(models.Model):
    coupon_number = models.CharField(max_length=40)
    order_number = models.CharField(max_length=50, null=True)
    prefix = models.CharField(max_length=10)
    suffix = models.CharField(max_length=10)
    start_from = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    discount_type = models.CharField(max_length=10)
    discount_amount = models.IntegerField()
    blocked = models.BooleanField(default=True)

    def __str__(self):
        return str(self.coupon_number)


class OrderSource(models.Model):
    source = models.CharField(max_length=50)

    def __str__(self):
        return self.source


class AllOrder(models.Model):
    order_number = models.CharField(max_length=50)
    order_status = models.CharField(max_length=50)
    onlinepay_status = models.CharField(max_length=50, null=True)
    offer_from_web = models.CharField(max_length=50, null=True)
    branch_assigned_at = models.DateTimeField(null=True)
    branch_assigned = models.CharField(max_length=50)
    placed_at = models.DateTimeField(null=True)
    expected_at = models.DateTimeField(null=True)
    no_of_people = models.CharField(max_length=15, null=True)
    accepted_by = models.CharField(max_length=50)
    accepted_at = models.DateTimeField(null=True)
    dispatched_by = models.CharField(max_length=50)
    dispatched_at = models.DateTimeField(null=True)
    dispatched_with = models.CharField(max_length=50)
    delivered_at = models.DateTimeField(null=True)
    paid_at = models.DateTimeField(null=True)
    payment_mode = models.CharField(max_length=50)
    delivery_type = models.CharField(max_length=50)
    customer_name = models.CharField(max_length=50)
    customer_mobile = models.CharField(max_length=50)
    source = models.CharField(max_length=50)
    address = models.TextField(null=True)
    special_comment = models.CharField(max_length=100)
    ordered_items = models.CharField(max_length=10000)
    subtotal = models.CharField(max_length=50)
    coupon_applied = models.CharField(max_length=50)
    discount_percent = models.CharField(max_length=50)
    vat_percent = models.CharField(max_length=50)
    service_charge_percent = models.CharField(max_length=50)
    service_tax_percent = models.CharField(max_length=50)
    e_wallet = models.CharField(max_length=50, default=0)
    delivery_charge = models.CharField(max_length=20, default=0)
    advance_pay = models.FloatField(default=0)
    grand_total = models.CharField(max_length=20)

    def get_timediff(self):
        current_time = timezone.now()
        if self.expected_at > current_time:
            return True
        else:
            return False

    def discount_rs(self):
        return (float(self.subtotal) * float(self.discount_percent)) / 100

    def service_tax_rs(self):
        return (float(self.subtotal) * float(self.service_tax_percent)) / 100

    def vat_rs(self):
        return (float(self.subtotal) * float(self.vat_percent)) / 100

    def service_charge_rs(self):
        return (float(self.subtotal) * float(self.service_charge_percent)) / 100

    def balance_amount(self):
        return (float(self.grand_total) - float(self.advance_pay))

    def __str__(self):
        return self.order_number


class ForOrdernumber(models.Model):
    number = models.IntegerField()

    def __str__(self):
        return str(self.number)


class PromotionImage(models.Model):
    image_url = models.CharField(max_length=200)

    def __str__(self):
        return self.image_url


class PromotionVideo(models.Model):
    video = models.CharField(max_length=200)

    def __str__(self):
        return self.video


class NewsAndEvent(models.Model):
    title = models.CharField(max_length=200)
    image_url = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title



Delivery_Days = ((1, 'Sunday'),
                 (2, 'Monday'),
                 (3, 'Tuesday'),
                 (4, 'Wednesday'),
                 (5, 'Thursday'),
                 (6, 'Friday'),
                 (7, 'Saturday'))

Payment_Mode = (('cod', 'Cash on Delivery'),
                ('online', 'Online Payment'),
                ('smd', 'Sodexo Meal Passes'),
                ('credit', 'Credit'))


class Offer(models.Model):
    offer_name = models.CharField(max_length=100)
    offer_image = models.CharField(max_length=200)
    applicable_on = models.CharField(max_length=50)
    offer_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.CharField(max_length=1500)
    discount = models.CharField(max_length=10, default=20)
    delivery_days = MultiSelectField(choices=Delivery_Days)
    payment_mode = MultiSelectField(choices=Payment_Mode)
    is_active = models.BooleanField(default=False)
    is_default_membership_applied = models.BooleanField(default=False)
    are_coupon_applied = models.BooleanField(default=False)

    def get_timediff(self):
        current_day = datetime.datetime.now() + timedelta(minutes=1)
        current_time = current_day.time()
        if self.start_time > current_time:
            return True
        else:
            return False

    def end_datetime(self):
        return datetime.datetime.combine(self.offer_date, self.end_time)

    def start_datetime(self):
        return datetime.datetime.combine(self.offer_date, self.start_time)

    def __str__(self):
        return self.offer_name


class OfferMenu(models.Model):
    date = models.DateField(null=True)
    daytime = models.CharField(max_length=50,null=True)
    item = models.ForeignKey("Item")
    discount_percent = models.CharField(max_length=20)
    offer = models.ForeignKey("Offer")

    def get_discount_price(self):
        discount = (int(self.item.price) * int(self.discount_percent) / 100)
        discount_price = int(self.item.price) - discount
        return discount_price

    def __str__(self):
        return self.item.item_name + ' ' + self.item.item_subname


class Customer(models.Model):
    customer_name = models.CharField(max_length=40)
    customer_number = models.CharField(max_length=40)
    customer_address = models.TextField(null=True)
    isblocked = models.BooleanField(default=False)
    order_number = models.CharField(max_length=40)

    def __str__(self):
        return self.customer_name


class Waiter(models.Model):
    name = models.CharField(max_length=100)
    userid = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    branch_name = models.CharField(max_length=50, default="MP Nagar")

    def __str__(self):
        return self.name


class CounterTable(models.Model):
    branch_name = models.CharField(max_length=50, default="MP Nagar")
    table_number = models.IntegerField()
    table_name = models.CharField(max_length=50)
    max_occupy = models.IntegerField()
    waiter = models.ForeignKey("Waiter", null=True)
    is_active = models.BooleanField(default=True)
    order_number = models.CharField(max_length=50, default='')

    def __str__(self):
        return self.table_name


class CounterOrder(models.Model):
    order_number = models.CharField(max_length=50)
    ordered_at = models.DateTimeField()
    order_status = models.CharField(max_length=50, default='active')
    branch = models.ForeignKey("Branch", null=True)
    assigned_waiter = models.ForeignKey("Waiter", null=True)
    assigned_at = models.DateTimeField(null=True)
    assigned_by = models.ForeignKey("Admin_User", null=True)
    payment_mode = models.ForeignKey("PaymentMode", null=True)
    customer = models.ForeignKey("Customer", null=True)
    branch_name = models.CharField(max_length=100, null=True)
    table_no = models.ForeignKey("CounterTable")
    bill_print = models.DateTimeField(null=True)
    ordered_items = models.CharField(max_length=10000)
    subtotal = models.CharField(max_length=50)
    discount_percent = models.CharField(max_length=50)
    vat_percent = models.CharField(max_length=50)
    service_charge_percent = models.CharField(max_length=50)
    service_tax_percent = models.CharField(max_length=50)
    credit_amount = models.FloatField(default=0)
    advance_pay = models.FloatField(default=0)
    grand_total = models.FloatField()

    def discount_rs(self):
        return (float(self.subtotal) * float(self.discount_percent)) / 100

    def service_tax_rs(self):
        return (float(self.subtotal) * float(self.service_tax_percent)) / 100

    def vat_rs(self):
        return (float(self.subtotal) * float(self.vat_percent)) / 100

    def service_charge_rs(self):
        return (float(self.subtotal) * float(self.service_charge_percent)) / 100

    def balance_pay(self):
        return (float(self.grand_total) - float(self.advance_pay))

    def __str__(self):
        return self.order_number


class CounterOrdernumber(models.Model):
    number = models.IntegerField()

    def __str__(self):
        return str(self.number)


class Expense(models.Model):
    date = models.DateTimeField()
    expense_for = models.CharField(max_length=80)
    amount = models.FloatField()
    branch_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.expense_for


class ExpenseCollection(models.Model):
    date = models.DateTimeField()
    collection_for = models.CharField(max_length=80)
    amount = models.FloatField()
    branch_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.collection_for


class PayDeliveryBoy(models.Model):
    date = models.DateTimeField()
    delivery_boy = models.ForeignKey("Admin_User", null=True)
    amount = models.FloatField()
    branch_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.delivery_boy.first_name


class CollectiontoDelboy(models.Model):
    date = models.DateTimeField()
    delivery_boy = models.ForeignKey("Admin_User", null=True)
    amount = models.FloatField()
    collected_at = models.DateTimeField(null=True)
    branch_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.delivery_boy.first_name


class InventoryItem(models.Model):
    item_name = models.CharField(max_length=50, unique=True)
    quantity = models.FloatField()
    alert_quantity = models.FloatField()
    alert_number = models.CharField(max_length=10)
    alert_email = models.EmailField(max_length=30)

    class Meta:
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"

    def __str__(self):
        return self.item_name


class InventoryDependency(models.Model):
    dependency_name = models.ForeignKey('Item')
    inventory_item = models.ForeignKey('InventoryItem')
    quantity = models.FloatField()

    def __str__(self):
        return self.dependency_name.item_name


class InventoryPurchase(models.Model):
    item_name = models.ForeignKey('InventoryItem')
    date = models.DateTimeField()
    quantity = models.FloatField()
    bill_no = models.CharField(max_length=50, null=True)
    amount = models.FloatField(null=True)

    def __str__(self):
        return self.item_name.item_name


class DelBoyCurrentLocation(models.Model):
    delboy_mob = models.CharField(max_length=50)
    delboy_name = models.CharField(max_length=50)
    lastupdated_latitude = models.CharField(max_length=50, null=True)
    lastupdated_longitude = models.CharField(max_length=50, null=True)
    lastupdated_at = models.DateTimeField()

    def __str__(self):
        return str(self.delboy_name)


class DelBoyLocationReport(models.Model):
    delboy_mob = models.CharField(max_length=50)
    delboy_name = models.CharField(max_length=50)
    date_of_entry = models.DateField()
    coordinate_info = models.CharField(max_length=1000000, null=True)

    def __str__(self):
        return str(self.delboy_name)


class ForDelBoyTripNumber(models.Model):
    number = models.IntegerField()

    def __str__(self):
        return str(self.number)


class DelBoyUpdatedTrips(models.Model):
    delboy_mob = models.CharField(max_length=50)
    number = models.IntegerField()

    def __str__(self):
        return str(self.delboy_mob)


class DueCreditInfo(models.Model):
    order_number = models.CharField(max_length=50)
    loginid = models.CharField(max_length=50, null=True)
    customer_mobile = models.CharField(max_length=50, null=True)
    amount_due = models.CharField(max_length=50)
    is_cleared = models.BooleanField(default=False)

    def __str__(self):
        return str(self.order_number)


########Models for Laundry Work#########

class PerItemRateList(models.Model):
    item_code = models.CharField(max_length=20, null=True)
    item_name = models.CharField(max_length=50)
    steam_iron_price = models.CharField(max_length=10, null=True)
    wash_fold_price = models.CharField(max_length=10, null=True)
    wash_iron_price = models.CharField(max_length=10, null=True)
    dryclean_price = models.CharField(max_length=10, null=True)
    is_express = models.BooleanField(default=False)

    def __str__(self):
        return str(self.item_name)


class LaundryPlans(models.Model):
    plan_code = models.CharField(max_length=50, null=True)
    plan_name = models.CharField(max_length=50)
    lot_size = models.CharField(max_length=50, null=True)
    pricing_per_kg = models.CharField(max_length=50, null=True)
    pricing_as_whole = models.CharField(max_length=50, null=True)

    def __str__(self):
        return str(self.plan_name)


class PickupDropSlots(models.Model):
    slot_code = models.CharField(max_length=50, null=True)
    pickup_or_drop = models.CharField(max_length=20)
    slot_begins_at = models.CharField(max_length=10)
    slot_ends_at = models.CharField(max_length=20)

    def __str__(self):
        return str(self.pickup_or_drop + " " + self.slot_begins_at + "-" + self.slot_ends_at)