import sys
import re
import json
import pickle
import netrc
import logging

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

__all__ = ['Session', 'get_session']

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)


def setup_webdriver():
    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)  # https://realpython.com/blog/python/headless-selenium-testing-with-python-and-phantomjs/
    return driver


def copy_cookies_to_session(driver, session):
    """Copy cookies from selenium webdriver to requests.Session"""
    cookies = driver.get_cookies()
    for cookie in cookies:
        session.cookies.set(
            cookie['name'],
            cookie['value'],
            domain=cookie['domain'],
            path=cookie['path']
        )


class Session(object):
    """A Google Analytics session"""

    def __init__(self):
        self.s = None

    def find_sign_in(self, driver):
        conditions = [
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Sign in")),
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "SIGN IN")),
        ]
        for condition in conditions:
            try:
                sign_in = WebDriverWait(driver, 5).until(condition)
            except:
                pass
            else:
                break
        return sign_in

    def login(self, username, password):
        driver = setup_webdriver()
        try:
            url = "http://www.google.com/analytics/"
            #url = "http://www.google.com/analytics/ce/nrs/?utm_expid=71218119-7.lBgmrTO8R3uEDwsxNxa_Nw.2"
            driver.get(url)
            sign_in = self.find_sign_in(driver)
            sign_in.click()
            driver.find_element_by_id("Email").clear()
            driver.find_element_by_id("Email").send_keys(username)
            try:
                driver.find_element_by_id("Passwd").clear()
                driver.find_element_by_id("Passwd").send_keys(password)
            except:
                driver.find_element_by_id("next").click()
                driver.find_element_by_id("Passwd").clear()
                driver.find_element_by_id("Passwd").send_keys(password)
            driver.find_element_by_id("signIn").click()
            self.s = requests.Session()
            copy_cookies_to_session(driver, self.s)
        except:
            driver.save_screenshot('/tmp/ga_problem.png')
            raise
        finally:
            driver.quit()

    def is_logged_in(self):
        url = "https://www.google.com/analytics/web/"
        response = self.s.get(url, params={'hl': 'en'})
        return "Reporting" in response.text

    def save(self, file):
        pickle.dump(self.s.cookies, file)

    def load(self, file):
        self.s = requests.Session()
        self.s.cookies = pickle.load(file)

    def get_csrf_token(self):
        url = "https://www.google.com/analytics/web/"
        response = self.s.get(url, params={'hl': 'en'})
        token = re.search('"token":{"value":"(.*?)"', response.text).group(1)
        return token

    def get_page(self, params):
        csrf_token = self.get_csrf_token()
        data = {
            'token': csrf_token,
        }
        url = "https://www.google.com/analytics/web/getPage"
        response = self.s.post(url, data=data, params=params)
        return response.json()

    def get_data(self, params):
        url = "https://www.google.com/analytics/realtime/realtime/getData"
        response = self.s.get(url, params=params)
        return response.json()


def get_session(session_path="saved_session"):
    username, _, password = netrc.netrc().authenticators("google.com")
    session = Session()
    logger.debug("trying to load saved session")
    try:
        session.load(file(session_path, 'rb'))
    except IOError:
        logger.debug("error loading saved session")
        logger.debug("logging in")
        session.login(username, password)
        session.save(file(session_path, 'wb'))
    else:
        logger.debug("loaded saved session")
        logger.debug("are we still logged in?")
        if not session.is_logged_in():
            logger.debug("no so logging in")
            session.login(username, password)
            logger.debug("saving session")
            session.save(file(session_path, 'wb'))
        else:
            logger.debug("yup, we're still logged in")
    return session
