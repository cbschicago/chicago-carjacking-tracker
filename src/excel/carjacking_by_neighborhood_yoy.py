import sys
import pandas as pd
from util import read_parse_date, write_excel_report

df = read_parse_date(sys.argv[1])
max_date = df.date.max()
df["year"] = df.date.dt.year
xt = pd.crosstab(
    index=df.pri_neigh, columns=df.year, values=df.case_number, aggfunc="nunique"
).fillna(0)
write_excel_report(
    {f"Through {max_date.strftime('%Y-%m-%d')}": xt}, sys.argv[2]
)
