import shelve
from dill import Pickler, Unpickler

from .utils import generate_game_data

shelve.Pickler = Pickler
shelve.Unpickler = Unpickler

class OpenChars(object):
    def __init__(self):
        self.data_path = "./data/wordle.db"

    async def start(self,group_id:int):
        with shelve.open(self.data_path) as data:
            if str(group_id) in data:
                game_data = data[str(group_id)]
                return True,game_data

            game_data = data.setdefault(str(group_id), await generate_game_data())
            return False,game_data

    def game_over(self,group_id:int):
        with shelve.open(self.data_path) as data:
            data.pop(str(group_id))

    def open_char(self,group_id:int,chars:str):
        with shelve.open(self.data_path) as data:
            if str(group_id) in data:
                game_data = data[str(group_id)]
                if chars.lower() in game_data['open_chars']:
                    return False,{}

                game_data['open_chars'].append(chars.lower())
                data[str(group_id)] = game_data
                return True,game_data

            return None,None

    def get_game_data(self,group_id:int):
        with shelve.open(self.data_path) as data:
            if str(group_id) in data:
                game_data = data[str(group_id)]
                return game_data

            return None

    async def update_game_data(self,group_id:int,game_data):
        with shelve.open(self.data_path) as data:
            if str(group_id) in data:
                data[str(group_id)] = game_data

            data.setdefault(str(group_id), await generate_game_data())


openchars = OpenChars()