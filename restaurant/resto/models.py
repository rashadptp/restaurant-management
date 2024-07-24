# restaurant/models.py

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from datetime import date
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group


class Section(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='section_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available=models.BooleanField(default=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE,null=True, related_name='menu_items')
    def __str__(self):
        return self.name

class Table(models.Model):
    
    number = models.IntegerField(unique=True)
    seats = models.IntegerField()

    def __str__(self):
        return f"Table {self.number}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('P', 'Processing'),
        ('D', 'Delivered'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    items = models.ManyToManyField(MenuItem)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    is_delivered = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    def total_amount(self):
        return sum(item.subtotal() for item in self.order_items.all())
    
    def __str__(self):
        return f"Order {self.id} by {self.customer.username}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='order_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.menu_item.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"


class Reservation(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    reservation_date = models.DateField()
    reservation_start_time = models.TimeField(default='12:00:00')
    reservation_end_time = models.TimeField(default='12:00:00')

    def __str__(self):
        return f"{self.customer.username} - Table {self.table.number} on {self.reservation_date} from {self.reservation_start_time} to {self.reservation_end_time}"

class TimeSlot(models.Model):
    time = models.TimeField()

    def __str__(self):
        return self.time.strftime("%H:%M")


@receiver(post_migrate)
def create_groups(sender, **kwargs):
    Group.objects.get_or_create(name='Admin')
    Group.objects.get_or_create(name='Staff')
    Group.objects.get_or_create(name='Customer')






class CoinTransaction(models.Model):
    TRANSACTION_CHOICES = [
        ('earn', 'Earn'),
        ('redeem', 'Redeem'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=10,choices=TRANSACTION_CHOICES) 
    total_redeemed = models.IntegerField(default=0)