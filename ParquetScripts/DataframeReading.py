import pandas as pd
import numpy as np

df = pd.read_parquet("C:/Users/PORTATIL/OneDrive/Documentos/Projects/CochecitosScrapping/OutputData/coches_data_consolidado_2025-02-19_17-27.parquet")
print(df.head())
print(df.columns)

# Convert price to integer (removing non-digit characters)
df["PriceInt"] = (
    df["Price"]
    .str.replace(r"[^\d]", "", regex=True)  # Keep only digits
    .replace("", np.nan)  # Replace empty strings with NaN
    .dropna()  # Drop NaN rows
    .astype(float)  # Convert to float (for large numbers)
    .astype(int)  # Convert to integer
)


df["FeaturesList"] = df["Features"].str.split(", ")

features_df = df["FeaturesList"].apply(pd.Series)
df = pd.concat([df, features_df.iloc[:,1]], axis=1)
df = df.rename(columns={1:"KM"})
print(df["KM"].describe())
#df["KMint"] = df["KM"].str.replace(r"[^\d]", "", regex=True).astype(int)
#df["KMint"].mean()

#df = pd.concat([df, features_df], axis=1)

#print(df.dtypes)
