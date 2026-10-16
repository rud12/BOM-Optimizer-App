import io

import pandas as pd
from fastapi import HTTPException


def read_component_file(file_bytes, file_name):
    buffer = io.BytesIO(file_bytes)
    if file_name.lower().endswith(".csv"):
        dataframe = pd.read_csv(buffer)
    else:
        dataframe = pd.read_excel(buffer)

    dataframe.columns = dataframe.columns.str.strip()
    if "Component" not in dataframe.columns or "Quantity" not in dataframe.columns:
        raise HTTPException(status_code=400, detail='File must contain "Component" and "Quantity" columns.')

    rows = []
    for _, row in dataframe[["Component", "Quantity"]].dropna(subset=["Component"]).iterrows():
        component = str(row["Component"]).strip()
        if not component:
            continue
        try:
            quantity = int(row["Quantity"])
        except Exception:
            quantity = 1
        rows.append({"component": component, "quantity": max(quantity, 1)})
    return rows
