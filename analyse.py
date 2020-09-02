# -*-coding:utf-8-*-
import requests
from bson import ObjectId
from pymongo import MongoClient
import logging
import requests
import json

def get_info():
    for item in info.find({},{"_id":1,"district":1,"community":1,"location":1}):
        url = "https://restapi.amap.com/v3/geocode/geo?parameters"
        # 如果所需数据为空，则写入错误日志，开始下一条记录
        if not item["district"] or not item["location"]:
            logger.error("id {} update error".format(item["_id"]))
            continue
        params = {
            "key":"13db921ffb8c54d473ee45d4920d1b87",
            "address": ''.join(["上海市",item["district"],'区',item["location"]]),
            "output":"json"
        }
        output = json.loads(requests.get(url,params=params).content)
        location = output['geocodes'][0]['location']
        info.update_one({"_id":item["_id"]},{"$set":{"coordinate":location}})
        logger.info("id {} update coordinate".format(item["_id"]))




if __name__=="__main__":
    # 连接数据库
    client = MongoClient("localhost")
    db = client["room_renting"]
    info = db["info"]
    # 生成日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s %(asctime)s %(lineno)d %(message)s")
    file_handler = logging.FileHandler("./datafile/analyse_logger.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    # 将地理位置转换为经纬度然后插入数据库
    get_info()

