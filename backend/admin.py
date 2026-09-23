from pyexpat import model
from django.contrib import admin
from .models import S2, All

class S2Admin(admin.ModelAdmin):
    list_display = ['name', 'status']

class AllAdmin(admin.ModelAdmin):
    list_display = ['name', 'status']

admin.site.register(S2, S2Admin)
admin.site.register(All, AllAdmin)