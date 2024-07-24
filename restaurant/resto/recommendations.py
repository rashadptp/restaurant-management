# recommendations.py

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def get_recommendations(user_id, user_item_matrix, item_similarity_df, num_recommendations=5):
    try:
        # Check if user_id exists in user_item_matrix index
        if user_id not in user_item_matrix.index:
            return get_default_recommendations(num_recommendations)

        # Fetch user's order history
        user_orders = user_item_matrix.loc[user_id]
        
        # Calculate the scores for items based on similarity to user's ordered items
        scores = item_similarity_df.dot(user_orders).div(item_similarity_df.sum(axis=1))
        
        # Exclude items already ordered by the user
        ordered_items = user_orders[user_orders > 0].index.tolist()
        scores = scores.drop(ordered_items)
        
        # Get the top recommendations
        recommendations = scores.nlargest(num_recommendations).index.tolist()
        
        return recommendations
    except KeyError as e:
        print(f"KeyError: {e}")
        get_default_recommendations(num_recommendations)

def get_default_recommendations(num_recommendations):
    # Example of providing default recommendations (e.g., popular items)
    # Replace this with your specific default recommendation logic
    popular_items = [
        34,35
        
    ]
    return popular_items[:num_recommendations]
