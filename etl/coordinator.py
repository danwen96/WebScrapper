"""
Module for coordinating etl operations
"""
import pathlib
import subprocess

from etl import webscraper_books, utils, books_database


def create_data_exports_folder():
    """
    Creates folders for exports and data
    :return:
    """
    subprocess.run(['mkdir', '-p', f'{pathlib.Path(__file__).parent}/state/data'])
    subprocess.run(['mkdir', '-p', f'{pathlib.Path(__file__).parent.parent}/exports/books'])


def perform_extract():
    """
    Coordinates the extraction of data
    :return:
    """
    print("Performing data extraction...")
    utils.clear_data()
    webscraper_books.extract_data()
    print("Data extracted successfully, you can transform it now!")


def perform_transform():
    """
    Coordinates the transform of data
    :return:
    """
    print("Performing data transformation...")
    webscraper_books.transform_data()



def perform_load():
    """
    Coordinates the load of data
    :return:
    """
    print("Performing data loading to db operation...")
    books_database.load_data()



def perform_export_of_table_to_files(table_name):
    """
    Coordinates the exporting table to files
    :param table_name: Name of the table to be exported
    :return:
    """
    print(f"Exporting data from table {table_name} to different files in export folder...")
    books_database.BooksDBOperator().export_table_elements(table_name)
    print(f'Export of books files complete')


def perform_export_of_table_to_csv(table_name):
    """
    Coordinates the exporting table to csv file
    :param table_name: Name of the table to be exported
    :return:
    """
    print(f"Exporting data from table {table_name} to csv file")
    books_database.BooksDBOperator().export_table_elements_csv(table_name)
    print(f'Export of books to csv file complete')

