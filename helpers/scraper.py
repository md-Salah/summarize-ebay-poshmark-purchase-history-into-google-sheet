from helpers.files import read_executable_path_info
import zipfile
import os
from sys import exit
import pickle
import time
import getpass
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from multiprocessing import freeze_support
freeze_support()
import undetected_chromedriver as uc


class Scraper:

    chrome_version = None                           # Chrome browser version
    wait_element_time = 3                           # The time we are waiting for element to get loaded in the html in each loop count
    cookies_folder = 'cookies' + os.path.sep        # In this folder we will save cookies from logged in users


    def __init__(self, url, headless=False, proxy=None, exit_on_missing_element = True):
        self.url = url
        self.exit_on_missing_element = exit_on_missing_element        # Wheather we exit or not if we are missing an element
        self.browser_paths = read_executable_path_info('chrome_path.txt', '=')
        self.browser_executable_path = self.browser_paths['browser'] or None
        self.driver_executable_path = os.path.join(os.getcwd(), self.browser_paths['driver']) if self.browser_paths['driver'] else None
        self.headless = headless or (True if self.browser_paths['headless'].lower() == 'true' else False)
        
        self.setup_driver_options(self.headless, proxy)
        self.setup_driver()

    # Automatically close driver on destruction of the object
    def __del__(self):
        if self.headless == False:
            # print('closing browser')
            pass

    # Add these options in order to make chrome driver appear as a human instead of detecting it as a bot
    def setup_driver_options(self, headless, proxy):
        self.driver_options = uc.ChromeOptions()

        arguments = [
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            '--start-maximized',
            # '--disable-blink-features=AutomationControlled',              # This will solve the driver.get(url) error & also selenium detection, chrome shows warning
            # '--disable-dev-shm-usage',                                    # May be required for headless chrome
            # '--no-sandbox',                                               # with sandbox, one tab cannot watch another tab
            '--disable-popup-blocking',                                     # Otherwise new tab will not be opened
            '--no-first-run --no-service-autorun --password-store=basic',   # just some options passing in to skip annoying popups
            # '--user-data-dir=c:\\temp\\profile',                            # Saving user profile
        ]

        # experimental_options = {
        #     'excludeSwitches': ['enable-automation', 'enable-logging'],
        #     'prefs': {
        #         'profile.default_content_setting_values.notifications': 2,

        #         
        #         'credentials_enable_service': False,          # Disable the save password popups
        #         'profile.password_manager_enabled': False
        #     }
        # }

        for argument in arguments:
            self.driver_options.add_argument(argument)

        # for key, value in experimental_options.items():
        # 	self.driver_options.add_experimental_option(key, value)

        if headless:
            self.driver_options.add_argument('--headless')

        if proxy:
            self.driver_options.add_argument(
                f'--proxy-server={proxy}')     # proxy=106.122.8.54:3128

    # Setup chrome driver with predefined options

    def setup_driver(self):

        self.driver = uc.Chrome(
            options=self.driver_options,
            driver_executable_path=self.driver_executable_path,
            browser_executable_path=self.browser_executable_path,
            version_main=self.chrome_version,
            use_subprocess = True
        )

        self.sleep(3, 4) # Wait for the browser to open properly
        self.go_to_page(self.url)

    def print_executable_path(self):
        print('chrome browser path: ', self.browser_executable_path)
        print('chromedriver path:   ', self.driver_executable_path)
        print('headless:    ', self.headless)
        
    # Add login functionality and load cookies if there are any with 'cookies_file_name'
    def add_login_functionality(self, is_logged_in_selector, loop_count=10, login_function=None, exit_on_login_failure=True, cookies_file_name='cookies'):
        # Three step Login. 1:Using cookies, 2:By Selenium UI automation, 3:Manual login Then press any key
        self.is_logged_in_selector = is_logged_in_selector
        self.cookies_file_name = cookies_file_name + '.pkl'
        self.cookies_file_path = self.cookies_folder + self.cookies_file_name
        self.login_status = False

        # Step 1: Check if there is a cookie file saved
        if self.is_cookie_file():
            self.load_cookies()		# Load cookies
            # Check if user is logged in after adding the cookies
            self.login_status = self.is_logged_in(loop_count)

        # Step 2: Call the login method for Selenium UI interaction login
        if self.login_status == False:
            if login_function:
                login_function()
                self.login_status = self.is_logged_in(
                    loop_count)  # Check if user is logged in

        # Step 3: Manual Login
        if self.login_status == False:
            input('Login manually, then press ENTER...')
            self.sleep(1.0, 3.0)
            self.login_status = self.is_logged_in(
                loop_count)  # Check if user is logged in

        if self.login_status == True:
            self.save_cookies()		# User is logged in. So, save the cookies

        elif exit_on_login_failure == True:
            self.exit_with_exception(
                reason='Sorry, We are failed to be logged In.')

        return self.login_status

    # Check if cookie file exists
    def is_cookie_file(self):
        return os.path.exists(self.cookies_file_path)

    # Load cookies from file
    def load_cookies(self):
        # Load cookies from the file
        cookies_file = open(self.cookies_file_path, 'rb')
        cookies = pickle.load(cookies_file)

        for cookie in cookies:
            self.driver.add_cookie(cookie)

        cookies_file.close()

        self.go_to_page(self.url)

        time.sleep(5)

    # Save cookies to file
    def save_cookies(self):
        # Do not save cookies if there is no cookies_file name
        if not hasattr(self, 'cookies_file_path'):
            return

        # Create folder for cookies if there is no folder in the project
        if not os.path.exists(self.cookies_folder):
            os.mkdir(self.cookies_folder)

        # Open or create cookies file
        cookies_file = open(self.cookies_file_path, 'wb')

        # Get current cookies from the driver
        cookies = self.driver.get_cookies()

        # Save cookies in the cookie file as a byte stream
        pickle.dump(cookies, cookies_file)

        cookies_file.close()

    # Check if user is logged in based on a html element that is visible only for logged in users
    def is_logged_in(self, loop_count=5):
        element = self.find_element(
            self.is_logged_in_selector, loop_count=loop_count)
        return True if element else False

    # Wait random amount of seconds before taking some action so the server won't be able to tell if you are a bot
    def sleep(self, a=0.10, b=0.50, implicit=False):
        random_sleep_seconds = round(random.uniform(a, b), 2)

        if implicit:
            self.driver.implicitly_wait(random_sleep_seconds)
        else:
            time.sleep(random_sleep_seconds)

    # Goes to a given page and waits random time before that to prevent detection as a bot
    def go_to_page(self, url):
        self.sleep()
        self.driver.get(url)

    def exit_with_exception(self, reason):  # Utility function
        if input('e: Exit | Press any key to exit...') == 'e':
            raise Exception(reason)

    def find_element(self, css_selector='', xpath='', ref_element=None, loop_count=1, exit_on_missing_element='f', wait_element_time=None):

        wait_element_time = wait_element_time or self.wait_element_time
        driver = ref_element or self.driver
        exit_on_missing_element = self.exit_on_missing_element if exit_on_missing_element == 'f' else exit_on_missing_element

        # Intialize the condition to wait
        if css_selector:
            wait_until = EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
        elif xpath:
            wait_until = EC.visibility_of_element_located((By.XPATH, xpath))
        else:
            self.exit_with_exception(reason='ERROR: CSS_SELECTOR | XPATH is required to find element')

        for _ in range(loop_count):
            try:
                # Wait for element to load
                element = WebDriverWait(driver, wait_element_time).until(wait_until)
                return element
            except TimeoutException:
                time.sleep(1)
            except Exception as e:
                self.exit_with_exception(e)
                

        if exit_on_missing_element:
            self.exit_with_exception(reason=f'ERROR: Timed out waiting for the element with selector "{css_selector or xpath}" to load')

        return None

    def find_elements(self, css_selector='', xpath='', ref_element=None, loop_count=1, exit_on_missing_element='f', wait_element_time=None):

        wait_element_time = wait_element_time or self.wait_element_time
        driver = ref_element or self.driver
        exit_on_missing_element = self.exit_on_missing_element if exit_on_missing_element == 'f' else exit_on_missing_element

        for _ in range(loop_count):
            try:
                if css_selector:
                    elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
                elif xpath:
                    elements = driver.find_elements(By.XPATH, xpath)
                else:
                    self.exit_with_exception(reason='ERROR: CSS_SELECTOR | XPATH is required to find elements')

                return elements
            except TimeoutException:
                time.sleep(1)
            except Exception as e:
                self.exit_with_exception(e)

        if exit_on_missing_element:
            self.exit_with_exception(reason=f'ERROR: Timed out waiting for the element with selector "{css_selector or xpath}" to load')

        return None

    def click_checkbox(self, css_selector='input[type="checkbox"]', index=0, loop_count=1):
        elements = self.find_elements(css_selector=css_selector, loop_count=loop_count)
        return self.element_click(element=elements[index])

    def click_radio(self, css_selector='input[type="radio"]', index=0, loop_count=1):
        elements = self.find_elements(css_selector=css_selector, loop_count=loop_count)
        return self.element_click(element=elements[index])

    def select_dropdown(self, css_selector, val, text=False):
        element = self.find_element(css_selector)
        select = Select(element)
        if text:
            select.select_by_visible_text(val)
        else:
            val = str(val) if type(val) == int else val
            select.select_by_value(val)

    def add_emoji(self, selector, text):
        JS_ADD_TEXT_TO_INPUT = """
		var elm = arguments[0], txt = arguments[1];
		elm.value += txt;
		elm.dispatchEvent(new Event('change'));
		"""
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        self.driver.execute_script(JS_ADD_TEXT_TO_INPUT, element, text)
        element.send_keys('.')
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(Keys.TAB)

    def scroll_wait(self, selector, sleep_duration=2):
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto',block: 'center',inline: 'center'});", element)
        time.sleep(sleep_duration)

    # Wait random time before cliking on the element
    def element_click(self, css_selector='', xpath='', element=None, loop_count=1, exit_on_missing_element=True, delay=True):

        if css_selector or xpath:
            element = self.find_element(css_selector=css_selector, xpath=xpath, loop_count=loop_count)

        if element:
            if delay:
                self.sleep()
            try:
                element.click()
            except ElementClickInterceptedException:
                self.element_click_by_javaScript(element=element)
            except Exception as e:
                self.exit_with_exception(reason=f'Error: Can not click {element} with selector {css_selector or xpath}\n{e}')
        elif exit_on_missing_element:
            self.exit_with_exception(f'No element to click with selector {css_selector or xpath}')
        
        return element

    # Wait random time before sending the keys to the element
    def element_send_keys(self, text, css_selector='', xpath='', element=None,  clear_input=True, loop_count=1, exit_on_missing_element=True, delay=True):

        if css_selector or xpath:
            element = self.find_element(css_selector=css_selector, xpath=xpath, loop_count=loop_count)

        if element:
            if delay:
                self.sleep()

            self.element_click(element=element, delay=False)
            if clear_input:
                self.element_clear(element=element, delay=False)
            element.send_keys(text)
        elif exit_on_missing_element:
            self.exit_with_exception(f'No element to send keys with selector {css_selector or xpath}')
            
        return element

    # scraper.input_file_add_files('input[accept="image/jpeg,image/png,image/webp"]', images_path)
    def input_file_add_files(self, css_selector, files, loop_count=1):
        input_file = self.find_element(
            css_selector=css_selector, loop_count=loop_count)

        self.sleep()

        try:
            input_file.send_keys(files)
        except InvalidArgumentException:
            self.exit_with_exception(reason=f'ERROR: Exiting input_file_add_files! Please check if these file paths are correct:\n {files}')

    # Wait random time before clearing the element (popup)
    def element_clear(self, css_selector='', xpath='', element=None, loop_count=1, exit_on_missing_element=True, delay=True):

        if css_selector or xpath:
            element = self.find_element(css_selector=css_selector, xpath=xpath, loop_count=loop_count)

        if element:
            self.element_click(element=element)
            if delay:
                self.sleep()
            element.clear()

            if element.get_attribute('value') != '':
                element.send_keys(Keys.CONTROL + "a")
                element.send_keys(Keys.DELETE)
        elif exit_on_missing_element:
            self.exit_with_exception(f'No element to send keys with selector {css_selector or xpath}')
            
        return element

    def element_wait_to_be_invisible(self, selector):
        wait_until = EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, selector))

        try:
            WebDriverWait(self.driver, self.wait_element_time).until(
                wait_until)
        except:
            self.exit_with_exception(
                reason=f'Error: waiting the element with selector {selector} to be invisible')

    def open_new_tab(self, url):
        self.driver.execute_script("window.open(arguments[0])", url)
        self.driver.switch_to.window(self.driver.window_handles[1])

    def close_tab_and_back_homepage(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def switch_to_tab(self, tab_index):
        tab_index = int(tab_index)
        self.driver.switch_to.window(self.driver.window_handles[tab_index])

    def element_click_by_javaScript(self, element):
        # If the element is not clickable in normal way because element is covered by another element
        self.driver.execute_script('arguments[0].click()', element)
        return element

    def element_set_attribute(self, element, key='value', value=''):
        self.driver.execute_script("arguments[0].setAttribute(arguments[1], arguments[2])", element, key, value)

    def get_network_log(self):
        logs = self.driver.execute_script('''
                                    var performance = window.performance || 
                                    window.mozPerformance || 
                                    window.msPerformance || 
                                    window.webkitPerformance || {}; 
                                    var network = performance.getEntries() || {}; 
                                    return network; 
                                    ''')
        return logs

    def move_to_element(self, element):
        action = ActionChains(self.driver)
        action.move_to_element(element)
        action.perform()
