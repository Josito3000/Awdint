import pandas as pd

def transformation(elem: str) -> any:
    '''
    Tranforms data tu return the unique element
    '''
    return elem.text.strip() if elem else "N/A"

def save_parquet(dataframe: pd.DataFrame, file_name: str) -> any:
    '''
    Update to make things more automatic
    '''
    return dataframe.to_parquet("OutputData/" + file_name, engine = "pyarrow", index = False)