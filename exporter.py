import requests
from bs4 import BeautifulSoup
import csv
from datetime import date
from config import username as USERNAME

BASE_URL = (
    "https://www.goodreads.com/review/list/{}?page={}&print=true&shelf=read&view=table"
)

FIELDS = {
    "title": "title",
    "author": "author",
    "rating": "rating",
    "avg_rating": "avg_rating",
    "num_ratings": "num_ratings",
    "date_started": "date_started",
    "date_read": "date_read",
    "date_added": "date_added",
    "date_pub": "date_pub",
    "date_pub_edition": "date_pub_edition",
    "num_pages": "num_pages",
    # "shelves": "shelves", # this isn't working
    # "notes": "notes",
    "isbn": "isbn",
    "isbn13": "isbn13",
    "asin": "asin",
    "read_count": "read_count",
    "owned": "owned",
    "comments": "comments",
    "review": "review",
}

RATING_MAPPER = {
    "did not like it": "1",
    "it was ok": "2",
    "liked it": "3",
    "really liked it": "4",
    "it was amazing": "5",
}


def get_last_page():
    """this finds the number of pages a user needs to extract"""

    response = requests.get(BASE_URL.format(USERNAME, 1))
    soup = BeautifulSoup(response.content, "html.parser")
    # Select all anchor tags inside the div excluding the "next" link
    pagination_links = soup.select("#reviewPagination a:not(.next_page)")
    return int(pagination_links[-1].text)


def field_converter(field_name):
    """adds the word field in front of the field name"""
    return f"field {field_name}"


def extract_field(row, field_name):
    """gets the value of a desired field and handles a few special cases"""
    field_class = field_converter(field_name)
    div = row.find("td", class_=field_class).div

    # Special case for date_read as it has an additional span element
    if field_class == "field date_read":
        span = div.find("span", class_="date_read_value")
        return span.get_text(strip=True) if span else None

    # Special case for title
    if field_class == "field title":
        # Get only the direct text of the anchor tag, excluding the nested span if it exists
        # this is removing the series name from the title
        return div.a.contents[0].strip()

    value = div.get_text(strip=True)
    # Special case for rating
    if field_class == "field rating":
        value = RATING_MAPPER.get(value, value)

    return value


def get_book_data(page_number):
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


def save_to_csv(books):
    todays_date = date.today().strftime(
        "%Y%m%d"
    )  # This will format today's date as YYYYMMDD
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
