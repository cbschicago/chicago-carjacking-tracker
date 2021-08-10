import sys
from util import read_parse_date

df = read_parse_date(sys.argv)
with open(sys.argv[2], "w") as f:
    f.write(df.date.max().strftime("%Y-%m-%d"))
