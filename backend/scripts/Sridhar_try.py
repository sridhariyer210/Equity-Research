from pathlib import Path
import pandas as pd

file = Path("backend/data/raw/May_2026/All-Schemes-Monthly-Portfolio---as-on-31st-May-2026.xlsx")

df = pd.read_excel(file, sheet_name="SSCF")

print(df.head())
print(df.columns)


