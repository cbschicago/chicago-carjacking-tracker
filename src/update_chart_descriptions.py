from datetime import datetime, date, timedelta
import json
import sys
from util import get_dw_client, is_last_day_of_month

dw = get_dw_client()
MDY_FORMAT = "%B %-d, %Y"

with open(sys.argv[1], "r") as f:
    chart_descriptions = json.load(f)

with open(sys.argv[2], "r") as f:
    max_date = datetime.strptime(f.read(), "%Y-%m-%d")
    month_pre_max_date = (max_date - timedelta(days=30)).strftime(MDY_FORMAT)
    max_complete_month = date(
        date.today().year,
        (
            max_date.month
            if is_last_day_of_month(max_date.date())
            else max_date.month - 1
            if max_date.month > 1
            else 1
        ),
        1,
    ).strftime("%B %Y")

replacement_values = {
    "MAX DATE": max_date.strftime(MDY_FORMAT),
    "30 DAY START DATE": month_pre_max_date,
    "MAX COMPLETE MONTH": max_complete_month,
}

for chart_id in chart_descriptions.keys():
    chart_description = chart_descriptions[chart_id]
    for key in replacement_values:
        chart_description = chart_description.replace(
            "[" + key + "]", replacement_values[key]
        )
    assert (
        "[" not in chart_description
    ), f"unreplaced key in description for chart {chart_id}"
    dw.update_metadata(chart_id, {"describe": {"intro": chart_description}})
    dw.publish_chart(chart_id)
