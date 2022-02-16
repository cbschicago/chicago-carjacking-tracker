import sys
import pandas as pd
from util import read_parse_date, write_excel_report

df = read_parse_date(sys.argv[1])
df["month"] = df.date.dt.month
df["year"] = df.date.dt.year
xt = pd.crosstab(
    index=df.month, columns=df.year, values=df.case_number, aggfunc="nunique"
)
max_date = df.date.max()
through_max_date_str = f"(through {max_date.strftime('%m-%d')})"
if "--ytd-columns" in sys.argv:
    xt.columns = xt.columns.map(
        lambda year: year if year != max_date.year else f"{year} {through_max_date_str}"
    )
    xt.index = xt.index.map(lambda m: pd.Timestamp(2021, m, 1).strftime("%B"))
else:
    xt.index = xt.index.map(
        lambda m: pd.Timestamp(2021, m, 1).strftime("%B")
        if m != max_date.month
        else pd.Timestamp(2021, m, 1).strftime("%B") + f" {through_max_date_str}"
    )
xt = xt.append(pd.Series(xt.sum(), name="Total"))
write_excel_report({f"Through {max_date.strftime('%Y-%m-%d')}": xt}, sys.argv[2])
