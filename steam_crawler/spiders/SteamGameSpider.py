from typing import Generator, List

from bs4 import BeautifulSoup
from scrapy import Spider, Request
from scrapy.http import Response

from steam_crawler.items import Game

import re
import requests
import user_settings


DESCRIPTION_WITH_FRANCHISE_REGEXPR = r"(Title:)(.*)(Genre:)(.+)(Developer:)(.+)(Publisher:)(.+)(Franchise:)(.+)(Release Date:)(.+)"
DESCRIPTION_WITHOUT_FRANCHISE_REGEXPR = r"(Title: )(.*)(Genre:)(.+)(Developer:)(.+)(Publisher:)(.+)(Release Date:)(.+)"

RELEASE_DATE_WITH_DAY_REGEXPR = r"^(\d+) ([a-zA-Z]+)(, )(\d+)"
RELEASE_DATE_WITHOUT_DAY_REGEXPR = r"^([a-zA-Z]+)( )(\d+)"

URL_SETTINGS = [
    "ndl=1",                 # Отключаем английский как обязательный поддерживаемый язык
    "ignore_preferences=1",  # Отключаем поиск по рекомендациям, который может отсеивать какие-то продукты
]

SEARCH_URL = "https://store.steampowered.com/search/?" + "&".join(URL_SETTINGS)

TRANSFORMATIONS = {
            r"+": r"%2B",
            r",": r"%2C",
            r":": r"%3A",
            r"/": r"%2F",
            "\\": r"%5C",
            r"?": r"%3F",
            r"'": r"%27",
            r"`": r"%60",
            r"!": r"%21",
            r"[": r"%5B",
            r"]": r"%5D",
            r"(": r"%28",
            r")": r"%29",
            r"{": r"%7B",
            r"}": r"%7D",
            r"%": r"%25",
            r"@": r"%40",
            r"#": r"%23",
            r"$": r"%24",
            r"^": r"%5E",
            r"&": r"%26",
            r"|": r"%7C",     
        }


class SteamGameSpider(Spider):
    name: str = "SteamGameSpider"
    allowed_domains: List[str] = ["store.steampowered.com"]

    # Public:
    def start_requests(self) -> Generator:
        since_page = user_settings.SINCE_PAGE
        if not user_settings.TURN_ON_PAGE_SETTINGS or since_page is None:
            since_page = 1

        till_page = user_settings.TILL_PAGE
        if not user_settings.TURN_ON_PAGE_SETTINGS or till_page is None:
            till_page = 10_000

        anchor = self.__form_query_anchor(user_settings.QUERY)
        query_url = "&".join([SEARCH_URL,  anchor]) if anchor else SEARCH_URL

        for page_number in range(since_page, till_page + 1):
            
            url = "&".join([query_url, self.__form_page_anchor(page=page_number)])
            request = requests.get(url)
            if request.status_code != 200:
                continue

            page = request.content.decode(encoding="utf-8")
            if self.__is_empty_query_search_page(page=page):
                return

            for product_url in self.__get_products_urls_from_query_search_page(page=page):
                yield Request(url=product_url)

    def parse(self, response: Response) -> Generator:
        page = response.text
        if not self.__is_product_page(page=page):
            return

        if not self.__is_released_product(page=page):
            return

        if self.__is_dlc_page(page=page):
            return

        if self.__is_soundtrack_page(page=page):
            return

        soup = BeautifulSoup(page, "html.parser")
        game = Game()

        name = self.__get_name(soup=soup)
        category = self.__get_category(soup=soup)
        overall = self.__get_overall(soup=soup)
        reviews_count = self.__get_reviews_count(soup=soup)

        price = self.__get_price(soup=soup)
        if user_settings.TURN_ON_PRICE_SETTINGS and not self.__is_required_price(price):
            return

        genres = self.__get_genres(soup=soup)
        if user_settings.TURN_ON_GENRE_SETTINGS and not self.__has_required_genres(genres):
            return

        tags = self.__get_tags(soup=soup)
        if user_settings.TURN_ON_TAGS_SETTINGS and not self.__has_required_tags(tags):
            return
        
        release_date = self.__get_release_date(soup=soup)
        if user_settings.TURN_ON_RELEASE_SETTINGS and not self.__is_required_release_year(release_date):
            return

        developers = self.__get_developers(soup=soup)
        if user_settings.DEVELOPERS and not self.__has_required_developers(developers):
            return

        publishers = self.__get_publishers(soup=soup)
        if user_settings.TURN_ON_PUBLISHER_SETTINGS and not self.__has_required_publishers(publishers):
            return

        franchises = self.__get_franchises(soup=soup)
        if user_settings.TURN_ON_FRANCHISE_SETTINGS and not self.__has_required_franchises(franchises):
            return

        platforms = self.__get_platforms(soup=soup)
        if user_settings.TURN_ON_OS_SETTINGS and not self.__has_required_platforms(platforms):
            return

        languages = self.__get_languages(soup=soup)
        if user_settings.TURN_ON_LANGUAGE_SETTINGS and not self.__has_required_languages(languages):
            return

        game["name"] = name
        game["price"] = price
        game["category"] = category
        game["genres"] = genres
        game["tags"] = tags
        game["overall"] = overall
        game["reviews_count"] = reviews_count
        game["release_date"] = release_date
        game["developers"] = developers
        game["publishers"] = publishers
        game["franchises"] = franchises
        game["platforms"] = platforms
        game["languages"] = languages

        yield game

    # Private:
    def __get_name(self, soup: BeautifulSoup) -> str:
        description = self.__get_game_description(soup=soup)
        belongs_to_franchise = self.__belongs_to_franchise(game_description=description)
        
        regexpr = DESCRIPTION_WITH_FRANCHISE_REGEXPR if belongs_to_franchise else DESCRIPTION_WITHOUT_FRANCHISE_REGEXPR
        return re.sub(regexpr, r"\2", description).strip()

    def __get_price(self, soup: BeautifulSoup) -> str:
        price = soup.find(name="meta", attrs={"itemprop": "price"})["content"].strip()
        currency = soup.find(name="meta", attrs={"itemprop": "priceCurrency"})["content"].strip()

        return f"{price} {currency}"

    def __get_category(self, soup: BeautifulSoup) -> str:
        category_blocks = soup.find(name="div", attrs={"class": "blockbg"}).find_all(name="a")
        labels = list()

        for index in range(1, len(category_blocks) - 1):
            category = category_blocks[index]

            label = category.text.strip()
            labels.append(label)

        return " > ".join(labels)

    def __get_genres(self, soup: BeautifulSoup) -> List[str]:
        description = self.__get_game_description(soup=soup)
        belongs_to_franchise = self.__belongs_to_franchise(game_description=description)

        regexpr = DESCRIPTION_WITH_FRANCHISE_REGEXPR if belongs_to_franchise else DESCRIPTION_WITHOUT_FRANCHISE_REGEXPR
        genres_str = re.sub(regexpr, r"\4", description).strip()

        genres = list(map(lambda genre: genre.strip(), genres_str.split(",")))
        return genres

    def __get_tags(self, soup: BeautifulSoup) -> List[str]:
        tags = list()
        for block in soup.find_all(name="a", attrs={"class": "app_tag"}):

            tag = block.text.strip()
            tags.append(tag)

        return tags

    def __has_reviews(self, soup: BeautifulSoup) -> bool:
        block = soup.find(name="div", attrs={"class": "noReviewsYetTitle"})
        if block is None:
            return True

        text = block.string.strip()
        if text == "There are no reviews for this product":
            return False

        block = soup.find(name="span", attrs={"class": "game_review_summary no_reviews"})
        if block is None:
            return True

        text = block.string.strip()
        return text.lower() != "no user reviews"

    def __get_overall(self, soup: BeautifulSoup) -> str:
        if not self.__has_reviews(soup=soup):
            return "No User Reviews"

        return soup.find(name="span", attrs={"itemprop": "description"}).string.strip()

    def __get_reviews_count(self, soup: BeautifulSoup) -> str:
        if not self.__has_reviews(soup=soup):
            return "0"

        count = soup.find(name="label", attrs={"for": "review_type_all"}).span.text
        return re.sub(r"(\()(.*)(\))", r"\2", count)  # Format before re: "(count)"

    def __get_release_date(self, soup: BeautifulSoup) -> str:
        description = self.__get_game_description(soup=soup)
        belongs_to_franchise = self.__belongs_to_franchise(game_description=description)

        regexpr = DESCRIPTION_WITH_FRANCHISE_REGEXPR if belongs_to_franchise else DESCRIPTION_WITHOUT_FRANCHISE_REGEXPR
        substitution = r"\12" if belongs_to_franchise else r"\10"

        return re.sub(regexpr, substitution, description).strip()

    def __get_developers(self, soup: BeautifulSoup) -> List[str]:
        description = self.__get_game_description(soup=soup)
        belongs_to_franchise = self.__belongs_to_franchise(game_description=description)

        regexpr = DESCRIPTION_WITH_FRANCHISE_REGEXPR if belongs_to_franchise else DESCRIPTION_WITHOUT_FRANCHISE_REGEXPR
        developers_str = re.sub(regexpr, r"\6", description).strip()

        developers = list(map(lambda dev: dev.strip(), developers_str.split(",")))
        return developers

    def __get_publishers(self, soup: BeautifulSoup) -> List[str]:
        description = self.__get_game_description(soup=soup)
        belongs_to_franchise = self.__belongs_to_franchise(game_description=description)

        regexpr = DESCRIPTION_WITH_FRANCHISE_REGEXPR if belongs_to_franchise else DESCRIPTION_WITHOUT_FRANCHISE_REGEXPR
        publishers_str = re.sub(regexpr, r"\8", description).strip()

        publishers = list(map(lambda pub: pub.strip(), publishers_str.split(",")))
        return publishers

    def __get_franchises(self, soup: BeautifulSoup) -> List[str]:
        description = self.__get_game_description(soup=soup)
        if not self.__belongs_to_franchise(game_description=description):
            return []

        franchises_str = re.sub(DESCRIPTION_WITH_FRANCHISE_REGEXPR, r"\10", description).strip()
        return list(map(lambda fr: fr.strip(), franchises_str.split(",")))

    def __get_platforms(self, soup: BeautifulSoup) -> List[str]:
        systems = list()
        os_to_full_name = {
            "win": "Windows",
            "mac": "macOS",
            "linux": "SteamOS + Linux",
        }

        for block in soup.find_all(name="div", attrs={"class": re.compile(r"game_area_sys_req sysreq_content")}):
            op_sys = block["data-os"]  # One of: "win", "max", "linux"
            systems.append(os_to_full_name[op_sys])

        return systems

    def __get_languages(self, soup: BeautifulSoup) -> List[str]:
        languages = list()
        for block in soup.find_all("td", attrs={"class": "ellipsis"}):
            
            language = block.string.strip()
            languages.append(language)

        return languages

    def __get_game_description(self, soup: BeautifulSoup) -> str:
        about_block = soup.find(name="div", attrs={"class": "details_block", "id": "genresAndManufacturer"})
        return about_block.text.replace("\n", " ").strip()

    def __belongs_to_franchise(self, game_description: str) -> bool:
        return True if re.match(DESCRIPTION_WITH_FRANCHISE_REGEXPR, game_description) else False

    def __any_of_in(self, required: List[str], existing: List[str]) -> bool:
        if required is None or required == []:
            return True

        if existing is None or existing == []:
            return False

        required_labels = set()
        for label in required:
            required_labels.add(label)

        for label in existing:
            if label in required_labels:
                return True

        return False

    def __all_of_in(self, required: List[str], existing: List[str]) -> bool:
        if required is None or required == []:
            return True

        if existing is None or existing == []:
            return False

        required_labels = set()
        for label in required:
            required_labels.add(label)

        for label in existing:
            required_labels.discard(label)

        return not required_labels  # Must be empty if OK

    def __is_required_price(self, price: str) -> bool:
        min_price = user_settings.MIN_PRICE
        if min_price is None:
            min_price = 0

        max_price = user_settings.MAX_PRICE
        if max_price is None:
            max_price = 1_000_000_000

        float_price = float(price.replace(",", ".").split()[0])  # Format: "Price Currency"
        return min_price <= float_price <= max_price

    def __is_required_release_year(self, release_date: str) -> bool:
        since_year = user_settings.SINCE_RELEASE_YEAR
        if since_year is None:
            since_year = 1900

        till_year = user_settings.TILL_RELEASE_YEAR
        if till_year is None:
            till_year = 3000

        is_date_with_day = True if re.match(RELEASE_DATE_WITH_DAY_REGEXPR, release_date) else False
        regexpr = RELEASE_DATE_WITH_DAY_REGEXPR if is_date_with_day else RELEASE_DATE_WITHOUT_DAY_REGEXPR
        substitution = r"\4" if is_date_with_day else r"\3"

        year = int(re.sub(regexpr, substitution, release_date))
        return since_year <= year <= till_year

    def __has_required_platforms(self, platforms: List[str] | None) -> bool:
        if user_settings.ALL_OF_OS:
            return self.__all_of_in(user_settings.PLATFORMS, platforms)
        else:
            return self.__any_of_in(user_settings.PLATFORMS, platforms)

    def __has_required_developers(self, developers: List[str] | None) -> bool:
        if user_settings.ALL_OF_DEVELOPERS:
            return self.__all_of_in(user_settings.DEVELOPERS, developers)
        else:
            return self.__any_of_in(user_settings.DEVELOPERS, developers)

    def __has_required_tags(self, tags: List[str] | None) -> bool:
        if user_settings.ALL_OF_TAGS:
            return self.__all_of_in(user_settings.TAGS, tags)
        else:
            return self.__any_of_in(user_settings.TAGS, tags)

    def __has_required_languages(self, languages: List[str] | None) -> bool:
        if user_settings.ALL_OF_LANGUAGES:
            return self.__all_of_in(user_settings.LANGUAGES, languages)
        else:
            return self.__any_of_in(user_settings.LANGUAGES, languages)

    def __has_required_genres(self, genres: List[str] | None) -> bool:
        if user_settings.ALL_OF_GENRES:
            return self.__all_of_in(user_settings.GENRES, genres)
        else:
            return self.__any_of_in(user_settings.GENRES, genres)

    def __has_required_publishers(self, publishers: List[str] | None) -> bool:
        if user_settings.ALL_OF_PUBLISHERS:
            return self.__all_of_in(user_settings.PUBLISHERS, publishers)
        else:
            return self.__any_of_in(user_settings.PUBLISHERS, publishers)

    def __has_required_franchises(self, franchises: List[str] | None) -> bool:
        if user_settings.ALL_OF_FRANCHISES:
            return self.__all_of_in(user_settings.FRANCHISES, franchises)
        else:
            return self.__any_of_in(user_settings.FRANCHISES, franchises)

    def __form_query_anchor(self, query: str) -> str:
        if not query:
            return ""

        anchor = query
        for before, after in TRANSFORMATIONS.items():
            anchor = anchor.replace(before, after)

        return f'term={"+".join(anchor.split(" "))}'

    def __form_page_anchor(self, page: int) -> str:
        return f"page={page}"

    def __is_empty_query_search_page(self, page: str) -> bool:
        soup = BeautifulSoup(page, "html.parser")
        return not soup.find_all(name="a", attrs={"class": re.compile("search_result_row ds_collapse_flag")})

    def __get_products_urls_from_query_search_page(self, page: str) -> List[str]:
        soup = BeautifulSoup(page, "html.parser")
        urls = list()

        for block in soup.find_all(name="a", attrs={"class": re.compile("search_result_row ds_collapse_flag")}):
            urls.append(block["href"])

        return urls

    def __is_product_page(self, page: str) -> bool:
        soup = BeautifulSoup(page, "html.parser")
        about_block = soup.find(name="div", attrs={"class": "details_block", "id": "genresAndManufacturer"})
        return about_block is not None

    def __is_dlc_page(self, page: str) -> bool:
        if not self.__is_product_page(page):
            return False

        soup = BeautifulSoup(page, "html.parser")
        block = soup.find(name="div", attrs={"class": "block responsive_apppage_details_right heading responsive_hidden"})

        text = block.string.strip()
        return text == "Is this DLC relevant to you?"

    def __is_soundtrack_page(self, page: str) -> bool:
        if not self.__is_product_page(page):
            return False

        soup = BeautifulSoup(page, "html.parser")
        block = soup.find(name="div", attrs={"class": "block responsive_apppage_details_right heading responsive_hidden"})

        text = block.string.strip()
        return text == "Is this soundtrack relevant to you?"

    def __is_released_product(self, page: str) -> bool:
        soup = BeautifulSoup(page, "html.parser")

        block = soup.find(name="span", attrs={"class": "not_yet"})
        if block is not None:
            return False

        release_date = self.__get_release_date(soup=soup)
        return release_date.lower() not in [
            "coming soon",
            "to be announced",
        ]
