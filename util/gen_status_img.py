from PIL import Image, ImageDraw, ImageFont
from util.Config import config
import psutil
import cpuinfo


def gen_status(is_connected=True):
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

    # 绘制文字
    ImageDraw.Draw(template).text((96, 22), config.bot_name, font=sy_title, fill='#E6E1E5')
    ImageDraw.Draw(template).text((97, 52), config.bot_version, font=sy_subtitle, fill='#E6E1E5')
    ImageDraw.Draw(template).text((83, 477), cpu_model + '@' + cpu_freq, font=yq_text, fill='#1C1B1F')
    ImageDraw.Draw(template).text((83, 556), f"{round(mem_used, 1)}G / {round(mem_total, 1)}G  |  {round(mem_total, 1)}%内存空闲", font=yq_text, fill='#1C1B1F')
    ImageDraw.Draw(template).text((83, 635), "已持续运行： 1天", font=yq_text, fill='#1C1B1F')

    # 贴网络贴图
    if is_connected:
        net = Image.open('./static/doc/On.png')
        template.paste(net, (393, 744), net)
    else:
        net = Image.open('./static/doc/Off.png')
        template.paste(net, (393, 744), net)
    # 保存文件
    template.save('tem.png')
