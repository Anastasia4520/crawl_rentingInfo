# -*-coding:utf-8-*-
import logging,datetime,time
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import pymongo
import base64
from fontTools.ttLib import TTFont
from lxml import etree

def open_url(url,agents,proxies):
    # 打开网页获取源代码
    # headers = random.choice(agents)
    # proxy = random.choice(proxies)
    try:
        response = requests.get(url)
        print(response.status_code)
    except Exception as e:
        print(e)
        # print(proxy, "劣质代理")
        # Proxies.delete_one(proxy)
        # Agents.delete_one(headers)
        # open_url(url,agents,proxies)
    #
    print("打开成功")
    return response

def find_item_information(each,df_file):
    # 提取所需信息
   if 1==1:
        url = re.findall(r"(.*?)\?", each['link'])[0]
        cover_url = each.a.img["lazy_src"]
        try:
            title = each.div.h3.text.strip()
        except AttributeError:
            title = ' '
            print("第{}条没有title".format(num))
        room_detail = each.find("p", class_="details-item tag").text
        room_detail_list = re.findall(r"(.*?)\|(.*?)\|(.*?)\s+", room_detail)
        room_type = room_detail_list[0][0].strip()
        room_area = room_detail_list[0][1].strip()
        room_height = room_detail_list[0][2].strip()
        address = each.find("address", class_="details-item").text
        address_list = re.findall(r"(.*?)\s+(.*?)-{1}(.*?)\s(.*)", address)
        community = address_list[0][0]
        district = address_list[0][1]
        subdistrict = address_list[0][2]
        location = address_list[0][3]
        other_detail = [i for i in each.find("p", class_="details-item bot-tag").text.split("\n") if
                        i != "" and i != "有电梯"]
        renting_type = other_detail[0]
        room_fase_to = other_detail[1]
        try:
            metro_line = other_detail[2]
        except IndexError:
            metro_line = False
        house_information_url = each.div.address.a["href"]
        price_info = each.find("div", class_="zu-side").text.split(" ")
        price = price_info[0].strip()
        price_unit = price_info[1].strip()
        # 将所需信息整理成字典
        information = {
            "price_unit": price_unit,
            "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "district": district,
            "room_height": room_height,
            "title": title,
            "url": url,
            "price": price,
            "subdistrict": subdistrict,
            "metro_line": metro_line,
            "cover_url": cover_url,
            "room_fase_to": room_fase_to,
            "community": community,
            "room_area": room_area,
            "house_information_url": house_information_url,
            "renting_type": renting_type,
            "room_type": room_type,
            "location": location

        }
        # 将所需信息插入数据库
        print(information)
        return information


def parse_secret(content):
    # 将网页信息中的字体部分转为二进制文件，网页利用@font_face进行了关键数字加密
    base64Str = content.split("base64,")[1].split("')")[0]
    binData = base64.decodebytes(base64Str.encode())
    with open("./datafile/anjvke_font.tff", "wb") as f:
        f.write(binData)
    font = TTFont("./datafile/anjvke_font.tff")
    font.saveXML(r"./datafile/anjvke_font.xml")
    # 用etree进行解析
    font_xml = etree.parse(r"./datafile/anjvke_font.xml")
    id = font_xml.xpath("//GlyphID/@id")
    name = font_xml.xpath("//GlyphID/@name")
    code = font_xml.xpath("//cmap_format_4//map/@code")
    name2 = font_xml.xpath("//cmap_format_4//map/@name")
    id_name = dict(zip(id, name))
    code_name = dict(zip(code, name2))
    id_code = {}
    for i in id_name.items():
        for j in code_name.items():
            if i[1] == j[1]:
                id_code[j[0]] = i[0]
    # 对网页中的数字进行替换操作
    content = content.replace("&#", "0")
    for each in id_code:
        content = content.replace(each + ";", id_code[each])

    return content

def find_renting_information():
    global num
    proxies = []
    agents = []
    # 将数据库中的代理池导出来
    for each in Agents.find({},{'User_Agent':1,"_id":0}):
        agents.append(each)
    for each in Proxies.find({}, {"_id": 0}):
            proxies.append(each)
    num = 0
    page_num = 1
    df_file = pd.DataFrame()
    while True:
        page_num += 1
        if page_num==1:
            url = 'https://sh.zu.anjuke.com'
        else:
            url = 'https://sh.zu.anjuke.com/fangyuan/p{}/'.format(page_num)
        print("进入第{}页".format(page_num))
        # 打开网页，获取网页信息
        html = open_url(url, agents, proxies)
        with open("安居客网页信息原生态{}.txt".format(page_num),'w',encoding='utf-8') as f:
            f.write(html.text)
        # 对加密的数字进行解密操作
        try:
            html_text = parse_secret(html.text)
        except IndexError:
            time.sleep(30)
            html = open_url(url,agents,proxies)
            html_text = parse_secret(html.text)

        with open("安居客网页信息解密后{}.txt".format(page_num),'w',encoding='utf-8') as f:
            f.write(html_text)
        soup = BeautifulSoup(html_text,"html.parser")
        # 解析要所需要的的元素信息
        renting_info_list = soup.find_all("div",class_="zu-itemmod")

        if not renting_info_list:
            print(html_text)
            print("爬取完毕，我退出啦！")
            break
        # 获取每个网页中的每个租房信息
        for each in renting_info_list:
            num += 1
            # 返回每条租房信息
            information = find_item_information(each,df_file)
            try:
                table.insert_one(information)
            except Exception as e:
                logger.error(str(e))
            logger.info("Document {} insert".format(num))
            df = pd.DataFrame.from_dict(information, orient='index').T
            df_file = df_file.append(df, ignore_index=True)
            # 导入csv文件
            if df_file.shape[0] == 500:
                df_file.to_csv(r"./datafile/renting_info[{}].csv".format(num // 500), encoding="utf_8_sig")
                logger.info("renting_info{}.csv created".format(1))
                df_file = pd.DateFrame()

if __name__ == "__main__":
    # 生成日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s %(asctime)s %(lineno)d %(message)s")
    file_handler = logging.FileHandler(r"./datafile/crawl_logger.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    # 连接数据库
    client = pymongo.MongoClient("localhost")
    db1 = client["room_renting"]
    table = db1["info"]
    db2 = client["proxy"]
    Proxies = db2["proxies"]
    Agents = db2["agents"]
    # 开始寻找每页的租房信息
    find_renting_information()

