from typing import List


"""
@QUERY: str - Пользовательский запрос. Парсятся продукты площадки Steam, выдываемые по указанному запросу
@FILENAME: str - Имя файла (без учета расширения), в который сохранить. Предыдущие данные затираются
"""
QUERY: str | None = "Zombie games"  # Поддерживает пустой запрос
FILENAME: str = "zombie"  # .json

"""
@TURN_ON_PAGE_SETTINGS: bool - Флаг на применение указанных настроек
@SINCE_PAGE: int | None - С какой страницы поиска начать парсинг    (None -> 1)
@TILL_PAGE: int | None - На какой странице поиска закончить парсинг (None -> +inf)
"""
TURN_ON_PAGE_SETTINGS: bool = True
SINCE_PAGE: int | None = 3
TILL_PAGE:  int | None = 19


"""
@TURN_ON_PRICE_SETTINGS: bool - Флаг на применение указанных настроек
@MIN_PRICE: float | None - Минимальная стоимость продукта включительно  (None -> 0.00)
@MAX_PRICE: float | None - Максимальная стоимость продукта включительно (None -> +inf)
"""
TURN_ON_PRICE_SETTINGS: bool = True
MIN_PRICE: float | None = 49
MAX_PRICE: float | None = 799


"""
@TURN_ON_RELEASE_SETTINGS: bool - Флаг на применение указанных настроек
@SINCE_RELEASE_YEAR: int | None - Минимальный год релиза игры включительно (None -> -inf)
@TILL_RELEASE_YEAR: int | None - Максимальный год релиза игры включительно (None -> +inf)
"""
TURN_ON_RELEASE_SETTINGS: bool = True
SINCE_RELEASE_YEAR: int | None = 2008
TILL_RELEASE_YEAR:  int | None = None


"""
@TURN_ON_OS_SETTINGS: bool - Флаг на применение указанных настроек
@ALL_OF_OS: bool | None - Флаг на обязательное присутствие всех указанных платформ.
                          Иначе, требует наличия хотя бы одной из них (None -> False).
@PLATFORMS: List[str] | None - Список платформ, хотя бы одна из которых должна поддерживаться;
                               Допустимо: "Windows", "macOS", "SteamOS + Linux" (None -> Any)
"""
TURN_ON_OS_SETTINGS: bool = False
ALL_OF_OS: bool | None = False
PLATFORMS: List[str] | None = None


"""
@TURN_ON_DEVELOPERS_SETTINGS: bool - Флаг на применение указанных настроек
@ALL_OF_DEVELOPERS: bool | None - Флаг на обязательное присутствие всех указанных разработчиков.
                                  Иначе, требует наличия хотя бы одного из них (None -> False).
@DEVELOPERS: List[str] | None - Список разработчиков, хотя бы один из которых должен был участвовать в создании игры;
                                Допустимы лишь те, что совпадают с приведенными на сайте в английском варианте (None -> Any)
"""
TURN_ON_DEVELOPERS_SETTINGS: bool = False
ALL_OF_DEVELOPERS: bool | None = False
DEVELOPERS: List[str] | None = None


"""
@TURN_ON_TAGS_SETTINGS: bool - Флаг на применение указанных настроек
@ALL_OF_TAGS: bool | None - Флаг на обязательное присутствие всех указанных тэгов.
                            Иначе, требует наличия хотя бы одного из них (None -> False).
@TAGS: List[str] | None - Список тэгов (меток) игры, хотя бы один из которых жолжен присутствовать;
                          Допустимы лишь те, что совпадают с приведенными на сайте в английском варианте (None -> Any)
"""
TURN_ON_TAGS_SETTINGS: bool = True
ALL_OF_TAGS: bool | None = False
TAGS: List[str] | None = ["Zombies", "Survival", "Horror"]


"""
@TURN_ON_LANGUAGE_SETTINGS: bool - Флаг на применение указанных настроек
@ALL_OF_LANGUAGES: bool | None - Флаг на обязательное наличие поддержки всех указанных языков.
                                 Иначе, требует наличия хотя бы одного из них (None -> False).
@LANGUAGES: List[str] | None- Список поддерживаемых продуктом языков;
                              Допустимы лишь те, что совпадают с приведенными на сайте в английском варианте (None -> Any)
"""
TURN_ON_LANGUAGE_SETTINGS: bool = True
ALL_OF_LANGUAGES: bool | None = True
LANGUAGES: List[str] | None = ["Russian"]


"""
@TURN_ON_GENRE_SETTINGS: bool - Флаг на применение указанных настроек
@ALL_OF_GENRES: bool | None - Флаг на обязательное присутствие всех указанных жанров.
                              Иначе, требует наличия хотя бы одного из них (None -> False).
@GENRES: List[str] | None - Список жанров, к хотя бы одному из которых должен относиться продукт;
                            Допустимы лишь те, что совпадают с приведенными на сайте в английском варианте (None -> Any)
"""
TURN_ON_GENRE_SETTINGS: bool = False
ALL_OF_GENRES: bool | None = False
GENRES: List[str] | None = None


"""
@TURN_ON_PUBLISHER_SETTINGS: bool - Флаг на применение указанных настроек
@ALL_OF_PUBLISHERS: bool | None - Флаг на обязательное присутствие всех указанных издателей.
                                  Иначе, требует наличия хотя бы одного из них (None -> False).
@PUBLISHERS: List[str] | None - Список издателей, хотя бы один из которых должен был участвовать в издании игры;
                                Допустимы лишь те, что совпадают с приведенными на сайте в английском варианте (None -> Any)
"""
TURN_ON_PUBLISHER_SETTINGS: bool = False
ALL_OF_PUBLISHERS: bool | None = False
PUBLISHERS: List[str] | None = None


"""
@TURN_ON_FRANCHISE_SETTINGS: bool - Флаг на применение указанных настроек
@ALL_OF_FRANCHISES: bool | None - Флаг на то, что игра обязательно относится ко всем указанным франшизам.
                                  Иначе, требует наличия вхождения хотя бы в одну из них (None -> False).
@FRANCHISES: List[str] | None - Список франшиз, хотя бы к одной из которых относится продукт;
                                Допустимы лишь те, что совпадают с приведенными на сайте в английском варианте (None -> Any)
"""
TURN_ON_FRANCHISE_SETTINGS: bool = False
ALL_OF_FRANCHISES: bool | None = False
FRANCHISES: List[str] | None = None
