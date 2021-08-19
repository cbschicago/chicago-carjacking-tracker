import sys
import pandas as pd
from util import print_df, read_parse_date

df = read_parse_date(sys.argv[1])
df["month"] = df.date.dt.month
df["year"] = df.date.dt.year
xt = pd.crosstab(
    index=df.month, columns=df.year, values=df.case_number, aggfunc="nunique"
)
max_date = df.date.max()
xt = xt[xt.index < max_date.month]
xt.index = xt.index.map(
    lambda m: pd.Timestamp(2021, m, 1).strftime("%B")
    # if m != max_date.month
    # else pd.Timestamp(2021, m, 1).strftime("%B")
    # + f" (through {max_date.strftime('%m-%d')})"
)
print_df(xt, index=True)
