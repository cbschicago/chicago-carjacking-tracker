import sys
import pandas as pd

df = pd.read_csv(sys.argv[1])
df["2015-2019 average"] = df.iloc[:, 1:-2].mean(axis=1)
df = df[["2015-2019 average", "2020", "2021"]]
fig = df.plot(
    kind="line",
    figsize=(15, 12),
    ylabel="Total carjackings",
    xlabel="Month",
).get_figure()
fig.savefig(sys.argv[2])
