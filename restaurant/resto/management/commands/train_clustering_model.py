import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import joblib

def train_model():
    df = pd.read_csv('user_stats.csv')

    # Preprocess data
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(df[['total_quantity', 'total_spent', 'order_count']])

    # Train clustering model
    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(data_scaled)

    # Save model and scaler
    joblib.dump(kmeans, 'customer_segmentation_model.pkl')
    joblib.dump(scaler, 'customer_data_scaler.pkl')

    print("Model trained and saved successfully")

if __name__ == "__main__":
    train_model()
