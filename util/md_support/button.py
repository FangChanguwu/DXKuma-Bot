import json
from dataclasses import dataclass, fields
from typing import List, Optional


@dataclass
class RenderData:
    label: str = str()
    """
    按钮上的文字
    """
    visited_label: str = str()
    """
    点击后按钮的上文字
    """
    style: int = 0
    """
    按钮样式：0 灰色线框，1 蓝色线框
    """

    def to_dict(self) -> dict[str]:
        _dict: dict[str] = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if value is not None:
                _dict[field.name] = value
        return _dict


@dataclass
class Permission:
    type: int = 2
    """
    0 指定用户可操作，1 仅管理者可操作，2 所有人可操作，3 指定身份组可操作（仅频道可用）
    """
    specify_user_ids: Optional[List[int]] = None
    """
    有权限的用户 id 的列表
    """
    specify_role_ids: Optional[List[int]] = None
    """
    有权限的身份组 id 的列表（仅频道可用）
    """

    def to_dict(self) -> dict[str]:
        _dict: dict[str] = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if value is not None:
                _dict[field.name] = value
        return _dict


@dataclass
class Action:
    type: int
    """
    设置 0 跳转按钮：http 或 小程序 客户端识别 scheme\n
    设置 1 回调按钮：回调后台接口, data 传给后台\n
    设置 2 指令按钮：自动在输入框插入 @bot data
    """
    data: str
    """
    操作相关的数据
    """
    permission: Permission
    """
    权限相关
    """
    reply: Optional[bool] = None
    """
    指令按钮可用，指令是否带引用回复本消息，默认 false。\n
    支持版本 8983
    """
    enter: Optional[bool] = None
    """
    指令按钮可用，点击按钮后直接自动发送 data，默认 false。\n
    支持版本 8983
    """
    anchor: Optional[int] = None
    """
    本字段仅在指令按钮下有效，设置后后会忽略 action.enter 配置。\n
    设置为 1 时 ，点击按钮自动唤起启手Q选图器，其他值暂无效果。\n
    （仅支持手机端版本 8983+ 的单聊场景，桌面端不支持）
    """
    unsupport_tips: str = "这是一个markdown消息喵~"
    """
    客户端不支持本action的时候，弹出的toast文案
    """

    def to_dict(self) -> dict[str]:
        _dict: dict[str] = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if value is not None:
                if isinstance(value, Permission):
                    _dict[field.name] = value.to_dict()
                else:
                    _dict[field.name] = value
        return _dict


@dataclass
class Button:
    render_data: RenderData
    action: Action

    id: Optional[int] = None
    """
    按钮ID：在一个keyboard消息内设置唯一ID
    """

    def to_dict(self) -> dict[str]:
        _dict: dict[str] = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if value is not None:
                if isinstance(value, (RenderData, Action, Permission)):
                    _dict[field.name] = value.to_dict()
                else:
                    _dict[field.name] = value
        return _dict


class Buttons:
    def __init__(self):
        self.buttons: List[Button] = []

    def add(self, button: Button):
        if len(self.buttons) < 5:
            self.buttons.append(button)
        return self

    def to_dict(self):
        return {"buttons": [button.to_dict() for button in self.buttons]}


class KeyBoard:
    def __init__(self):
        self.rows: List[Buttons] = []

    def add(self, buttons: Buttons):
        if len(self.rows) < 5:
            self.rows.append(buttons)
        return self

    def to_message(self):
        return [buttons.to_dict() for buttons in self.rows]


def test():
    button = Button(
        render_data=RenderData(label="点击前", visited_label="点击后"),
        action=Action(type=2, data="/echo 2222", permission=Permission()),
    )

    buttons = Buttons().add(button).add(button)

    keyboard = KeyBoard().add(buttons).add(buttons)

    print(json.dumps(keyboard.to_message(), ensure_ascii=False))
