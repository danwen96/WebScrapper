import argparse
import webscraper_books
import books_database

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("--etl", action='store_true', help="Perform all etl processes")
    parser.add_argument("--show_saved_tables", action='store_true', help="Displays saved tables")
    parser.add_argument("--show_table", help="Displays given table, require table name "
                                             "after this option usage")
    parser.add_argument("--remove_table", help="Removed given table, requires table "
                                               "name after this option usage")

    args = parser.parse_args()

    if args.etl:
        print("Start of data web scraping")
        books = webscraper_books.WebScraper().get_top_100_data()
        print("Top 100 collected, books: ")
        print(books)
        webscraper_books.BookDetailsWebScrapper().add_books_details(books)
        print("Book details added:")
        print(books)
        books_database.BooksSaver().save_books_to_db(books)
        print("Books saved to db")

    if args.show_saved_tables:
        books_database.BooksSaver().show_existing_tables()

    if args.show_table:
        print(f"args.show_table: {args.show_table}")
        books_database.BooksSaver().show_table_elements(args.show_table)

    if args.remove_table:
        print(f"args.remove_table {args.remove_table}")
        books_database.BooksSaver().remove_table(args.remove_table)
