# BreakBot的入口脚本
# 用于检测并启动拉格兰和NoneBot并自动进行连接配置
import atexit
import os.path
import subprocess
import sys
import time

from util.Config import config
from util.Logger import logger
from app import nonebot_init

# 检测Lagrange是否启用并已经部署到了对应的位置
if config.is_lagrange:
    logger.info("检测到配置文件中启用了Lagrange支持，正在尝试启动Lagrange并连接。")
    if not os.path.exists('./lagrange'):
        logger.fail("未找到Lagrange程序目录，自动生成了目录。")
        os.mkdir('./lagrange')
    if not os.path.exists('./lagrange/Lagrange.OneBot.exe') and not os.path.exists('./lagrange/Lagrange.OneBot'):
        logger.info("未找到Lagrange可执行程序！")
        logger.info("请将对应平台的Lagrange.Onebot可执行文件放入lagrange目录中，请不要更改可执行文件的名称！")
        sys.exit()
    logger.success("成功检测到了Lagrange可执行程序，正在准备进行启动程序。")
    if not os.path.exists('./lagrange/appsettings.json'):
        logger.info("检测到目录中不存在appsetting.json配置文件，Lagrange为初次启动。")
        logger.info(
            "请手动进入目录根据Lagrange文档对其进行配置和登录： https://lagrangedev.github.io/Lagrange.Doc/Lagrange.OneBot/Config/")
        sys.exit()

    # 设置二进制文件的名称
    if os.path.exists('./lagrange/Lagrange.OneBot.exe'):
        lagrange_executable = "Lagrange.OneBot.exe"
    else:
        lagrange_executable = "Lagrange.OneBot"

    # 运行Lagrange进程并输出stdout
    with open("lagrange.log", 'w+') as outputer:
        process = subprocess.Popen([f"./lagrange/{lagrange_executable}"], cwd="./lagrange", stdout=outputer,
                                   stderr=outputer)

# 完成Lagrange的启动之后，启动Nonebot并进行连接
logger.success("启动Lagrange成功！")

# 首先更新Nonebot的环境配置文件
with open('.env', 'w', encoding='utf-8') as v:
    file = (f"DRIVER=~quart+~websockets\n"
            f"HOST={config.listen_host}\n"
            f"PORT={config.listen_port}\n"
            f"ONEBOT_ACCESS_TOKEN={config.token}\n"
            f'COMMAND_START=[""]\n')
    v.write(file)
    logger.info("生成了NoneBot的环境配置文件.env")
    v.close()

# 启动NoneBot
logger.info("正在启动nonebot...")
nonebot_init()


# 在进程结束时关闭Lagrange
def terminate_process():
    logger.info("检测到进程即将推出，自动结束Lagrange")
    process.terminate()


atexit.register(terminate_process)
