import json

data1 = "/home/jihyunlee/MI/profile/source/reddit_posts_masked.json"
data2 = "reddit_posts_masked4.json"


data1 = json.load(open(data1, "r", encoding="utf-8"))
data2 = json.load(open(data2, "r", encoding="utf-8"))


data = {**data1, **data2}
json.dump(data, open("reddit_posts_masked_merged.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)