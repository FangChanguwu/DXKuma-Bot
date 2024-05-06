import json

from nonebot.adapters.onebot.v11 import Bot

from .button import KeyBoard


async def send_markdown(
        bot: Bot, group_id: int, markdown: str, keyboard: KeyBoard = None
):
    messages = [
        {
            "type": "markdown",
            "data": {
                "content": json.dumps(
                    {"content": markdown},
                    ensure_ascii=False,
                ),
            },
        },
    ]
    if keyboard:
        messages.append(
            {
                "type": "keyboard",
                "data": {"content": {"rows": keyboard.to_message()}},
            },
        )
    await bot.call_api(
        "send_group_msg",
        group_id=group_id,
        message=messages,
    )
