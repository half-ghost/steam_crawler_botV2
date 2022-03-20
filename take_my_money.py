import os
from PIL import Image, ImageFont, ImageDraw
from bs4 import BeautifulSoup as bs
import io
import math
import re
import base64
import json
from .config import *
from datetime import datetime
from hoshino import Service,priv,get_bot

sv = Service("stbot-促销信息")

font_path = os.path.join(FILE_PATH, "msyh.ttc")
font1 = ImageFont.truetype(font_path, 18)
font2 = ImageFont.truetype(font_path, 12)
font3 = ImageFont.truetype(font_path, 13)

def resize_font(font_size, text_str, limit_width):
    '''
    在给定的长度内根据文字内容来改变文字的字体大小
    font_size为默认大小,即如果函数判断以此字体大小所绘制出来的文字内容不会超过给定的长度时,则保持这个大小
    若绘制出来的文字内容长度大于给定长度,则会不断对减小字体大小直至刚好小于给定长度
    text_str为文字内容,limit_width为给定的长度
    返回内容为PIL.ImageFont.FreeTypeFont对象,以及调整字体过后的文字长宽
    '''

    font = ImageFont.truetype(font_path, font_size)
    font_lenth = font.getsize(str(text_str))[0]
    while font_lenth > limit_width:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        font_lenth = font.getsize(str(text_str))[0]
    font_width = font.getsize(str(text_str))[1]

    return font,font_lenth,font_width

def steam_monitor():
    url = "https://keylol.com"
    r = other_request(url).text
    soup = bs(r, "lxml")
    stat = soup.find(name = "div", id = "steam_monitor")
    a = stat.findAll(name = "a")
    for i in a:
        if "状态" in str(i.text):
            continue
        sell_name = i.text.replace(" ","").strip()
    script = stat.find_next_sibling(name = "script").string
    date = re.findall(r'new Date\("(.*?)"', script)[0]
    a=datetime.strptime(date, "%Y-%m-%d %H:%M")
    b=datetime.now()
    xc = (a-b).total_seconds()
    m, s = divmod(int(xc), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    sell_date =  "%d日%d时%d分%d秒" % (d, h, m, s)
    return sell_name,sell_date

def pic_creater(data:list, num=Limit_num, is_steam=True, monitor_on=False):
    '''
    生成一个图片,data为小黑盒或steam爬取的数据 num为图片中游戏项目的数量,默认为config.py里设定的数量
    is_steam为判断传入的数据是否steam来源,monitor_on为是否加入促销活动信息 两者需手动指定
    '''
    if len(data) < num:
        num = len(data)

    if monitor_on:
        background = Image.new("RGB", (520, (60+10)*num + 10 + 110), (27, 40, 56))
        start_pos = 110
        sell_info = steam_monitor()
        sell_bar = Image.new("RGB", (500, 100), (22, 32, 45))
        draw_sell_bar = ImageDraw.Draw(sell_bar, "RGB")
        uppper_text = sell_info[0].split(":")[0]
        if "正在进行中" in sell_info[0].split(":")[1]:
            lower_text = f"正在进行中(预计{sell_info[1]}后结束)"
            cdtext_color = (255,0,0)
        else:
            lower_text = f"预计{sell_info[1]}后开始"
            cdtext_color = (0,255,0)
        uppper_text_font = resize_font(20, uppper_text, 490)
        draw_sell_bar.text(((500-uppper_text_font[1])/2,20), uppper_text, font = uppper_text_font[0], fill = (199, 213, 224))
        draw_sell_bar.text(((500-font1.getsize(lower_text)[0])/2,62), lower_text, font = font1, fill = cdtext_color)
        background.paste(sell_bar, (10, 10))
    else:
        background = Image.new("RGB", (520, (60+10)*num + 10), (27, 40, 56))
        start_pos = 0

    for i in range(num):
        game_bgbar = Image.new("RGB", (500, 60), (22, 32, 45))
        draw_game_bgbar = ImageDraw.Draw(game_bgbar, "RGB")

        if not is_steam:
            if "非steam平台" in data[i].get('平台',""):
                a = other_request(data[i].get('其他平台图片')).content
                aimg_bytestream = io.BytesIO(a)
                a_imgb = Image.open(aimg_bytestream).resize((160, 60))
                game_bgbar.paste(a_imgb, (0, 0))
                draw_game_bgbar.text((165, 5), data[i].get('标题'), font = font1, fill = (199, 213, 224))
                draw_game_bgbar.text((165, 35), data[i].get('平台'), font = font2, fill = (199, 213, 224))
                background.paste(game_bgbar, (10, 60*i+10*(i+1)))
                continue

        try:
            if not is_steam:
                a = other_request(data[i].get('图片')).content
            else:
                a = other_request(data[i].get('高分辨率图片')).content
            aimg_bytestream = io.BytesIO(a)
            a_imgb = Image.open(aimg_bytestream).resize((160, 60))
        except:
            a = other_request(data[i].get('低分辨率图片')).content
            aimg_bytestream = io.BytesIO(a)
            a_imgb = Image.open(aimg_bytestream).resize((160, 60))
        game_bgbar.paste(a_imgb, (0, 0))

        if is_steam:
            rate_bg = Image.new("RGBA", (54, 18), (0,0,0,200))
            a = rate_bg.split()[3]
            game_bgbar.paste(rate_bg, (106, 0), a)
            draw_game_bgbar.text((107, 0), data[i].get('评测').split(",")[0], font = font3, fill = (255, 255, 225))

        gameinfo_area = Image.new("RGB", (280, 60), (22, 32, 45))
        draw_gameinfo_area = ImageDraw.Draw(gameinfo_area, "RGB")
        draw_gameinfo_area.text((0, 5), data[i].get('标题'), font = font1, fill = (199, 213, 224))
        if is_steam:
            draw_gameinfo_area.text((0, 35), data[i].get('标签'), font = font2, fill = (199, 213, 224))
        else:
            if data[i].get('原价') == "免费开玩":
                text = "免费开玩"
            elif data[i].get('平史低价') == "无平史低价格信息":
                text = "无平史低价格信息"
            elif data[i].get('折扣比') == "当前无打折信息":
                text = f"平史低价:¥{data[i].get('平史低价')} | 当前无打折信息"
            else:
                text = f"平史低价:¥{data[i].get('平史低价')} | {data[i].get('是否史低')} | {data[i].get('截止日期')} | {data[i].get('是否新史低') if data[i].get('是否新史低')!=' ' else '不是新史低'}"
            draw_gameinfo_area.text((0, 35), text, font = font2, fill = (199, 213, 224))
        game_bgbar.paste(gameinfo_area, (165, 0))

        if (is_steam and data[i].get('折扣价'," ") != " ") or (not is_steam and data[i].get('原价') != "免费开玩" and data[i].get('折扣比') != "当前无打折信息"):
            if is_steam:
                original_price = data[i].get('原价')
                discount_price, discount_percent = re.findall(r"^(.*?)\((.*?)\)", data[i].get('折扣价'))[0]
            else:
                original_price = f"¥{data[i].get('原价')}"
                discount_price = f"¥{data[i].get('当前价')}"
                discount_percent = f"-{data[i].get('折扣比')}%"
            green_bar = Image.new("RGB", (font2.getsize(discount_percent)[0], font2.getsize(discount_percent)[1]+4), (76, 107, 34))
            game_bgbar.paste(green_bar, (math.ceil(445+(55 - font2.getsize(discount_percent)[0])/2), 4))
            draw_game_bgbar.text((math.ceil(445+(55 - font2.getsize(discount_percent)[0])/2), 4), discount_percent, font = font2, fill = (199, 213, 224))
            draw_game_bgbar.text((math.ceil(445+(55 - font2.getsize(original_price)[0])/2), 22), original_price, font = font2, fill = (136, 136, 136))
            del_line = Image.new("RGB", (font2.getsize(original_price)[0], 1), (136, 136, 136))
            game_bgbar.paste(del_line, (445 + math.ceil((55-font2.getsize(original_price)[0])/2), 22 + math.ceil(font2.getsize(original_price)[1]/2)+2))
            draw_game_bgbar.text((math.ceil(445+(55 - font2.getsize(discount_price)[0])/2), 40), discount_price, font = font2, fill = (199, 213, 224))
        else:
            if is_steam:
                original_price = data[i].get('原价')
            else:
                if data[i].get('原价') == "免费开玩":
                    original_price = "免费开玩"
                else:
                    original_price = "¥"+data[i].get('原价')
            temp_font = resize_font(12,original_price,55)
            draw_game_bgbar.text((math.ceil(445+(55-temp_font[1])/2), math.ceil(30-temp_font[2]/2)), original_price, font = temp_font[0], fill = (199, 213, 224))

        background.paste(game_bgbar, (10, start_pos+60*i+10*(i+1)))

    b_io = io.BytesIO()
    background.save(b_io, format = "JPEG")
    base64_str = 'base64://' + base64.b64encode(b_io.getvalue()).decode()
    return base64_str

def sell_remind_group(groupid, add:bool):
    data = {}
    if not os.path.exists(os.path.join(FILE_PATH, "data\\sell_remind_group.txt")):
        with open(os.path.join(FILE_PATH, "data\\sell_remind_group.txt"), "w", encoding="utf-8")as f:
            data["groupid"] = []
            f.write(json.dumps(data, ensure_ascii=False))
    with open(os.path.join(FILE_PATH, "data\\sell_remind_group.txt"), "r", encoding="utf-8")as f:
        data = json.loads(f.read())
    groupid_list = data["groupid"]
    if add:
        groupid_list.append(groupid)
        data["groupid"] = groupid_list
    if not add:
        data["groupid"].remove(groupid)
    with open(os.path.join(FILE_PATH, "data\\sell_remind_group.txt"), "w", encoding="utf-8")as f:
        f.write(json.dumps(data,ensure_ascii=False))

# 每日促销提醒开关
@sv.on_suffix('每日促销提醒')
async def sell_remind_control(bot , ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, "只有管理员才能控制开关哦")
        return
    mes = ev.message.extract_plain_text().strip()
    gid = str(ev.group_id)
    if mes == "开启":
        sell_remind_group(gid, add=True)
        await bot.send(ev, "每日促销提醒已开启")
    elif mes == "关闭":
        try:
            sell_remind_group(gid, add=False)
            await bot.send(ev, "每日促销提醒已关闭")
        except ValueError:
            await bot.send(ev, "本群并未开启每日促销提醒")

# 每天9点发送每日促销提醒消息
@sv.scheduled_job('cron', hour='9')
async def sell_remind():
    from .steam_crawler_botV2 import steam_crawler
    from .xiaoheihe import hey_box

    bot = get_bot()
    with open(os.path.join(FILE_PATH, "data\\sell_remind_group.txt"), "r")as f:
            groupid_data = json.loads(f.read())
    groupid = groupid_data['groupid']
    try:
        if sell_remind_data_from_steam:
            try:
                data = steam_crawler(url_specials)
                steam = True
            except:
                data = hey_box(1)
                steam = False
        else:
            try:
                data = hey_box(1)
                steam = False
            except:
                data = steam_crawler(url_specials)
                steam = True
        for gid in groupid:
            try:
                await bot.send_group_msg(group_id=int(gid),message=f"[CQ:image,file={pic_creater(data, is_steam=steam, monitor_on=True)}]")
            except Exception as e:
                await bot.send_group_msg(group_id=int(gid),message=f"每日促销提醒出错,报错内容为:{e}")
    except Exception as err:
        sv.logger.info(f"每日促销提醒出错,报错内容为:{err}")

@sv.on_fullmatch('查询促销')
async def query_sell_info(bot, ev):
    try:
        sell_info = steam_monitor()
    except Exception as e:
        sv.logger.info(f"Error:{e}")
        await bot.send(ev, f"获取信息失败,报错内容为:{e}")
    sell_name = sell_info[0].split(":")[0]
    if "正在进行中" in sell_info[0].split(":")[1]:
        sell_time = f"正在进行中(预计{sell_info[1]}后结束)"
    else:
        sell_time = f"预计{sell_info[1]}后开始"
    await bot.send(ev, f"{sell_name}:{sell_time}")
