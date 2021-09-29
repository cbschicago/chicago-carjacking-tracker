import calendar
from datetime import date
import os
from datawrapper import Datawrapper
import openpyxl
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


def get_col_widths(dataframe):
    idx_max = [
        max(
            [len(str(s)) for s in dataframe.index.get_level_values(idx)]
            + [len(str(idx))]
        )
        for idx in dataframe.index.names
    ]
    return idx_max + [
        max(
            [len(str(s)) for s in dataframe[col].values] + [len(str(x)) for x in col]
            if dataframe.columns.nlevels > 1
            else [len(str(col))]
        )
        for col in dataframe.columns
    ]


def write_excel_report(dfs, filename, pct_cols=None):
    # pylint: disable=abstract-class-instantiated
    # pylint: disable=no-member
    writer = pd.ExcelWriter(filename, engine="xlsxwriter")
    for df_name in dfs:
        df = dfs[df_name]
        df.to_excel(writer, sheet_name=df_name)
    workbook = writer.book
    pct_format = workbook.add_format({"num_format": "0.0%"})
    for sheet_name in dfs:
        worksheet = writer.sheets[sheet_name]
        for i, width in enumerate(get_col_widths(dfs[sheet_name])):
            if pct_cols is not None:
                invalid_pct_cols_er = "pct_cols must be either 'all', 'last', a list of column indices, or None"
                if pct_cols == "all":
                    fmt = pct_format
                elif pct_cols == "last":
                    fmt = pct_format if i == len(dfs[sheet_name].columns) else None
                elif isinstance(pct_cols, list):
                    if not all(isinstance(ci, int) for ci in pct_cols):
                        raise ValueError(invalid_pct_cols_er)
                    if i in pct_cols:
                        fmt = pct_format
                    else:
                        fmt = None
                else:
                    raise ValueError(invalid_pct_cols_er)
            else:
                fmt = None
            worksheet.set_column(i, i, width, cell_format=fmt)
    writer.close()
    # hack to keep pandas from writing a blank line below multiindex columns
    book = openpyxl.load_workbook(filename)
    for sheet_name in dfs:
        df_cols = dfs[sheet_name].columns
        if isinstance(df_cols, pd.MultiIndex):
            sheet = book[sheet_name]
            sheet.delete_rows(df_cols.nlevels + 1, 1)
            book.save(filename)
