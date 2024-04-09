import nonebot
from nonebot.adapters.onebot import V11Adapter as Adapter
from util.Config import config


def nonebot_init():
    # 初始化 NoneBot
    nonebot.init()

    # 注册适配器
    driver = nonebot.get_driver()
    driver.register_adapter(Adapter)

    # 在这里加载插件
    nonebot.load_builtin_plugins("echo")  # 内置插件
    nonebot.load_plugins("plugins")
    nonebot.load_plugins("plugins/bot")  # 本地插件
    nonebot.load_plugins("plugins/maimai")  # 本地插件

    nonebot.run()
