from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.

from payroll_app.models import Employer, User, Position, LeaveManage

class UserAdmin (admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email']
    list_filter = ['position']

admin.site.register(User, UserAdmin)
admin.site.register(Employer)