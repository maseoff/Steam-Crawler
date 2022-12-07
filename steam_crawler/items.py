from scrapy import Item, Field
from typing import List


class Game(Item):
    
    #
    name:          str       = Field()  # Название игры
    price:         str       = Field()  # Стоимость игры

    #
    category:      str       = Field()  # Категория
    genres:        List[str] = Field()  # Жанры игры
    tags:          List[str] = Field()  # Тэги (метки) игры

    #
    overall:       str       = Field()  # Общая оценка
    reviews_count: str       = Field()  # Суммарное число обзоров

    #
    release_date:  str       = Field()  # Дата выхода
    developers:    List[str] = Field()  # Разработчики
    publishers:    List[str] = Field()  # Издатели
    franchises:    List[str] = Field()  # Франшизы

    #
    platforms:     List[str] = Field()  # Доступные платформы
    languages:     List[str] = Field()  # Поддерживаемые языки
