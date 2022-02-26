import os
import requests

# 配置项
# 代理ip设置
proxies={
    'https':'http://127.0.0.1:33334'
}

# 图片形式的消息里最多展现的项目数量
Limit_num = 20

# 促销提醒的图片的数据来源，1为steam，0为小黑盒，当数据来源获取失败时会切换另一个来源
sell_remind_data_from_steam = 1

# 与steam和小黑盒有关的消息是否以图片形式发送，默认为否，注意，如果消息被风控发不出去，会自动转为图片发送
send_pic_mes = False

# 其他必需的配置项，不了解的话请勿乱改
s = requests.session()
s.keep_alive = False
FILE_PATH = os.path.join(os.path.dirname(__file__))
url_new = "https://store.steampowered.com/search/results/?l=schinese&query&sort_by=Released_DESC&category1=998&os=win&infinite=1&start=0&count=50"
url_specials = "https://store.steampowered.com/search/results/?l=schinese&query&sort_by=_ASC&category1=998&specials=1&os=win&filter=topsellers&start=0&count=50"
def other_request(url, headers = None):
    try:
        content = s.get(url, headers = headers, timeout=4)
    except:
        content = s.get(url, headers = headers, proxies=proxies, timeout=4)
    return content