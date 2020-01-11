import mysql.connector
import pathlib
import json
import csv

from datetime import datetime

from etl import utils

PATH_TO_STATE = f"{pathlib.Path(__file__).parent}/state"
PATH_TO_EXPORTS = f"{pathlib.Path(__file__).parent}/../exports"


def load_data():
    """
    Performs loading books to data base operation
    :return:
    """
    with open(f'{PATH_TO_STATE}/current_state.json', 'r') as f:
        cur_state = json.load(f)

    if cur_state['current_state'] != 1:
        print("You have to perform transfer operations first!")
        return
    books = cur_state['books']
    BooksDBOperator().save_books_to_db(books)
    utils.clear_data()
    print("Data successfully saved in database")


class BooksDBOperator:

    def __init__(self):
        self.HOST = 'localhost'
        self.USER = 'root'
        self.PASSWD = 'Hurtownie123!'
        self.DB_NAME ='webscraper_lubimyczytac'

    def connect_to_db(self):
        """
        Connect to database
        :return: None
        """
        my_db = mysql.connector.connect(
            host=self.HOST,
            user=self.USER,
            passwd=self.PASSWD,
            database=self.DB_NAME,
            auth_plugin='mysql_native_password'
        )
        return my_db

    def save_books_to_db(self, books):
        """
        Method that will connect to proper mysql database and save book data
        :param books: List of dicts with book details, each dict represents one book
        :return: None
        """
        db_to_save_books = self.connect_to_db()

        table_name = self._create_table_for_books(db_to_save_books)
        self._save_books_to_table(db_to_save_books, table_name, books)

    @staticmethod
    def _save_books_to_table(my_db, table_name, books):
        my_cursor = my_db.cursor()
        sql = f"INSERT INTO {table_name} (book_name, author_name, book_rating, nmb_of_ratings, " \
            f"genres, nmb_of_opinions, nmb_of_pages, apx_reading_time, avg_book_price) VALUES ( " \
            f"%s, %s, %s, %s, %s," \
            f"%s, %s, %s, %s) "

        val_to_insert = []
        for book in books:
            val_to_insert.append((
                book['book_name'],
                book['author_name'],
                book['book_rating'],
                book['nmb_of_ratings'],
                book['genres'],
                book['nmb_of_opinions'],
                book.get('nmb_of_pages', 0),
                book.get('apx_reading_time', "not available"),
                book.get('avg_book_price', 0.0)
            ))

        my_cursor.executemany(sql, val_to_insert)
        my_db.commit()
        print(my_cursor.rowcount, " records were inserted")

    @staticmethod
    def _create_table_for_books(my_db) -> str:
        my_cursor = my_db.cursor()
        table_name = "lubimyczytac_top100books_{0}".format(
            str(datetime.now().strftime("%Y%m%d_%H%M_%S")))

        my_cursor.execute("CREATE TABLE {0} ("
                          "id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,"
                          "book_name VARCHAR(255),"
                          "author_name VARCHAR(100),"
                          "book_rating FLOAT,"
                          "nmb_of_ratings INT,"
                          "genres VARCHAR(255),"
                          "nmb_of_opinions INT,"
                          "nmb_of_pages INT,"
                          "apx_reading_time VARCHAR(50),"
                          "avg_book_price FLOAT"
                          ")".format(table_name))
        return table_name

    def show_existing_tables(self):
        """
        Displays tables that are saved in database
        :return: None
        """
        my_db = self.connect_to_db()
        my_cursor = my_db.cursor()
        my_cursor.execute(f"SHOW TABLES")
        result = my_cursor.fetchall()
        print("Currently saved tables:")
        for table_tuple in result:
            print(table_tuple[0])

    def export_table_elements(self, table_name):
        """
        Exports table elements to different files in exports folder
        :param table_name: Name of the table to be exported
        :return:
        """
        my_db = self.connect_to_db()
        my_cursor = my_db.cursor()
        my_cursor.execute(f"SELECT * FROM {table_name}")
        records = my_cursor.fetchall()
        for i, row in enumerate(records):
            with open(f'{PATH_TO_EXPORTS}/books/{i + 1}.txt', 'w') as file:
                print(f"Saving details for book {i + 1}")
                file.write(self._get_row_str(row))

    def export_table_elements_csv(self, table_name):
        """
        Exports table elements to csv file
        :param table_name: Name of the table to be exported
        :return:
        """
        my_db = self.connect_to_db()
        my_cursor = my_db.cursor()
        my_cursor.execute(f"SELECT * FROM {table_name}")
        records = my_cursor.fetchall()
        with open(f'{PATH_TO_EXPORTS}/books_{table_name}.csv', mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"',
                                              quoting=csv.QUOTE_MINIMAL)

            fieldnames = ['ID', 'book_name', 'author_name', 'book_rating', 'nmb_of_ratings',
                          'genres', 'nmb_of_opinions', 'nmb_of_pages', 'apx_reading_time',
                          'avg_book_price']
            csv_writer.writerow(fieldnames)
            for row in records:
                csv_writer.writerow(row)


    def show_table_elements(self, table_name):
        """
        Show records for given table
        :param table_name: Name of the table, that will have the record displayed
        :return: None
        """
        my_db = self.connect_to_db()
        my_cursor = my_db.cursor()
        my_cursor.execute(f"SELECT * FROM {table_name}")
        records = my_cursor.fetchall()
        print(f"{table_name} records:")
        for row in records:
            print(self._get_row_str(row))
            # print()
            # print(f"ID  {row[0]}")
            # print(f"book_name {row[1]}")
            # print(f"author_name {row[2]}")
            # print(f"book_rating {row[3]}")
            # print(f"nmb_of_ratings {row[4]}")
            # print(f"genres {row[5]}")
            # print(f"nmb_of_opinions {row[6]}")
            # print(f"nmb_of_pages {row[7]}")
            # print(f"apx_reading_time {row[8]}")
            # print(f"avg_book_price {row[9]}")
            # print()

    def _get_row_str(self, row):
        row_str = f"""
book_name {row[1]}
author_name {row[2]}
book_rating {row[3]}
nmb_of_ratings {row[4]}
genres {row[5]}
nmb_of_opinions {row[6]}
nmb_of_pages {row[7]}
apx_reading_time {row[8]}
avg_book_price {row[9]}        
"""
        return row_str

    def remove_table(self, table_name):
        """
        Removed given table from database
        :param table_name: Name of the table, that will be removed
        :return: None
        """
        my_db = self.connect_to_db()
        my_cursor = my_db.cursor()
        my_cursor.execute(f"DROP TABLE {table_name}")
        print(f"Table: {table_name} is dropped")
