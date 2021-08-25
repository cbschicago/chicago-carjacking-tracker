import sys
from util import get_dw_client

dw = get_dw_client()

chart_id = sys.argv[1]
filepath = sys.argv[2]
dw.export_chart(chart_id=chart_id, filepath=filepath, unit="px", width=800)
