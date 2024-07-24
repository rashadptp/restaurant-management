# restaurant/management/commands/train_model.py
from django.core.management.base import BaseCommand
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
from resto.models import Order,OrderItem

class Command(BaseCommand):
    help = 'Train demand forecasting model'

    def handle(self, *args, **kwargs):
        # Load data
        orders = Order.objects.all()
        data = []

        for order in orders:
            for item in order.order_items.all():
                data.append({
                    'order_date': order.created_at,
                    'menu_item': item.menu_item.name,
                    'quantity': item.quantity,
                    'price': item.menu_item.price
                })

        df = pd.DataFrame(data)
    
        # Feature extraction
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['day_of_week'] = df['order_date'].dt.dayofweek
        df['month'] = df['order_date'].dt.month
        df['year'] = df['order_date'].dt.year

        print("DataFrame Head:")
        print(df.tail(5))  
        
        # Preprocess data
        X = df[['day_of_week', 'month', 'year', 'menu_item']]
        y = df['quantity']
        
        # Encode categorical data
        X = pd.get_dummies(X, columns=['menu_item'])

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Save model
        joblib.dump(model, 'restaurant_model.pkl')
        joblib.dump(X.columns, 'restaurant_model_columns.pkl')
        self.stdout.write(self.style.SUCCESS('Model trained and saved successfully'))
