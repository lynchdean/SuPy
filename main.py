import requests
from bs4 import BeautifulSoup


def main():
    # driver = webdriver.Chrome('./chromedriver')
    base_url = "https://www.supremenewyork.com/shop/all"

    page = requests.get(base_url)
    soup = BeautifulSoup(page.content, features="lxml")

    cat_tags = soup.find("ul", id="nav-categories")

    for link in cat_tags[1:]:
        print(link.contents[0].get('href'))

if __name__ == '__main__':
    main()
