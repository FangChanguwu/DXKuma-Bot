import os.path
import shutil
import tomllib


class Config:
    def __init__(self):
        if not os.path.exists('./config.toml'):
            shutil.copyfile('./static/config_example.toml', './config.toml')

        self.log_level = None

        # 解析配置文件
        self.read_config()

    def read_config(self):
        with open('./config.toml', 'rb') as f:
            data = tomllib.load(f)
            f.close()
        self.log_level = data['log']['log_level']


config = Config()
