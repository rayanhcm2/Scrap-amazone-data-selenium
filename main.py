import sqlite3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

with open("data.json", "w") as f:
    json.dump([], f)


def delet_tb_from_db():
    db = sqlite3.connect('data.db')
    cr = db.cursor()
    cr.execute("DROP TABLE IF EXISTS products")
    db.commit()
    db.close()


def insert_into_database(title, price, image, url):
    db = sqlite3.connect('data.db')
    try:
        print('Connected To Database Successfully')
        cr = db.cursor()
        cr.execute("CREATE TABLE if not exists products (title TEXT,price TEXT,image TEXT,url TEXT)")
        cr.execute(f"insert into products(title,price,image,url) values('{title}','{price}','{image}','{url}')")
        db.commit()
    except sqlite3.Error as er:
        print(f"Error Reading Data {er}")
    finally:
        db.close()
        print('Connection to database is closed')


def write_json(new_data, filename='data.json'):
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        file_data.append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)

delet_tb_from_db()
chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
driver.get(
    'https://www.amazon.com/s?i=computers-intl-ship&bbn=16225007011&rh=n%3A16225007011%2Cp_36%3A1253503011&dc&fs=true'
    '&qid=1645954406&ref=sr_ex_n_1')

isNextDisabled = False
while not isNextDisabled:
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '//div[@data-component-type="s-search-result"]')))

        elem_list = driver.find_element(
            By.CSS_SELECTOR, "div.s-main-slot.s-result-list.s-search-results.sg-row")

        list_items = elem_list.find_elements(
            By.XPATH, '//div[@data-component-type="s-search-result"]')

        for item in list_items:
            title_product = " Price not found"
            try:
                title_product = item.find_element(By.TAG_NAME, "h2").text
            except:
                pass
            price_product = " Price not found"
            image_product = " Image not found"
            link_product = item.find_element(By.CSS_SELECTOR, 'a[class ="a-link-normal s-no-outline"]').get_attribute(
                "href")
            try:
                price_product = item.find_element(By.CLASS_NAME, 'a-price').text.replace("\n", ".")
            except:
                pass
            try:
                image_product = item.find_element(By.CLASS_NAME, 's-image').get_attribute("src")
            except:
                pass

            # current_page = driver.find_element(
            #     (By.CSS_SELECTOR, 'span[class="s-pagination-item s-pagination-selected"]'))
            # print("Page : " + current_page)
            print("Title : " + title_product)
            print("Price : " + price_product)
            print("Image : " + image_product)
            print("Link : " + link_product + "\n")

            my_product = {
                "Title": title_product,
                "Price": price_product,
                "Image": image_product,
                "Link": link_product,
            }
            insert_into_database(title_product,
                                 price_product,
                                 image_product,
                                 link_product)
            write_json(my_product)

        next_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CLASS_NAME, 's-pagination-next')))
        next_class = next_btn.get_attribute('class')

        if 'disabled' in next_class:
            isNextDisabled = True
        else:
            next_btn.click()
    except Exception as e:
        print(e, "Main Error")
        isNextDisabled = True
