from io import BytesIO
import os

from PIL import Image, ImageDraw, ImageFont

from util.DivingFish import get_player_data, get_player_record
from .Config import (
    font_path,
    maimai_Jacket,
    maimai_Static,
    maimai_Version,
    maimai_Plus,
    maimai_MusicType,
    maimai_Rank,
)

ttf_bold_path = font_path / "SourceHanSans-Bold.ttc"
ttf_heavy_path = font_path / "SourceHanSans-Heavy.ttc"
ttf_regular_path = font_path / "SourceHanSans-Regular.ttc"


def resize_image(image, scale):
    # 计算缩放后的目标尺寸
    width = int(image.width * scale)
    height = int(image.height * scale)

    # 缩放图像
    resized_image = image.resize((width, height))

    return resized_image


def format_songid(id):
    id_str = str(id)
    if len(id_str) == 5 and id_str.startswith("10"):
        # 五位数且以"10"开头,去掉"10"然后补齐前导零
        return id_str[2:].zfill(6)
    if len(id_str) == 5 and id_str.startswith("1"):
        # 五位数且以"1"开头,去掉"1"然后补齐前导零
        return id_str[1:].zfill(6)
    # 直接补齐前导零至六位
    return id_str.zfill(6)


async def music_info(song_data, qq: str):
    # 底图
    bg = Image.open("./src/maimai/musicinfo_bg.png")
    drawtext = ImageDraw.Draw(bg)

    # 初始化用户数据
    data, status = await get_player_data(qq)
    if status == 200:
        b50_status = True
        b35 = data["charts"]["sd"]
        b15 = data["charts"]["dx"]
    else:
        b50_status = False

    # 歌曲封面
    cover_id = format_songid(song_data["id"])
    cover_path = maimai_Jacket / f"UI_Jacket_{cover_id}.png"
    if not os.path.exists(cover_path):
        cover_path = maimai_Jacket / "UI_Jacket_000000.png"
    cover = Image.open(cover_path).resize((295, 295))
    bg.paste(cover, (204, 440), cover)

    # 绘制标题
    song_title = song_data["title"]
    ttf = ImageFont.truetype(ttf_bold_path, size=40)
    title_position = (545, 626)
    text_bbox = drawtext.textbbox(title_position, song_title, font=ttf)
    max_width = 1110
    ellipsis = "..."
    # 检查文本的宽度是否超过最大宽度
    if text_bbox[2] <= max_width:
        # 文本未超过最大宽度,直接绘制
        drawtext.text(title_position, song_title, font=ttf, fill=(0, 0, 0))
    else:
        # 文本超过最大宽度,截断并添加省略符号
        truncated_title = song_title
        while text_bbox[2] > max_width and len(truncated_title) > 0:
            truncated_title = truncated_title[:-1]
            text_bbox = drawtext.textbbox(
                title_position, truncated_title + ellipsis, font=ttf
            )
        drawtext.text(
            title_position, truncated_title + ellipsis, font=ttf, fill=(0, 0, 0)
        )

    # 绘制曲师
    song_artist = song_data["basic_info"]["artist"]
    ttf = ImageFont.truetype(ttf_regular_path, size=30)
    artist_position = (545, 694)
    text_bbox = drawtext.textbbox(artist_position, song_artist, font=ttf)
    max_width = 1110
    ellipsis = "..."
    # 检查文本的宽度是否超过最大宽度
    if text_bbox[2] <= max_width:
        # 文本未超过最大宽度,直接绘制
        drawtext.text(artist_position, song_artist, font=ttf, fill=(0, 0, 0))
    else:
        # 文本超过最大宽度,截断并添加省略符号
        truncated_title = song_artist
        while text_bbox[2] > max_width and len(truncated_title) > 0:
            truncated_title = truncated_title[:-1]
            text_bbox = drawtext.textbbox(
                artist_position, truncated_title + ellipsis, font=ttf
            )
        drawtext.text(
            artist_position, truncated_title + ellipsis, font=ttf, fill=(0, 0, 0)
        )

    # id
    ttf = ImageFont.truetype(ttf_bold_path, size=28)
    id_position = (239, 872)
    drawtext.text(
        id_position, song_data["id"], anchor="mm", font=ttf, fill=(28, 43, 110)
    )
    # bpm
    song_bpm = str(song_data["basic_info"]["bpm"])
    bpm_position = (341, 872)
    drawtext.text(bpm_position, song_bpm, anchor="mm", font=ttf, fill=(28, 43, 110))
    # 分类
    song_genre = song_data["basic_info"]["genre"]
    genre_position = (544, 872)
    drawtext.text(genre_position, song_genre, anchor="mm", font=ttf, fill=(28, 43, 110))
    # 谱面类型
    song_type = song_data["type"]
    type_path = maimai_MusicType / f"{song_type}.png"
    type = Image.open(type_path)
    type = resize_image(type, 0.9)
    bg.paste(type, (708, 858), type)
    # version
    song_ver = song_data["basic_info"]["from"]
    song_ver = Image.open(maimai_Version / f"{song_ver}.png")
    song_ver = resize_image(song_ver, 0.8)
    bg.paste(song_ver, (860, 768), song_ver)

    # 等级
    ttf = ImageFont.truetype(ttf_heavy_path, size=50)
    songs_level = song_data["level"]
    level_color = [
        (14, 117, 54),
        (214, 148, 19),
        (192, 33, 56),
        (103, 20, 141),
        (186, 126, 232),
    ]
    level_x = 395
    level_y = 1046
    for i, song_level in enumerate(songs_level):
        if "+" in song_level:
            song_level = song_level.replace("+", "")
            level_label = ["Basic", "Advanced", "Expert", "Master", "Re:MASTER"][i]
            plus_path = maimai_Plus / f"{level_label}.png"
            plus_icon = Image.open(plus_path)
            bg.paste(plus_icon, (level_x + 33, level_y - 70), plus_icon)
        level_position = (level_x, level_y)
        drawtext.text(
            level_position, song_level, anchor="mm", font=ttf, fill=level_color[i]
        )
        level_x += 170

    # 定数->ra
    ttf = ImageFont.truetype(ttf_bold_path, size=18)
    songs_ds = song_data["ds"]
    is_new = song_data["basic_info"]["is_new"]
    song_ra = [int(value * 1.005 * 22.4) for value in songs_ds]  # 该ds鸟加的ra值
    ds_x = 395
    ds_y = 1124
    basic_ra = 0
    if b50_status:
        if b35:
            basic_ra = b35[-1]["ra"]
        if is_new:
            if b15:
                basic_ra = b15[-1]["ra"]
    for i, song_ds in enumerate(songs_ds):
        ds_position = (ds_x, ds_y)
        if b50_status and basic_ra > 0:
            drawtext.text(
                ds_position,
                f"{song_ds} -> +{song_ra[i] - basic_ra if song_ra[i] - basic_ra >= 0 else 0}",
                anchor="mm",
                font=ttf,
                fill=(28, 43, 110),
            )
        else:
            drawtext.text(
                ds_position,
                f"{song_ds} -> +{song_ra[i]}",
                anchor="mm",
                font=ttf,
                fill=(28, 43, 110),
            )
        ds_x += 170

    # 物量
    ttf = ImageFont.truetype(ttf_bold_path, size=40)
    song_charts = song_data["charts"]
    notes_x = 395
    for chart in song_charts:
        notes_y = 1200
        notes = chart["notes"]
        if song_type == "SD":
            notes.insert(3, 0)
        total_num = sum(notes)
        dx_num = total_num * 3
        notes.insert(0, total_num)
        notes.append(dx_num)
        for i, note in enumerate(notes):
            notes_position = (notes_x, notes_y)
            drawtext.text(
                notes_position, str(note), anchor="mm", font=ttf, fill=(28, 43, 110)
            )
            notes_y += 80
        notes_x += 170

    # 谱师
    ttf = ImageFont.truetype(ttf_bold_path, size=20)
    song_charters = [item["charter"] for item in song_charts[2:]]
    charter_x = 448
    charter_y = 1792
    charter_color = [(192, 33, 56), (103, 20, 141), (186, 126, 232)]
    for i, song_charter in enumerate(song_charters):
        charter_position = (charter_x, charter_y)
        drawtext.text(
            charter_position, song_charter, anchor="mm", font=ttf, fill=charter_color[i]
        )
        charter_x += 292

    img_byte_arr = BytesIO()
    bg.save(img_byte_arr, format="PNG", quality=90)
    img_byte_arr.seek(0)
    img_bytes = img_byte_arr.getvalue()

    return img_bytes


async def play_info(song_data, qq: str):
    data, status = await get_player_record(qq, song_data["id"])
    if status == 400:
        msg = "迪拉熊未找到用户信息，可能是没有绑定水鱼\n水鱼网址：https://www.diving-fish.com/maimaidx/prober/"
        return msg
    if status == 200:
        if not data:
            msg = "迪拉熊发现你未游玩过该乐曲"
            return msg
        records = data[song_data["id"]]
    else:
        msg = "迪拉熊发现你未游玩过该乐曲"
        return msg

    playdata = sorted(records, key=lambda x: x["level_index"])
    # 底图
    bg = Image.open("./src/maimai/playinfo_bg.png")
    drawtext = ImageDraw.Draw(bg)

    # 歌曲封面
    cover_id = format_songid(song_data["id"])
    cover = Image.open(maimai_Jacket / f"UI_Jacket_{cover_id}.png").resize((295, 295))
    bg.paste(cover, (204, 440), cover)

    # 绘制标题
    song_title = song_data["title"]
    ttf = ImageFont.truetype(ttf_bold_path, size=40)
    title_position = (545, 626)
    text_bbox = drawtext.textbbox(title_position, song_title, font=ttf)
    max_width = 1110
    ellipsis = "..."
    # 检查文本的宽度是否超过最大宽度
    if text_bbox[2] <= max_width:
        # 文本未超过最大宽度,直接绘制
        drawtext.text(title_position, song_title, font=ttf, fill=(0, 0, 0))
    else:
        # 文本超过最大宽度,截断并添加省略符号
        truncated_title = song_title
        while text_bbox[2] > max_width and len(truncated_title) > 0:
            truncated_title = truncated_title[:-1]
            text_bbox = drawtext.textbbox(
                title_position, truncated_title + ellipsis, font=ttf
            )
        drawtext.text(
            title_position, truncated_title + ellipsis, font=ttf, fill=(0, 0, 0)
        )

    # 绘制曲师
    song_artist = song_data["basic_info"]["artist"]
    ttf = ImageFont.truetype(ttf_regular_path, size=30)
    artist_position = (545, 694)
    text_bbox = drawtext.textbbox(artist_position, song_artist, font=ttf)
    max_width = 1110
    ellipsis = "..."
    # 检查文本的宽度是否超过最大宽度
    if text_bbox[2] <= max_width:
        # 文本未超过最大宽度,直接绘制
        drawtext.text(artist_position, song_artist, font=ttf, fill=(0, 0, 0))
    else:
        # 文本超过最大宽度,截断并添加省略符号
        truncated_title = song_artist
        while text_bbox[2] > max_width and len(truncated_title) > 0:
            truncated_title = truncated_title[:-1]
            text_bbox = drawtext.textbbox(
                artist_position, truncated_title + ellipsis, font=ttf
            )
        drawtext.text(
            artist_position, truncated_title + ellipsis, font=ttf, fill=(0, 0, 0)
        )

    # id
    ttf = ImageFont.truetype(ttf_bold_path, size=28)
    id_position = (239, 872)
    drawtext.text(
        id_position, song_data["id"], anchor="mm", font=ttf, fill=(28, 43, 110)
    )
    # bpm
    song_bpm = str(song_data["basic_info"]["bpm"])
    bpm_position = (341, 872)
    drawtext.text(bpm_position, song_bpm, anchor="mm", font=ttf, fill=(28, 43, 110))
    # 分类
    song_genre = song_data["basic_info"]["genre"]
    genre_position = (544, 872)
    drawtext.text(genre_position, song_genre, anchor="mm", font=ttf, fill=(28, 43, 110))
    # 谱面类型
    song_type = song_data["type"]
    type_path = maimai_MusicType / f"{song_type}.png"
    type = Image.open(type_path)
    type = resize_image(type, 0.9)
    bg.paste(type, (708, 858), type)
    # version
    song_ver = song_data["basic_info"]["from"]
    song_ver = Image.open(maimai_Version / f"{song_ver}.png")
    song_ver = resize_image(song_ver, 0.8)
    bg.paste(song_ver, (860, 760), song_ver)

    # 绘制成绩
    score_color = [
        (14, 117, 54),
        (214, 148, 19),
        (192, 33, 56),
        (103, 20, 141),
        (186, 126, 232),
    ]
    for _, play_datum in enumerate(playdata):
        level_x = 229
        level_y = 1100
        achieve_x = 471
        achieve_y = 1102
        rate_x = 646
        rate_y = 1074
        fc_x = 809
        fc_y = 1060
        fs_x = 895
        fs_y = 1060
        dsra_x = 1047
        dsra_y = 1102
        plus_x = 262
        plus_y = 1030
        score = play_datum
        achieve = str(score["achievements"])
        if "." not in achieve:
            achieve = f"{achieve}.0"
        achieve1, achieve2 = achieve.split(".")
        achieve2 = (achieve2.ljust(4, "0"))[:4]
        achieve = f"{achieve1}.{achieve2}%"
        ds = str(score["ds"])
        fc = score["fc"]
        fs = score["fs"]
        level = str(score["level"])
        level_index = score["level_index"]
        level_label = score["level_label"]
        ra = str(score["ra"])
        rate = score["rate"]
        color = score_color[level_index]

        level_y += level_index * 150
        achieve_y += level_index * 150
        rate_y += level_index * 150
        fc_y += level_index * 150
        fs_y += level_index * 150
        dsra_y += level_index * 150
        plus_y += level_index * 150

        # 等级
        if "+" in level:
            level = level.replace("+", "")
            plus_path = maimai_Plus / f"{level_label}.png"
            plus_icon = Image.open(plus_path)
            bg.paste(plus_icon, (plus_x, plus_y), plus_icon)
        ttf = ImageFont.truetype(ttf_heavy_path, size=50)
        drawtext.text((level_x, level_y), level, font=ttf, fill=color, anchor="mm")

        # 达成率
        ttf = ImageFont.truetype(ttf_bold_path, size=43)
        drawtext.text(
            (achieve_x, achieve_y), achieve, font=ttf, fill=color, anchor="mm"
        )

        # 评价
        rate_path = maimai_Rank / f"{rate}.png"
        rate = Image.open(rate_path)
        rate = resize_image(rate, 0.5)
        bg.paste(rate, (rate_x, rate_y), rate)

        # fc & fs
        if fc:
            fc_path = maimai_Static / f"playicon_{fc}.png"
            fc = Image.open(fc_path)
            fc = resize_image(fc, 0.33)
            bg.paste(fc, (fc_x, fc_y), fc)

        if fs:
            fs_path = maimai_Static / f"playicon_{fs}.png"
            fs = Image.open(fs_path)
            fs = resize_image(fs, 0.33)
            bg.paste(fs, (fs_x, fs_y), fs)

        # 定数->ra
        ttf = ImageFont.truetype(ttf_bold_path, size=20)
        drawtext.text(
            (dsra_x, dsra_y), f"{ds}->{ra}", font=ttf, fill=color, anchor="mm"
        )

    img_byte_arr = BytesIO()
    bg.save(img_byte_arr, format="PNG", quality=90)
    img_byte_arr.seek(0)
    img_bytes = img_byte_arr.getvalue()

    return img_bytes
