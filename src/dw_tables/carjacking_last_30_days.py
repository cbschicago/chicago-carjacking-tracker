import re
import sys
import pandas as pd
from util import read_parse_date, print_df


def get_block_description(block):
    parts = block.split(" ")
    block_no = parts[0]
    block_desc = parts[1:]
    if block_no == "0000X":
        block_no = "0-100"
    else:
        block_no = str(int(block_no.replace("XX", "00")))
    block_desc = " ".join(block_desc).title()
    pat = r"(?<=[NSEW]\s)\d+(?P<nsuf>Th|Rd|St)"
    m = re.search(pat, block_desc)
    if m:
        nsuf = m.group("nsuf")
        block_desc = block_desc.replace(nsuf, nsuf.lower())
    return block_no + " block of " + block_desc


df = read_parse_date(sys.argv[1])
df = df[df.date >= df.date.max() - pd.Timedelta(days=30)]
df["block_description"] = df.block.apply(get_block_description)

print_df(df)
