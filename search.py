# -*-coding:utf-8-*-
import requests

def transform_location(key,city,address):
    url = 'https://restapi.amap.com/v3/geocode/geo?parameters'
    output = 'json'
    params = {
        'city':city,
        'address':address,
        'key': key,
        'output':output}
    result = requests.get(url,params=params).json()
    print(key)
    print(result)
    location = result['geocodes'][0]["location"]
    return location

def POI_information(key,location):
    url = 'https://restapi.amap.com/v3/place/around?parameters'
    keywords = input('请输入要查询的关键字（如：美食） ')
    radius = input('请输入要查询半径（如：20）' )
    output = 'json'
    params = {
        'key':key,
        'location':location,
        'keywords':keywords,
        'output':output,
        'radius':radius
    }
    result = requests.get(url,params=params).json()

    return result

def main():
    city = input("请输入城市名称（如：北京市） ")
    address = input("请输入地址（如：朝阳区马戏城） ")
    key = '13db921ffb8c54d473ee45d4920d1b87'
    # 将地理坐标转换为经纬度
    location = transform_location(key,city,address)
    print(location)
    # 范围内目标查询
    result = POI_information(key,location)
    print(result)

if __name__ == '__main__':
    main()
