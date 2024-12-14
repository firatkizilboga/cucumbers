import pandas as pd

import sys

if len(sys.argv) != 3:
    print("Please provide in and out files")
    exit(1)

input_csv = pd.read_csv(sys.argv[1])
output_csv = sys.argv[2]
print(input_csv, output_csv)
df: pd.DataFrame = pd.read_csv(input_csv)
df.replace("NA", None)
df.to_csv(output_csv, index=False)
