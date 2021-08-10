import sys
import pandas as pd
from util import read_parse_date, print_df

df = read_parse_date(sys.argv)
df["year"] = df.date.dt.year
xt = pd.crosstab(
    index=df.pri_neigh, columns=df.year, values=df.case_number, aggfunc="nunique"
)
print_df(xt, index=True)
