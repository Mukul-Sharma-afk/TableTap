from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Business, Table, Menu, MenuCategory, MenuItem, Order, OrderItem, BusinessStaff
from django.utils import timezone

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'is_archived', 'archived_at')}),
    )
    readonly_fields = ('created_at', 'tstamp',)
    list_display = ('id', 'username', 'first_name', 'last_name', 'email', 'role', 'is_active', 'is_archived')
    list_filter = ('role', 'is_archived')
    search_fields = ('username', 'email')
    actions = ['archive_items', 'unarchive_items']
    list_per_page = 10

    # Added functionality to admin panel so that we can archive users instead of only having the option to delete.

    def archive_items(self, request, queryset):
        queryset.update(is_archived=True, archived_at=timezone.now())
        self.message_user(request, f"{queryset.count()} user(s) have been archived")

    def unarchive_items(self, request, queryset):
        queryset.update(is_archived=False, archived_at=timezone.now())
        self.message_user(request, f"{queryset.count()} user(s) have been unarchived")

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):

    def business_owner(self, obj):
        return obj.user.first_name + " " + obj.user.last_name
    
    list_display = ('id', 'name', 'business_type', 'business_owner')
    list_filter = ('business_type', 'name')
    search_fields = ('name', 'business_type')
    list_per_page = 10

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_no', 'business', 'capacity', 'status')
    list_filter = ('business', 'capacity', 'status')
    search_fields = ('business__name', 'table_no')
    list_per_page = 10

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'business', 'is_enabled')
    list_filter = ('business', 'name')
    search_fields = ('business__name', 'name')

    actions = ['enable_menus', 'disable_menus']
    list_per_page = 10

    def enable_menus(self, request, queryset):
        queryset.update(is_enabled=True, tstamp=timezone.now())
        self.message_user(request, f"{queryset.count()} menu(s) have been enabled")

    def disable_menus(self, request, queryset):
        queryset.update(is_enabled=False, tstamp=timezone.now())
        self.message_user(request, f"{queryset.count()} menu(s) have been disabled")

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):

    def business_name(self, obj):
        return obj.menu.business.name

    list_display = ('id', 'name', 'menu', 'business_name')
    list_filter = ('menu__business' ,  'menu')
    search_fields = ('menu__business__name', 'name')
    list_per_page = 10

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):

    def business_name(self, obj):
        return obj.category.menu.business.name

    list_display = ('id', 'name', 'category', 'price', 'is_available','business_name')
    list_filter = ('menu__business' ,  'category')
    search_fields = ('category__menu__business__name', 'name')

    actions = ['make_available', 'make_unavailable']
    list_per_page = 10

    def make_available(self, request, queryset):
        queryset.update(is_available=True, tstamp=timezone.now())
        self.message_user(request, f"{queryset.count()} menu item(s) have been made available")

    def make_unavailable(self, request, queryset):
        queryset.update(is_available=False, tstamp=timezone.now())
        self.message_user(request, f"{queryset.count()} menu item(s) have been made unavaialble")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    def business_name(self, obj):
        return obj.table.business.name

    list_display = ('id', 'business_name', 'table', 'total_price', 'status', 'created_at','tstamp')
    list_filter = ('status', 'created_at')
    search_fields = ('table__table_no', 'table__business__name')
    list_per_page = 10

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    def business_name(self, obj):
        return obj.order.table.business.name

    list_display = ('id', 'business_name', 'order__table__table_no', 'menu_item', 'quantity', 'item_price', 'order__status', 'order__created_at', 'order__tstamp')
    list_filter = ('order__status', 'order__created_at', 'menu_item')
    search_fields = ('order__table__table_no', 'order__table__business__name', 'menu_item__name')
    list_per_page = 10


@admin.register(BusinessStaff)
class BusinessStaffAdmin(admin.ModelAdmin):
    def business_name(self, obj):
        return obj.business.name

    def full_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name

    list_display = ('id', 'full_name', 'business_name', 'role', 'created_at', 'tstamp')
    list_filter = ('business', 'role')
    search_fields = ('user__first_name', 'user__last_name', 'business__name', 'role')
    list_per_page = 10