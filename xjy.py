from bs4 import BeautifulSoup as bs
import os
from .config import *
import json
from hoshino import Service,get_bot,priv
from PIL import ImageDraw,Image,ImageFont
import re
import io
import base64

sv = Service('stbot-喜加一')

head = {"User-Agent":"Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 \
    (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36"}

def xjy_compare():
    '''
    爬取it之家喜加一页面数据,对比data文件夹中xjy_result.json已记录的数据及新数据
    返回一个对比列表,列表里包含了新更新的文章链接
    '''
    data = {}
    xjy_url = "https://www.ithome.com/tag/xijiayi"
    try:
        xjy_page = other_request(url = xjy_url, headers=head).text
        soup = bs(xjy_page, "lxml")
        url_new = []
        for xjy_info in soup.find_all(name = "a", class_ = "title"):
            info_soup = bs(str(xjy_info), "lxml")
            url_new.append(info_soup.a["href"])
        if url_new == []:
            return "Server Error"
        else:
            if not os.path.exists(os.path.join(FILE_PATH, "data/xjy_result.json")):
                with open(os.path.join(FILE_PATH, "data/xjy_result.json"), "w+", encoding="utf-8")as f:
                    data["url"] = url_new
                    data["groupid"] = []
                    f.write(json.dumps(data, ensure_ascii=False))
            url_old = []
            with open(os.path.join(FILE_PATH, "data/xjy_result.json"), "r+", encoding="utf-8")as f:
                content = json.loads(f.read())
                url_old = content["url"]
                groupid = content["groupid"]
            seta = set(url_new)
            setb = set(url_old)
            compare_list = list(seta-setb)
            with open(os.path.join(FILE_PATH, "data/xjy_result.json"), "w+", encoding="utf-8")as f:
                data["url"] = url_new
                data["groupid"] = groupid
                f.write(json.dumps(data, ensure_ascii=False))
    except Exception as e:
        compare_list = f"xjy_compare_error:{e}"

    return compare_list

def xjy_result(model,compare_list):
    '''
    model为Default时则compare_list为xjy_compare返回的对比列表
    model为Query时则compare_list为要查询的项目数量,从data文件夹中xjy_result.json取得对应数量的链接列表
    按照一定格式处理从文章链接爬取的数据并返回
    '''
    result_text_list = []
    xjy_list = []
    if model == "Default":
        xjy_list = compare_list
    elif model == "Query":
        with open(os.path.join(FILE_PATH, "data/xjy_result.json"), "r+", encoding="utf-8")as f:
            url = json.loads(f.read())["url"]
            for i in url:
                xjy_list.append(i.strip())
                if url.index(i) == compare_list-1:
                    break
    try:
        for news_url in xjy_list:
            page = other_request(url= news_url,headers= head).text
            soup = bs(page, "lxml")
            info_soup = bs(str(soup.find(name = "div", class_ = "post_content")), "lxml").find_all(name = "p")
            second_text = ""
            for i in info_soup:
                if i.a != None:
                    if i.a['href'] == "https://www.ithome.com/":
                        text = i.text + "|"
                    elif "ithome" in i.a['href']:
                        text = ""
                    elif "ithome_super_player" in i.a.get("class",""):
                        text = i.text + "|"
                    else:
                        text = i.a["href"] + "|"
                    first_text = text
                else:
                    first_text = i.text + "|"
                second_text += first_text.replace("\xa0", " ")
            temp_text = second_text.split("|")
            third_text = list(set(temp_text))
            third_text.sort(key=temp_text.index)
            xjy_url_text = ""
            for part in third_text:
                if "http" in part:
                    xjy_url_text += "领取地址:" + part + "\n"
            full_text = ""
            for i in third_text:
                if "https://" in i or "http://" in i:
                    continue
                full_text += i
            final_text = f"{third_text[0]}......(更多内容请阅读原文)\n{xjy_url_text}"
            result_text_list.append(final_text + f"原文地址:{news_url}")
    except Exception as e:
        full_text = ""
        result_text_list = f"xjy_result_error:{e}"

    return result_text_list, full_text

def xjy_remind_group(groupid, add:bool):
    with open(os.path.join(FILE_PATH, "data/xjy_result.json"), "r")as f:
        data = json.loads(f.read())
    groupid_list = data["groupid"]
    if add:
        groupid_list.append(groupid)
        data["groupid"] = groupid_list
    if not add:
        data["groupid"].remove(groupid)
    with open(os.path.join(FILE_PATH, "data/xjy_result.json"), "w")as f:
        f.write(json.dumps(data,ensure_ascii=False))

def text_to_img(text):
    font_path = os.path.join(FILE_PATH, "msyh.ttc")
    font = ImageFont.truetype(font_path, 16)
    a = re.findall(r".{1,30}", text.replace(" ", ""))
    text = "\n".join(a)
    width, height = font.getsize_multiline(text.strip())
    img = Image.new("RGB", (width + 20, height + 20), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), text, font=font, fill=(0,0,0))
    b_io = io.BytesIO()
    img.save(b_io, format = "JPEG")
    base64_str = 'base64://' + base64.b64encode(b_io.getvalue()).decode()
    return base64_str

xjy_compare()

# 后接想要的资讯条数（阿拉伯数字）
@sv.on_prefix('喜加一资讯')
async def xjy_info(bot, ev):
    if not os.path.exists(os.path.join(FILE_PATH, "data/xjy_result.json")):
        try:
            xjy_compare()
        except Exception as e:
            sv.logger.error(f"Error:{e}")
            await bot.send(ev, f"哦吼,出错了,报错内容为:{e},请检查运行日志!")
    num = ev.message.extract_plain_text().strip()
    result = xjy_result("Query", int(num))[0]
    mes_list = []
    if "error" in result:
        sv.logger.error(result)
        await bot.send(ev, f"哦吼,出错了,报错内容为:{result},请检查运行日志!")
        return
    else:
        if len(result) <= 3:
            for i in result:
                await bot.send(ev, message = i)
        else:
            for i in result:
                data = {
                    "type": "node",
                    "data": {
                        "name": "sbeam机器人",
                        "uin": "2854196310",
                        "content":i
                            }
                        }
                mes_list.append(data)
            await bot.send_group_forward_msg(group_id=ev['group_id'], messages=mes_list)

# 喜加一提醒开关
@sv.on_suffix('喜加一提醒')
async def xjy_remind_control(bot , ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, "只有管理员才能控制开关哦")
        return
    mes = ev.message.extract_plain_text().strip()
    gid = str(ev.group_id)
    if mes == "开启":
        xjy_remind_group(gid, add=True)
        await bot.send(ev, "喜加一提醒已开启,如有新喜加一信息则会推送")
    elif mes == "关闭":
        try:
            xjy_remind_group(gid, add=False)
            await bot.send(ev, "喜加一提醒已关闭")
        except ValueError:
            await bot.send(ev, "本群并未开启喜加一提醒")

# 定时检查是否有新的喜加一信息
@sv.scheduled_job('cron', hour='*', minute = '*')
async def xjy_remind():
    bot = get_bot()
    url_list = xjy_compare()
    with open(os.path.join(FILE_PATH, "data/xjy_result.json"), "r")as f:
        data = json.loads(f.read())
    group_list = data["groupid"]
    if "Server Error" in url_list:
        sv.logger.info("访问it之家出错,非致命错误,可忽略")
    elif "error" in url_list:
        sv.logger.error(url_list)
    elif len(url_list) != 0:
        mes = xjy_result("Default",url_list)
        for gid in group_list:
            try:
                await bot.send_group_msg(group_id=int(gid),message="侦测到在途的喜加一信息,即将进行推送...")
                for i in mes[0]:
                    await bot.send_group_msg(group_id=int(gid),message=i)
            except Exception as e:
                if "retcode=100" in str(e):
                    mes_list = []
                    for i in mes[0]:
                        data = {
                    "type": "node",
                    "data": {
                        "name": "sbeam机器人",
                        "uin": "2854196310",
                        "content":i
                            }
                        }
                        mes_list.append(data)
                    try:
                        await bot.send_group_forward_msg(group_id=int(gid), messages=mes_list)
                    except Exception as e1:
                        if "retcode=100" in str(e1):
                            await bot.send_group_msg(group_id=int(gid),message=text_to_img(mes[1]))
    else:
        sv.logger.info("无新喜加一信息")
