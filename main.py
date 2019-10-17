import requests
from bs4 import BeautifulSoup


def main():
    # driver = webdriver.Chrome('./chromedriver')
    base_url = "https://www.supremenewyork.com"

    page = requests.get(base_url + "/shop/all")
    soup = BeautifulSoup(page.content, features="lxml")

    # Get the url tails for each of the categories
    cat_tags = soup.find("ul", id="nav-categories")
    cat_url_tails = [link.contents[0].get('href') for link in cat_tags][2:]


if __name__ == '__main__':
    main()
