from sqlalchemy import Column, Integer, String
from base.Base import Base


# 定义qq用户表
class User(Base):
    __tablename__ = 'qquser'

    # 定义表字段
    uid = Column(String, primary_key=True)  # 存储用户的唯一id，id应为一串基于qq号和初次注册日期混淆的32位md5
    point = Column(Integer)
    sign_date = Column(Integer)
    qqid = Column(Integer)
    kookid = Column(Integer)
    wechatid = Column(String)
    tgid = Column(Integer)
    discordid = Column(Integer)
    items = Column(String)  # 存储用户的物品数据，应该存储json字符串
