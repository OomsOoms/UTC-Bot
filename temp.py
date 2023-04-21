import pandas as pd

# Read the data from the file
df = pd.read_csv('data/Results.tsv', sep="\t")

# Group the data by the 'event_id' column and sort each group by the 'average' column
grouped_data = df.groupby('event_id').apply(lambda x: x.sort_values('average'))

# Write the grouped data back to the same file
with open('data/Results.tsv', 'w') as f:
    for _, row in grouped_data.iterrows():
        f.write('\t'.join(str(val) for val in row.values) + '\n')
