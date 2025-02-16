# Predictive Model for E-Commerce Product Reorders

A Flask-based API that integrates with Google Cloud Vertex AI to predict the likeliness of a customer to reorder products from an online grocery store. Developed as part of the Guided Studies in Machine Learning Pipelines course

## Setup & Installation
1. Clone the repository.
2. Run `pip install -r requirements.txt` to install dependencies. Setting up on a virtual environment is recommended but not required.
3. This project requires Google Cloud authentication. Create a `.env` file in the root directory and add:
```
GOOGLE_APPLICATION_CREDENTIALS=service_account.json
ENDPOINT_ID=your_vertex_ai_endpoint_id
PROJECT_ID=your_google_cloud_project_id
```
4. You may contact me for the `service_account.json` file and specific details. Alternatively, you may opt to use your own Google Cloud credentials and update the `.env` file accordingly.
5. Run `python app.py`.
