import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime


def read_parse_date(filename):
    df = pd.read_csv(filename)
    if not is_datetime(df.date):
        df["date"] = pd.to_datetime(df.date)
    return df


def print_df(df, index=False):
    print(df.to_csv(line_terminator="\n", index=index))
