import hashlib
import time
from datetime import datetime

import requests
import yaml
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select

from page_monitor import PageMonitor

target_desc = "Tagless Tees"
target_colour = "Black"  # Case-sensitive
target_size = "Medium"  # Case-sensitive & must be exact match, e.g.: "Small", "Medium", "Large" or "XLarge"


def main():
    with open("autofill.yaml", 'r') as file:
        autofill_props = yaml.safe_load(file)

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    driver = webdriver.Chrome('./chromedriver', options=chrome_options)
    base_url = "https://www.supremenewyork.com"
    driver.get(base_url)


    wait_for_page_update(base_url)
    start = datetime.now()

    page = requests.get(base_url + "/shop/all")
    soup = BeautifulSoup(page.content, features="lxml")

    # Get the url tails for each of the categories
    cat_tags = soup.find("ul", id="nav-categories")
    cat_url_tails = [link.contents[0].get('href') for link in cat_tags][2:]

    item_dict = get_item_dict(base_url, cat_url_tails)
    target_url_tail = get_target_url_tail(item_dict)

    xpaths = autofill_props.get("xpaths")
    # test_navigate_product_page(base_url + target_url_tail)
    navigate_product_page(driver, base_url + target_url_tail, xpaths)
    navigate_checkout(driver, autofill_props)

    end = datetime.now()
    print("Execution time {0} seconds.".format(str(end - start)))


def test_navigate_product_page(url):
    page = requests.get(url)
    print(page.content)


def wait_for_page_update(base_url):
    pm = PageMonitor(base_url + "/shop/all", 0.5)
    # pm.wait_for_update()


def navigate_product_page(driver, url, xpaths):
    force_get_page(driver, url, 0.1)

    if target_size != "":
        size_drop_down = Select(driver.find_element_by_xpath(xpaths.get("size")))
        size_drop_down.select_by_visible_text(target_size)

    atc_btn = driver.find_element_by_xpath(xpaths.get("atc"))
    atc_btn.click()


def navigate_checkout(driver, properties):
    force_get_page(driver, "https://www.supremenewyork.com/checkout", 0.1)

    xpaths = properties.get("xpaths")
    textbox_xpaths = xpaths.get("textbox")
    dd_xpaths = xpaths.get("dropdown")
    inputs = properties.get("input")

    for key in textbox_xpaths.keys():
        xpath = textbox_xpaths[key]
        fill_input(driver, xpath, inputs.get(key))

    for key in dd_xpaths.keys():
        xpath = dd_xpaths[key]
        set_dropdown(driver, xpath, inputs.get(key))

    checkbox = driver.find_element_by_xpath(xpaths.get("checkbox"))
    checkbox.click()


def fill_input(driver, xpath, text):
    element = driver.find_element_by_xpath(xpath)
    driver.execute_script("arguments[0].value = arguments[1];", element, text)


def set_dropdown(driver, xpath, option):
    dd = Select(driver.find_element_by_xpath(xpath))
    dd.select_by_visible_text(option)


def force_get_page(driver, url, interval):
    driver.get(url)
    while driver.current_url != url:
        driver.get(url)
        time.sleep(interval)


def get_target_url_tail(item_dict):
    descriptions = item_dict.keys()
    if target_desc in descriptions:
        return get_colour_url_tail(item_dict[target_desc])
    else:
        for desc in descriptions:
            if target_desc.lower() in desc.lower():
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
