import datetime
import os.path

from colorama import Fore, Back, init

from util.Config import config


# 定义日志类
class Logger:
    """
    用于生成日志文件的类，实例化后会自动输出log文件到logs文件夹中\n
    包含DEBUG，INFO，WARNING，ERROR，CRITICAL等多个等级\n
    0: DEBUG\n
    1: INFO\n
    2: SUCCESS\n
    3: WARNING\n
    4: FAIL\n
    5: ERROR\n
    6: CRITICAL\n
    """

    def __init__(self):
        if not os.path.exists('./logs/'):
            os.mkdir('./logs/')
        init()
        self.level = config.log_level
        self.level_color = [
            ["DEBUG", Fore.CYAN],
            ["INFO", Fore.WHITE],
            ["SUCCESS", Fore.GREEN],
            ["WARNING", Fore.YELLOW],
            ["FAIL", Fore.RED],
            ["ERROR", Back.RED + Fore.YELLOW],
            ["CRITICAL", Back.LIGHTYELLOW_EX + Fore.RED]
        ]
        self.log_time = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

    def lprint(self, level, text):
        # 强制转换类型
        text = str(text)
        # 获取当前时间
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 检测传入的日志等级和预设的日志等级之间的大小，然后输出到终端中
        if level >= self.level:
            print(f"{self.level_color[level][1]}{now} [{self.level_color[level][0]}] | {text}")
        # 追加保存日志文件
        with open(f'./logs/log{self.log_time}.log', 'a+', encoding='utf-8') as f:
            f.write(f"{now} [{self.level_color[level][0]}] | {text}\n")
            f.close()

    def debug(self, text):
        self.lprint(0, text)

    def info(self, text):
        self.lprint(1, text)

    def success(self, text):
        self.lprint(2, text)

    def warning(self, text):
        self.lprint(3, text)

    def fail(self, text):
        self.lprint(4, text)

    def error(self, text):
        self.lprint(5, text)

    def critical(self, text):
        self.lprint(6, text)


logger = Logger()
