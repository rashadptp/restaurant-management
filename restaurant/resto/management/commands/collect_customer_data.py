from django.core.management.base import BaseCommand
import pandas as pd
from resto.models import Order, OrderItem

class Command(BaseCommand):
    help = 'Collect customer data for segmentation'

    def handle(self, *args, **kwargs):
        orders = Order.objects.all()
        data = []

        for order in orders:
            for item in order.order_items.all():
                data.append({
                    'customer_id': order.customer.id,
                    'order_date': order.created_at,
                    'menu_item': item.menu_item.name,
                    'quantity': item.quantity,
                    'price': item.menu_item.price,
                    'total_price': item.quantity * item.menu_item.price
                })

        df = pd.DataFrame(data)
        df.to_csv('customer_data.csv', index=False)
        self.stdout.write(self.style.SUCCESS('Customer data collected successfully'))
