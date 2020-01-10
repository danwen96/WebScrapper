"""
Module for coordinating etl operations
"""
import pathlib
import subprocess

from etl import webscraper_books, utils, books_database


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
    print("Data successfully transformed, it is ready to be loaded to data base!")


def perform_load():
    print("Performing data loading to db operation...")
    books_database.load_data()
    print("Data successfully saved in database")


# def perform_all_etl():
#     perform_extract()
#     perform_transform()
#     perform_load()




