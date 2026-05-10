from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    # Using AbstractUser so that fields like username, password, and email are captured.

    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tstamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Business(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=100)
    address = models.TextField()
    table_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    phone_no = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    tstamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Table(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    table_no = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    capacity = models.IntegerField()
    status = models.CharField(max_length=20, default='inactive')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tstamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Table {self.table_no} - {self.business.name}"


class BusinessStaff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    tstamp = models.DateTimeField(auto_now=True)


class Menu(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    tstamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MenuCategory(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    tstamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tstamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    tstamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - Table {self.table.table_no}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    item_price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)