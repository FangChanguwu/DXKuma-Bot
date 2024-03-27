import datetime
import io
import time
import matplotlib.pyplot as plt

from PIL import Image, ImageDraw, ImageFont
from util.Config import config
from util.DataPasser import datapasser
from util.Logger import logger
import psutil
import cpuinfo


async def gen_status(is_connected=True):
    logger.debug("正在调用status图片生成模板...")
    # 打开模板
    template = Image.open('./static/templates/status.png')
    # 设置字体
    gensen = './static/fonts/GenSenMaruGothicTW-Bold.ttf'
    siyuan = './static/fonts/SourceHanSansSC-Heavy.otf'

    sy_title = ImageFont.truetype(siyuan, 20)
    sy_subtitle = ImageFont.truetype(siyuan, 14)
    yq_text = ImageFont.truetype(gensen, 14)

    # 获取运行状态
    cpu_info = cpuinfo.get_cpu_info()
    cpu_model = cpu_info['brand_raw']  # CPU型号
    cpu_freq = cpu_info['hz_actual_friendly']  # CPU主频

    mem_info = psutil.virtual_memory()
    mem_total = mem_info.total / (1024 ** 3)  # 总内存
    mem_used = mem_info.used / (1024 ** 3)  # 已使用内存
    mem_percent = mem_info.percent  # 内存使用比例

    run_time = datapasser.get_run_time()
    run_dt = datetime.timedelta(seconds=run_time)
    day = run_dt.days
    hour = (run_dt.seconds // 3600) % 24
    minute = (run_dt.seconds // 60) % 60
    second = run_dt.seconds % 60

    # 绘制文字
    ImageDraw.Draw(template).text((96, 22), config.bot_name, font=sy_title, fill='#E6E1E5')
    ImageDraw.Draw(template).text((97, 52), config.bot_version, font=sy_subtitle, fill='#E6E1E5')
    ImageDraw.Draw(template).text((83, 477), cpu_model + '@' + cpu_freq, font=yq_text, fill='#1C1B1F')
    ImageDraw.Draw(template).text((83, 556), f"{round(mem_used, 1)}G / {round(mem_total, 1)}G  |  {round(mem_percent, 1)}%内存已使用", font=yq_text, fill='#1C1B1F')
    ImageDraw.Draw(template).text((83, 635), f"已持续运行： {day}天{hour}时{minute}分{second}秒", font=yq_text, fill='#1C1B1F')

    # 贴网络贴图
    if is_connected:
        net = Image.open('./static/doc/On.png')
        template.paste(net, (393, 744), net)
    else:
        net = Image.open('./static/doc/Off.png')
        template.paste(net, (393, 744), net)

    # 创建一个新的图表，并设置其大小为400x200
    plt.figure(figsize=(460 / 80, 230 / 80), dpi=80)

    # 设置图表的背景颜色为透明
    plt.gca().patch.set_facecolor('none')

    # 设置图表的框线颜色为白色
    plt.gca().spines['bottom'].set_color('none')
    plt.gca().spines['top'].set_color('none')
    plt.gca().spines['right'].set_color('none')
    plt.gca().spines['left'].set_color('white')

    # 获取当前时间，并四舍五入到最近的10分钟
    now = datetime.datetime.now()
    minutes = (now.minute // 10) * 10
    now = now.replace(minute=minutes, second=0, microsecond=0)

    # 创建一个表示时间的列表，每个元素表示过去的10分钟
    time = [(now - datetime.timedelta(minutes=i * 10)).strftime('%H:%M') for i in range(12)][::-1]

    # CPU使用率
    cpu_usage = datapasser.get_usage()

    # 使用plot函数绘制折线图，其中x轴为时间，y轴为CPU使用率
    plt.plot(time, cpu_usage)

    # 移除横坐标轴上的所有文本
    plt.xticks([])

    # 设置刻度线和刻度标签的颜色为白色
    plt.tick_params(colors='white')

    # 创建一个BytesIO对象
    buf = io.BytesIO()

    # 保存图表到buf
    plt.savefig(buf, format='png', transparent=True)

    # 移动到缓冲区的开始位置
    buf.seek(0)

    # 使用Pillow从buf中读取图像
    img = Image.open(buf).convert('RGBA')

    # 将图表塞到模板里面
    template.paste(img, (0, 141), img)
    logger.debug("status图片模板生成结束")

    # 传出字节流
    img_byte_arr = io.BytesIO()
    template.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()

    # 保存文件
    return img_bytes
