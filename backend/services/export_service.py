import io

import pandas as pd

def export_dataframe(bom):
    rows = []
    for item in bom.items:
        rows.append(
            {
                "Alias Name": item.alias_name or item.component_name,
                "Component": item.component_name,
                "Quantity": item.quantity,
                "Vendor": item.vendor.display_name if item.vendor else "",
                "Manufacturer": item.manufacturer or "",
                "Unit Price": float(item.unit_price),
                "Total Price": float(item.total_price),
                "Stock": item.stock or "",
                "Product URL": item.product_url or "",
            }
        )
    return pd.DataFrame(rows)


def export_csv_bytes(bom):
    return export_dataframe(bom).to_csv(index=False).encode("utf-8")


def export_excel_buffer(bom):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        dataframe = export_dataframe(bom)
        dataframe.to_excel(writer, index=False, sheet_name="BOM")
        worksheet = writer.sheets["BOM"]
        for column in worksheet.columns:
            max_length = max((len(str(cell.value)) for cell in column if cell.value), default=10)
            worksheet.column_dimensions[column[0].column_letter].width = min(max_length + 4, 60)
    buffer.seek(0)
    return buffer
