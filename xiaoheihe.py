import json
from .config import *
from hoshino import Service
from .take_my_money import pic_creater

sv = Service("stbot-小黑盒")

# 小黑盒爬虫
def hey_box(page:int):
    url = "https://api.xiaoheihe.cn/game/web/all_recommend/games/?os_type=web&version=999.0.0&show_type=discount&limit=30&offset=" + str((page-1)*30)
    json_page = json.loads(other_request(url).text)
    result_list = json_page['result']['list']
    result = []
    for i in result_list:
        gameinfo = {}
        appid = str(i["appid"])
        gameinfo['appid'] = appid
        gameinfo['链接'] = "https://store.steampowered.com/app/" + appid
        gameinfo['图片'] = "https://media.st.dl.pinyuncloud.com/steam/apps/" + appid + "/capsule_sm_120.jpg"
        gameinfo['标题'] = i["game_name"]
        gameinfo['原价'] = str(i["price"]["initial"])
        gameinfo['当前价'] = str(i["price"]["current"])
        gameinfo['平史低价'] = str(i["price"].get("lowest_price","无平史低价格信息"))
        try:
            lowest = i["price"]["is_lowest"]
        except:
            try:
                lowest = i["heybox_price"]["is_lowest"]
            except:
                lowest = 2
        try:
            discount = str(i["price"]["discount"])
        except:
            discount = str(i["heybox_price"]["discount"])
        gameinfo['折扣比'] = discount
        if lowest == 0:
            lowest_stat = "不是史低哦"
        elif lowest == 1:
            lowest_stat = "是史低哦"
        elif lowest == 2:
            lowest_stat = "无当前是否史低信息"
        gameinfo['是否史低'] = lowest_stat
        new_lowest = i["price"].get("new_lowest"," ")
        newlowest = "好耶!是新史低!" if new_lowest == 1 else " "
        gameinfo['是否新史低'] = newlowest
        gameinfo['截止日期'] = i["price"].get("deadline_date","无截止日期信息")
        result.append(gameinfo)
    
    return result

# 小黑盒搜索爬虫
def hey_box_search(game_name:str):
    url = "https://api.xiaoheihe.cn/game/search/?os_type=web&version=999.0.0&q=" + str(game_name)
    json_page = json.loads(other_request(url).text)
    game_result = json_page["result"]["games"]
    result = []
    for i in game_result:
        gameinfo = {}
        steamappid = str(i["steam_appid"])
        gameinfo["appid"] = steamappid
        gameinfo["标题"] = i["name"]
        gameinfo["图片"] = "https://media.st.dl.pinyuncloud.com/steam/apps/" + steamappid + "/capsule_sm_120.jpg"
        gameinfo["其他平台图片"] = i["image"]
        platform = i.get("platforms","非steam平台,不进行解析,请自行查看链接")
        gameinfo["平台"] = platform
        if "steam" in platform:
            gameinfo["链接"] = "https://store.steampowered.com/app/" + steamappid
            try:
                original = i["price"]["initial"]
                gameinfo["原价"] = original
            except:
                gameinfo["原价"] = "免费开玩"
                result.append(gameinfo)
                continue
            current = i["price"]["current"]
            gameinfo["当前价"] = current
            gameinfo["平史低价"] = str(i["price"].get("lowest_price","无平史低价格信息"))
            if original != current:
                lowest = i["price"]["is_lowest"]
                gameinfo["折扣比"] = i["price"]["discount"]
                lowest_state = "是史低哦" if lowest == 1 else "不是史低哦"
                gameinfo["是否史低"] = lowest_state
                new_lowest = i["price"].get("new_lowest"," ")
                newlowest = "好耶!是新史低!" if new_lowest == 1 else " "
                gameinfo["是否新史低"] = newlowest
                gameinfo["截止日期"] = i["price"].get("deadline_date","无截止日期信息")
            else:
                gameinfo["折扣比"] = "当前无打折信息"
                gameinfo["是否史低"]=gameinfo["是否新史低"]=gameinfo["截止日期"] = " "
        else:
            gameinfo["平台"] = "非steam平台,不进行解析,请自行查看链接"
            gameinfo["链接"] = "https://www.xiaoheihe.cn/games/detail/" + steamappid
        result.append(gameinfo)
        
    return result

def mes_creater(result, gamename):
    mes_list = []
    if result[0].get("平台","") == "":
        content = f"    ***数据来源于小黑盒官网***\n***默认展示小黑盒steam促销页面***"
        for i in range(len(result)):
            mes = f"[CQ:image,file={result[i]['图片']}]\n{result[i]['标题']}\n原价:¥{result[i]['原价']} \
                当前价:¥{result[i]['当前价']}(-{result[i]['折扣比']}%)\n平史低价:¥{result[i]['平史低价']} {result[i]['是否史低']}\n链接:{result[i]['链接']}\
                \n{result[i]['截止日期']}(不一定准确,请以steam为准)\n{result[i]['是否新史低']}\nappid:{result[i]['appid']}".strip().replace("\n ", "").replace("    ", "")
            data = {
            "type": "node",
            "data": {
                "name": "sbeam机器人",
                "uin": "2854196310",
                "content":mes
                    }
                }
            mes_list.append(data)
    else:
        content = f"***数据来源于小黑盒官网***\n游戏{gamename}搜索结果如下"
        for i in range(len(result)):
            if "非steam平台" in result[i]['平台']:
                mes = f"[CQ:image,file={result[i]['其他平台图片']}]\n{result[i]['标题']}\n{result[i]['平台']}\n{result[i]['链接']} (请在pc打开,在手机打开会下载小黑盒app)".strip().replace("\n ", "")
            else:
                if result[i]['原价'] == "免费开玩":
                    mes = mes = f"[CQ:image,file={result[i]['图片']}]\n{result[i]['标题']}\n原价:{result[i]['原价']}\n链接:{result[i]['链接']}\nappid:{result[i]['appid']}".strip().replace("\n ", "").replace("    ", "")
                elif result[i]['折扣比'] == "当前无打折信息":
                    mes = f"[CQ:image,file={result[i]['图片']}]\n{result[i]['标题']}\n{result[i]['折扣比']}\n当前价:¥{result[i]['当前价']} \
                        平史低价:¥{result[i]['平史低价']}\n链接:{result[i]['链接']}\nappid:{result[i]['appid']}".strip().replace("\n ", "").replace("    ", "")
                else:
                    mes = f"[CQ:image,file={result[i]['图片']}]\n{result[i]['标题']}\n原价:¥{result[i]['原价']} 当前价:¥{result[i]['当前价']}\
                        (-{result[i]['折扣比']}%)\n平史低价:¥{result[i]['平史低价']} {result[i]['是否史低']}\n链接:{result[i]['链接']}\n\
                            {result[i]['截止日期']}\n{result[i]['是否新史低']}\nappid:{result[i]['appid']}".strip().replace("\n ", "").replace("    ", "")
            data = {
            "type": "node",
            "data": {
                "name": "sbeam机器人",
                "uin": "2854196310",
                "content":mes
                    }
                }
            mes_list.append(data)
    announce = {
    "type": "node",
    "data": {
        "name": "sbeam机器人",
        "uin": "2854196310",
        "content":content
            }
        }
    mes_list.insert(0,announce)
    return mes_list

@sv.on_prefix('小黑盒')
async def heybox(bot, ev):
    mes = ev.message.extract_plain_text().strip()
    gamename = ""
    try:
        if "特惠" in mes:
            data = hey_box(1)
        elif "搜" in mes:
            gamename = mes[1:]
            data = hey_box_search(gamename)
            if len(data) == 0:
                await bot.send(ev, "无搜索结果")
                return
        else:
            return
        await bot.send(ev, "正在搜索并生成消息中,请稍等片刻!", at_sender=True)
    except Exception as e:
        sv.logger.error(f"Error:{e}")
        await bot.send(ev, f"哦吼,获取信息出错了,报错内容为{e},请检查运行日志!")
    try:
        if send_pic_mes:
            await bot.send(ev, f"[CQ:image,file={pic_creater(data, is_steam=False)}]")
            return
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=mes_creater(data, gamename))
    except Exception as err:
        if "retcode=100" in str(err):
            await bot.send(ev, "消息可能被风控,正在转为其他形式发送!")
            try:
                if send_pic_mes:
                    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=mes_creater(data, gamename))
                    return
                if not send_pic_mes:
                    await bot.send(ev, f"[CQ:image,file={pic_creater(data, is_steam=False)}]")
            except Exception as err:
                if "retcode=100" in str(err):
                    await bot.send(ev, "消息可能依旧被风控,无法完成发送!")
        else:
            sv.logger.error(f"Error:{err}")
            await bot.send(ev, f"发生了其他错误,报错内容为{err},请检查运行日志!")
