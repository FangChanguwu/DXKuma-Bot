from nonebot import on_regex


xc = on_regex(r'(香草|想草)(迪拉熊|滴蜡熊|dlx)')

@xc.handle()
async def _():
    await xc.finish('变态！！！')