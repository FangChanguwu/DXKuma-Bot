import atexit
import os.path
import subprocess
import sys

import nonebot
from nonebot import logger
from nonebot.adapters.onebot import V11Adapter as OBAdapter

from util.Config import config

if __name__ == "__main__":
    # 初始化部分数据
    logger.info("正在初始化 NoneBot 环境配置文件...")

    # 首先更新Nonebot的环境配置文件
    with open(".env", "w", encoding="utf-8") as v:
        file = (
            f"DRIVER=~quart+~websockets\n"
            f"HOST={config.listen_host}\n"
            f"PORT={config.listen_port}\n"
            f"ONEBOT_ACCESS_TOKEN={config.token}\n"
            f"LOG_LEVEL={config.log_level}\n"
        )
        v.write(file)
        v.close()

    # 初始化 NoneBot
    nonebot.init()

    # 注册适配器
    driver = nonebot.get_driver()
    driver.register_adapter(OBAdapter)

    # 启动加载模块
    logger.info("正在加载模块...")

    # 在这里加载插件
    nonebot.load_plugins("plugins/bot")  # 本地插件
    nonebot.load_plugins("plugins/maimai")  # 本地插件

    # 启动NoneBot
    logger.info("正在启动 NoneBot...")

    nonebot.run()

