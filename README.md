# Predictive Model for E-Commerce Product Reorders

This project was developed as part of the Guided Studies in Machine Learning Pipelines course. It is a Flask-based API that integrates with Google Cloud Vertex AI to predict the likeliness of a customer to reorder products from an online grocery store.

## Setup & Installation
1. Clone the repository.
2. Run `pip install -r requirements.txt` to install required packages. Setting up on a virtual environment is recommended but not required.
3. This project requires Google Cloud authentication. To set up, create a [new project](https://console.cloud.google.com/projectcreate?pli=1&inv=1&invt=AbqK7A) and enable the [Vertex AI API](https://developers.google.com/workspace/guides/enable-apis). Create a [service account](https://cloud.google.com/iam/docs/service-accounts-create) with the required permissions, then generate a [service account key](https://cloud.google.com/iam/docs/keys-create-delete#iam-service-account-keys-create-console).
4. Once you have your credentials, create a `.env` file in the root directory and replace the values accordingly. Make sure the downloaded JSON key is in the same directory.
```
GOOGLE_APPLICATION_CREDENTIALS=service_account.json
ENDPOINT_ID=your_vertex_ai_endpoint_id
PROJECT_ID=your_google_cloud_project_id
```
5. Run `python app.py`.
