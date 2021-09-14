import sys
import pandas as pd
from util import read_parse_date, is_last_day_of_month

df = read_parse_date(sys.argv[1])
df["month"] = df.date.dt.month
by_neigh_30_days = (
    df.groupby([pd.Grouper(freq="M", key="date"), "pri_neigh"])
    .case_number.nunique()
    .unstack()
    .transpose()
)
max_date = df.date.max()
if is_last_day_of_month(max_date):
    by_neigh_30_days = by_neigh_30_days.sort_values(
        by_neigh_30_days.columns[-1], ascending=False
    )
    by_neigh_30_days.columns = by_neigh_30_days.columns.map(
        lambda t: t.strftime("%B %Y")
    )
else:
    by_neigh_30_days = by_neigh_30_days.sort_values(
        by_neigh_30_days.columns[-2], ascending=False
    )
    by_neigh_30_days.columns = by_neigh_30_days.columns.map(
        lambda t: t.strftime("%B %Y")
        if t != by_neigh_30_days.columns.max()
        else t.strftime("%B %Y") + f" (through {max_date.strftime('%B %d')})"
    )
# reverse column order so most recent is first
by_neigh_30_days = by_neigh_30_days.iloc[:, ::-1]
by_neigh_30_days.to_excel(sys.argv[2])
