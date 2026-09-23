from django.contrib import admin
from .models import Logs, LogDetails, Wallet, Order, Cart, ViewLog, Transaction_History, Contact, Category, LogOrder, Shopviaclone22, DollarRate, Payment, Accsmtp, Verify_Payment, ProfileDetails, Clonevn, Bank_Account, APIs, SMMCategory, Platform, SMMService, SMMOrder

class LogAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'api_id']

class ProfileDetailsAdmin(admin.ModelAdmin):
    list_display = ['which_log', 'details', 'used']
    search_fields = ['which_log__name']
    
class LogDetailsAdmin(admin.ModelAdmin):
    list_display = ['which_log', 'details', 'used']
    search_fields = ['which_log__name']

class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance']
    search_fields = ['user__email', 'user__username']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'log', 'qty']
    search_fields = ['id']

class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'log']
    
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id']
    
class VerifyAdmin(admin.ModelAdmin):
    list_display = ['key']
    
class DollarRateAdmin(admin.ModelAdmin):
    list_display = ['rate']
    
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    
class Shopviaclone22Admin(admin.ModelAdmin):
    list_display = ['username']
    
class ClonevnAdmin(admin.ModelAdmin):
    list_display = ['username']
    
class Bank_AccountAdmin(admin.ModelAdmin):
    list_display = ['bank_name', 'account_number']
    search_fields = ['bank_name', 'account_number']
    
class AccsmtpAdmin(admin.ModelAdmin):
    list_display = ['username']

class ViewLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'log']
    
class LogOrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'log']
    search_fields = ['log']

class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status']
    search_fields = ['email']
    
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject']
    search_fields = ['name']
    
class SMMCategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ['name']
    
class PlatformAdmin(admin.ModelAdmin):
    list_display = ["name", "code"]
    search_fields = ['name']

class SMMServiceAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ['name']

class SMMOrderAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "order_id", "status", "date"]
    
class APIsAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "percentage"]
    search_fields = ["name"]


admin.site.register(Platform, PlatformAdmin)
admin.site.register(SMMCategory, SMMCategoryAdmin)
admin.site.register(SMMService, SMMServiceAdmin)
admin.site.register(SMMOrder, SMMOrderAdmin)
admin.site.register(APIs, APIsAdmin)
admin.site.register(Logs, LogAdmin)
admin.site.register(Bank_Account, Bank_AccountAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(ProfileDetails, ProfileDetailsAdmin)
admin.site.register(LogDetails, LogDetailsAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Shopviaclone22, Shopviaclone22Admin)
admin.site.register(Clonevn, ClonevnAdmin)
admin.site.register(Accsmtp, AccsmtpAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(ViewLog, ViewLogAdmin)
admin.site.register(Verify_Payment, VerifyAdmin)
admin.site.register(LogOrder, LogOrderAdmin)
admin.site.register(DollarRate, DollarRateAdmin)
admin.site.register(Transaction_History, TransactionHistoryAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Category, CategoryAdmin)