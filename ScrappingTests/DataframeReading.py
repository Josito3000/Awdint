import pandas as pd
df = pd.read_parquet("coches_data_15_02_2025.parquet")
print(df.head())
print(df['Price'])
