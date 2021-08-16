from datetime import datetime
import json
import os
import sys
from datawrapper import Datawrapper

dw = Datawrapper(access_token=os.getenv("datawrapper_api_token"))

with open(sys.argv[1], "r") as f:
    chart_descriptions = json.load(f)

with open(sys.argv[2], "r") as f:
    max_date = datetime.strptime(f.read(), "%Y-%m-%d").strftime("%B %-d, %Y")

for chart_id in chart_descriptions.keys():
    chart_description = chart_descriptions[chart_id].replace("[MAX DATE]", max_date)
    dw.update_metadata(chart_id, {"describe": {"intro": chart_description}})
