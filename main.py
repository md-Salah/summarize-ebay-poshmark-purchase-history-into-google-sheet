from sys import exit
import os
import random
import time
from selenium.webdriver.common.keys import Keys

from helpers.scraper import Scraper
from helpers.utility import formatted_time, data_countdown, countdown, execution_time
from helpers.files import read_csv, read_txt, write_to_csv, write_to_txt, read_contact_info
from helpers.numbers import float_within_text, numbers_within_text, str_to_int
from helpers.gsheet import gsheet

def is_visited(href): #Utility function for checking visited href
    for url in prev_urls:
        if href == url:
            return True
    return False

def write_to_gsheet(Title, Size, Dollar, Date, Order_href): #Utility function for inserting into gsheet
    global sheet_index
    
    data = [Title, Size, '', '', Dollar, '', '', '', Date, '', '', '', '', Order_href]
    worksheet.insert_row(data, index=sheet_index)
    
    sheet_index += 1

def set_end_marker(for_site, href):
    if for_site == 'ebay':
        end_marker[0] = href
    elif for_site == 'poshmark':
        end_marker[1] = href
    else:
        print('end marker for ebay or poshmark?')
    write_to_txt(end_marker, file_name='inputs/end_marker.txt')
    
def poshmark_login():
    logInBtn = d.find_element('a[href="/login"]')
    d.element_click(element=logInBtn)
    d.sleep(3, 4)
    
    d.element_send_keys(credentials['pm_username'], 'input[name="login_form[username_email]"]')
    d.element_send_keys(credentials['pm_password'], 'input[name="login_form[password]"]')
    d.element_click('button[data-pa-name="login"]')
    d.sleep(3, 4)
    
def poshmark_main():
    d.add_login_functionality('ul[class="header__account-info-list"]', 
                              login_function=poshmark_login, cookies_file_name='pm_cookies')

    d.go_to_page('https://poshmark.com/order/purchases')
    sales_div = d.find_element('div[class^="order-activity"]', loop_count=3)
    time.sleep(3)
    for _ in range(6):
        orders = d.find_elements('div a[href^="/order/purchases/"]', ref_element=sales_div)
        if orders and len(orders) > 0:
            d.scroll_wait(element=orders[-1])
        else:
            time.sleep(2)
    links = []
    for a in orders:
        href = a.get_attribute('href')
        links.append(href)
    # print('Len of order links: ', len(links))
    
    # visit the links
    for Order_href in links:
        if end_marker[1] == Order_href:
            set_end_marker('poshmark', links[0])
            return
        if is_visited(Order_href):
            continue

        d.go_to_page(Order_href)
        date_div = d.find_element('div[class="listing-info__detail"]', loop_count=2, wait_element_time=10)
        Date = date_div.text.strip()
        
        title_divs = d.find_elements('div[class^="order-items__item-title"]')
        size_divs = d.find_elements('div[class="order-items__item-info"]')
        
        dollar_div = d.find_element(xpath="//div[contains(text(), 'Order Total')]")
        Dollar = f'${float_within_text(dollar_div.text.strip())[0]//len(title_divs)}'
        
        for i, title_div in enumerate(title_divs):
            Title = title_div.text.strip()
            Size = size_divs[i].text.split('Size:')[1].strip()
            
            write_to_gsheet(Title, Size, Dollar, Date, Order_href)

def ebay_login():
    signInBtn = e.find_element('a[href^="https://signin.ebay.com"]')
    if signInBtn:
        signInBtn.click()
        time.sleep(2)
        e.element_send_keys(credentials['ebay_username'], '#userid')
        e.element_click('#signin-continue-btn')
        e.element_send_keys(credentials['ebay_password'], '#pass')
        e.element_click('#sgnBt')
        e.element_click('#smsWithCode-btn', exit_on_missing_element=False) #Send OTP
        input('Enter ebay OTP then press any key...')

def ebay_main():
    e.add_login_functionality('#gh-ug b', 
            login_function=ebay_login, cookies_file_name='ebay_cookies')

    e.go_to_page('https://www.ebay.com/mye/myebay/purchase')
    
    while True:
        orders_div = e.find_elements('div.m-container-items', loop_count=5)[1]
        orders = e.find_elements('div.m-order-card', ref_element=orders_div)

        for i, order in enumerate(orders):
            # Order href
            order_num_div = e.find_element('div.ph-col__info-orderNumber dd', ref_element=order)
            Order_href = 'https://www.ebay.com/vod/FetchOrderDetails?orderId=' + order_num_div.text.strip()            
            if i == 0:
                starting_href = Order_href
            
            if end_marker[0] == Order_href:
                set_end_marker('ebay', starting_href)
                return
            
            if is_visited(Order_href):
                continue  
            
            date_div = e.find_element('div.ph-col__info-orderDate dd', ref_element=order)
            Date = date_div.text.strip()
            
            dollar_div = e.find_element('dl.ph-col__info-orderTotal', ref_element=order)
            Dollar = f'${float_within_text(dollar_div.text.strip())[0]}'
            
            product_href_a = e.find_elements('a[href^="https://www.ebay.com/itm/"]', ref_element=order)[1]
            product_href = product_href_a.get_attribute('href')
            Title = product_href_a.text.strip()
            
            # Go for size
            e.open_new_tab(product_href)
            size_div = e.find_element(xpath="//div[contains(@class, 'ux-layout-section__row') and contains(., 'US Shoe Size')]", wait_element_time=5)
            Size = size_div.text.split('US Shoe Size:')[1].split('\n')[0].strip()
            e.close_tab_and_back_homepage()
            
            write_to_gsheet(Title, Size, Dollar, Date, Order_href)
            
        #Go to next page 
        next_page_btn = e.find_element('button[class*=pagination__next]', exit_on_missing_element=False)
        if next_page_btn:
            time.sleep(2)
            next_page_btn.click()
            time.sleep(8)
        else:
            break          
                

if __name__ == "__main__":
    START_TIME = time.time()
    
    ## Global variables
    credentials = read_contact_info('inputs/credentials.txt', '=')
    end_marker = read_txt('inputs/end_marker.txt')
    worksheet = gsheet()
    prev_urls = worksheet.col_values(14) # Index 14 represents column E which contains the previous order urls
    sheet_index = len(prev_urls) + 1
    
    ## Start poshmark
    d = Scraper('https://poshmark.com')
    d.print_executable_path()
    poshmark_main()
    d.driver.quit()
    
    ## Start ebay
    time.sleep(3)
    e = Scraper('https://www.ebay.com/')
    ebay_main()
    e.driver.quit()
    
    ## Footer for reporting
    execution_time(START_TIME, f'{sheet_index-len(prev_urls)-1} row inserted into google sheet')
