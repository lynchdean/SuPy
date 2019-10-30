import hashlib
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select

target_desc = "Tagless Tee"
target_colour = "Black"
target_size = "Medium"


def main():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    driver = webdriver.Chrome('./chromedriver', options=chrome_options)
    base_url = "https://www.supremenewyork.com"
    driver.get(base_url)

    wait_for_page_update(base_url)

    page = requests.get(base_url + "/shop/all")
    soup = BeautifulSoup(page.content, features="lxml")

    # Get the url tails for each of the categories
    cat_tags = soup.find("ul", id="nav-categories")
    cat_url_tails = [link.contents[0].get('href') for link in cat_tags][2:]

    item_dict = get_item_dict(base_url, cat_url_tails)
    target_url_tail = get_target_url_tail(item_dict)
    driver.get(base_url + target_url_tail)

    navigate_product_page(driver)
    navigate_checkout(driver)


def wait_for_page_update(base_url):
    has_updated = False
    url = base_url + "/shop/all"
    page = requests.get(url)
    reference_hash = hashlib.md5(page.text.encode('utf-8'))
    reference_digest = reference_hash.hexdigest()

    while not has_updated:
        new_page = requests.get(url)
        new_hash = hashlib.md5(new_page.text.encode('utf-8'))
        if new_hash.hexdigest() == reference_digest:
            print("No changes.")
            reference_digest = new_hash.hexdigest()
        else:
            print("Live.")
            has_updated = True

        time.sleep(0.5)


def navigate_product_page(driver):
    size_drop_down = Select(driver.find_element_by_xpath("//*[@id=\"size\"]"))
    size_drop_down.select_by_visible_text(target_size)

    atc_btn = driver.find_element_by_xpath("/html/body/div[2]/div/div[2]/div/form/fieldset[3]/input")
    atc_btn.click()


def navigate_checkout(driver):
    driver.get("https://www.supremenewyork.com/checkout")
    driver.get("https://www.supremenewyork.com/checkout")

    name = driver.find_element_by_xpath("//*[@id=\"order_billing_name\"]")
    name.send_keys("")
    email = driver.find_element_by_xpath("//*[@id=\"order_email\"]")
    email.send_keys("")
    telephone = driver.find_element_by_xpath("//*[@id=\"order_tel\"]")
    telephone.send_keys("")

    address_1 = driver.find_element_by_xpath("//*[@id=\"bo\"]")
    address_1.send_keys("")
    address_2 = driver.find_element_by_xpath("//*[@id=\"oba3\"]")
    address_2.send_keys("")
    address_3 = driver.find_element_by_xpath("//*[@id=\"order_billing_address_3\"]")
    address_3.send_keys("")

    city = driver.find_element_by_xpath("//*[@id=\"order_billing_city\"]")
    city.send_keys("")
    postcode = driver.find_element_by_xpath("//*[@id=\"order_billing_zip\"]")
    postcode.send_keys("")
    country_dd = Select(driver.find_element_by_xpath("//*[@id=\"order_billing_country\"]"))
    country_dd.select_by_visible_text("")

    card_type_dd = Select(driver.find_element_by_xpath("//*[@id=\"credit_card_type\"]"))
    card_type_dd.select_by_visible_text("")
    card_no = driver.find_element_by_xpath("//*[@id=\"cnb\"]")
    card_no.send_keys("")
    card_month_dd = Select(driver.find_element_by_xpath("//*[@id=\"credit_card_month\"]"))
    card_month_dd.select_by_visible_text("")
    card_year_dd = Select(driver.find_element_by_xpath("//*[@id=\"credit_card_year\"]"))
    card_year_dd.select_by_visible_text("")
    ccv = driver.find_element_by_xpath("//*[@id=\"vval\"]")
    ccv.send_keys("")

    checkbox = driver.find_element_by_xpath("/html/body/div[2]/div[1]/form/div[2]/div[2]/fieldset/p/label/div/ins")
    checkbox.click()


def get_target_url_tail(item_dict):
    descriptions = item_dict.keys()
    if target_desc in descriptions:
        return get_colour_url_tail(item_dict[target_desc])
    else:
        for desc in descriptions:
            if target_desc in desc:
                return get_colour_url_tail(item_dict[desc])
        # If it's not found, just go to homepage
        return ""


def get_colour_url_tail(colours):
    for item in colours:
        if target_colour in item[0]:
            return item[1]
    # Return any colour if a match isn't found
    return colours[0][1]


def get_item_dict(base_url, cat_url_tails):
    item_colours = {}
    for tail in cat_url_tails:
        cat_page = requests.get(base_url + tail)
        cat_soup = BeautifulSoup(cat_page.content, features="lxml")
        inner_articles = cat_soup.findAll("div", class_="inner-article")
        for inner_article in inner_articles:
            links = inner_article.findAll("a", class_="name-link")
            desc = links[0].text
            colour = links[1].text
            link = links[1].get('href')

            if desc not in item_colours:
                item_colours.setdefault(desc, [])
            item_colours[desc].append([colour, link])

    return item_colours


if __name__ == '__main__':
    main()
