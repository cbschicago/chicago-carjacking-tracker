import sys
import pandas as pd

df = pd.read_csv(sys.argv[1])[["date", "total_carjackings"]]
fig = df.plot(
    kind="line",
    figsize=(15, 12),
    ylabel="Total carjackings",
    xlabel="Month",
).get_figure()
fig.savefig(sys.argv[2])
