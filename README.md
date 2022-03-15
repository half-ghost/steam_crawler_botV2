# steam_crawler_botV2
指令部分，与[第一版](https://github.com/half-ghost/steam_crawler_bot)基本无异，新增了一些功能，在群里发送“st帮助”以发送此图片

![help](https://user-images.githubusercontent.com/55418764/155833576-86e57da8-4814-457a-a71c-159c9ba0eb5b.png)

可在config.py中查看编辑配置项，配置项的作用已在config文件中说明，这里不在赘述

目前已知的问题：喜加一和steam爬虫数据处理部分还有点问题（2022.3.6 已修复，如发现其他问题请提pr）

以及还有一个新模块还在打磨中

# 注意
1.目前steam在国内访问十分不稳定，导致插件与steam有关的部分经常报网络错误，如有条件可在config处填入代理地址。如果没有代理的话，请尽量使用小黑盒作为数据源。
2.该插件中有一个模块（take_my_money.py）用到了字体，为微软雅黑（msyh.ttc），请在windows自带的字体库中获取，并放至与该模块同目录下
