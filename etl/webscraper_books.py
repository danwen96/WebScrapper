import time
import pathlib
import json
from telnetlib import EC

import selenium
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

from etl import utils

DRIVER_PATH = "/usr/bin/chromedriver"
PATH_TO_STATE = f"{pathlib.Path(__file__).parent}/state"
PATH_TO_DATA = f"{pathlib.Path(__file__).parent}/state/data"


def extract_data():
    """
    Extracts the data from the web page
    :return:
    """
    books = WebScraper().get_top_100_data()
    time.sleep(2)
    BookDetailsWebScrapper().save_book_details(books)
    _save_extract_state(books)


def _save_extract_state(books):
    """
    Saves information about successful extraction
    :return:
    """
    extract_state = {
        'current_state': 0,
        'books': books
    }
    with open(f'{PATH_TO_STATE}/current_state.json', 'w') as f:
        json.dump(extract_state, f)


def transform_data():
    """
    Transforms the collected data
    :return:
    """
    with open(f'{PATH_TO_STATE}/current_state.json', 'r') as f:
        cur_state = json.load(f)
    if cur_state['current_state'] != 0:
        print("You have to extract before transforming the data!")
        return
    books = cur_state['books']
    BookDetailsWebScrapper().transform_book_details(books)
    _save_transform_state(books)
    print("Data successfully transformed, it is ready to be loaded to data base!")


def _save_transform_state(books):
    """
    Saves the transformed data to load it later
    :param books:
    :return:
    """
    utils.clear_data()
    transform_state = {
        'current_state': 1,
        'books': books
    }
    with open(f'{PATH_TO_STATE}/current_state.json', 'w') as f:
        json.dump(transform_state, f)


class WebScraper:

    def __init__(self):
        self.BASE_URL="https://lubimyczytac.pl"
        self.TOP_100_BOOKS_URL= "{}/top100".format(self.BASE_URL)
        # options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(DRIVER_PATH, chrome_options=chrome_options)
        self.driver.set_page_load_timeout(20)
        self.FIRST_PAGE_TO_CLICK = 2
        self.NMB_OF_PAGES = 15

    def get_top_100_data(self):
        """
        Creates list with books from top150 category on lubimyczytac.pl.
        Returned list of books contains details like book name, book author, book href, book_rating,
        nmb_of_ratings
        :return: List with dicts containing books data
        """
        self.driver.get(self.TOP_100_BOOKS_URL)

        cookies_button = self.driver.find_element_by_xpath("/html/body")
        cookies_button.click()

        books_list = []

        print("Getting books data from page 1")
        try:
            for page_numb in range(self.FIRST_PAGE_TO_CLICK, self.NMB_OF_PAGES+2):
                content = self.driver.page_source
                page_soup = BeautifulSoup(content, features='html.parser')
                books_list += self._get_books_from_page(page_soup)

                if page_numb == self.NMB_OF_PAGES+1:
                    break
                self._load_page(page_numb)
                print(f"Getting books data from page {page_numb}")
        except:
            pass

        return books_list

    def _load_page(self, page_numb):
        link = self.driver.find_element_by_xpath(f"//a[@data-pager-page='{page_numb}']")
        time.sleep(4)
        self.driver.execute_script("arguments[0].click();", link)
        time.sleep(4)

    def _get_books_from_page(self, page_soup):
        books_collection_from_page = []
        for book_soup in page_soup.findAll('div', attrs={'class': 'authorAllBooks__single'}):
            book = self._get_data_from_book_element(book_soup)
            books_collection_from_page.append(book)
        return books_collection_from_page

    @staticmethod
    def _get_data_from_book_element(book_soup) -> dict:
        book_name_soup = book_soup\
            .find('a', attrs={'class': 'authorAllBooks__singleTextTitle'})
        author_name_soup = book_soup\
            .find('div', attrs={'class': 'authorAllBooks__singleTextAuthor'})\
            .find('a')
        book_rating_soup = book_soup\
            .find('span', attrs={'class': 'listLibrary__ratingStarsNumber'})
        nmb_of_ratings_soup = book_soup\
            .find('div', attrs={'class': 'listLibrary__ratingAll'})
        return {
            'book_name': book_name_soup.text.strip(),
            'book_page_href': book_name_soup.attrs['href'],
            'author_name': author_name_soup.text.strip(),
            'book_rating': float(book_rating_soup.text.strip().replace(',', '.')),
            'nmb_of_ratings': int(nmb_of_ratings_soup.text.replace('ocen', '').strip())
        }


class BookDetailsWebScrapper(WebScraper):

    def __init__(self):
        super().__init__()

    def save_book_details(self, book_dict_with_href):
        """
        Saves each book page to file in data
        :param book_dict_with_href:
        :return:
        """
        for i, book_dict in enumerate(book_dict_with_href):
            print(f'Saving data for book {i + 1}')
            self._save_book_detail(book_dict, i)

    def _save_book_detail(self, book_dict, book_nmb):
        """
        Saves details about given book to file
        :param book_dict:
        :return:
        """
        content = self._get_book_content(book_dict['book_page_href'])
        with open(f'{PATH_TO_DATA}/{book_nmb}.html', 'w') as file:
            file.write(content)

    def transform_book_details(self, books_dict):
        """
        Transforms the book details
        :param books_dict:
        :return:
        """
        for i, book_dict in enumerate(books_dict):
            print(f'Transforming data for book {i + 1}')
            with open(f'{PATH_TO_DATA}/{i}.html', 'r') as f:
                content = f.read()
            self._add_book_details(book_dict, content)

    def add_books_details(self, books_dict_with_href):
        """
        Adds more info to each book by using its href address
        :param books_dict_with_href: List of dicts with books details that is going to have
        additional information added
        :return: None
        """
        for i, book_dict in enumerate(books_dict_with_href):
            print(f'Getting more details for book {i + 1}')
            book_content = self._get_book_content(book_dict['book_page_href'])
            self._add_book_details(book_dict, book_content)

    def _add_book_details(self, book_dict, content):
        book_page_soup = BeautifulSoup(content, features='html.parser')
        book_dict['genres'] = book_page_soup\
            .find('a', attrs={'class': 'book__category'}).text.strip()
        book_dict['nmb_of_opinions'] = int(book_page_soup
                                           .find('a', attrs={'href': '#lista-opinii'}).text
                                           .replace('opinii', '').strip())
        try:
            book_dict['nmb_of_pages'] = int(book_page_soup
                                            .find('span', attrs={'class': 'book__pages'}).text
                                            .replace('str.', '').strip())
            book_dict['apx_reading_time'] = book_page_soup\
                .find('span', attrs={'class': 'book__hours'})\
                .find('span', attrs={'class': 'js-hours'}).text.strip()
        except AttributeError:
            pass
        self._add_book_stores_with_prices_to_book(book_dict, book_page_soup)

    def _add_book_stores_with_prices_to_book(self, book_dict, book_page_soup):
        book_stores_recommended_soup_list = book_page_soup\
            .find('div', attrs={'id': 'buybox-bookstores-promoted'})\
            .find_all('a', attrs={'data-type': 'książka'})
        book_stores_others_soup = book_page_soup\
            .find('div', attrs={'id': 'buybox-bookstores'})\
            .find_all('a', attrs={'data-type': 'książka'})

        recommended_book_stores_with_prices = self._create_dict_with_store_and_price(
            book_stores_recommended_soup_list)
        book_stores_others_soup = self._create_dict_with_store_and_price(
            book_stores_others_soup)

        book_dict['book_stores_with_prices'] = {**recommended_book_stores_with_prices,
                                                **book_stores_others_soup}
        book_values = book_dict['book_stores_with_prices'].values()
        book_dict['avg_book_price'] = sum(book_values)/len(book_values) if len(book_values) != 0 \
            else 0.0

    @staticmethod
    def _create_dict_with_store_and_price(book_store_soup_list):
        book_store_with_prices_dict = {}
        for book_store_soup in book_store_soup_list:
            book_store_name = book_store_soup\
                .find('div', attrs={'class': 'bookstore-name'}).text.strip()
            book_store_price = book_store_soup\
                .find('div', attrs={'class': 'bookstore-item-price'}).text\
                .replace('\xa0zł', '')\
                .replace('od', '')\
                .strip()
            book_store_price = float(book_store_price)
            book_store_with_prices_dict[book_store_name] = book_store_price

        return book_store_with_prices_dict

    def _get_book_content(self, book_href) -> str:
        is_content_rdy = False
        while not is_content_rdy:
            try:
                self.driver.get(self.BASE_URL + book_href)
                content = self.driver.page_source
                is_content_rdy = True
            except TimeoutException:
                print("Trying to get page again")
        return content
