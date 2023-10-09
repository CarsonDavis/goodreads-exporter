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
    "Title": "field title",
    "Author": "field author",
    "My Rating": "field rating",
    "Average Rating": "field avg_rating",
    "Num Ratings": "field num_ratings",
    "Date Started": "field date_started",
    "Date Read": "field date_read",
    "Date Added": "field date_added",
    "Original Publication Year": "field date_pub",
    "Year Published": "field date_pub_edition",
    "Number of Pages": "field num_pages",
    # "Shelves": "field shelves", # this isn't working
    # "Notes": "field notes",
    "ISBN": "field isbn",
    "ISBN13": "field isbn13",
    "Asin": "field asin",
    "Read Count": "field read_count",
    "Owned Copies": "field owned",
    "Comments": "field comments",
    "My Review": "field review",
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


def date_reformatter(date_str: str) -> str:
    try:
        date_obj = parser.parse(date_str)
        return date_obj.strftime("%Y/%m/%d")
    except ValueError:  # If parsing fails
        return None


def extract_date_read(div: BeautifulSoup) -> str:
    """
    finds the date if it exists and converts it to the same format
    as the official goodreads export YYYY/MM/DD
    """
    span = div.find("span", class_="date_read_value")
    if span:
        date_str = span.get_text(strip=True)
        return date_reformatter(date_str)
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


def extract_field(row: BeautifulSoup, field_class: str) -> str:
    """Extracts the value of a desired field based on its type."""
    div = row.find("td", class_=field_class).div

    # these fields needs some custom processing
    wierd_field_to_extractor_mapping = {
        "field date_read": extract_date_read,
        "field title": extract_title,
        "field review": extract_review,
        "field rating": extract_rating,
    }

    if field_class in wierd_field_to_extractor_mapping:
        # process the wierd fields
        return wierd_field_to_extractor_mapping[field_class](div)
    else:
        # process the rest
        value = div.get_text(strip=True)
        if "date" in field_class:
            value = date_reformatter(value)
        return value


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
