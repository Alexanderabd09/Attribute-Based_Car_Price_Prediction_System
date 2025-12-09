import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.src.backend.jax.random import categorical
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split

#load dataset
data = pd.read_csv("car details v4.csv")

#clean up dataset (removing spaces, fixing formatting...)
data = data.drop_duplicates()
data.columns = data.columns.str.lower().str.replace(' ', '_')
data = data.dropna(subset=["price", "year"])

data["engine"] = data["engine"].astype(str).str.lower().str.strip()
cc_mask = data["engine"].str.contains("cc", na=False)
data.loc[cc_mask, "engine"] = (
    data.loc[cc_mask, "engine"]
    .str.replace("cc", "", regex=False)
    .str.strip()
    .astype(float) / 1000
)
data["engine"] = pd.to_numeric(data["engine"], errors="coerce")

data["mileage"] = data["kilometer"] * 0.621
data.drop("kilometer", axis=1, inplace=True)
data["mileage"] = data["mileage"].replace(np.nan, 0)

# Extract numeric parts only
data["max_power"] = data["max_power"].astype(str).str.extract(r"(\d+\.?\d*)")
data["max_torque"] = data["max_torque"].astype(str).str.extract(r"(\d+\.?\d*)")

data["max_power"] = pd.to_numeric(data["max_power"], errors="coerce")
data["max_torque"] = pd.to_numeric(data["max_torque"], errors="coerce")

#engineered features
data["age"] = 2025 - data["year"]
data["price per mile"] = data["price"] / data["mileage"]

for col in ["make","model", "fuel_type","transmission", "owner","seller_type","location", "color"]:
    data[col] = data[col].astype(str).str.strip().str.lower()


#drop empty rows
data.dropna(inplace=True)

#OneHotEncode categorical data
categorical_columns = ["make", "model", "fuel_type", "transmission", "seller_type", "owner", "location", "color"]
encoder = OneHotEncoder(sparse_output= False, handle_unknown="ignore")
one_hot_encoded = encoder.fit_transform(data[categorical_columns])
one_hot_df = pd.DataFrame(one_hot_encoded, columns=encoder.get_feature_names_out(categorical_columns))
df_encoded = pd.concat([data.drop(categorical_columns, axis=1), one_hot_df], axis=1)

print(df_encoded.dtypes[df_encoded.dtypes == "object"])

#Split into to x and Y
x = df_encoded.drop("price", axis=1)
y = df_encoded["price"]

#Split into train_test_val
x_train, x_temp, y_train, y_temp = train_test_split(
    x, y,
    test_size=0.3,
    random_state=42
)

# Second split: Validation vs Test
x_val, x_test, y_val, y_test = train_test_split(
    x_temp, y_temp,
    test_size=0.5,
    random_state=42
)

model = LinearRegression()
model.fit(x_train, y_train)

#print(data.head(), data.shape)