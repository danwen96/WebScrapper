import argparse
from etl import books_database, webscraper_books, coordinator

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("--etl", action='store_true', help="Perform all etl steps with one run")
    parser.add_argument("--extract", action='store_true', help="Performs extract step")
    parser.add_argument("--transform", action='store_true', help="Perform transform step")
    parser.add_argument("--load", action='store_true', help="Perform load to database step")
    parser.add_argument("--show_saved_tables", action='store_true', help="Displays saved tables")
    parser.add_argument("--show_table", help="Displays given table, require table name "
                                             "after this option usage")
    parser.add_argument("--remove_table", help="Removed given table, requires table "
                                               "name after this option usage")
    parser.add_argument("--export_table_csv", help="Exports data from given table "
                                                   "to file in csv format in folder exports")
    parser.add_argument("--export_table_to_files", help="Exports data from given table to "
                                                        "different files in folder exports")

    args = parser.parse_args()

    coordinator.create_data_exports_folder()

    if args.export_table_csv:
        coordinator.perform_export_of_table_to_csv(args.export_table_csv)

    if args.export_table_to_files:
        coordinator.perform_export_of_table_to_files(args.export_table_to_files)

    if args.extract:
        coordinator.perform_extract()

    if args.transform:
        coordinator.perform_transform()

    if args.load:
        coordinator.perform_load()

    if args.etl:
        print("Start of data web scraping")
        books = webscraper_books.WebScraper().get_top_100_data()
        print("Top 100 books collected, fetching more details for each book:")
        webscraper_books.BookDetailsWebScrapper().add_books_details(books)
        print("Book details added, saving to db:")
        books_database.BooksDBOperator().save_books_to_db(books)
        print("Books saved to db")

    if args.show_saved_tables:
        books_database.BooksDBOperator().show_existing_tables()

    if args.show_table:
        print(f"args.show_table: {args.show_table}")
        books_database.BooksDBOperator().show_table_elements(args.show_table)

    if args.remove_table:
        print(f"args.remove_table {args.remove_table}")
        books_database.BooksDBOperator().remove_table(args.remove_table)
