from nonebot import on_fullmatch,on_message,on_regex,on_startswith
import re
from nonebot.adapters.onebot.v11 import GroupMessageEvent,MessageSegment
from .database import openchars
from .utils import generate_message_state,check_music_id,generate_success_state
from util.Data import get_music_data, find_songid_by_alias

start_open_chars = on_regex('dlx猜歌', re.I)
@start_open_chars.handle()
async def _(event: GroupMessageEvent):
    group_id = event.group_id
    is_exist,game_data = await openchars.start(group_id)
    await start_open_chars.send("准备开始猜歌游戏！\n□：字母或数字\n○：假名或汉字\n☆：符号\n\n发送“开（字母）”开出字母\n发送“结束猜歌”结束\n发送别名或ID即可猜歌")
    is_game_over,game_state,char_all_open,game_data = generate_message_state(game_data)
    # openchars.update_game_data(group_id,game_data)
    await start_open_chars.send(game_state)
    # if is_game_over:
    #     openchars.game_over(group_id)
    #     await start_open_chars.send('全部答对啦，恭喜各位🎉\n本轮猜歌已结束，可发送“dlx猜歌”再次游玩')


open_chars = on_startswith("开")
@open_chars.handle()
async def _(event: GroupMessageEvent):
    msg = event.get_plaintext()
    char = msg.replace("开", "").strip()
    group_id = event.group_id

    if len(char) != 1:
        await open_chars.finish()

    is_start,game_data = openchars.open_char(group_id,char)
    if is_start is not None:
        if is_start:
            is_game_over,game_state,char_all_open,game_data = generate_message_state(game_data)
            await openchars.update_game_data(group_id,game_data)

            if char_all_open:
                await open_chars.send(char_all_open)
            await open_chars.send(game_state)
            if is_game_over:
                openchars.game_over(group_id)
                await open_chars.send('全部答对啦，恭喜各位🎉\n本轮猜歌已结束，可发送“dlx猜歌”再次游玩')
        else:
            await open_chars.send([MessageSegment.reply(event.message_id),MessageSegment.text("该字母已经开过了噢，换一个字母吧~")])


all_message_handle = on_message(priority=18,block=False)
@all_message_handle.handle()
async def _(event: GroupMessageEvent):
    group_id = event.group_id
    game_data = openchars.get_game_data(group_id)
    if game_data:
        msg_content = event.get_plaintext()
        songList = await get_music_data()
        if msg_content.isnumeric():
            music_ids = [d["id"] for d in songList if d["id"] == msg_content]
        elif msg_content:
            music_ids = await find_songid_by_alias(msg_content, songList)

        if music_ids:
            guess_success,game_data = check_music_id(game_data,music_ids)
            if guess_success:
                await all_message_handle.send(guess_success)
                is_game_over,game_state,char_all_open,game_data = generate_message_state(game_data)
                if is_game_over:
                    openchars.game_over(group_id)
                    await start_open_chars.send('全部答对啦，恭喜各位🎉\n本轮猜歌已结束，可发送“dlx猜歌”再次游玩')
                else:
                    await openchars.update_game_data(group_id,game_data)
                await start_open_chars.send(game_state)


pass_game = on_fullmatch('结束猜歌',priority=20)
@pass_game.handle()
async def _(event: GroupMessageEvent):
    group_id = event.group_id
    game_data = openchars.get_game_data(group_id)
    if game_data:
        await pass_game.send(generate_success_state(game_data))
        await pass_game.send("本轮猜歌已结束，可发送“dlx猜歌”再次游玩")
        openchars.game_over(group_id)