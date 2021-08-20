from datetime import datetime
import sys
import pandas as pd

readme = """# chicago-carjacking-tracker

[![update-data](https://github.com/hackerlikecomputer/chicago-carjacking-tracker/actions/workflows/update-data.yml/badge.svg)](https://github.com/hackerlikecomputer/chicago-carjacking-tracker/actions/workflows/update-data.yml)

---"""

with open(sys.argv[1], "r") as f:
    max_date = datetime.strptime(f.read(), "%Y-%m-%d")

readme += f"\n\n## Data current through {max_date.strftime('%B %d, %Y')}\n\n"

for filename in sys.argv[2:-1]:
    ext = filename.split(".")[1]
    if ext == "xlsx":
        df = pd.read_excel(filename)
    elif ext == "csv":
        df = pd.read_csv(filename)

    title = (
        filename.replace("carjacking-", "")
        .replace("-", " ")
        .title()
        .replace("Yoy", "YOY")
        .replace("." + ext.title(), "")
    )
    readme += df.to_markdown(index=False)

with open(sys.argv[-1], "w") as f:
    f.write(readme)
