from django.contrib import admin
from .models import *
# Register your models here.

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user','payment_id','payment_method','amount_paid','status','created_at']
    list_filter = ['status','created_at']
    search_fields = ['payment_id','status','created_at']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','first_name','last_name','phone','email','city','order_total','status','is_ordered','created_at','full_name']
    list_filter = ['status','is_ordered']
    search_fields = ['order_number','first_name','last_name','phone','email','city']


admin.site.register(Payment,PaymentAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct)