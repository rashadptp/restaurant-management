from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from resto.models import Order, OrderItem
import pandas as pd

class Command(BaseCommand):
    help = 'Calculate user statistics'

    def handle(self, *args, **kwargs):
        customers = User.objects.all()
        data = []

        for customer in customers:
            orders = Order.objects.filter(customer=customer)
            total_quantity = sum(item.quantity for order in orders for item in order.order_items.all())
            
            # Calculate total spent
            total_spent = sum(item.quantity * item.menu_item.price for order in orders for item in order.order_items.all())
            order_count = orders.count()

            data.append({
                'user_id': customer.id,
                'total_quantity': total_quantity,
                'total_spent': total_spent,
                'order_count': order_count
            })

        df = pd.DataFrame(data)
        df.to_csv('user_stats.csv', index=False)
        self.stdout.write(self.style.SUCCESS('User statistics calculated and saved to user_stats.csv'))
