import sys
import pandas as pd
from util import print_df, read_parse_date

df = read_parse_date(sys.argv[1])
gb = (
    df.groupby(pd.Grouper(freq="m", key="date", label="right"))
    .case_number.nunique()
    .to_frame("total_carjackings")
)
gb["rollavg"] = gb.total_carjackings.rolling(6).mean()
max_date = df.date.max()
gb.index = gb.index.map(
    lambda t: t.strftime("%B %Y")
    if not (t.year == max_date.year and t.month == max_date.month)
    else t.strftime("%B %Y") + f" (through {max_date.strftime('%m-%d')})"
)
print_df(gb, index=True)
