# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 23:41:55 2018

@author: gli26
"""

import schedule
import pandas as pd
import numpy as np
from selenium import webdriver
import urllib2
import time
import re

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# function to continue to use last session

def create_driver_session(session_id, executor_url):
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

    # Save the original function, so we can revert our patch
    org_command_execute = RemoteWebDriver.execute

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return org_command_execute(self, command, params)

    # Patch the function before creating the driver object
    RemoteWebDriver.execute = new_command_execute

    new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    new_driver.session_id = session_id

    # Replace the patched function with original function
    RemoteWebDriver.execute = org_command_execute

    return new_driver


class qiangke:
    def __init__(self):
        None
        
    
    def take_action(self):
        get_success = False
        trial = 0
        self.driver=webdriver.Firefox()
        self.session_id =self.driver.session_id
        self.executor_url =self.driver.command_executor._url
        while not get_success and trial < 4:
            try:
                self.driver.get('https://my.ucdavis.edu/')
                time.sleep(5)
                self.driver.find_element_by_class_name("init-login").click()
                time.sleep(5)
                self.driver.find_element_by_id("username").send_keys("jtan19")
                self.driver.find_element_by_id("password").send_keys("Lisa1997925!")
                self.driver.find_element_by_id("submit").click()
                time.sleep(2)
                self.driver.get("https://my.ucdavis.edu/schedulebuilder/index.cfm?termCode=201803&helpTour=")
                get_success = True
        #    driver.find_element_by_link_text("Register ALL").click()
            except Exception as e:
                print e
                trial +=1
                time.sleep(5)
                continue
            
    def repeat(self):
        get_success = False
        trial = 0
        while not get_success and trial < 4:
            try:
                self.driver.find_element_by_link_text("Register ALL").click()
                get_success = True
        #    driver.find_element_by_link_text("Register ALL").click()
            except Exception as e:
                print e
                trial +=1
                time.sleep(5)
                continue
    
#instance
qiangke = qiangke() 

#
#qiangke.take_action()
#qiangke.repeat()
    
# =============================================================================
# ###################
 
schedule.every().day.at("6:30").do(qiangke.take_action)
schedule.every().day.at("6:01").do(qiangke.repeat)
schedule.every().day.at("6:51").do(qiangke.repeat)
 
 ######################    
     
     
while True:
    schedule.run_pending()
     
    time.sleep(1)
## =============================================================================
