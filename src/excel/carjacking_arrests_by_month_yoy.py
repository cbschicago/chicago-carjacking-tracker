import sys
import pandas as pd
from util import read_parse_date, write_excel_report

df = read_parse_date(sys.argv[1])
df["month"] = df.date.dt.month
df["year"] = df.date.dt.year
xt = pd.crosstab(
    index=df.month,
    columns=[df.year, df.arrest],
    values=df.case_number,
    aggfunc="nunique",
)
xt = xt.append(pd.Series(xt.sum(), name="Total"))
# get arrest rate for each year
for year in xt.columns.get_level_values(0).unique():
    xt[(year, "arrest_rate")] = round(
        xt[(year, True)] / (xt[(year, True)] + xt[(year, False)]), 4
    )
xt = xt.rename(columns={False: "no_arrest_made", True: "arrest_made"})
# custom sort of multiindex columns
cols = []
for year in xt.columns.get_level_values(0).unique():
    cols.append((year, "arrest_made"))
    cols.append((year, "no_arrest_made"))
    cols.append((year, "arrest_rate"))
xt = xt[cols]
max_date = df.date.max()
xt.index = xt.index.map(
    lambda m: (
        pd.Timestamp(2021, m, 1).strftime("%B")
        if m != max_date.month
        else pd.Timestamp(2021, m, 1).strftime("%B")
        + f" (through {max_date.strftime('%m-%d')})"
    )
    if m != "Total"
    else m
)
write_excel_report(
    {f"Through {max_date.strftime('%Y-%m-%d')}": xt},
    sys.argv[2],
    pct_cols=list(range(3, len(xt.columns) + 2, 3)),
)
