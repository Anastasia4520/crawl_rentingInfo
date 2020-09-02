# -*-coding:utf-8-*-
import pymongo
import pandas as pd

client = pymongo.MongoClient("localhost")
db = client["room_renting"]
info = db["info"]
list_info = []

for i in info.find({},{"_id":0}):
    list_info.append(i)
df = pd.DataFrame(list_info)
df.to_csv("安居客房源信息.csv",encoding="utf_8_sig")