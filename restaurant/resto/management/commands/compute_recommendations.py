# compute_recommendations.py

from django.core.management.base import BaseCommand
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from resto.models import Order, OrderItem, MenuItem

class Command(BaseCommand):
    help = 'Compute and save the user-item matrix and item similarity matrix'

    def handle(self, *args, **kwargs):
        # Fetch order data
        orders = Order.objects.all()
        order_items = OrderItem.objects.all()

        # Create a DataFrame for user-item interactions
        data = []
        for order in orders:
            for item in order_items.filter(order=order):
                data.append({
                    'user_id': order.customer.id,
                    'item_id': item.menu_item.id,
                    'quantity': item.quantity
                })

        df = pd.DataFrame(data)

        # Create a user-item matrix
        user_item_matrix = df.pivot_table(index='user_id', columns='item_id', values='quantity', fill_value=0)

        # Calculate the cosine similarity matrix
        item_similarity_matrix = cosine_similarity(user_item_matrix.T)
        item_similarity_df = pd.DataFrame(item_similarity_matrix, index=user_item_matrix.columns, columns=user_item_matrix.columns)

        # Save the matrices to files
        user_item_matrix.to_pickle('resto/user_item_matrix.pkl')
        item_similarity_df.to_pickle('resto/item_similarity_df.pkl')

        self.stdout.write(self.style.SUCCESS('User-item matrix and item similarity matrix computed and saved!'))
