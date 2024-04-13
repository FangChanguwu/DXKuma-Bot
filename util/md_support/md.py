import json

from nonebot.adapters.onebot.v11 import Bot
from nonebot.log import logger

from .button import KeyBoard


async def send_markdown(
        bot: Bot, group_id: int, markdown: str, keyboard: KeyBoard = None
):
    messages = [
        {
            "type": "node",
            "data": {
                "name": "小助手",
                "uin": "100000",
                "content": [
                    {
                        "type": "markdown",
                        "data": {
                            "content": json.dumps(
                                {"content": markdown},
                                ensure_ascii=False,
                            ),
                        },
                    },
                ],
            },
        }
    ]
    if keyboard:
        messages[0]["data"]["content"].append(
            {
                "type": "keyboard",
                "data": {"content": {"rows": keyboard.to_message()}},
            },
        )

    res_id = await bot.call_api("send_forward_msg", messages=messages)
    logger.info(f"获取res_id:{res_id}")
    await bot.call_api(
        "send_group_msg",
        group_id=group_id,
        message=[{"type": "longmsg", "data": {"id": res_id}}],
    )
