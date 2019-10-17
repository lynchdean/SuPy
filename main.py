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

    for tail in cat_url_tails:
        cat_page = requests.get(base_url + tail)
        cat_soup = BeautifulSoup(cat_page.content, features="lxml")
        inner_articles = cat_soup.findAll("div", class_="inner-article")
        for inner_article in inner_articles:
            links = inner_article.find("a", class_="name-link")
            print(links)


if __name__ == '__main__':
    main()
