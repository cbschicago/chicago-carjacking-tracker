import calendar
from datetime import date
import os
from datawrapper import Datawrapper
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime


def read_parse_date(filename):
    df = pd.read_csv(filename)
    if not is_datetime(df.date):
        df["date"] = pd.to_datetime(df.date)
    return df


def print_df(df, index=False):
    print(df.to_csv(line_terminator="\n", index=index))


def get_dw_client():
    return Datawrapper(access_token=os.getenv("datawrapper_api_token"))


def is_last_day_of_month(d):
    last_day_of_month = calendar.monthrange(d.year, d.month)[1]
    if d == date(d.year, d.month, last_day_of_month):
        return True
    return False
