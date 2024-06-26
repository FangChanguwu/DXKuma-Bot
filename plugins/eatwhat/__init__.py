import os
from pathlib import Path
from random import SystemRandom

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageSegment

random = SystemRandom()

sawhat = on_regex(r"^萨吃?什么$")


@sawhat.handle()
async def _():
    path = "./src/saliya"
    files = os.listdir(path)
    file = random.choice(files)
    name, price = file.split("-")
    price = price.replace(".jpeg", "")
    pic_path = os.path.join(path, file)
    msg = (
        MessageSegment.text(f"迪拉熊推荐你试一下：\n{name}\n{price}元"),
        MessageSegment.image(Path(pic_path)),
        MessageSegment.text("*价格以广州地区为准"),
    )
    await sawhat.finish(msg)
