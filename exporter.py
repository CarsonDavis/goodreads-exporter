import csv
from datetime import date

import requests
from bs4 import BeautifulSoup
from dateutil import parser

from config import username as USERNAME

BASE_URL = "https://www.goodreads.com/review/list/{}?page={}&print=true&shelf=read&view=table"

# TODO: The official goodreads export has these fields, but I haven't mapped them yet
# Book Id
# Author l-f
# Additional Authors
# Publisher
# Binding
# Bookshelves
# Bookshelves with positions
# Exclusive Shelf
# Spoiler
# Private Notes

FIELDS = {
    # "name to print": "value in html"
    "Title": "title",
    "Author": "author",
    "My Rating": "rating",
    "Average Rating": "avg_rating",
    "Num Ratings": "num_ratings",
    "Date Started": "date_started",
    "Date Read": "date_read",
    "Date Added": "date_added",
    "Original Publication Year": "date_pub",
    "Year Published": "date_pub_edition",
    "Number of Pages": "num_pages",
    # "Shelves": "shelves", # this isn't working
    # "Notes": "notes",
    "ISBN": "isbn",
    "ISBN13": "isbn13",
    "Asin": "asin",
    "Read Count": "read_count",
    "Owned Copies": "owned",
    "Comments": "comments",
    "My Review": "review",
}

RATING_MAPPER = {
    "did not like it": "1",
    "it was ok": "2",
    "liked it": "3",
    "really liked it": "4",
    "it was amazing": "5",
}


def get_last_page() -> int:
    """this finds the number of pages a user needs to extract"""

    response = requests.get(BASE_URL.format(USERNAME, 1))
    soup = BeautifulSoup(response.content, "html.parser")
    # Select all anchor tags inside the div excluding the "next" link
    pagination_links = soup.select("#reviewPagination a:not(.next_page)")
    return int(pagination_links[-1].text)


def field_converter(field_name: str) -> str:
    """adds the word 'field' in front of the field name"""
    return f"field {field_name}"


def extract_date_read(div: BeautifulSoup) -> str:
    """
    finds the date if it exists and converts it to the same format
    as the official goodreads export YYYY/MM/DD
    """
    span = div.find("span", class_="date_read_value")
    if span:
        date_str = span.get_text(strip=True)
        try:
            date_obj = parser.parse(date_str)
            return date_obj.strftime("%Y/%m/%d")
        except ValueError:  # If parsing fails
            return None
    else:
        return None


def extract_title(div: BeautifulSoup) -> str:
    return div.a.contents[0].strip()


def extract_review(div: BeautifulSoup) -> str:
    spans = div.find_all("span")
    if len(spans) > 1:
        return spans[1].get_text(strip=True)
    else:
        return spans[0].get_text(strip=True)


def extract_rating(div: BeautifulSoup) -> str:
    value = div.get_text(strip=True)
    return RATING_MAPPER.get(value, value)


def extract_field(row: BeautifulSoup, field_name: str) -> str:
    """Extracts the value of a desired field based on its type."""
    field_class = field_converter(field_name)
    div = row.find("td", class_=field_class).div

    field_extractors = {
        "field date_read": extract_date_read,
        "field title": extract_title,
        "field review": extract_review,
        "field rating": extract_rating,
    }

    if field_class in field_extractors:
        return field_extractors[field_class](div)
    else:
        return div.get_text(strip=True)


def get_book_data(page_number: int) -> list:
    response = requests.get(BASE_URL.format(USERNAME, page_number))
    soup = BeautifulSoup(response.content, "html.parser")

    books = []

    # Find all rows with book data
    rows = soup.find_all("tr", class_="bookalike review")

    for row in rows:
        book = {}
        for field, class_name in FIELDS.items():
            book[field] = extract_field(row, class_name)
        books.append(book)

    return books


def save_to_csv(books: list[dict[str, str]]) -> None:
    todays_date = date.today().strftime("%Y%m%d")  # This will format today's date as YYYYMMDD
    filename = f"goodreads_export-{todays_date}.csv"

    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(FIELDS.keys()))
        writer.writeheader()
        for book in books:
            writer.writerow(book)


all_books = []
for i in range(1, get_last_page() + 1):
    all_books.extend(get_book_data(i))

save_to_csv(all_books)
