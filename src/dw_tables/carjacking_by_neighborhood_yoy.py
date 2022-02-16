import sys
import pandas as pd
from util import read_parse_date, print_df

df = read_parse_date(sys.argv[1])
df["year"] = df.date.dt.year
xt = pd.crosstab(
    index=df.pri_neigh, columns=df.year, values=df.case_number, aggfunc="nunique"
).fillna(0)
CURRENT_YEAR = pd.Timestamp().today().year
PREV_YEAR = CURRENT_YEAR - 1


def tooltip_comparison_text(row):
    if row[CURRENT_YEAR] == row[PREV_YEAR]:
        return ("the same number as", "black")
    else:
        dif = int(row[CURRENT_YEAR] - row[PREV_YEAR])
        if dif > 0:
            return (f"{dif} more than", "#cc281d")
        else:
            return (f"{abs(dif)} fewer than", "#009c1d")


xt["tooltip_comparison_text"] = xt.apply(tooltip_comparison_text, axis=1)
xt["tooltip_comparison_text_color"] = xt.tooltip_comparison_text.apply(lambda t: t[1])
xt["tooltip_comparison_text"] = xt.tooltip_comparison_text.apply(lambda t: t[0])
print_df(xt, index=True)
