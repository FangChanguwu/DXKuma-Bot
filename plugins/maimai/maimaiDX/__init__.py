import math
import os
import re
import shelve
from datetime import date
from pathlib import Path
from random import SystemRandom

import aiohttp
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment

from util.Data import (
    get_chart_stats,
    get_music_data,
    get_alias_list_lxns,
    get_alias_list_ycn,
)
from util.DivingFish import get_player_data, get_player_records
from .GenB50 import (
    compute_record,
    generateb50,
    generate_wcb,
    get_page_records,
    ratings,
    records_filter,
    find_song_by_id,
    dxscore_proc,
    get_fit_diff,
)
from .MusicInfo import music_info, play_info, utage_music_info, score_info

random = SystemRandom()

best50 = on_regex(r"^dlxb?50( *\[CQ:at.*?\] *)?$", re.I)
fit50 = on_regex(r"^dlxf50( *\[CQ:at.*?\] *)?$", re.I)
dxs50 = on_regex(r"^dlxs50( *\[CQ:at.*?\] *)?$", re.I)
star50 = on_regex(r"^dlxx50( *[1-5])+( *\[CQ:at.*?\] *)?$", re.I)
rate50 = on_regex(
    r"^dlxr50( *(s{1,3}(p|\+)?|a{1,3}|b{1,3}|[cd]))+?( *\[CQ:at.*?\] *)?$",
    re.I,
)
ap50 = on_regex(r"^dlxap(50)?( *\[CQ:at.*?\] *)?$", re.I)
fc50 = on_regex(r"^dlxfc(50)?( *\[CQ:at.*?\] *)?$", re.I)
cf50 = on_regex(r"^dlxcf(50)?( *\[CQ:at.*?\] *)$", re.I)
fd50 = on_regex(r"^dlxfd(50)?( *\[CQ:at.*?\] *)?$", re.I)
all50 = on_regex(r"^dlx(all?(50)?|b)( *\[CQ:at.*?\] *)?$", re.I)
rr50 = on_regex(r"^dlxrr(50)?$", re.I)
sunlist = on_regex(r"^dlx([sc]un|寸|🤏)( *\d+?)?$", re.I)
locklist = on_regex(r"^dlx(suo|锁|🔒)( *\d+?)?$", re.I)

songinfo = on_regex(r"^id *\d+$", re.I)
playinfo = on_regex(r"^info *.+$", re.I)
scoreinfo = on_regex(r"^(score|分数表) *(绿|黄|红|紫|白) *\d+$", re.I)
# playmp3 = on_regex(r"^mai点歌 *.+$", re.I)
randomsong = on_regex(r"^随(歌|个|首|张) *(绿|黄|红|紫|白)? *\d+(\.\d|\+)?$")
maiwhat = on_regex(r"^mai什么$", re.I)

wcb = on_regex(
    r"^(list|完成表) *(\d+(\.\d|\+)?|真|超|檄|橙|晓|桃|樱|紫|堇|白|雪|辉|舞|熊|华|爽|煌|宙|星|祭|祝|双)( +\d+)?$",
    re.I,
)

whatSong = on_regex(r"^((search|查歌) *.+|.+是什么歌)$", re.I)
aliasSearch = on_regex(r"^(查看?别名 *\d+|\d+有什么别名)$")

all_plate = on_regex(r"^(plate|看姓名框)$", re.I)
all_frame = on_regex(r"^(frame|看背景)$", re.I)

set_plate = on_regex(r"^(setplate|设置?姓名框) *\d{6}$", re.I)
set_frame = on_regex(r"^(setframe|设置?背景) *\d{6}$", re.I)

ratj_on = on_regex(r"^(开启?|启用)分数推荐$")
ratj_off = on_regex(r"^(关闭?|禁用)分数推荐$")

allow_other_on = on_regex(r"^(开启?|启用|允许)代查$")
allow_other_off = on_regex(r"^(关闭?|禁用|禁止)代查$")


# 根据乐曲别名查询乐曲id列表
async def find_songid_by_alias(name, song_list):
    # 芝士id列表
    matched_ids = []

    # 芝士查找
    for info in song_list:
        if name in info["title"] or name.lower() in info["title"].lower():
            matched_ids.append(info["id"])

    alias_list = await get_alias_list_lxns()
    for info in alias_list["aliases"]:
        if str(info["song_id"]) in matched_ids:
            continue
        for alias in info["aliases"]:
            if name == alias or name.lower() == alias.lower():
                matched_ids.append(str(info["song_id"]))
                break

    alias_list = await get_alias_list_ycn()
    for info in alias_list["content"]:
        if str(info["SongID"]) in matched_ids:
            continue
        for alias in info["Alias"]:
            if name == alias or name.lower() == alias.lower():
                matched_ids.append(str(info["SongID"]))
                break

    # 芝士排序
    # sorted_matched_ids = sorted(matched_ids, key=int)

    # 芝士输出
    return matched_ids


async def records_to_b50(
    records: list | None,
    songList,
    fc_rules: list | None = None,
    rate_rules: list | None = None,
    is_fit: bool = False,
    is_fd: bool = False,
    is_dxs: bool = False,
    is_all: bool = False,
    dx_star_count: str | None = None,
):
    sd = []
    dx = []
    if is_fit or is_fd:
        charts = await get_chart_stats()
    mask_enabled = False
    if not records:
        records = []
        for song in songList:
            if len(song["id"]) > 5:
                continue
            for i, j in enumerate(song["ds"]):
                record = {
                    "achievements": 101,
                    "ds": j,
                    "dxScore": sum(song["charts"][i]["notes"]) * 3,
                    "fc": "fsdp",
                    "fs": "app",
                    "level": "",
                    "level_index": i,
                    "level_label": [
                        "Basic",
                        "Advanced",
                        "Expert",
                        "Master",
                        "Re:MASTER",
                    ][i],
                    "ra": int(j * 22.512),
                    "rate": "sssp",
                    "song_id": int(song["id"]),
                    "title": song["title"],
                    "type": song["type"],
                }
                records.append(record)
    for record in records:
        if record["level_label"] == "Utage":
            continue
        if fc_rules and record["fc"] not in fc_rules:
            continue
        if rate_rules and record["rate"] not in rate_rules:
            continue
        song_id = record["song_id"]
        song_data = [d for d in songList if d["id"] == str(song_id)][0]
        is_new = song_data["basic_info"]["is_new"]
        if is_fit or is_fd:
            if record["ra"] == 0:
                continue
            if record["achievements"] > 0 and record["dxScore"] == 0:
                mask_enabled = True
                continue
            fit_diff = get_fit_diff(
                str(record["song_id"]), record["level_index"], record["ds"], charts
            )
            record["s_ra"] = record["ds"] if is_fit else record["ra"]
            record["ds"] = round(fit_diff, 2)
            record["ra"] = int(
                fit_diff
                * (record["achievements"] if record["achievements"] < 100.5 else 100.5)
                * get_ra_in(record["rate"])
                / 100
            )
        if is_dxs:
            if record["achievements"] > 0 and record["dxScore"] == 0:
                mask_enabled = True
                continue
            if not dx_star_count:
                song_data = find_song_by_id(str(record["song_id"]), songList)
                record["achievements"] = (
                    record["dxScore"]
                    / (sum(song_data["charts"][record["level_index"]]["notes"]) * 3)
                    * 101
                )
                record["ra"] = int(
                    record["ds"]
                    * record["achievements"]
                    * get_ra_in(record["rate"])
                    / 100
                )
            else:
                sum_dxscore = (
                    sum(song_data["charts"][record["level_index"]]["notes"]) * 3
                )
                _, stars = dxscore_proc(record["dxScore"], sum_dxscore)
                if str(stars) not in dx_star_count:
                    continue
        if record["ra"] == 0 or record["achievements"] > 101:
            continue
        if is_new or is_all:
            dx.append(record)
        else:
            sd.append(record)
    if is_all:
        all_records = sorted(
            dx, key=lambda x: (x["ra"], x["ds"], x["achievements"]), reverse=True
        )
        dx.clear()
        for record in [i for i in all_records if i["ra"] >= all_records[49]["ra"]]:
            song_id = record["song_id"]
            song_data = [d for d in songList if d["id"] == str(song_id)][0]
            is_new = song_data["basic_info"]["is_new"]
            if is_new:
                dx.append(record)
                all_records.remove(record)
                if len(dx) >= 15:
                    break
        if len(dx) < 15:
            dx.extend(all_records[36 : 51 - len(dx)])
        sd = all_records[:35]
        return sd, dx, mask_enabled
    b35 = sorted(sd, key=lambda x: (x["ra"], x["ds"], x["achievements"]), reverse=True)[
        :35
    ]
    b15 = sorted(dx, key=lambda x: (x["ra"], x["ds"], x["achievements"]), reverse=True)[
        :15
    ]
    if is_fd:
        b35 = sorted(
            b35,
            key=lambda x: (x["ra"] - x["s_ra"]) * x["ds"] * get_ra_in(record["rate"]),
            reverse=True,
        )
        b15 = sorted(
            b15,
            key=lambda x: (x["ra"] - x["s_ra"]) * x["ds"] * get_ra_in(record["rate"]),
            reverse=True,
        )
    return b35, b15, mask_enabled


async def compare_b50(sender_records, target_records, songList):
    handle_type = len(sender_records) > len(target_records)
    sd = []
    dx = []
    mask_enabled = False
    b35, b15, mask_enabled = await records_to_b50(sender_records, songList)
    if not b35 and not b15:
        return sd, dx, mask_enabled
    sd_min = b35[-1]["ra"] if b35 else -1
    dx_min = b15[-1]["ra"] if b15 else -1
    for record in target_records if handle_type else sender_records:
        if record["level_label"] == "Utage":
            continue
        if record["ra"] == 0 or record["achievements"] > 101:
            continue
        if record["achievements"] > 0 and record["dxScore"] == 0:
            mask_enabled = True
            continue
        other_record = [
            d
            for d in (sender_records if handle_type else target_records)
            if d["song_id"] == record["song_id"]
            and d["level_index"] == record["level_index"]
        ]
        if not other_record:
            continue
        other_record = other_record[0]
        if other_record["ra"] == 0 or other_record["achievements"] > 101:
            continue
        if other_record["achievements"] > 0 and other_record["dxScore"] == 0:
            mask_enabled = True
            continue
        song_id = record["song_id"]
        song_data = [d for d in songList if d["id"] == str(song_id)][0]
        is_new = song_data["basic_info"]["is_new"]
        if handle_type:
            record["preferred"] = record["ra"] >= (dx_min if is_new else sd_min)
            record["s_ra"] = other_record["ra"]
            if is_new:
                dx.append(record)
            else:
                sd.append(record)
        else:
            other_record["preferred"] = other_record["ra"] >= (
                dx_min if is_new else sd_min
            )
            other_record["s_ra"] = record["ra"]
            if is_new:
                dx.append(other_record)
            else:
                sd.append(other_record)
    b35 = sorted(
        sd,
        key=lambda x: (x["preferred"], x["ra"] - x["s_ra"], x["ds"], x["achievements"]),
        reverse=True,
    )[:35]
    b15 = sorted(
        dx,
        key=lambda x: (x["preferred"], x["ra"] - x["s_ra"], x["ds"], x["achievements"]),
        reverse=True,
    )[:15]
    return b35, b15, mask_enabled


def get_ra_in(rate: str) -> float:
    return ratings[rate][1]


@best50.handle()
async def _(event: MessageEvent):
    target_qq = event.get_user_id()
    for message in event.get_message():
        if message.type != "at":
            continue
        target_qq = message.data["qq"]
        if target_qq == event.get_user_id():
            continue
        with shelve.open("./data/maimai/b50_config.db") as config:
            if (
                target_qq not in config
                or "allow_other" not in config[target_qq]
                or config[target_qq]["allow_other"]
            ):
                break
    else:
        if target_qq != event.get_user_id():
            msg = (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("他不允许其他人查询他的成绩"),
            )
            await best50.finish(msg)
    data, status = await get_player_data(target_qq)
    if status == 400:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text(
                f"迪拉熊没有找到{"你" if target_qq == event.get_user_id() else "他"}的信息"
            ),
        )
        await best50.finish(msg)
    elif status == 403:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text(
                f"{"你" if target_qq == event.get_user_id() else "他"}在查分器启用了隐私或者没有同意查分器的用户协议"
            ),
        )
        await best50.finish(msg)
    elif not data:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("（查分器出了点问题）"),
            MessageSegment.image(Path("./Static/maimai/-1.png")),
        )
        await best50.finish(msg)
    songList = await get_music_data()
    charts = data["charts"]
    b35, b15 = sorted(
        charts["sd"], key=lambda x: (x["ra"], x["ds"], x["achievements"]), reverse=True
    ), sorted(
        charts["dx"], key=lambda x: (x["ra"], x["ds"], x["achievements"]), reverse=True
    )
    if not b35 and not b15:
        msg = MessageSegment.text(
            f"{"你" if target_qq == event.get_user_id() else "他"}没有上传任何成绩"
        )
        await best50.finish((MessageSegment.reply(event.message_id), msg))
    await best50.send(
        (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
        )
    )
    nickname = data["nickname"]
    dani = data["additional_rating"]
    img = await generateb50(
        b35=b35,
        b15=b15,
        nickname=nickname,
        qq=target_qq,
        dani=dani,
        type="b50",
        songList=songList,
    )
    msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
    await best50.send(msg)


@ap50.handle()
async def _(event: MessageEvent):
    target_qq = event.get_user_id()
    for message in event.get_message():
        if message.type != "at":
            continue
        target_qq = message.data["qq"]
        if target_qq == event.get_user_id():
            continue
        with shelve.open("./data/maimai/b50_config.db") as config:
            if (
                target_qq not in config
                or "allow_other" not in config[target_qq]
                or config[target_qq]["allow_other"]
            ):
                break
    else:
        if target_qq != event.get_user_id():
            msg = (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("他不允许其他人查询他的成绩"),
            )
            await ap50.finish(msg)
    data, status = await get_player_records(target_qq)
    if status == 400:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text(
                f"迪拉熊没有找到{"你" if target_qq == event.get_user_id() else "他"}的信息"
            ),
        )
        await ap50.finish(msg)
    elif not data:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("（查分器出了点问题）"),
            MessageSegment.image(Path("./Static/maimai/-1.png")),
        )
        await ap50.finish(msg)
    records = data["records"]
    if not records:
        msg = MessageSegment.text(
            f"{"你" if target_qq == event.get_user_id() else "他"}没有上传任何成绩"
        )
        await ap50.finish((MessageSegment.reply(event.message_id), msg))
    songList = await get_music_data()
    ap35, ap15, _ = await records_to_b50(records, songList, ["ap", "app"])
    if not ap35 and not ap15:
        msg = MessageSegment.text(
            f"{"你" if target_qq == event.get_user_id() else "他"}没有全完美的成绩"
        )
        await ap50.finish((MessageSegment.reply(event.message_id), msg))
    await ap50.send(
        (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
        )
    )
    nickname = data["nickname"]
    dani = data["additional_rating"]
    img = await generateb50(
        b35=ap35,
        b15=ap15,
        nickname=nickname,
        qq=target_qq,
        dani=dani,
        type="ap50",
        songList=songList,
    )
    msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
    await ap50.send(msg)


@fc50.handle()
async def _(event: MessageEvent):
    target_qq = event.get_user_id()
    for message in event.get_message():
        if message.type != "at":
            continue
        target_qq = message.data["qq"]
        if target_qq == event.get_user_id():
            continue
        with shelve.open("./data/maimai/b50_config.db") as config:
            if (
                target_qq not in config
                or "allow_other" not in config[target_qq]
                or config[target_qq]["allow_other"]
            ):
                break
    else:
        if target_qq != event.get_user_id():
            msg = (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("他不允许其他人查询他的成绩"),
            )
            await fc50.finish(msg)
    data, status = await get_player_records(target_qq)
    if status == 400:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text(
                f"迪拉熊没有找到{"你" if target_qq == event.get_user_id() else "他"}的信息"
            ),
        )
        await fc50.finish(msg)
    elif not data:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("（查分器出了点问题）"),
            MessageSegment.image(Path("./Static/maimai/-1.png")),
        )
        await fc50.finish(msg)
    records = data["records"]
    if not records:
        msg = MessageSegment.text(
            f"{"你" if target_qq == event.get_user_id() else "他"}没有上传任何成绩"
        )
        await fc50.finish((MessageSegment.reply(event.message_id), msg))
    songList = await get_music_data()
    fc35, fc15, _ = await records_to_b50(records, songList, ["fc", "fcp"])
    if not fc35 and not fc15:
        msg = MessageSegment.text(
            f"{"你" if target_qq == event.get_user_id() else "他"}没有全连的成绩"
        )
        await fc50.finish((MessageSegment.reply(event.message_id), msg))
    await fc50.send(
        (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
        )
    )
    nickname = data["nickname"]
    dani = data["additional_rating"]
    img = await generateb50(
        b35=fc35,
        b15=fc15,
        nickname=nickname,
        qq=target_qq,
        dani=dani,
        type="fc50",
        songList=songList,
    )
    msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
    await fc50.send(msg)


@fit50.handle()
async def _(event: MessageEvent):
    target_qq = event.get_user_id()
    for message in event.get_message():
        if message.type != "at":
            continue
        target_qq = message.data["qq"]
        if target_qq == event.get_user_id():
            continue
        with shelve.open("./data/maimai/b50_config.db") as config:
            if (
                target_qq not in config
                or "allow_other" not in config[target_qq]
                or config[target_qq]["allow_other"]
            ):
                break
    else:
        if target_qq != event.get_user_id():
            msg = (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("他不允许其他人查询他的成绩"),
            )
            await fit50.finish(msg)
    data, status = await get_player_records(target_qq)
    if status == 400:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text(
                f"迪拉熊没有找到{"你" if target_qq == event.get_user_id() else "他"}的信息"
            ),
        )
        await fit50.finish(msg)
    elif not data:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("（查分器出了点问题）"),
            MessageSegment.image(Path("./Static/maimai/-1.png")),
        )
        await fit50.finish(msg)
    records = data["records"]
    if not records:
        msg = MessageSegment.text(
            f"{"你" if target_qq == event.get_user_id() else "他"}没有上传任何成绩"
        )
        await fit50.finish((MessageSegment.reply(event.message_id), msg))
    songList = await get_music_data()
    b35, b15, mask_enabled = await records_to_b50(records, songList, is_fit=True)
    if not b35 and not b15:
        if mask_enabled:
            msg = MessageSegment.text(
                f"迪拉熊无法获取{"你" if target_qq == event.get_user_id() else "他"}的真实成绩"
            )
        else:
            msg = MessageSegment.text(
                f"{"你" if target_qq == event.get_user_id() else "他"}没有上传任何匹配的成绩"
            )
        await fit50.finish((MessageSegment.reply(event.message_id), msg))
    await fit50.send(
        (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
        )
    )
    nickname = data["nickname"]
    dani = data["additional_rating"]
    img = await generateb50(
        b35=b35,
        b15=b15,
        nickname=nickname,
        qq=target_qq,
        dani=dani,
        type="fit50",
        songList=songList,
    )
    msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
    await fit50.send(msg)


@rate50.handle()
async def _(event: MessageEvent):
    target_qq = event.get_user_id()
    for message in event.get_message():
        if message.type != "at":
            continue
        target_qq = message.data["qq"]
        if target_qq == event.get_user_id():
            continue
        with shelve.open("./data/maimai/b50_config.db") as config:
            if (
                target_qq not in config
                or "allow_other" not in config[target_qq]
                or config[target_qq]["allow_other"]
            ):
                break
    else:
        if target_qq != event.get_user_id():
            msg = (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("他不允许其他人查询他的成绩"),
            )
            await rate50.finish(msg)
    data, status = await get_player_records(target_qq)
    if status == 400:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text(
                f"迪拉熊没有找到{"你" if target_qq == event.get_user_id() else "他"}的信息"
            ),
        )
        await rate50.finish(msg)
    elif not data:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("（查分器出了点问题）"),
            MessageSegment.image(Path("./Static/maimai/-1.png")),
        )
        await rate50.finish(msg)
    records = data["records"]
    if not records:
        msg = MessageSegment.text(
            f"{"你" if target_qq == event.get_user_id() else "他"}没有上传任何成绩"
        )
        await rate50.finish((MessageSegment.reply(event.message_id), msg))
    msg_text = event.get_plaintext().replace("+", "p").lower()
    rate_rules = re.findall(r"s{1,3}p?|a{1,3}|b{1,3}|[cd]", msg_text)
    songList = await get_music_data()
    rate35, rate15, _ = await records_to_b50(records, songList, rate_rules=rate_rules)
    if not rate35 and not rate15:
        msg = MessageSegment.text(
            f"{"你" if target_qq == event.get_user_id() else "他"}没有上传任何匹配的成绩"
        )
        await rate50.finish((MessageSegment.reply(event.message_id), msg))
    await rate50.send(
        (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
        )
    )
    nickname = data["nickname"]
    dani = data["additional_rating"]
    img = await generateb50(
        b35=rate35,
        b15=rate15,
        nickname=nickname,
        qq=target_qq,
        dani=dani,
        type="rate50",
        songList=songList,
    )
    msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
    await rate50.send(msg)


@dxs50.handle()
async def _(event: MessageEvent):
    target_qq = event.get_user_id()
    for message in event.get_message():
        if message.type != "at":
            continue
        target_qq = message.data["qq"]
        if target_qq == event.get_user_id():
            continue
        with shelve.open("./data/maimai/b50_config.db") as config:
            if (
                target_qq not in config
                or "allow_other" not in config[target_qq]
                or config[target_qq]["allow_other"]
            ):
                break
    else:
        if target_qq != event.get_user_id():
            msg = (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("他不允许其他人查询他的成绩"),
            )
            await dxs50.finish(msg)
    data, status = await get_player_records(target_qq)
    if status == 400:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text(
                f"迪拉熊没有找到{"你" if target_qq == event.get_user_id() else "他"}的信息"
            ),
        )
        await dxs50.finish(msg)
    elif not data:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("（查分器出了点问题）"),
            MessageSegment.image(Path("./Static/maimai/-1.png")),
        )
        await dxs50.finish(msg)
    records = data["records"]
    if not records:
        msg = MessageSegment.text(
            f"{"你" if target_qq == event.get_user_id() else "他"}没有上传任何成绩"
        )
        await dxs50.finish((MessageSegment.reply(event.message_id), msg))
    songList = await get_music_data()
    dxs35, dxs15, mask_enabled = await records_to_b50(records, songList, is_dxs=True)
    if not dxs35 and not dxs15:
        if mask_enabled:
            msg = MessageSegment.text(
                f"迪拉熊无法获取{"你" if target_qq == event.get_user_id() else "他"}的真实成绩"
            )
        else:
            msg = MessageSegment.text(
                f"{"你" if target_qq == event.get_user_id() else "他"}没有上传任何匹配的成绩"
            )
        await dxs50.finish((MessageSegment.reply(event.message_id), msg))
    await dxs50.send(
        (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
        )
    )
    nickname = data["nickname"]
    dani = data["additional_rating"]
    img = await generateb50(
        b35=dxs35,
        b15=dxs15,
        nickname=nickname,
        qq=target_qq,
        dani=dani,
        type="dxs50",
        songList=songList,
    )
    msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
    await dxs50.send(msg)


@star50.handle()
async def _(event: MessageEvent):
    target_qq = event.get_user_id()
    for message in event.get_message():
        if message.type != "at":
            continue
        target_qq = message.data["qq"]
        if target_qq == event.get_user_id():
            continue
        with shelve.open("./data/maimai/b50_config.db") as config:
            if (
                target_qq not in config
                or "allow_other" not in config[target_qq]
                or config[target_qq]["allow_other"]
            ):
                break
    else:
        if target_qq != event.get_user_id():
            msg = (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("他不允许其他人查询他的成绩"),
            )
            await star50.finish(msg)
    data, status = await get_player_records(target_qq)
    if status == 400:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text(
                f"迪拉熊没有找到{"你" if target_qq == event.get_user_id() else "他"}的信息"
            ),
        )
        await star50.finish(msg)
    elif not data:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("（查分器出了点问题）"),
            MessageSegment.image(Path("./Static/maimai/-1.png")),
        )
        await star50.finish(msg)
    records = data["records"]
    if not records:
        msg = MessageSegment.text(
            f"{"你" if target_qq == event.get_user_id() else "他"}没有上传任何成绩"
        )
        await star50.finish((MessageSegment.reply(event.message_id), msg))
    songList = await get_music_data()
    find = re.fullmatch(r"dlxx50((?: *[1-5])+)", event.get_plaintext(), re.I)
    star35, star15, mask_enabled = await records_to_b50(
        records, songList, is_dxs=True, dx_star_count=find.group(1)
    )
    if not star35 and not star15:
        if mask_enabled:
            msg = MessageSegment.text(
                f"迪拉熊无法获取{"你" if target_qq == event.get_user_id() else "他"}的真实成绩"
            )
        else:
            msg = MessageSegment.text(
                f"{"你" if target_qq == event.get_user_id() else "他"}没有上传任何匹配的成绩"
            )
        await star50.finish((MessageSegment.reply(event.message_id), msg))
    await star50.send(
        (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
        )
    )
    nickname = data["nickname"]
    dani = data["additional_rating"]
    img = await generateb50(
        b35=star35,
        b15=star15,
        nickname=nickname,
        qq=target_qq,
        dani=dani,
        type="star50",
        songList=songList,
    )
    msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
    await star50.send(msg)


@cf50.handle()
async def _(event: MessageEvent):
    sender_qq = event.get_user_id()
    for message in event.get_message():
        if message.type != "at":
            continue
        target_qq = message.data["qq"]
        if target_qq == sender_qq:
            continue
        with shelve.open("./data/maimai/b50_config.db") as config:
            if (
                target_qq not in config
                or "allow_other" not in config[target_qq]
                or config[target_qq]["allow_other"]
            ):
                break
    else:
        if target_qq != sender_qq:
            msg = (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("他不允许其他人查询他的成绩"),
            )
            await cf50.finish(msg)
    if target_qq == sender_qq:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("你不可以和自己比较"),
        )
        await cf50.finish(msg)
    sender_data, status = await get_player_records(sender_qq)
    if status == 400:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊没有找到你的信息"),
        )
        await cf50.finish(msg)
    elif status == 403:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("你在查分器启用了隐私或者没有同意查分器的用户协议"),
        )
        await cf50.finish(msg)
    elif not sender_data:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("（查分器出了点问题）"),
            MessageSegment.image(Path("./Static/maimai/-1.png")),
        )
        await cf50.finish(msg)
    target_data, status = await get_player_records(target_qq)
    if status == 400:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊没有找到他的信息"),
        )
        await cf50.finish(msg)
    elif status == 403:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("他在查分器启用了隐私或者没有同意查分器的用户协议"),
        )
        await cf50.finish(msg)
    elif not target_data:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("（查分器出了点问题）"),
            MessageSegment.image(Path("./Static/maimai/-1.png")),
        )
        await cf50.finish(msg)
    songList = await get_music_data()
    sender_records = sender_data["records"]
    if not sender_records:
        msg = MessageSegment.text("你没有上传任何成绩")
        await cf50.finish((MessageSegment.reply(event.message_id), msg))
    target_records = target_data["records"]
    if not target_records:
        msg = MessageSegment.text("他没有上传任何成绩")
        await cf50.finish((MessageSegment.reply(event.message_id), msg))
    songList = await get_music_data()
    b35, b15, mask_enabled = await compare_b50(sender_records, target_records, songList)
    if not b35 and not b15:
        if mask_enabled:
            msg = MessageSegment.text("迪拉熊无法获取真实成绩")
        else:
            msg = MessageSegment.text("没有上传任何匹配的成绩")
        await cf50.finish((MessageSegment.reply(event.message_id), msg))
    await cf50.send(
        (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
        )
    )
    nickname = target_data["nickname"]
    dani = target_data["additional_rating"]
    img = await generateb50(
        b35=b35,
        b15=b15,
        nickname=nickname,
        qq=target_qq,
        dani=dani,
        type="cf50",
        songList=songList,
    )
    msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
    await cf50.send(msg)


@fd50.handle()
async def _(event: MessageEvent):
    target_qq = event.get_user_id()
    for message in event.get_message():
        if message.type != "at":
            continue
        target_qq = message.data["qq"]
        if target_qq == event.get_user_id():
            continue
        with shelve.open("./data/maimai/b50_config.db") as config:
            if (
                target_qq not in config
                or "allow_other" not in config[target_qq]
                or config[target_qq]["allow_other"]
            ):
                break
    else:
        if target_qq != event.get_user_id():
            msg = (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("他不允许其他人查询他的成绩"),
            )
            await fd50.finish(msg)
    data, status = await get_player_records(target_qq)
    if status == 400:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text(
                f"迪拉熊没有找到{"你" if target_qq == event.get_user_id() else "他"}的信息"
            ),
        )
        await fd50.finish(msg)
    elif not data:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("（查分器出了点问题）"),
            MessageSegment.image(Path("./Static/maimai/-1.png")),
        )
        await fd50.finish(msg)
    records = data["records"]
    if not records:
        msg = MessageSegment.text(
            f"{"你" if target_qq == event.get_user_id() else "他"}没有上传任何成绩"
        )
        await fd50.finish((MessageSegment.reply(event.message_id), msg))
    songList = await get_music_data()
    b35, b15, mask_enabled = await records_to_b50(records, songList, is_fd=True)
    if not b35 and not b15:
        if mask_enabled:
            msg = MessageSegment.text(
                f"迪拉熊无法获取{"你" if target_qq == event.get_user_id() else "他"}的真实成绩"
            )
        else:
            msg = MessageSegment.text(
                f"{"你" if target_qq == event.get_user_id() else "他"}没有上传任何匹配的成绩"
            )
        await fd50.finish((MessageSegment.reply(event.message_id), msg))
    await fd50.send(
        (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
        )
    )
    nickname = data["nickname"]
    dani = data["additional_rating"]
    img = await generateb50(
        b35=b35,
        b15=b15,
        nickname=nickname,
        qq=target_qq,
        dani=dani,
        type="fd50",
        songList=songList,
    )
    msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
    await fd50.send(msg)


@all50.handle()
async def _(event: MessageEvent):
    target_qq = event.get_user_id()
    for message in event.get_message():
        if message.type != "at":
            continue
        target_qq = message.data["qq"]
        if target_qq == event.get_user_id():
            continue
        with shelve.open("./data/maimai/b50_config.db") as config:
            if (
                target_qq not in config
                or "allow_other" not in config[target_qq]
                or config[target_qq]["allow_other"]
            ):
                break
    else:
        if target_qq != event.get_user_id():
            msg = (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("他不允许其他人查询他的成绩"),
            )
            await all50.finish(msg)
    data, status = await get_player_records(target_qq)
    if status == 400:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text(
                f"迪拉熊没有找到{"你" if target_qq == event.get_user_id() else "他"}的信息"
            ),
        )
        await all50.finish(msg)
    elif not data:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("（查分器出了点问题）"),
            MessageSegment.image(Path("./Static/maimai/-1.png")),
        )
        await all50.finish(msg)
    records = data["records"]
    if not records:
        msg = MessageSegment.text(
            f"{"你" if target_qq == event.get_user_id() else "他"}没有上传任何成绩"
        )
        await all50.finish((MessageSegment.reply(event.message_id), msg))
    songList = await get_music_data()
    all35, all15, _ = await records_to_b50(records, songList, is_all=True)
    await all50.send(
        (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
        )
    )
    nickname = data["nickname"]
    dani = data["additional_rating"]
    img = await generateb50(
        b35=all35,
        b15=all15,
        nickname=nickname,
        qq=target_qq,
        dani=dani,
        type="all50",
        songList=songList,
    )
    msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
    await all50.send(msg)


@rr50.handle()
async def _(event: MessageEvent):
    cache_dir = "./Cache/Riren/"
    cache_path = f"{cache_dir}{date.today().isoformat()}.png"
    if not os.path.exists(cache_path):
        files = os.listdir(cache_dir)
        songList = await get_music_data()
        rr35, rr15, _ = await records_to_b50(None, songList)
        await rr50.send(
            (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
            )
        )
        nickname = "科技哥（？）"
        dani = 22
        img = await generateb50(
            b35=rr35,
            b15=rr15,
            nickname=nickname,
            qq="0",
            dani=dani,
            type="rr50",
            songList=songList,
        )
        with open(cache_path, "wb") as fd:
            fd.write(img)
        if files:
            for file in files:
                os.remove(f"{cache_dir}{file}")
    with open(cache_path, "rb") as fd:
        img = fd.read()
    msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
    await rr50.send(msg)


@sunlist.handle()
async def _(event: MessageEvent):
    qq = event.get_user_id()
    data, status = await get_player_records(qq)
    if status == 400:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊没有找到你的信息"),
        )
        await sunlist.finish(msg)
    elif not data:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("（查分器出了点问题）"),
            MessageSegment.image(Path("./Static/maimai/-1.png")),
        )
        await sunlist.finish(msg)
    records = data["records"]
    if not records:
        msg = MessageSegment.text("你没有上传任何成绩")
        await sunlist.finish((MessageSegment.reply(event.message_id), msg))
    songList = await get_music_data()
    filted_records, mask_enabled = records_filter(
        records=records, is_sun=True, songList=songList
    )
    if not filted_records:
        if mask_enabled:
            msg = MessageSegment.text("迪拉熊无法获取你的真实成绩")
        else:
            msg = MessageSegment.text("你没有上传任何匹配的成绩")
        await sunlist.finish((MessageSegment.reply(event.message_id), msg))
    msg = event.get_plaintext()
    pattern = r"\d+"
    match = re.search(pattern, msg)
    if match:
        page = int(match.group())
        if page <= 0:
            page = 1
    else:
        page = 1
    all_page_num = math.ceil(len(filted_records) / 55)
    if page > all_page_num:
        page = all_page_num
    await sunlist.send(
        (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
        )
    )
    input_records = get_page_records(filted_records, page=page)
    nickname = data["nickname"]
    rating = data["rating"]
    dani = data["additional_rating"]
    img = await generate_wcb(
        qq=qq,
        page=page,
        nickname=nickname,
        dani=dani,
        rating=rating,
        input_records=input_records,
        all_page_num=all_page_num,
        songList=songList,
    )
    msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
    await sunlist.send(msg)


@locklist.handle()
async def _(event: MessageEvent):
    qq = event.get_user_id()
    data, status = await get_player_records(qq)
    if status == 400:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊没有找到你的信息"),
        )
        await locklist.finish(msg)
    elif not data:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("（查分器出了点问题）"),
            MessageSegment.image(Path("./Static/maimai/-1.png")),
        )
        await locklist.finish(msg)
    records = data["records"]
    if not records:
        msg = MessageSegment.text("你没有上传任何成绩")
        await locklist.finish((MessageSegment.reply(event.message_id), msg))
    songList = await get_music_data()
    filted_records, mask_enabled = records_filter(
        records=records, is_lock=True, songList=songList
    )
    if not filted_records:
        if mask_enabled:
            msg = MessageSegment.text("迪拉熊无法获取你的真实成绩")
        else:
            msg = MessageSegment.text("你没有上传任何匹配的成绩")
        await locklist.finish((MessageSegment.reply(event.message_id), msg))
    msg = event.get_plaintext()
    pattern = r"\d+"
    match = re.search(pattern, msg)
    if match:
        page = int(match.group())
        if page <= 0:
            page = 1
    else:
        page = 1
    all_page_num = math.ceil(len(filted_records) / 55)
    if page > all_page_num:
        page = all_page_num
    await locklist.send(
        (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
        )
    )
    input_records = get_page_records(filted_records, page=page)
    nickname = data["nickname"]
    rating = data["rating"]
    dani = data["additional_rating"]
    img = await generate_wcb(
        qq=qq,
        page=page,
        nickname=nickname,
        dani=dani,
        rating=rating,
        input_records=input_records,
        all_page_num=all_page_num,
        songList=songList,
    )
    msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
    await locklist.send(msg)


@wcb.handle()
async def _(event: MessageEvent):
    qq = event.get_user_id()
    msg = event.get_plaintext()
    pattern = r"(?:((?:\d+)(?:\.\d|\+)?)|(真|超|檄|橙|晓|桃|樱|紫|堇|白|雪|辉|舞|熊|华|爽|煌|宙|星|祭|祝|双))(?: *(\d+))?"
    match = re.search(pattern, msg)
    data, status = await get_player_records(qq)
    if status == 400:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊没有找到你的信息"),
        )
        await wcb.finish(msg)
    elif not data:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("（查分器出了点问题）"),
            MessageSegment.image(Path("./Static/maimai/-1.png")),
        )
        await wcb.finish(msg)
    records = data["records"]
    if not records:
        msg = MessageSegment.text("你没有上传任何成绩")
        await wcb.finish((MessageSegment.reply(event.message_id), msg))
    songList = await get_music_data()
    level = match.group(1)
    if level and "." in level:
        ds = float(level)
        level = None
    else:
        ds = None
    gen = match.group(2)
    filted_records, _ = records_filter(
        records=records, level=level, ds=ds, gen=gen, songList=songList
    )
    if len(filted_records) == 0:
        msg = MessageSegment.text("你没有上传任何匹配的成绩")
        await wcb.finish((MessageSegment.reply(event.message_id), msg))

    if match.group(3):
        page = int(match.group(3))
        if page <= 0:
            page = 1
    else:
        page = 1
    all_page_num = math.ceil(len(filted_records) / 55)
    if page > all_page_num:
        page = all_page_num
    await wcb.send(
        (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
        )
    )
    input_records = get_page_records(filted_records, page=page)
    rate_count = compute_record(records=filted_records)
    nickname = data["nickname"]
    rating = data["rating"]
    dani = data["additional_rating"]
    img = await generate_wcb(
        qq=qq,
        level=level,
        ds=ds,
        gen=gen,
        page=page,
        nickname=nickname,
        dani=dani,
        rating=rating,
        input_records=input_records,
        rate_count=rate_count,
        all_page_num=all_page_num,
        songList=songList,
    )
    msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
    await wcb.send(msg)


@songinfo.handle()
async def _(event: MessageEvent):
    msg = event.get_plaintext()
    song_id = re.search(r"\d+", msg).group()
    songList = await get_music_data()
    song_info = find_song_by_id(song_id, songList)
    if not song_info:
        msg = MessageSegment.text("迪拉熊没有找到匹配的乐曲")
    else:
        await songinfo.send(
            (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
            )
        )
        if song_info["basic_info"]["genre"] == "宴会場":
            img = await utage_music_info(song_data=song_info)
        else:
            img = await music_info(song_data=song_info)
        msg = MessageSegment.image(img)
    await songinfo.send((MessageSegment.reply(event.message_id), msg))


@playinfo.handle()
async def _(event: MessageEvent):
    qq = event.get_user_id()
    msg = event.get_plaintext()
    match = re.fullmatch(r"info *(.+)", msg, re.I)
    song = match.group(1)
    if not song:
        await playinfo.finish(
            (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("迪拉熊没有找到匹配的乐曲"),
            )
        )
    songList = await get_music_data()
    song_info = find_song_by_id(song, songList)
    if not song_info:
        rep_ids = await find_songid_by_alias(song, songList)
        if not rep_ids:
            await playinfo.finish(
                (
                    MessageSegment.reply(event.message_id),
                    MessageSegment.text("迪拉熊没有找到匹配的乐曲"),
                )
            )
        for song_id in rep_ids.copy():
            song_info = find_song_by_id(song_id, songList)
            if not song_info:
                rep_ids.remove(song_id)
                continue
            song_id_len = len(song_id)
            if song_id_len < 5:
                other_id = f"1{int(song_id):04d}"
                if other_id in rep_ids:
                    continue
                other_info = find_song_by_id(other_id, songList)
                if other_info:
                    rep_ids.append(other_id)
        if not rep_ids:
            await playinfo.finish(
                (
                    MessageSegment.reply(event.message_id),
                    MessageSegment.text("迪拉熊没有找到匹配的乐曲"),
                )
            )
        elif len(rep_ids) == 1:
            song_id = rep_ids.pop()
            song_info = find_song_by_id(song_id, songList)
        elif len(rep_ids) > 20:
            await playinfo.finish(
                (
                    MessageSegment.reply(event.message_id),
                    MessageSegment.text("结果太多啦，缩小范围再试试吧~"),
                )
            )
        else:
            output_lst = "迪拉熊找到啦~结果有："
            for song_id in sorted(rep_ids, key=int):
                song_info = find_song_by_id(song_id, songList)
                song_title = song_info["title"]
                output_lst += f"\n{song_id}：{song_title}"
            await playinfo.finish(MessageSegment.text(output_lst))
    if not song_info:
        await playinfo.finish(
            (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("迪拉熊没有找到匹配的乐曲"),
            )
        )
    img = await play_info(song_data=song_info, qq=qq)
    if isinstance(img, str):
        msg = MessageSegment.text(img)
    else:
        msg = MessageSegment.image(img)
    await playinfo.send((MessageSegment.reply(event.message_id), msg))


@scoreinfo.handle()
async def _(event: MessageEvent):
    msg = event.get_plaintext()
    pattern = r"(绿|黄|红|紫|白) *(\d+)"
    match = re.search(pattern, msg)
    type_index = ["绿", "黄", "红", "紫", "白"].index(match.group(1))
    song_id = match.group(2)
    songList = await get_music_data()
    song_info = find_song_by_id(song_id, songList)
    if (
        not song_info
        or song_info["basic_info"]["genre"] == "宴会場"
        or len(song_info["level"]) <= type_index
    ):
        msg = MessageSegment.text("迪拉熊没有找到匹配的乐曲")
    else:
        await scoreinfo.send(
            (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("迪拉熊绘制中，稍等一下mai~"),
            )
        )
        img = await score_info(song_data=song_info, index=type_index)
        msg = MessageSegment.image(img)
    await scoreinfo.send((MessageSegment.reply(event.message_id), msg))


# @playmp3.handle()
# async def _(event: GroupMessageEvent):
#     msg = event.get_plaintext()
#     song = msg.replace("dlx点歌", "").strip()
#     if not song:
#         await playmp3.finish(
#             (
#                 MessageSegment.reply(event.message_id),
#                 MessageSegment.text("迪拉熊没有找到匹配的乐曲"),
#             )
#         )
#     songList = await get_music_data()
#     rep_ids = await find_songid_by_alias(song, songList)
#     if rep_ids:
#         songinfo = find_song_by_id(song_id=rep_ids[0], songList=songList)
#         if not songinfo:
#             await playmp3.finish(
#                 (
#                     MessageSegment.reply(event.message_id),
#                     MessageSegment.text("迪拉熊没有找到匹配的乐曲"),
#                 )
#             )
#         songname = songinfo["title"]
#         await playmp3.send(
#             MessageSegment.text(f"迪拉熊找到啦~\n开始播放{songinfo["id"]}——{songname}")
#         )
#         music_path = f"./Cache/Music/{rep_ids[0][-4:].lstrip("0")}.mp3"
#         if not os.path.exists(music_path):
#             async with aiohttp.ClientSession() as session:
#                 async with session.get(
#                     f"https://assets2.lxns.net/maimai/music/{rep_ids[0][-4:].lstrip("0")}.mp3"
#                 ) as resp:
#                     with open(music_path, "wb") as fd:
#                         async for chunk in resp.content.iter_chunked(1024):
#                             fd.write(chunk)
#         await playmp3.send(MessageSegment.record(music_path))
#     else:
#         songinfo = find_song_by_id(song, songList)
#         if songinfo:
#             songname = songinfo["title"]
#             await playmp3.send(
#                 MessageSegment.text(
#                     f"迪拉熊找到啦~\n开始播放{songinfo["id"]}——{songname}"
#                 )
#             )
#             music_path = f"./Cache/Music/{song[-4:].lstrip("0")}.mp3"
#             if not os.path.exists(music_path):
#                 async with aiohttp.ClientSession() as session:
#                     async with session.get(
#                         f"https://assets2.lxns.net/maimai/music/{song[-4:].lstrip("0")}.mp3"
#                     ) as resp:
#                         with open(music_path, "wb") as fd:
#                             async for chunk in resp.content.iter_chunked(1024):
#                                 fd.write(chunk)
#             await playmp3.send(MessageSegment.record(music_path))
#         else:
#             await playmp3.send(
#                 (
#                     MessageSegment.reply(event.message_id),
#                     MessageSegment.text("迪拉熊没有找到匹配的乐曲"),
#                 )
#             )


@randomsong.handle()
async def _(event: MessageEvent):
    msg = event.get_plaintext()
    pattern = r"(绿|黄|红|紫|白)? *((?:\d+)(?:\.\d|\+)?)"
    match = re.search(pattern, msg)
    level_label = match.group(1)
    if level_label:
        level_index = ["绿", "黄", "红", "紫", "白"].index(level_label)
    else:
        level_index = None
    level = match.group(2)
    s_type = "level"
    if "." in level:
        s_type = "ds"
    s_songs = []
    songList = await get_music_data()
    for song in songList:
        s_list = song[s_type]
        if s_type == "ds":
            level = float(level)
        if level_index:
            if len(s_list) > level_index:
                if level == s_list[level_index]:
                    s_songs.append(song)
        elif level in s_list:
            s_songs.append(song)
    if len(s_songs) == 0:
        msg = MessageSegment.text("迪拉熊没有找到匹配的乐曲")
        await randomsong.finish((MessageSegment.reply(event.message_id), msg))
    song = random.choice(s_songs)
    if song["basic_info"]["genre"] == "宴会場":
        img = await utage_music_info(song_data=song)
    else:
        img = await music_info(song_data=song)
    msg = MessageSegment.image(img)
    await randomsong.send((MessageSegment.reply(event.message_id), msg))


@maiwhat.handle()
async def _(event: MessageEvent):
    songList = await get_music_data()
    song = random.choice(songList)
    if song["basic_info"]["genre"] == "宴会場":
        img = await utage_music_info(song_data=song)
    else:
        img = await music_info(song_data=song)
    msg = MessageSegment.image(img)
    await maiwhat.send((MessageSegment.reply(event.message_id), msg))


@whatSong.handle()
async def _(event: MessageEvent):
    msg = event.get_plaintext()
    match = re.fullmatch(r"(?:search|查歌) *(.+)|(.+)是什么歌", msg, re.I)
    if match:
        if match.group(1):
            name = match.group(1)
        elif match.group(2):
            name = match.group(2)
        else:
            await whatSong.finish(
                (
                    MessageSegment.reply(event.message_id),
                    MessageSegment.text("迪拉熊没有找到匹配的乐曲"),
                )
            )

        songList = await get_music_data()
        rep_ids = await find_songid_by_alias(name, songList)
        if not rep_ids:
            msg = (
                MessageSegment.reply(event.message_id),
                MessageSegment.text("迪拉熊没有找到匹配的乐曲"),
            )
        for song_id in rep_ids.copy():
            song_info = find_song_by_id(song_id, songList)
            if not song_info:
                rep_ids.remove(song_id)
                continue
            song_id_len = len(song_id)
            if song_id_len < 5:
                other_id = f"1{int(song_id):04d}"
                if other_id in rep_ids:
                    continue
                other_info = find_song_by_id(other_id, songList)
                if other_info:
                    rep_ids.append(other_id)
        if not rep_ids:
            await whatSong.finish(
                (
                    MessageSegment.reply(event.message_id),
                    MessageSegment.text("迪拉熊没有找到匹配的乐曲"),
                )
            )
        elif len(rep_ids) == 1:
            song_id = rep_ids.pop()
            song_info = find_song_by_id(song_id, songList)
            if song_info["basic_info"]["genre"] == "宴会場":
                img = await utage_music_info(song_data=song_info)
            else:
                img = await music_info(song_data=song_info)
            msg = (MessageSegment.reply(event.message_id), MessageSegment.image(img))
        elif len(rep_ids) > 20:
            await whatSong.finish(
                (
                    MessageSegment.reply(event.message_id),
                    MessageSegment.text("结果太多啦，缩小范围再试试吧~"),
                )
            )
        else:
            output_lst = "迪拉熊找到啦~结果有："
            for song_id in sorted(rep_ids, key=int):
                song_info = find_song_by_id(song_id, songList)
                song_title = song_info["title"]
                output_lst += f"\n{song_id}：{song_title}"
            msg = MessageSegment.text(output_lst)
        await whatSong.send(msg)


# 查看别名
@aliasSearch.handle()
async def _(event: MessageEvent):
    msg = event.get_plaintext()
    song_id = re.search(r"\d+", msg).group()

    alias = set()
    alias_list = await get_alias_list_lxns()
    for d in alias_list["aliases"]:
        if d["song_id"] in [int(song_id), int(song_id) / 10]:
            alias |= set(d["aliases"])
    alias_list = await get_alias_list_ycn()
    for d in alias_list["content"]:
        if d["SongID"] in [int(song_id), int(song_id) / 10]:
            alias |= set(d["Alias"])
    if not alias:
        msg = (
            MessageSegment.reply(event.message_id),
            MessageSegment.text("迪拉熊没有找到匹配的乐曲"),
        )
    else:
        song_alias = "\n".join(alias)
        msg = MessageSegment.text(f"迪拉熊找到啦~别名有：\n{song_alias}")
    await aliasSearch.send(msg)


@all_frame.handle()
async def _():
    path = "./Static/maimai/allFrame.png"
    await all_frame.send(MessageSegment.image(Path(path)))


@all_plate.handle()
async def _():
    path = "./Static/maimai/allPlate.png"
    await all_plate.send(MessageSegment.image(Path(path)))


@set_plate.handle()
async def _(event: MessageEvent):
    qq = event.get_user_id()
    msg = event.get_plaintext()
    id = re.search(r"\d+", msg).group()
    plate_path = f"./Cache/Plate/{id}.png"
    if not os.path.exists(plate_path):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://assets2.lxns.net/maimai/plate/{id.lstrip("0") or "0"}.png"
            ) as resp:
                if resp.status != 200:
                    msg = MessageSegment.text("迪拉熊没有找到合适的姓名框")
                    await set_plate.finish(
                        (MessageSegment.reply(event.message_id), msg)
                    )

                with open(plate_path, "wb") as fd:
                    async for chunk in resp.content.iter_chunked(1024):
                        fd.write(chunk)

    with shelve.open("./data/maimai/b50_config.db") as config:
        if qq not in config:
            config.setdefault(qq, {"plate": id})
        else:
            cfg = config[qq]
            if "plate" not in config[qq]:
                cfg.setdefault("plate", id)
            else:
                cfg["plate"] = id
            config[qq] = cfg

    msg = MessageSegment.text("迪拉熊帮你换好啦~")
    await set_plate.send((MessageSegment.reply(event.message_id), msg))


@set_frame.handle()
async def _(event: MessageEvent):
    qq = event.get_user_id()
    msg = event.get_plaintext()
    id = re.search(r"\d+", msg).group()
    dir_path = "./Static/maimai/Frame/"
    file_name = f"UI_Frame_{id}.png"
    file_path = Path(dir_path) / file_name
    if os.path.exists(file_path):
        with shelve.open("./data/maimai/b50_config.db") as config:
            if qq not in config:
                config.setdefault(qq, {"frame": id})
            else:
                cfg = config[qq]
                if "frame" not in config[qq]:
                    cfg.setdefault("frame", id)
                else:
                    cfg["frame"] = id
                config[qq] = cfg

        msg = MessageSegment.text("迪拉熊帮你换好啦~")
    else:
        msg = MessageSegment.text("迪拉熊没有找到合适的背景")
    await set_frame.send((MessageSegment.reply(event.message_id), msg))


@ratj_on.handle()
async def _(event: MessageEvent):
    qq = event.get_user_id()
    with shelve.open("./data/maimai/b50_config.db") as config:
        if qq not in config:
            config.setdefault(qq, {"rating_tj": True})
        else:
            cfg = config[qq]
            if "rating_tj" not in config[qq]:
                cfg.setdefault("rating_tj", True)
            else:
                cfg["rating_tj"] = True
            config[qq] = cfg

    msg = MessageSegment.text("迪拉熊帮你改好啦~")
    await ratj_on.send((MessageSegment.reply(event.message_id), msg))


@ratj_off.handle()
async def _(event: MessageEvent):
    qq = event.get_user_id()
    with shelve.open("./data/maimai/b50_config.db") as config:
        if qq not in config:
            config.setdefault(qq, {"rating_tj": False})
        else:
            cfg = config[qq]
            if "rating_tj" not in config[qq]:
                cfg.setdefault("rating_tj", False)
            else:
                cfg["rating_tj"] = False
            config[qq] = cfg

    msg = MessageSegment.text("迪拉熊帮你改好啦~")
    await ratj_off.send((MessageSegment.reply(event.message_id), msg))


@allow_other_on.handle()
async def _(event: MessageEvent):
    qq = event.get_user_id()
    with shelve.open("./data/maimai/b50_config.db") as config:
        if qq not in config:
            config.setdefault(qq, {"allow_other": True})
        else:
            cfg = config[qq]
            if "allow_other" not in config[qq]:
                cfg.setdefault("allow_other", True)
            else:
                cfg["allow_other"] = True
            config[qq] = cfg

    msg = MessageSegment.text("迪拉熊帮你改好啦~")
    await allow_other_on.send((MessageSegment.reply(event.message_id), msg))


@allow_other_off.handle()
async def _(event: MessageEvent):
    qq = event.get_user_id()
    with shelve.open("./data/maimai/b50_config.db") as config:
        if qq not in config:
            config.setdefault(qq, {"allow_other": False})
        else:
            cfg = config[qq]
            if "allow_other" not in config[qq]:
                cfg.setdefault("allow_other", False)
            else:
                cfg["allow_other"] = False
            config[qq] = cfg

    msg = MessageSegment.text("迪拉熊帮你改好啦~")
    await allow_other_off.send((MessageSegment.reply(event.message_id), msg))
