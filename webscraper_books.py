import time

import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import collections


DRIVER_PATH = "/usr/bin/chromedriver"

Book = collections.namedtuple('Book', 'book_name author_name book_rating nmb_of_ratings')


class WebScraper:

    def __init__(self):
        self.TOP_100_BOOKS_URL= "https://lubimyczytac.pl/top100"
        # options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        self.driver = webdriver.Chrome(DRIVER_PATH)
        self.FIRST_PAGE_TO_CLICK = 2
        self.NMB_OF_PAGES = 8

    def get_top_100_data(self):
        self.driver.get(self.TOP_100_BOOKS_URL)

        books_collection = []

        cookies_button = self.driver.find_element_by_xpath("/html/body")
        cookies_button.click()

        books_list = []

        for page_numb in range(self.FIRST_PAGE_TO_CLICK, self.NMB_OF_PAGES+2):
            content = self.driver.page_source
            page_soup = BeautifulSoup(content, features='html.parser')
            books_list += self._get_books_from_page(page_soup)

            if page_numb == self.NMB_OF_PAGES+1:
                break

            self._load_page(page_numb)

        return books_list

    def _load_page(self, page_numb):
        link = self.driver.find_element_by_xpath(f"//a[@data-pager-page='{page_numb}']")
        print(link.get_attribute('innerHTML'))
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
    def _get_data_from_book_element(book_soup) -> Book:
        book_name_soup = book_soup.find('a', attrs={'class': 'authorAllBooks__singleTextTitle'})
        author_name_soup = book_soup.find('div', attrs={'class': 'authorAllBooks__singleTextAuthor'})\
                                    .find('a')
        book_rating_soup = book_soup.find('span', attrs={'class': 'listLibrary__ratingStarsNumber'})
        nmb_of_ratings_soup = book_soup.find('div', attrs={'class': 'listLibrary__ratingAll'})
        return Book(
            book_name=book_name_soup.text.strip(),
            author_name=author_name_soup.text.strip(),
            book_rating=float(book_rating_soup.text.strip().replace(',', '.')),
            nmb_of_ratings=int(nmb_of_ratings_soup.text.replace('ocen', '').strip())
        )




if __name__ == '__main__':
    print("Hello")
    books = WebScraper().get_top_100_data()
    for i, book in enumerate(books):
        print(f"{i}\t\t {book}")
