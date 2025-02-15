import kagglehub

path = kagglehub.dataset_download("hunter0007/ecommerce-dataset-for-predictive-marketing-2023")

print(path)
import os
print(os.listdir(path))
import pandas as pd
data = pd.read_csv(os.path.join(path, os.listdir(path)[0]))
print(data.head())

# data.to_csv("ecommerce.csv") 

# export 100 rows
data.head(100).to_csv("ecommerce_100.csv")