import sys
import pandas as pd
from util import read_parse_date, print_df

df = read_parse_date(sys.argv)
df["year"] = df.date.dt.year
xt = pd.crosstab(
    index=df.pri_neigh, columns=df.year, values=df.case_number, aggfunc="nunique"
)


def tooltip_comparison_text(row):
    if row[2021] == row[2020]:
        return ("the same number as", "black")
    else:
        dif = row[2021] - row[2020]
        if dif > 0:
            return (f"{dif} more than", "#cc281d")
        else:
            return (f"{dif} fewer than", "#009c1d")


xt["tooltip_comparison_text"] = xt.apply(tooltip_comparison_text, axis=1)
xt["tooltip_comparison_text_color"] = xt.tooltip_comparison_text.apply(lambda t: t[1])
xt["tooltip_comparison_text"] = xt.tooltip_comparison_text.apply(lambda t: t[0])
print_df(xt, index=True)
