# 用于和数据库进行沟通，实现数据存储和拉取的类
# 使用sqlalchemy
import os.path
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from base.Base import Base
from base.QQUser import User
from util.Config import config


class Database:
    def __init__(self):
        if not os.path.exists('./data/'):
            os.mkdir('./data')
        self.session = None
        self.connect()
        pass

    def connect(self):
        engine = create_engine('sqlite:///data/break.db', echo=True)
        # 创建表结构
        Base.metadata.create_all(engine, checkfirst=True)

        # 实例化会话
        self.session = sessionmaker(bind=engine)()

    def add_test(self):
        user = User(uid='asdasdasd', qq=2913844577)
        self.session.add(user)

        self.session.commit()


db = Database()
