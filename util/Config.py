import os.path
import shutil
import tomllib


class Config:
    def __init__(self):
        if not os.path.exists('./config.toml'):
            shutil.copyfile('./static/config_example.toml', './config.toml')
        # info
        self.admin = None
        self.dev_token = None
        # log
        self.log_level = None
        # backend
        self.is_lagrange = None
        # nonebot
        self.listen_host = None
        self.listen_port = None
        self.token = None

        # 解析配置文件
        self.read_config()

    def read_config(self):
        with open('./config.toml', 'rb') as f:
            data = tomllib.load(f)
            f.close()
        self.admin = data['info']['admin']
        self.dev_token = data['info']['dev_token']
        self.log_level = data['log']['log_level']
        self.is_lagrange = data['backend']['is_lagrange']
        self.listen_host = data['nonebot']['listen_host']
        self.listen_port = data['nonebot']['listen_port']
        self.token = data['nonebot']['token']


config = Config()
