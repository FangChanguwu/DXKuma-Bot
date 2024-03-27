# 这个类用于实现权限的传入和判断
import os.path


class Permission:
    """
    用于实现权限的传入和判断的类
    """

    def __init__(self):
        self.ops = []
        self.groups_enabled = []
        self.groups_unlimited = []
        # 检测对应的权限设置文件是否存在，不在则生成
        if not os.path.exists("ops.txt"):
            with open('ops.txt', 'w+') as f:
                f.write("")
                f.close()
        if not os.path.exists("groups_enabled.txt"):
            with open('groups_enabled.txt', 'w+') as f:
                f.write("")
                f.close()
        if not os.path.exists("groups_unlimited.txt"):
            with open('groups_unlimited.txt', 'w+') as f:
                f.write("")
                f.close()
        # 初始化文件中的权限
        self.get_permissions()

    @staticmethod
    def _read_permissions(file_name):
        with open(file_name, 'r') as f:
            acc_list = f.readlines()
            rt_list = []
            for acc in acc_list:
                try:
                    acc = int(acc)
                    rt_list.append(acc)
                except ValueError as e:
                    continue
            f.close()
        return rt_list

    def get_permissions(self):
        self.ops = self._read_permissions('ops.txt')
        self.groups_enabled = self._read_permissions('groups_enabled.txt')
        self.groups_unlimited = self._read_permissions('groups_unlimited.txt')

    def is_op(self, event_id):
        if event_id in self.ops:
            return True
        else:
            return False

    def is_group_enabled(self, group_id):
        if not self.groups_enabled:
            return True
        elif group_id in self.groups_enabled:
            return True
        else:
            return False

    def is_group_unlimited(self, group_id):
        if group_id in self.groups_unlimited:
            return True
        else:
            return False

    def get_ops(self):
        return self.ops

    def get_groups_enabled(self):
        return self.groups_enabled

    def get_groups_unlimited(self):
        return self.groups_unlimited

    def add_op(self, user_id):
        if user_id not in self.ops:
            self.ops.append(user_id)
            with open('ops.txt', 'a') as f:
                f.write(f"\n{user_id}")
                f.close()
            return True
        else:
            return False

    def add_group_enabled(self, group_id):
        if group_id not in self.groups_enabled:
            self.groups_enabled.append(group_id)
            with open('groups_enabled.txt', 'a') as f:
                f.write(f"\n{group_id}")
                f.close()
            return True
        else:
            return False

    def add_group_unlimited(self, group_id):
        if group_id not in self.groups_unlimited:
            self.groups_unlimited.append(group_id)
            with open('groups_unlimited.txt', 'a') as f:
                f.write(f"\n{group_id}")
                f.close()
            return True
        else:
            return False


permisson = Permission()
