import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.goodreads.com/review/list/142587487-random-programmer?page={}&print=true&shelf=read&view=table"

FIELDS = {
    "title": "title",
    "author": "author",
    "isbn": "isbn",
    "isbn13": "isbn13",
    "asin": "asin",
    "num_pages": "num_pages",
    "avg_rating": "avg_rating",
    "num_ratings": "num_ratings",
    "date_pub": "date_pub",
    "date_pub_edition": "date_pub_edition",
    "rating": "rating",  # this isn't working
    "shelves": "shelves",
    "review": "review",
    "notes": "notes",
    "comments": "comments",
    # "votes": "votes",
    "read_count": "read_count",
    "date_started": "date_started",
    "date_read": "date_read",
    "date_added": "date_added",
    "owned": "owned",
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

    response = requests.get(BASE_URL.format(1))
    soup = BeautifulSoup(response.content, "html.parser")
    pagination_links = soup.select(
        "#reviewPagination a:not(.next_page)"
    )  # Select all anchor tags inside the div excluding the "next" link
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

    value = div.get_text(strip=True)
    if field_class == "field rating":
        value = RATING_MAPPER.get(value, value)

    return value


def get_book_data(page_number):
    response = requests.get(BASE_URL.format(page_number))
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


# Assuming there are 10 pages to loop through
last_page = get_last_page()
all_books = []
for i in range(1, last_page + 1):
    all_books.extend(get_book_data(i))

# for book in all_books:
#     print(", ".join([f"{key.capitalize()}: {value}" for key, value in book.items()]))

for key, value in all_books[0].items():
    print(f"{key}: {value}")
