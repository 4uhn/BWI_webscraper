import pandas as pd
import time

from bs4 import BeautifulSoup
from flask import session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument('--headless') 
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
chrome_options.add_argument(f'user-agent={user_agent}')

service = Service(ChromeDriverManager().install())  
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1080, 800)

class LoginFailureException(Exception):
    pass

def login(BWI_username, BWI_password):
    driver.get("https://www.bestwineimporters.com/login/")

    if not session.get("cookie_button_clicked"):
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
            )
            cookie_button.click()
            print("Cookie button clicked")
            session["cookie_button_clicked"] = True
        except Exception as e:
            print(f"Failed to click cookie button because {e}")

    WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, 'bdb-login-form'))
            )
    username = driver.find_element(By.ID, 'user_login')
    password = driver.find_element(By.ID, 'user_password')
    login_button = driver.find_element(By.CSS_SELECTOR, "button.bdata-log-in.w-btn[value='Log In']")

    username.send_keys(BWI_username)

    password.send_keys(BWI_password)

    login_button.click()
    print("Login Button clicked")

    try:
        WebDriverWait(driver, 10).until(
                EC.url_changes('https://www.bestwineimporters.com/login/')
            )
        print("Login successful")
    except Exception as e:
        raise LoginFailureException("Login failed. Incorrect username or password.")

def extract_wine_data(wine_url, country, product_origin, result_count):
    driver.get(wine_url)
    

    try: 
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "bfi-table"))
        )
    except Exception as e:
        print(f"Failed to load page: {e}")
        return None

    try:
        country_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ng-binding') and contains(text(), 'Filter by Countries')]"))
        )
        country_filter.click()

        france_option_div = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, f"//div[@class='checkBoxContainer']//span[@country='{country}' and @class='f16']/ancestor::div[contains(@class, 'multiSelectItem')]"))
        )

        checkbox2_container = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'db-filter-country')]//div[contains(@class, 'checkboxLayer')]//div[@class='checkBoxContainer']"))
        )

        driver.execute_script("""
            arguments[0].scrollTop = arguments[1].offsetTop - arguments[0].offsetHeight / 2;
        """, checkbox2_container, france_option_div)

 #. makes the search relative to the descendents of the current div

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(france_option_div)
        
        )
        driver.execute_script("arguments[0].click();", france_option_div)

        time.sleep(2)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//button[div[@class='buttonLabel' and contains(., ' ') and span[@class='f16' and @country='{country}' and @size='16']]]"))
        )
 

    except Exception as e:
        print(f"Failed to select {country} as country: {e}")


    try:
        origin_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ng-binding') and contains(text(), 'Filter by Product Origin')]"))
        )
        origin_filter.click()


        spain_option_div = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'db-filter-origin')]//div[contains(@class, 'checkboxLayer')]//div[@class='checkBoxContainer']//span[@country='{product_origin}' and @class='f16']/ancestor::div[contains(@class, 'multiSelectItem')]"))
        )

        checkbox_container = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'db-filter-origin')]//div[contains(@class, 'checkboxLayer')]//div[@class='checkBoxContainer']"))
        )

        driver.execute_script("""
            arguments[0].scrollTop = arguments[1].offsetTop - arguments[0].offsetHeight / 2;
        """, checkbox_container, spain_option_div) #blessed claude
        
        driver.execute_script("arguments[0].click();", spain_option_div)


        time.sleep(2)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//button[div[@class='buttonLabel' and contains(., ' ') and span[@class='f16' and @country='{product_origin}' and @size='16']]]"))
        )
   
    except Exception as e:
        print(f"Failed to select {product_origin} as country: {e}")
        driver.save_screenshot("error_screenshot.png")


    try:

        number_selector = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//select[@name='bfi-table_length']"))
        )
        number_selector.click()

        number_option = number_selector.find_element(By.XPATH, f"//option[@value='{result_count}']")
        number_option.click()

    except Exception as e:
        print(f"Failed to select Number of Importers: {e}")


    try:
        filter_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.bfi.button"))
        )
        driver.execute_script("arguments[0].click();", filter_button)
        print("Filter button clicked")


    except Exception as e:
        print(f"Failed to click filter button: {e}")



    WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.ID, "bfi-table"))
    )
    print("Looking at table data....")

    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    bfi_table = soup.find("table", id="bfi-table")

    data = []
    headers = ["Company", "Phone", "General Email", "Website"]

    tbody = bfi_table.find("tbody")
    rows = tbody.find_all("tr")

    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 8:  
            company = cells[2].text.strip()
            phone = cells[3].text.strip()
            email = cells[4].text.strip()
            website = cells[7].text.strip()
            data.append([company, phone, email, website])

    df = pd.DataFrame(data, columns=headers)
    excel_filename = "wine_importers_data.xlsx"
    df.to_excel(excel_filename, index=False)

    return excel_filename
