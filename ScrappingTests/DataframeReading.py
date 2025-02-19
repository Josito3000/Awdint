import pandas as pd
df = pd.read_parquet("coches_data_15_02_2025.parquet")
print(df.head())
print(df.columns)

df["PriceInt"] = df["Price"].str.replace(r"[^\d]", "", regex=True).astype(int)
df["FeaturesList"] = df["Features"].str.split(", ")

features_df = df["FeaturesList"].apply(pd.Series)
df = pd.concat([df, features_df.iloc[:,1]], axis=1)
df = df.rename(columns={1:"KM"})
print(df["KM"].describe())
#df["KMint"] = df["KM"].str.replace(r"[^\d]", "", regex=True).astype(int)
#df["KMint"].mean()

#df = pd.concat([df, features_df], axis=1)

#print(df.dtypes)
