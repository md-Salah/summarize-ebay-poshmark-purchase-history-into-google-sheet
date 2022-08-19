from sys import exit
import os
import random
import time
from selenium.webdriver.common.keys import Keys

from helpers.scraper import Scraper
from helpers.utility import formatted_time, data_countdown, countdown, execution_time
from helpers.files import read_csv, read_txt, write_to_csv, write_to_txt, read_contact_info
from helpers.numbers import formatted_number_with_comma, numbers_within_text, str_to_int



if __name__ == "__main__":
    START_TIME = time.time()


    # Global variables
    url = 'https://www.google.com'
    d = Scraper(url, exit_on_missing_element=True)
    d.print_executable_path()

    print('hello world')
    
    
    
    # Footer for reporting
    execution_time(START_TIME)

    # Finally Close the browser
    input('Press any key to exit the browser...')
    d.driver.quit()
