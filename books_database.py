import mysql.connector

from datetime import datetime


class BooksSaver:

    def __init__(self):
        self.HOST = 'localhost'
        self.USER = 'root'
        self.PASSWD = 'Hurtownie123!'
        self.DB_NAME ='webscraper_lubimyczytac'

    def connect_to_db(self):
        my_db = mysql.connector.connect(
            host=self.HOST,
            user=self.USER,
            passwd=self.PASSWD,
            database=self.DB_NAME,
            auth_plugin='mysql_native_password'
        )
        return my_db

    def save_books_to_db(self, books, db_to_save_books=None):
        if not db_to_save_books:
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
        print(my_cursor.rowcount, " was inserted")
        print("Last row id: ", my_cursor.lastrowid)

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
