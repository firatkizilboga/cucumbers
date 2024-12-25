import pandas as pd

df = pd.read_csv("downloaded.csv")

old_season_id = df["Season_ID"].apply(lambda x: x)
df.Season_ID = df["Season_ID"].apply(lambda x: 2000)

df2 = df
shots = df2.pop("shot_id")
df2.to_csv("create_example.csv", index=False)
df.Season_ID = old_season_id
df.Team_ID = df.Team_ID.apply(lambda x: 51)
df["shot_id"] = shots
df.to_csv("update_example.csv", index=False)
print(shots.to_list())
