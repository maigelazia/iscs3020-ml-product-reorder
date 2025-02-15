import pandas as pd
# Load and preprocess the dataset
data = pd.read_csv("ecommerce.csv")

# Preprocess data for reusable fields
data.drop_duplicates(inplace=True)
data['days_since_prior_order'].fillna(data['days_since_prior_order'].mean(), inplace=True)
data.columns = [col.lower() for col in data.columns]

# Calculate reusable aggregate features
product_purchase_frequency = data.groupby('product_id').size().rename('purchase_frequency')
print(product_purchase_frequency)
avg_time_between_purchases = data.groupby('product_id')['days_since_prior_order'].mean().rename('avg_days_between_orders')

# Prepare list of unique users and products for the dropdowns
unique_users = data['user_id'].unique().tolist()
unique_products = data[['product_id', 'product_name']].drop_duplicates().to_dict(orient='records')
