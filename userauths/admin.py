from django.contrib import admin
from userauths.models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'bio', 'email_confirmed']
    search_fields = ['email']

admin.site.register(User, UserAdmin)