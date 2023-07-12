"""
This script scrapes the validator staking data from the Polygon staking website
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
import time
import numpy as np

#import model.constants as constants


def get_validator_info():
    # Use Chrome as the web browser
    ## Customized: need to change local chromedriver PATH
    service = ChromeService(executable_path='/Users/wenxuan/Desktop/polygon/cadCAD/polygon-economic-model/data/api/chromedriver')
    options = ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    #driver = webdriver.Chrome()
    # Load the web page
    driver.get("https://staking.polygon.technology/validators")
    time.sleep(20)
    # Wait for the page to load
    driver.implicitly_wait(100)
    button = driver.find_element(By.CSS_SELECTOR, "button.secondary > i.fa-arrows-alt-v")
    button.click()
    # Get the HTML of the page
    html = driver.page_source
    # Parse the HTML
    soup = BeautifulSoup(html, features='html.parser')
    # Scraping the data
    raw_data_by_row = soup.find_all("a")
    validator_name = []
    stake_amount = []
    commission_rate = []
    checkpoints_signed = []
    health_status = []
    liveness_status = []
    for row in raw_data_by_row:
        validator_name_element = row.find("div", class_="list-item__left__validator-name")
        if validator_name_element:
            validator_name.append(validator_name_element.get_text())
        else:
            validator_name.append(None)
        stake_amount_element = row.find("span", class_="list-item__info__amount--value pr-2")
        if stake_amount_element:
            stake_amount.append(stake_amount_element.get_text())
        else:
            stake_amount.append(None)
        commission_rate_element = row.find("div", class_="list-item__info__item__green")
        if commission_rate_element:
            commission_rate.append(commission_rate_element.get_text())
        else:
            commission_rate.append(None)
        checkpoints_signed_element = row.find("div", class_="list-item__info__item__purple")
        if checkpoints_signed_element:
            checkpoints_signed.append(checkpoints_signed_element.get_text())
        else:
            checkpoints_signed.append(None)
        # health_status_element = row.find("div", class_="list-item__info__item__health__tooltip__text list-item__info__item__health__tooltip__text--row-view")
        # if health_status_element:
        #     health_status.append(health_status_element.get_text())
        # live_status_element = row.find("button", class_="btn secondary list-item__action__button")
        # if live_status_element:
        #     liveness_status.append(live_status_element.get_text())
    # Close the web browser
    driver.close()
    return validator_name, stake_amount, commission_rate, checkpoints_signed


def get_validator_staking_values(default=np.repeat(30_000_000, 100)):
    validator_name, stake_amount, _, _ = get_validator_info()
    stake_amount = [float(value.replace(',', '')) for value in stake_amount if value]
    if len(stake_amount) > 0:
        return np.array(stake_amount)
    else:
        return default


def get_validator_staking_total_value(default=3_000_000_000):
    total_stake = sum(get_validator_staking_values())
    return total_stake

