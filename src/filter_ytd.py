import sys
import pandas as pd
import util


def filter_ytd(df):
    max_date = df.date.max()
    df = df[
        (df.date.dt.year == max_date)
        | (
            (df.date.dt.month.isin(range(1, max_date.month)))
            | ((df.date.dt.month == max_date.month) & (df.date.dt.day <= max_date.day))
        )
    ]
    return df


if __name__ == "__main__":
    df = util.read_parse_date(sys.argv)
    df = filter_ytd(df)
    util.print_df(df)
