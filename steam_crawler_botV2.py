from bs4 import BeautifulSoup as bs
import re
import json
import os
from .config import *
from hoshino import Service
from .take_my_money import pic_creater

sv = Service("stbot-steam")

with open(os.path.join(FILE_PATH, "data/tag.json"), "r", encoding="utf-8")as f:
    tagdata = json.loads(f.read())
# steam爬虫
def steam_crawler(url_choose:str):
    result = []
    get_url = other_request(url_choose).text
    soup = bs(get_url.replace(r"\n", "").replace(r"\t", "").replace(r"\r", "").replace("\\", ""), "lxml")
    row_list = soup.find_all(name = "a", class_ = "search_result_row")
    for row in row_list:
        gameinfo = {}
        gameinfo['标题'] = row.find(name = "span", class_ = "title").text
        href = row.get("href")
        gameinfo['链接'] = href
        appid = row.get("data-ds-appid")
        gameinfo['appid'] = appid
        gameinfo['高分辨率图片'] = "https://media.st.dl.pinyuncloud.com/steam/apps/" + appid + "/capsule_231x87.jpg"
        gameinfo['低分辨率图片'] = row.find(name = "img").get("src")
        if str(row.strike) == "None" :
            try:
                price = row.find(name = "div", class_ = "col search_price responsive_secondrow").text.replace("\r", "").replace("\n", "").replace(" ", "")
                gameinfo['折扣价'] = " "
                if price!="" and "免费" not in price and "Free" not in price:
                    gameinfo['原价'] = price
                elif price!="":
                    gameinfo['原价'] = ("无价格信息")
                else:
                    gameinfo['原价'] = "免费开玩"
            except:
                gameinfo['原价'] = ("无价格信息")
                gameinfo['折扣价'] = " "
        else:
            discount_price = re.findall(r"<br/>(.*?)  ", str(row))[0]
            discount_percent = row.find(name = "div", class_ = "col search_discount responsive_secondrow").text.replace("\n", "").strip()
            gameinfo['原价'] = row.strike.string.strip().replace(" ", "")
            gameinfo['折扣价'] = f'{str(discount_price).strip().replace(" ", "")}({discount_percent})'
        try:
            rate = row.find(name = "span", class_ = "search_review_summary").get("data-tooltip-html")
            gameinfo['评测'] = rate.replace("<br>", ",").replace(" ", "")
        except:
            gameinfo['评测'] = "暂无评测"
        try:
            tag = row.get("data-ds-tagids").strip("[]").split(",")
            tagk = ""
            for i in tag:
                tagk += tagdata["tag_dict"].get(i) + ","
            gameinfo['标签'] = tagk.strip(",")
        except:
            gameinfo['标签'] = '无用户标签'
        result.append(gameinfo)

    return result
# 根据传入的tag创建tag搜索链接,返回tag搜索链接以及传入的tag中有效的tag(有效tag具体参考data文件夹中的tag.json)
def tagurl_creater(tag:list, page:int):
    tag_search_num = "&tags="
    tag_name = ""
    tag_list = tag
    count = f"&start={(page-1)*50}&count=50"
    for i in tag_list:
        try:
            tag_search_num += tagdata["tag_dict"][i] + ","
            tag_name += i + ","
        except:
            pass
    tag_search_url = "https://store.steampowered.com/search/results/?l=schinese&query&force_infinite=1&filter=topsellers&category1=998&infinite=1" + tag_search_num.strip(",") + count
    return tag_search_url,tag_name.strip(",")

def mes_creater(result:dict):
    mes_list = []
    for i in range(len(result)):
        if result[i]['原价'] == "免费开玩" or result[i]['原价'] == "无价格信息":
            mes = f"[CQ:image,file={result[i]['低分辨率图片']}]\n{result[i]['标题']}\n原价:{result[i]['原价']}\
                \n链接:{result[i]['链接']}\n{result[i]['评测']}\n用户标签:{result[i]['标签']}\nappid:{result[i]['appid']}"
        else:
            mes = f"[CQ:image,file={result[i]['低分辨率图片']}]\n{result[i]['标题']}\n原价:{result[i]['原价']} 折扣价:{result[i]['折扣价']}\
                \n链接:{result[i]['链接']}\n{result[i]['评测']}\n用户标签:{result[i]['标签']}\nappid:{result[i]['appid']}"
        data = {
        "type": "node",
        "data": {
            "name": "sbeam机器人",
            "uin": "2854196310",
            "content":mes
                }
            }
        mes_list.append(data)
    return mes_list

# 匹配关键词发送相关信息,例:今日特惠,发送今日特惠信息,今日新品则发送新品信息
@sv.on_prefix('今日')
async def Gameinfo(bot, ev):
    model = ev.message.extract_plain_text().strip()
    try:
        if model == "新品":
            data = steam_crawler(url_new)
        elif model == "特惠":
            data = steam_crawler(url_specials)
        else:
            return
    except Exception as e:
        sv.logger.error(f"Error:{e}")
        await bot.send(ev, f"哦吼,出错了,报错内容为:{e},请检查运行日志!")
        return
    await bot.send(ev, "正在生成消息,请稍等片刻!", at_sender=True)
    try:
        if send_pic_mes:
            await bot.send(ev, f"[CQ:image,file={pic_creater(data, is_steam=True)}]")
            return
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=mes_creater(data))
    except Exception as err:
        if str(err) == "<ActionFailed, retcode=100>":
            await bot.send(ev, "消息被风控,正在转为其他形式发送!")
            try:
                if send_pic_mes:
                    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=mes_creater(data))
                    return
                if not send_pic_mes:
                    await bot.send(ev, f"[CQ:image,file={pic_creater(data, is_steam=True)}]")
            except Exception as err:
                if str(err) == "<ActionFailed, retcode=100>":
                    await bot.send(ev, "消息依旧被风控,无法完成发送!")
        else:
            sv.logger.error(f"Error:{err}")
            await bot.send(ev, f"发生了其他错误,报错内容为{err},请检查运行日志!")

# 后接格式:页数(阿拉伯数字) 标签1 标签2,例:st搜标签 动作 射击
@sv.on_prefix(('st搜','St搜','ST搜','sT搜'))
async def search_tag(bot, ev):
    mes = ev.message.extract_plain_text().strip()
    try:
        if "标签" in mes:
            tags = mes[2:].split(" ")
            tagurl = tagurl_creater(tags, 1)
            if tagurl[1] == "":
                await bot.send(ev, "没有匹配到有效标签")
                return
            data = steam_crawler(tagurl[0])
        elif "游戏" in mes:
            gamename = mes[2:]
            search_url = r"https://store.steampowered.com/search/results/?l=schinese&query&start=0&count=50&dynamic_data=&sort_by=_ASC&snr=1_7_7_151_7&infinite=1&term=" + gamename
            data = steam_crawler(search_url)
            if len(data) == 0:
                await bot.send(ev, "无搜索结果")
                return
    except Exception as e:
        sv.logger.error(f"Error:{e}")
        await bot.send(ev, f"哦吼,出错了,报错内容为{e},请检查运行日志!")
        return
    try:
        await bot.send(ev, "正在搜索并生成合并消息中,请稍等片刻!", at_sender=True)
        if "标签" in mes:
            await bot.send(ev, f"标签{tagurl[1]}搜索结果如下:")
        elif "游戏" in mes:
            await bot.send(ev, f"游戏{gamename}搜索结果如下:")
        if send_pic_mes:
            await bot.send(ev, f"[CQ:image,file={pic_creater(data, is_steam=True)}]")
            return
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=mes_creater(data))
    except Exception as err:
        if str(err) == "<ActionFailed, retcode=100>":
            await bot.send(ev, "消息被风控,正在转为其他形式发送!")
            try:
                if send_pic_mes:
                    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=mes_creater(data))
                    return
                if not send_pic_mes:
                    await bot.send(ev, f"[CQ:image,file={pic_creater(data, is_steam=True)}]")
            except Exception as err:
                if str(err) == "<ActionFailed, retcode=100>":
                    await bot.send(ev, "消息依旧被风控,无法完成发送!")
        else:
            sv.logger.error(f"Error:{err}")
            await bot.send(ev, f"发生了其他错误,报错内容为{err},请检查运行日志!")
