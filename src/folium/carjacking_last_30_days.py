# pylint: disable=no-member,unsupported-assignment-operation
import sys
import mapping
import pandas as pd
from titlecase import titlecase

df = pd.read_csv(sys.argv[1], parse_dates=["date"])
if len(df.date.dt.year.unique()) > 1:
    strftime_format = "%B %d, %Y"
else:
    strftime_format = "%B %d"
df["date_strftime"] = df.date.dt.strftime(strftime_format)
df["time_strftime"] = df.date.dt.strftime("%I:%M:%p")
df["block"] = (
    df.block.str.replace("XX", "00 block of")
    .str.replace(r"^0+(?=\d+)", "", regex=True)
    .str.replace("0000X", "0-100 block of")
    .str.lower()
    .apply(titlecase)
)

with open(sys.argv[2], "r") as f:
    tooltip_html = f.read()

m = mapping.Map(df)
m.add_points(
    tooltip_html=tooltip_html,
    cluster=True,
    max_cluster_radius=40,
    disable_clustering_at_zoom=12,
)
m.save(sys.argv[3])
