import pandas as pd

df = pd.read_csv("data/Results.tsv", sep = "\t")

# print original dataframe
print('Original dataframe:')
print(df)

# switch positions of columns A and B
df = df[["competition_id","event_id","user_id","guild_id","pos","round_type","average","best","value_1","value_2","value_3","value_4","value_5"]]

# print updated dataframe
print('Updated dataframe:')
print(df)
df.to_csv('data/Results.tsv', sep='\t', index=False)
