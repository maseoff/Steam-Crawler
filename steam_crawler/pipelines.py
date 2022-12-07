from itemadapter import ItemAdapter
from typing import IO

from steam_crawler.items import Game
from steam_crawler.spiders.SteamGameSpider import SteamGameSpider

import json
import user_settings


class SteamCrawlerPipeline(object):

    __slots__ = ["__file"]

    def __init__(self) -> None:
        self.__file: IO = None

    def open_spider(self, spider: SteamGameSpider) -> None:
        self.__file = open(file=f"{user_settings.FILENAME}.json", mode="w")

    def close_spider(self, spider: SteamGameSpider) -> None:
        self.__file.close()

    def process_item(self, game: Game, spider: SteamGameSpider) -> Game:
        line = json.dumps(ItemAdapter(game).asdict()) + "\n"
        self.__file.write(line)
        return game
