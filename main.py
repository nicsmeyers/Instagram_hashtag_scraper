"""Instagram web scrapper"""
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

import variables

delay = 5  # seconds


def time_out_xpath(_browser, _xpath):
    """Function waits for element to appear before
    continuing else it raises timeout exception"""
    try:
        WebDriverWait(_browser, delay).until(ec.presence_of_element_located((By.XPATH, _xpath)))
        return False
    except TimeoutException:
        return True


def time_out_css(_browser, _css):
    """Function waits for element to appear before
    continuing else it raises timeout exception"""
    try:
        WebDriverWait(_browser, delay).until(ec.presence_of_element_located((By.XPATH, _css)))
        return False
    except TimeoutException:
        return True


username = input("Please enter your Instagram username: ")
password = input("Please enter your Instagram password: ")

browser = webdriver.Chrome(ChromeDriverManager().install())
base_url = "https://www.instagram.com"

browser.get(base_url)
if not time_out_xpath(browser, variables.username):
    browser.find_element_by_xpath(variables.username).send_keys(username)
browser.find_element_by_xpath(variables.password).send_keys(password)
browser.find_element_by_xpath(variables.login).click()

if not time_out_xpath(browser, variables.deny_save_info):
    browser.find_element_by_xpath(variables.deny_save_info).click()
if not time_out_xpath(browser, variables.deny_turn_on_notification):
    browser.find_element_by_xpath(variables.deny_turn_on_notification).click()

search = input("What would you like to search? (Hashtags only): ")
browser.find_element_by_xpath(variables.search).send_keys(search)
if not time_out_xpath(browser, variables.result):
    browser.find_element_by_xpath(variables.result).click()

while True:
    try:
        pages = int(input("How many pages would you like scrapped?: "))
        break
    except ValueError:
        print("Please enter a valid number of pages.")

search_url = browser.current_url
pages_scrapped = 0
while True:
    time.sleep(3)
    posts = browser.find_elements_by_css_selector(variables.posts)
    post_links = list()
    for post in posts:
        href = post.find_element_by_tag_name("a").get_attribute("href")
        post_links.append(href)

    browser.execute_script("window.open('https://google.com','_blank')")
    browser.switch_to.window(window_name=browser.window_handles[1])

    for link in post_links:
        with open(".\\log\\posts.txt", "r+") as file:
            scrapped_posts = file.readlines()
            if f"{link}\n" in scrapped_posts:
                pass
            else:
                browser.get(link)
                user = browser.find_element_by_xpath(variables.user).text
                description = browser.find_element_by_xpath(variables.description).text.replace("\n", " ")
                try:
                    media_link = browser.find_element_by_css_selector(variables.image)
                    src = media_link.find_element_by_tag_name("img").get_attribute("src")
                except NoSuchElementException:
                    media_link = browser.find_element_by_css_selector(variables.video)
                    src = media_link.find_element_by_tag_name("video").get_attribute("src")
                with open(".\\log\\posts.csv", "a", encoding="utf-8") as csv:
                    csv.write(f"{link},{user},{description},{src}\n")
                file.write(f"{link}\n")
            file.close()

    browser.close()
    browser.switch_to.window(window_name=browser.window_handles[0])

    pages_scrapped += 1
    print(f"PAGE {pages_scrapped} SCRAPPED")
    if pages_scrapped == pages:
        break
    time.sleep(1)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
