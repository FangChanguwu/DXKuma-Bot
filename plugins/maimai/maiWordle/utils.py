import random
import unicodedata
from util.Data import get_music_data

def check_game_over(game_data):
    return all([game_content['is_correct'] for game_content in game_data['game_contents']])

async def generate_game_data():
    game_data = {
        "open_chars":[]
    }
    game_contents = []
    temp_game_contents_ids = []
    while len(game_contents) <= 4:
        music = random.choice(await get_music_data())
        if music["id"] in temp_game_contents_ids:continue
        game_contents.append({"index":len(game_contents)+1,"title":music["title"],"music_id":int(music["id"]),"is_correct":False})
    game_data['game_contents'] = game_contents
    return game_data

def generate_message_state(game_data):
    game_state = []
    char_all_open = []
    for game_content in game_data['game_contents']:
        if game_content['is_correct']:
            game_state.append(f"{game_content['index']}."+game_content['title']+"（已猜出）")
            continue
        display_title = ""
        is_all_open = True
        for c in game_content['title']:
            if c.lower() in game_data['open_chars'] or c == ' ' or not c.isprintable():
                display_title += c
            else:
                unicode_name = unicodedata.name(c)
                if "LATIN" in unicode_name or "DIGIT" in unicode_name:
                    display_title += "□"
                elif "CJK" in unicode_name or "HIRAGANA" in unicode_name or "KATAKANA" in unicode_name:
                    display_title += "○"
                else:
                    display_title += "☆"
                is_all_open = False
        if is_all_open:
            game_content['is_correct'] = True
            char_all_open.append(f"第{game_content['index']}行的歌曲是{game_content['title']}")
            game_state.append(f"{game_content['index']}."+game_content['title']+"（已猜出）")
        else:
            game_state.append(f"{game_content['index']}."+display_title)

    is_game_over = check_game_over(game_data)
    # if is_game_over:
    #     game_state.append("所有歌曲已全部被开出来啦,游戏结束。")
    char_all_open = "猜对了！"+"\n".join(char_all_open) if char_all_open else None
    return is_game_over,"\n".join(game_state),char_all_open,game_data

def check_music_id(game_data,music_ids:list):
    guess_success = []
    for music_id in music_ids:
        for game_content in game_data['game_contents']:
            if int(music_id) == game_content['music_id'] and not game_content['is_correct']:
                guess_success.append(f"第{game_content['index']}行的歌曲是{game_content['title']}")
                game_content['is_correct'] = True
    return "猜对了！"+"\n".join(guess_success) if guess_success else None,game_data

def generate_success_state(game_data):
    game_state = []
    for game_content in game_data['game_contents']:
        game_state.append(f"{game_content['index']}."+game_content['title'])
    return "\n".join(game_state)