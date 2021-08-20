from datetime import datetime
import sys
import pandas as pd

readme = """# chicago-carjacking-tracker

[![update-data](https://github.com/hackerlikecomputer/chicago-carjacking-tracker/actions/workflows/update-data.yml/badge.svg)](https://github.com/hackerlikecomputer/chicago-carjacking-tracker/actions/workflows/update-data.yml)

---"""

with open(sys.argv[1], "r") as f:
    max_date = datetime.strptime(f.read(), "%Y-%m-%d")

readme += f"\n\n## Data current through {max_date.strftime('%B %d, %Y')}\n\n"

fileargs = sys.argv[2:-1]
for i, filename in enumerate(fileargs):
    ext = filename.split(".")[1]
    if ext in ["xlsx", "csv"]:
        if ext == "xlsx":
            df = pd.read_excel(filename)
        elif ext == "csv":
            df = pd.read_csv(filename)
        readme += df.to_markdown(index=False)
    elif ext in ["png", "svg"]:
        readme += f"![{filename}]({filename})"
    if i + 1 < len(fileargs):
        readme += "\n\n"

with open(sys.argv[-1], "w") as f:
    f.write(readme)
