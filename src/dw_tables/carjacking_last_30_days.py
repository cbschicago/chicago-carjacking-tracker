import sys
import pandas as pd
from util import read_parse_date, print_df

df = read_parse_date(sys.argv)
df = df[df.date >= df.date.max() - pd.Timedelta(days=30)]
print_df(df)
