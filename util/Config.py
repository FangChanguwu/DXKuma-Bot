import os
import shutil

import toml


class Config:
    def __init__(self):
        if not os.path.exists("./config.toml"):
            shutil.copyfile("./config_example.toml", "./config.toml")
        # info
        self.version = None
        # log
        self.log_level = None
        # nonebot
        self.listen_host = None
        self.listen_port = None
        self.token = None
        # group
        self.dev_group = None
        self.special_group = None
        # nsfw
        self.allowed_accounts = None
        # diving_fish
        self.df_token = None

        # 解析配置文件
        self.read_config()

    def read_config(self):
        data = toml.load("./config.toml")
        self.version = data["info"]["version"]
        self.log_level = data["log"]["log_level"]
        self.listen_host = data["nonebot"]["listen_host"]
        self.listen_port = data["nonebot"]["listen_port"]
        self.token = data["nonebot"]["token"]
        self.dev_group = data["group"]["dev"]
        self.special_group = data["group"]["special"]
        self.allowed_accounts = data["nsfw"]["allowed_accounts"]
        self.df_token = data["diving_fish"]["token"]


config = Config()
