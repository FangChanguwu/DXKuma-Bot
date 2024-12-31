import json
import os
from asyncio import Lock
from datetime import date
from os import path

from aiohttp import ClientSession

music_data_lock = Lock()
chart_stats_lock = Lock()
alias_list_lxns_lock = Lock()
alias_list_ycn_lock = Lock()


async def get_music_data():
    cache_dir = "./Cache/Data/MusicData/"
    cache_path = f"{cache_dir}{date.today().isoformat()}.json"
    async with music_data_lock:
        if not path.exists(cache_path):
            files = os.listdir(cache_dir)
            async with ClientSession() as session:
                async with session.get(
                    "https://www.diving-fish.com/api/maimaidxprober/music_data"
                ) as resp:
                    with open(cache_path, "wb") as fd:
                        async for chunk in resp.content.iter_chunked(1024):
                            fd.write(chunk)
            if files:
                for file in files:
                    os.remove(f"{cache_dir}{file}")
    with open(cache_path) as fd:
        return json.loads(fd.read())


async def get_chart_stats():
    cache_dir = "./Cache/Data/ChartStats/"
    cache_path = f"{cache_dir}{date.today().isoformat()}.json"
    async with chart_stats_lock:
        if not path.exists(cache_path):
            files = os.listdir(cache_dir)
            async with ClientSession() as session:
                async with session.get(
                    "https://www.diving-fish.com/api/maimaidxprober/chart_stats"
                ) as resp:
                    with open(cache_path, "wb") as fd:
                        async for chunk in resp.content.iter_chunked(1024):
                            fd.write(chunk)
            if files:
                for file in files:
                    os.remove(f"{cache_dir}{file}")
    with open(cache_path) as fd:
        return json.loads(fd.read())


async def get_alias_list_lxns():
    cache_dir = "./Cache/Data/Alias/Lxns/"
    cache_path = f"{cache_dir}{date.today().isoformat()}.json"
    async with alias_list_lxns_lock:
        if not os.path.exists(cache_path):
            files = os.listdir(cache_dir)
            async with ClientSession() as session:
                async with session.get(
                    "https://maimai.lxns.net/api/v0/maimai/alias/list"
                ) as resp:
                    with open(cache_path, "wb") as fd:
                        async for chunk in resp.content.iter_chunked(1024):
                            fd.write(chunk)
            if files:
                for file in files:
                    os.remove(f"{cache_dir}{file}")
    with open(cache_path) as fd:
        return json.loads(fd.read())


async def get_alias_list_ycn():
    cache_dir = "./Cache/Data/Alias/YuzuChaN/"
    cache_path = f"{cache_dir}{date.today().isoformat()}.json"
    async with alias_list_ycn_lock:
        if not os.path.exists(cache_path):
            files = os.listdir(cache_dir)
            async with ClientSession() as session:
                async with session.get(
                    "https://api.yuzuchan.moe/maimaidx/maimaidxalias"
                ) as resp:
                    with open(cache_path, "wb") as fd:
                        async for chunk in resp.content.iter_chunked(1024):
                            fd.write(chunk)
            if files:
                for file in files:
                    os.remove(f"{cache_dir}{file}")
    with open(cache_path) as fd:
        return json.loads(fd.read())


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
