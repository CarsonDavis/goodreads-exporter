import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.goodreads.com/review/list/142587487-random-programmer?page={}&print=true&shelf=read&view=table"


def get_book_data(page_number):
    response = requests.get(BASE_URL.format(page_number))
    soup = BeautifulSoup(response.content, "html.parser")

    titles = []
    dates_read = []

    # Find all rows with book data
    rows = soup.find_all("tr", class_="bookalike review")

    for row in rows:
        # Get the title
        title_div = row.find("td", class_="field title").div
        title = title_div.a.get_text(strip=True)
        titles.append(title)

        # Get the read date
        date_read_div = row.find("td", class_="field date_read").div
        date_read_element = date_read_div.find("span", class_="date_read_value")
        date_read = None
        if date_read_element:
            date_read = date_read_element.get_text(strip=True)
        dates_read.append(date_read)

    return titles, dates_read


# Assuming there are 10 pages to loop through
all_titles = []
all_dates_read = []
for i in range(1, 2):  # Replace 11 with the actual number of pages + 1
    titles, dates_read = get_book_data(i)
    all_titles.extend(titles)
    all_dates_read.extend(dates_read)

for title, date in zip(all_titles, all_dates_read):
    print(f"Title: {title}, Date Read: {date}")
