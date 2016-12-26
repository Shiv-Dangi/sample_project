from django.contrib import admin
from . import models
# Register your models here.


admin.site.register(models.Admin_User)
admin.site.register(models.Branch)
admin.site.register(models.Item_Category)
admin.site.register(models.Item_Subcategory)
admin.site.register(models.Item)
admin.site.register(models.City)
admin.site.register(models.RestrictedAreas)
admin.site.register(models.Membership)
admin.site.register(models.User)
admin.site.register(models.Partner)
admin.site.register(models.PartnerMenu)
admin.site.register(models.Coupons)
admin.site.register(models.CouponInfo)
admin.site.register(models.AllOrder)
admin.site.register(models.ForOrdernumber)
admin.site.register(models.PromotionImage)
admin.site.register(models.PromotionVideo)
admin.site.register(models.Offer)
admin.site.register(models.OfferMenu)
admin.site.register(models.Customer)
admin.site.register(models.OrderSource)
admin.site.register(models.PaymentMode)
admin.site.register(models.DeliveryCharge)
admin.site.register(models.Waiter)
admin.site.register(models.CounterTable)
admin.site.register(models.CounterOrder)
admin.site.register(models.CounterOrdernumber)
admin.site.register(models.Expense)
admin.site.register(models.ExpenseCollection)
admin.site.register(models.PayDeliveryBoy)
admin.site.register(models.CollectiontoDelboy)
admin.site.register(models.InventoryItem)
admin.site.register(models.InventoryDependency)
admin.site.register(models.InventoryPurchase)
admin.site.register(models.DelBoyCurrentLocation)
admin.site.register(models.DelBoyLocationReport)
admin.site.register(models.ForDelBoyTripNumber)
admin.site.register(models.DelBoyUpdatedTrips)
admin.site.register(models.DueCreditInfo)
admin.site.register(models.NewsAndEvent)
admin.site.register(models.PerItemRateList)
admin.site.register(models.LaundryPlans)
admin.site.register(models.PickupDropSlots)
admin.site.register(models.AppCarousel)


# class DependencyInline(admin.TabularInline):
#     model = models.Dependency
#     max_num = 10
#     extra = 1


# class InventoryItemAdmin(admin.ModelAdmin):
#     inlines = (DependencyInline, )
#     search_fields = ('item_name', )
#     list_filter = ('updated_on', 'quantity_left', 'alert_quantity', )
#     ordering = ('item_name', )


# admin.site.register(models.InventoryItem, InventoryItemAdmin)
