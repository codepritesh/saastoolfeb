from django.contrib import admin

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
# Unregister the provided model admin
admin.site.unregister(User)


# Register out own model admin, based on the default UserAdmin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass


# Register your models here.
from .models import APIKEY


class MyAPIKey(admin.ModelAdmin, DynamicArrayMixin):
    SHOW_APIS = ['vip_trader01', 'vip_trader02']
    model = APIKEY
    exclude = ('added_by',)
    list_display = ('name', 'own_name', 'passphrase', 'exclude_pnl', 'tags', 'added_by')

    def get_queryset(self, request):
        qs = super(MyAPIKey, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.username in self.SHOW_APIS:
            return qs.exclude(added_by='master')
        return qs.filter(added_by=request.user.username)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.added_by = request.user.username
        super().save_model(request, obj, form, change)


admin.site.site_title = "Trading System Admin"
admin.site.site_header = "Trading System Admin"
admin.site.index_title = "Trading System Admin"
admin.site.register(APIKEY, MyAPIKey)
