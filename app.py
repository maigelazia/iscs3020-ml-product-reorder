from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pandas as pd
import requests
import google.auth
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import re

app = Flask(__name__)
# CORS(app)/

# Load and preprocess the dataset
data = pd.read_csv("ecommerce.csv")

# Preprocess data for reusable fields
data.drop_duplicates(inplace=True)
data['days_since_prior_order'].fillna(data['days_since_prior_order'].mean(), inplace=True)
data.columns = [col.lower() for col in data.columns]

# Calculate reusable aggregate features
product_purchase_frequency = data.groupby('product_id').size().rename('purchase_frequency')

avg_time_between_purchases = data.groupby('product_id')['days_since_prior_order'].mean().rename('avg_days_between_orders')

# Prepare list of unique users and products for the dropdowns
unique_users = data['user_id'].unique().tolist()
unique_products = data[['product_id', 'product_name']].drop_duplicates().to_dict(orient='records')

# Define constants for service account and API endpoint
SERVICE_ACCOUNT_FILE = 'iscs-3020-ml-endpoint-4a2ef8396be9.json'
ENDPOINT_ID = "6515073687014604800"
PROJECT_ID = "1003347448964"
API_URL = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/endpoints/{ENDPOINT_ID}:predict"

@app.route('/api/user_search', methods=['GET'])
def user_search():
    """Endpoint to return filtered user IDs based on search term."""
    term = request.args.get('term', '').strip()
    
    # Only include user IDs that match the search term and are not None
    filtered_users = [user for user in unique_users if user is not None and str(user).startswith(term)]
    # Limit the results to the first 10 matches
    return jsonify({"users": filtered_users[:10]})

@app.route('/api/product_search', methods=['GET'])
def product_search():
    """Endpoint to return filtered products based on search term."""
    term = request.args.get('term', '').lower()
    filtered_products = [prod for prod in unique_products if term in prod['product_name'].lower()]
    return jsonify({"products": filtered_products[:10]})


def get_access_token():
    """Retrieve an access token using the service account JSON file."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(Request())  # Refresh to get the access token
    return credentials.token


def preprocess_input(user_id, order_hour_of_day, order_dow, product_id):
    """Prepares a single instance with all required columns for the API request."""
    # Retrieve user data and calculate required fields
    user_data = data[data['user_id'] == int(user_id)]
    days_since_prior_order = str(user_data['days_since_prior_order'].min()) if not user_data.empty else "0"
    purchase_frequency = str(product_purchase_frequency.get(int(product_id), 0))
    avg_days_between_orders = str(avg_time_between_purchases.get(int(product_id), data['days_since_prior_order'].mean()))
    high_priority_product = "true" if bool(user_data[user_data['department'] == 'produce'].shape[0]) else "false"
    
    # Log computed values for debugging
    print("Computed fields:")
    print(f"days_since_prior_order: {days_since_prior_order}")
    print(f"purchase_frequency: {purchase_frequency}")
    print(f"avg_days_between_orders: {avg_days_between_orders}")
    print(f"high_priority_product: {high_priority_product}")
    
    # Create instance with initial fields as strings
    instance = {
        "order_hour_of_day": str(order_hour_of_day) if order_hour_of_day is not None else "0",
        "order_dow": str(order_dow) if order_dow is not None else "0",
        "days_since_prior_order": days_since_prior_order,
        "purchase_frequency": purchase_frequency,
        "avg_days_between_orders": avg_days_between_orders,
        "high_priority_product": high_priority_product,
        "product_id": str(product_id) if product_id is not None else "0"
    }

    # Get the department for the given product_id
    product_row = data[data['product_id'] == int(product_id)]
    if not product_row.empty:
        department = product_row.iloc[0]['department']
        product_name = product_row.iloc[0]['product_name']
    else:
        department = None
        product_name = None

    # One-hot encode departments and products, initializing all as False
    all_departments = [f"dept_{d}" for d in data['department'].unique()]
    all_products = [f"product_{p}" for p in data['product_name'].unique()]
    
    # Set specific department and product columns to True
    one_hot_encoded = {f"dept_{department}": True} if department else {}
    one_hot_encoded.update({f"product_{product_name}": True} if product_name else {})
    
    # Set all other one-hot encoded fields to False
    for dept in all_departments:
        if dept not in one_hot_encoded:
            one_hot_encoded[dept] = False
    for prod in all_products:
        if prod not in one_hot_encoded:
            one_hot_encoded[prod] = False

    # Update the instance with the one-hot encoded columns
    instance.update(one_hot_encoded)
    
    # Clean column names and log final instance
    instance = {clean_column_name(k): str(v) for k, v in instance.items()}
    print("Final instance structure:", instance)
    
    return instance



def clean_column_name(name):
    """Clean column name to match the required format in the AI model."""
    return re.sub(r'[^A-Za-z0-9_]', '_', name).lower()

@app.route('/')
def index():
    """Serve the HTML form."""
    return render_template('index.html')

@app.route('/api/users', methods=['GET'])
def get_users():
    """API endpoint to return unique user IDs."""
    return jsonify({"users": unique_users})

@app.route('/api/products', methods=['GET'])
def get_products():
    """API endpoint to return unique products."""
    return jsonify({"products": unique_products})

@app.route('/api/predict', methods=['POST'])
def predict():
    """Endpoint to handle prediction requests."""
    req_data = request.json['instances'][0]
    user_id = req_data.get('user_id')
    order_hour_of_day = req_data.get('order_hour_of_day')
    order_dow = req_data.get('order_dow')
    product_id = req_data.get('product_id')
    print(req_data)
    # Preprocess input data
    instance = preprocess_input(user_id, order_hour_of_day, order_dow, product_id)
    instances = [instance]
    print(instances)
    # Get the access token
    access_token = get_access_token()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    # Send the request to the AI Platform endpoint
    response = requests.post(API_URL, headers=headers, json={"instances": instances})
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to get prediction", "details": response.json()}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
