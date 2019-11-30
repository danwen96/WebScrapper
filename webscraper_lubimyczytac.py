import webscraper_books
import books_database

if __name__ == '__main__':
    print("Hello")
    books = webscraper_books.WebScraper().get_top_100_data()
    for i, book in enumerate(books):
        print(f"{i}\t\t {book}")

    webscraper_books.BookDetailsWebScrapper().add_books_details(books)

    print("*" * 100)
    print()

    for i, book in enumerate(books):
        print(f"{i + 1}\t\t {book}")

    books_database.BooksSaver().save_books_to_db(books)
