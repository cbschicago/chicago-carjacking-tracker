import sys
import pandas as pd
from util import get_dw_client

dw = get_dw_client()

df = pd.read_csv(sys.argv[1])
chart_id = sys.argv[2]
filepath = sys.argv[3]
# add data to force chart refresh
dw.add_data(chart_id, df)
dw.export_chart(chart_id=chart_id, filepath=filepath, unit="px", width=800, scale=2)
