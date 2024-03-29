# 这个函数用于实现和管理权限系统
import json
import os


class PermissonManager:
    """
    权限组管理类
    """
    def __init__(self):
        # 初始化部分值
        self.default_user_perms = ['user', 'op', 'admin']
        self.default_group_perms = ['default', 'unlimited', 'controler']
        self.user_pg = {}
        self.group_pg = {}
        # 存储权限字典
        self.perms = {}
        # 读取权限文件
        self.read_perms()

    def init_perms(self):
        # 初始化列表
        user_pg = self.default_user_perms
        group_pg = self.default_group_perms
        user_pgs = []
        group_pgs = []
        # 创建字典中的键值
        for user_perm in user_pg:
            permer = {
                "pg_name": user_perm,
                "owner": []
            }
            user_pgs.append(permer)
        for group_perm in group_pg:
            permer = {
                "pg_name": group_perm,
                "owner": []
            }
            group_pgs.append(permer)
        perms = {
            'Users': user_pgs,
            'Groups': group_pgs
        }
        # 存入权限
        self.perms = perms
        self.save_perms()

    def read_perms(self):
        if not os.path.exists('permissions.json'):
            self.init_perms()
        with open('permissions.json', 'r', encoding='utf-8') as j:
            # 读取并存储权限
            perms = json.loads(j.read())
            self.perms = perms
            j.close()

    def save_perms(self):
        # 从内存中获取权限
        perms = self.perms
        # 存储权限到静态文件
        with open('permissions.json', 'w+', encoding='utf-8') as f:
            f.write(
                json.dumps(perms, indent=4, ensure_ascii=False)
            )
            f.close()

    def add_user_pg(self, perm_name: str):
        """
        增加用户权限组，返回1为已存在对应名称的权限组，0为操作成功
        :param perm_name: str
        :return: int
        """
        perm_name = str(perm_name)
        for pg in self.perms['Users']:
            if pg["pg_name"] == perm_name:
                return 1
        new_perm = {
            "pg_name": perm_name,
            "owner": []
        }
        self.perms['Users'].append(new_perm)
        self.save_perms()
        return 0

    def add_group_pg(self, perm_name: str):
        """
        增加群组权限组，返回1为已存在对应名称的权限组，0为操作成功
        :param perm_name: str
        :return: int
        """
        perm_name = str(perm_name)
        for pg in self.perms['Groups']:
            if pg["pg_name"] == perm_name:
                return 1
        new_perm = {
            "pg_name": perm_name,
            "owner": []
        }
        self.perms['Groups'].append(new_perm)
        self.save_perms()
        return 0

    def add_user(self, perm: str, uid: int):
        """
        向指定用户权限组中添加用户uid
        :param perm: str
        :param uid: int
        :return: int：0为成功，1为user（无需添加），2为未找到对应权限组，3为用户已存在于对应权限组
        """
        perm = str(perm)
        if perm == 'user':
            return 1
        for pg in self.perms['Users']:
            if pg['pg_name'] == perm:
                if uid in pg['owner']:
                    return 3
                pg['owner'].append(uid)
                self.save_perms()
                return 0
        return 2

    def add_group(self, perm: str, uid: int):
        """
        向指定群组权限组中添加群组uid
        :param perm: str
        :param uid: int
        :return: int：0为成功，1为user（无需添加），2为未找到对应权限组，3为用户已存在于对应权限组
        """
        perm = str(perm)
        if perm == 'default':
            return 1
        for pg in self.perms['Groups']:
            if pg['pg_name'] == perm:
                if uid in pg['owner']:
                    return 3
                pg['owner'].append(uid)
                self.save_perms()
                return 0
        return 2

    def is_user_perm(self, perm: str, uid: int):
        """
        检测用户是否存在于指定权限组
        :param perm: str 权限组名称
        :param uid: int 用户id
        :return: int 0为存在，1为不存在，2为权限组不存在
        """
        # 检测对应权限组是否存在
        perm = str(perm)
        for pg in self.perms["Users"]:
            if pg["pg_name"] == perm:
                if uid in pg["owner"]:
                    return 0
                else:
                    return 1
        return 2

    def is_group_perm(self, perm: str, uid: int):
        """
        检测群组是否存在于指定权限组
        :param perm: str 权限组名称
        :param uid: int 用户id
        :return: int 0为存在，1为不存在，2为权限组不存在
        """
        # 检测对应权限组是否存在
        perm = str(perm)
        for pg in self.perms["Groups"]:
            if pg["pg_name"] == perm:
                if uid in pg["owner"]:
                    return 0
                else:
                    return 1
        return 2

    def get_user_perm(self, uid) -> list:
        """
        检测用户目前所在的权限组
        :param uid:
        :return:
        """
        rt_list = ['user']
        for pg in self.perms["Users"]:
            if uid in pg['owner']:
                rt_list.append(pg["pg_name"])
        return rt_list

    def get_group_perm(self, uid) -> list:
        """
        检测用户目前所在的权限组
        :param uid:
        :return:
        """
        rt_list = ['default']
        for pg in self.perms["Groups"]:
            if uid in pg['owner']:
                rt_list.append(pg["pg_name"])
        return rt_list

    def is_op(self, uid: int):
        perms = self.get_user_perm(uid)
        if "op" in perms or "admin" in perms:
            return True
        else:
            return False

    def is_admin(self, uid: int):
        perms = self.get_user_perm(uid)
        if "admin" in perms:
            return True
        else:
            return False

    def is_unlimited(self, uid: int):
        perms = self.get_group_perm(uid)
        if "unlimited" in perms or "controler" in perms:
            return True
        else:
            return False

    def is_controler(self, uid: int):
        perms = self.get_group_perm(uid)
        if "controler" in perms:
            return True
        else:
            return False


pm = PermissonManager()
