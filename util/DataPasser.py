# 这个类用于在项目中共享一个全局的数据存储实例
import time


class DataPasser:
    """
    这个类用于实例化一组全局存储的数据，方便在不同的插件之间交换使用
    """

    def __init__(self):
        # 存储启动时间戳
        self.start_time = 0
        # 存储2小时内cpu使用率列表，每十分钟存一次，共十二个点
        self.cpu_usage = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def set_start_time(self):
        self.start_time = int(time.time())

    def get_start_time(self):
        return self.start_time

    def get_run_time(self):
        run_time = int(time.time()) - self.start_time
        return run_time

    def add_usage(self, usage: float):
        self.cpu_usage.append(usage)
        self.cpu_usage.pop(0)

    def get_usage(self):
        return self.cpu_usage


datapasser = DataPasser()
