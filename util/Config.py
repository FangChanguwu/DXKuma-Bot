import os.path
import shutil
import tomllib


class Config:
    def __init__(self):
        if not os.path.exists('./config.toml'):
            shutil.copyfile('./static/config_example.toml', './config.toml')
        # info
        self.bot_name = None
        self.bot_version = None
        self.comm_prefix = None
        self.admin = None
        # log
        self.log_level = None
        # backend
        self.is_lagrange = None
        # nonebot
        self.listen_host = None
        self.listen_port = None
        self.token = None
        # database
        self.db_type = None
        self.db_host = None
        self.db_port = None
        self.db_username = None
        self.db_password = None

        # 解析配置文件
        self.read_config()

    def read_config(self):
        with open('./config.toml', 'rb') as f:
            data = tomllib.load(f)
            f.close()
        self.bot_name = data['info']['bot_name']
        self.bot_version = data['info']['bot_version']
        self.comm_prefix = data['info']['comm_prefix']
        self.admin = data['info']['admin']
        self.log_level = data['log']['log_level']
        self.is_lagrange = data['backend']['is_lagrange']
        self.listen_host = data['nonebot']['listen_host']
        self.listen_port = data['nonebot']['listen_port']
        self.token = data['nonebot']['token']
        self.db_type = data['database']['db_type']
        self.db_host = data['database']['db_host']
        self.db_port = data['database']['db_port']
        self.db_username = data['database']['db_username']
        self.db_password = data['database']['db_password']


config = Config()
