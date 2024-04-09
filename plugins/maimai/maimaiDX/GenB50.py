import aiohttp
import asyncio
import requests
import json
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw

from .Config import maimai_src, maimai_Frame, songList


# 字体路径
ttf_bold_path = './src/maimai/font/GenSenMaruGothicTW-Bold.ttf'
ttf_heavy_path = './src/maimai/font/GenSenMaruGothicTW-Heavy.ttf'
ttf_regular_path = './src/maimai/font/GenSenMaruGothicTW-Regular.ttf'

async def get_player_data(payload):
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return None, 400
        if resp.status == 403:
            return None, 403
        obj = await resp.json()
        return obj

async def resize_image(image, scale):
    # 计算缩放后的目标尺寸
    width = int(image.width * scale)
    height = int(image.height * scale)

    # 缩放图像
    resized_image = image.resize((width, height))

    return resized_image

async def format_songid(id):
    id_str = str(id)
    if len(id_str) == 5 and id_str.startswith("10"):
        # 五位数且以"10"开头，去掉"10"然后补齐前导零
        return id_str[2:].zfill(6)
    elif len(id_str) == 5 and id_str.startswith("1"):
        # 五位数且以"1"开头，去掉"1"然后补齐前导零
        return id_str[1:].zfill(6)
    else:
        # 直接补齐前导零至六位
        return id_str.zfill(6)
    

async def dxscore_proc(dxscore, sum_dxscore):
    percentage = (dxscore / sum_dxscore) * 100

    if percentage < 85.00:
        return 0, 0
    elif percentage < 90.00:
        return 1, 1
    elif percentage < 93.00:
        return 1, 2
    elif percentage < 95.00:
        return 2, 3
    elif percentage < 97.00:
        return 2 ,4
    else:
        return 3 ,5

async def rank_proc(rank: str):
    if rank == 'clear':
        file = 'music_icon_clear.png'
    elif rank == 's':
        file = 'music_icon_s.png'
    elif rank == 'sp':
        file = 'music_icon_sp.png'
    elif rank == 'ss':
        file = 'music_icon_ss.png'
    elif rank == 'ssp':
        file = 'music_icon_ssp.png'
    elif rank == 'sss':
        file = 'music_icon_sss.png'
    elif rank == 'sssp':
        file = 'music_icon_sssp.png'
    else:
        file = None
    return file

async def combo_proc(combo: int):
    if combo == 0:
        return None
    elif combo == 1:
        return 'music_icon_fc.png'
    elif combo == 2:
        return 'music_icon_fcp.png'
    elif combo == 3:
        return 'music_icon_ap.png'
    elif combo == 4:
        return 'music_icon_app.png'


async def sync_proc(combo: int):
    if combo == 0:
        return None
    elif combo == 1:
        return 'music_icon_fs.png'
    elif combo == 2:
        return 'music_icon_fsp.png'
    elif combo == 3:
        return 'music_icon_fsd.png'
    elif combo == 4:
        return 'music_icon_fsdp.png'

async def computeRa(ra:int):
    if ra < 999:
        return 1
    elif ra < 1999:
        return 2
    elif ra < 3999:
        return 3
    elif ra < 6999:
        return 4
    elif ra < 9999:
        return 5
    elif ra < 11999:
        return 6
    elif ra < 12999:
        return 7
    elif ra < 13999:
        return 8
    elif ra < 14499:
        return 9
    elif ra < 14999:
        return 10
    else:
        return 11

async def music_to_part(achievements:float, ds:float, dxScore:int, fc:str, fs:str, level:str, level_index:int, level_label:str, ra:int, rate:str, song_id:str, title:str, type:str, index:int):
    color = (255,255,255)
    if level_index == 4:
        color = (166,125,199)
    
    # 根据难度 底图
    partbase_path = f'./src/maimai/Static/PartBase_{level_label}.png'
    partbase = Image.open(partbase_path)

    # 歌曲封面
    jacket_path = f'./src/maimai/Jacket/UI_Jacket_{await format_songid(song_id)}.png'
    jacket = Image.open(jacket_path)
    jacket = await resize_image(jacket, 0.56)
    partbase.paste(jacket, (36, 41), jacket)

    # 歌曲分类 DX / SD
    icon_path = f'./src/maimai/Static/music_{type}.png'
    icon = Image.open(icon_path)
    partbase.paste(icon, (40, 230), icon)

    # 歌名
    ttf = ImageFont.truetype(ttf_bold_path, size=40)
    text_position = (305.4, 16.8)
    draw = ImageDraw.Draw(partbase)
    text_bbox = draw.textbbox(text_position, title, font=ttf)
    max_width = 850
    ellipsis = "..."
    
    # 检查文本的宽度是否超过最大宽度
    if text_bbox[2] <= max_width:
        # 文本未超过最大宽度，直接绘制
        draw.text(text_position, title, font=ttf, fill=color)
    else:
        # 文本超过最大宽度，截断并添加省略符号
        truncated_title = title
        while text_bbox[2] > max_width and len(truncated_title) > 0:
            truncated_title = truncated_title[:-1]
            text_bbox = draw.textbbox(text_position, truncated_title + ellipsis, font=ttf)
        draw.text(text_position, truncated_title + ellipsis, font=ttf, fill=color)

    # 达成率
    ttf = ImageFont.truetype(ttf_heavy_path, size=73)
    draw = ImageDraw.Draw(partbase)
    achievements = f'{achievements}'.split('.')
    achievements1 = f'{achievements[0]}.        %'
    achievements2 = str(achievements[1]).ljust(4,'0')
    shadow_color = (0, 0, 0)  # 阴影颜色
    if level_index == 4:
        shadow_color = (188, 163, 209)
    shadow_offset = (2, 4)  # 阴影偏移量
    text_position = (375, 90)
    text_content = f'{achievements1}'
    shadow_position = (text_position[0] + shadow_offset[0], text_position[1] + shadow_offset[1])
    draw.text(shadow_position, text_content, font=ttf, fill=shadow_color)
    draw.text(text_position, text_content, font=ttf, fill=color)
    ttf = ImageFont.truetype(ttf_heavy_path, size=55)
    draw = ImageDraw.Draw(partbase)
    if len(achievements[0])==3:
        text_position = (529, 105)
    else:
        text_position = (488, 105)
    text_content = f'{achievements2}'
    shadow_position = (text_position[0] + shadow_offset[0], text_position[1] + shadow_offset[1])
    draw.text(shadow_position, text_content, font=ttf, fill=shadow_color)
    draw.text(text_position, text_content, font=ttf, fill=color)

    # 一些信息
    ttf = ImageFont.truetype(ttf_bold_path, size=32)
    # best序号
    ImageDraw.Draw(partbase).text((310, 245), f'#{index}', font=ttf,fill=(255,255,255))
    # 乐曲ID
    ImageDraw.Draw(partbase).text((385, 245), f'ID:{song_id}', font=ttf,fill=(28,43,120))
    # 定数和ra
    ImageDraw.Draw(partbase).text((385, 182), f'{ds} -> {ra}', font=ttf,fill=color)
    # dx分数和星星
    songData = next((d for d in songList if d['id'] == str(song_id)), None)
    sum_dxscore = sum(songData['charts'][level_index]['notes']) * 3
    ImageDraw.Draw(partbase).text((580, 245), f'{dxScore}/{sum_dxscore}', font=ttf,fill=(28,43,120))
    star_level, stars = await dxscore_proc(dxScore, sum_dxscore)
    if star_level:
        star_width = 30
        star_path = f'./src/maimai/Static/dxscore_star_{star_level}.png'
        star = Image.open(star_path)
        star = await resize_image(star, 1.3)
        for i in range(stars):
            x_offset = i * star_width
            partbase.paste(star, (x_offset + 570, 178), star)



    # 评价
    rate_path = f'./src/maimai/Static/bud_music_icon_{rate}.png'
    rate = Image.open(rate_path)
    partbase.paste(rate, (735, 100), rate)

    # fc ap
    if fc:
        fc_path = f'./src/maimai/Static/music_icon_{fc}.png'
        fc = Image.open(fc_path)
        fc = await resize_image(fc, 1.1)
        partbase.paste(fc, (850, 233), fc)
    if fs:
        fs_path = f'./src/maimai/Static/music_icon_{fs}.png'
        fs = Image.open(fs_path)
        fs = await resize_image(fs, 1.1)
        partbase.paste(fs, (900, 233), fs)

    partbase = partbase.resize((340,110))
    return partbase


async def draw_best(bests:list):
    index = 0
    # 计算列数
    queue_nums = int(len(bests) / 4) + 1
    # 初始化行列标号
    queue_index = 0
    row_index = 0
    # 初始化坐标
    x = 350
    y = 0
    # 初始化底图
    base = Image.new('RGBA', (1440, queue_nums * 110 + (queue_nums - 1) * 10), (0, 0, 0, 0))
    # 通过循环构建列表并传入数据
    # 遍历列表中的选项
    # 循环生成列
    while queue_index < queue_nums:
        # 设置每行的列数
        if queue_index == 0:
            max_row_index = 3  # 第一行3个
        else:
            max_row_index = 4  # 其他行4个

        # 循环生成行
        while row_index < max_row_index:
            # 根据索引从列表中抽取数据
            song_data = bests[index]
            # 传入数据生成图片
            part = await music_to_part(**song_data, index=index+1)
            # 将图片粘贴到底图上
            base.paste(part, (x, y), part)
            # 增加x坐标，序列自增
            x += 350
            row_index += 1
            index += 1

        # 重置x坐标，增加y坐标
        x = 0
        y += 120
        row_index = 0
        queue_index += 1

    return base

async def generateb50(b35: list, b15: list, nickname: str, plate: int=101, frame: int=200502, rating: int=None, qq: str=None):
    b50 = Image.new('RGBA', (1440, 2560), '#FFFFFF')

    # BG
    # background = Image.open(maimai_src / 'BG.png')
    background = Image.open('./src/maimai/Static/BG.png')
    b50.paste(background)

    # 底板
    # frame_path = maimai_Frame / f'UI_Frame_{frame:06d}.png'
    frame_path = f'./src/maimai/Frame/UI_Frame_{frame:06d}.png'
    frame = Image.open(frame_path)
    frame = await resize_image(frame, 0.95)
    b50.paste(frame, (45, 45))

    # 牌子
    plate_path = f'./src/maimai/Plate/UI_Plate_{plate:06d}.png'
    plate = Image.open(plate_path)
    b50.paste(plate, (60, 60), plate)

    # 头像框
    iconbase_path = f'./src/maimai/Static/icon_base.png'
    iconbase = Image.open(iconbase_path)
    iconbase = await resize_image(iconbase, 0.308)
    b50.paste(iconbase, (60, 46), iconbase)
    # 头像
    icon = requests.get(f"http://q.qlogo.cn/headimg_dl?dst_uin={qq}&spec=640&img_type=png")
    icon = Image.open(BytesIO(icon.content)).resize((88, 88))
    # icon_path = f'./src/maimai/UI_Icon_000101.png'
    # icon = Image.open(icon_path)
    b50.paste(icon, (73, 75))

    # 姓名框
    namebase_path = f'./src/maimai/Static/namebase.png'
    namebase = Image.open(namebase_path)
    b50.paste(namebase, (0, 0), namebase)

    # rating推荐
    # ratingbase_path = f'./src/maimai/Static/rating_base.png'
    # ratingbase = Image.open(ratingbase_path)
    # b50.paste(ratingbase, (0, 0), ratingbase)

    # rating框
    ratingbar = await computeRa(rating)
    ratingbar_path = f'./src/maimai/Rating/UI_CMN_DXRating_{ratingbar:02d}.png'
    ratingbar = Image.open(ratingbar_path)
    ratingbar = await resize_image(ratingbar, 0.26)
    b50.paste(ratingbar, (175, 70), ratingbar)

    # rating数字
    rating_str = str(rating).zfill(5)
    num1 = Image.open(f'./src/maimai/number/{rating_str[0]}.png').resize((18, 21))
    num2 = Image.open(f'./src/maimai/number/{rating_str[1]}.png').resize((18, 21))
    num3 = Image.open(f'./src/maimai/number/{rating_str[2]}.png').resize((18, 21))
    num4 = Image.open(f'./src/maimai/number/{rating_str[3]}.png').resize((18, 21))
    num5 = Image.open(f'./src/maimai/number/{rating_str[4]}.png').resize((18, 21))

    b50.paste(num1, (253, 77), num1)
    b50.paste(num2, (267, 77), num2)
    b50.paste(num3, (280, 77), num3)
    b50.paste(num4, (294, 77), num4)
    b50.paste(num5, (308, 77), num5)

    # 名字
    ttf = ImageFont.truetype(ttf_regular_path, size=28)
    ImageDraw.Draw(b50).text((182,113), nickname, font=ttf, fill=(0,0,0))

    # rating合计
    ttf = ImageFont.truetype(ttf_bold_path, size=14)
    b35_ra = sum(item['ra'] for item in b35)
    b15_ra = sum(item['ra'] for item in b15)
    ImageDraw.Draw(b50).text((208,148), f'旧版本: {b35_ra} + 新版本: {b15_ra} = {rating}', font=ttf, fill=(255,255,255))
    
    # b50
    b35 = await draw_best(b35)
    b15 = await draw_best(b15)
    b50.paste(b35, (25,795), b35)
    b50.paste(b15, (25,1985), b15)

    
    img_byte_arr = BytesIO()
    b50.save(img_byte_arr, format='PNG', quality=90)
    img_byte_arr.seek(0)
    img_bytes = img_byte_arr.getvalue()

    return img_bytes

async def main():
    with open('data.json', 'r') as f:
        data = json.load(f)

    b35 = data['charts']['sd']
    b15 = data['charts']['dx']
    nickname = data['nickname']
    # plate = data['plate']
    plate = 101
    rating = data['rating']
    img = await generateb50(b35=b35, b15=b15, nickname=nickname, plate=plate, rating=rating, qq='1716530046')
    with open("b50.png", "wb") as file:
        file.write(img)
    print('ok!')
    # with open('data.json', 'r') as f:
    #     data = json.load(f)
    # b35 = data['charts']['sd']
    # img = await draw_best(b35)
    # with open("b50_test.png", "wb") as file:
    #     file.write(img)
    # print('ok!')

asyncio.run(main())


