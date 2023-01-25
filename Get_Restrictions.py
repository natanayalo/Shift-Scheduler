#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 13:15:16 2023

@author: ayalo
"""

import os, json

from selenium import webdriver

chrome_options = webdriver.chrome.options.Options()
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument('--headless')
chrome_options.add_argument("disable-infobars"); # disabling infobars
chrome_options.add_argument("--disable-extensions"); # disabling extensions
chrome_options.add_argument("--disable-dev-shm-usage"); # overcome limited resource problems
chrome_options.add_argument("--no-sandbox"); # Bypass OS security model

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')

driver = webdriver.Chrome(chrome_options=chrome_options)

driver.get("https://www.timetable.co.il/")

#Get the location of the fill boxes of username and password on TimeTable
userNameTextBox = driver.find_element(webdriver.common.by.By.ID, "ctl00_ContentPlaceHolderMain_MultiLogin1_txtUsername")
passwordTextBox = driver.find_element(webdriver.common.by.By.ID, "ctl00_ContentPlaceHolderMain_MultiLogin1_txtPass")

#Clear the fill boxes of username and password on TimeTable
userNameTextBox.clear()
passwordTextBox.clear()

#Set the fill boxes of username and password on TimeTable
userNameTextBox.send_keys("natan.ayalo@dynamicyield.com")
passwordTextBox.send_keys("Ayalo461")
passwordTextBox.send_keys(webdriver.common.keys.Keys.RETURN)

driver.implicitly_wait(20)

#enter requests on TimeTable
driver.find_element(webdriver.common.by.By.XPATH,"/html/body/div[1]/div[1]/div[1]/span/div/div[3]/div/div[3]/div[2]/span[3]/div").click()
print('ok!!!')
driver.implicitly_wait(20)
# print(driver.find_element(webdriver.common.by.By.ID,"_srv2461280611_c442"))
# element = driver.find_element(webdriver.common.by.By.XPATH,"/html/body/div[1]/div[1]/div[1]/span/div/div[1]/div[2]/span/span/div/div[3]/div[1]/div/div[5]/div[1]/div[2]").text
# print(element)

shifts = ["Morning", "Evening", "Night"]

# List of days
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


#detailed shift list
open_shifts = []
blocked_shift = []

# Load Dictionary of restrictions
restrictions = json.load(open("Restrictions.json"))

for day in range(1,8):
    for shift in range(1,4):
        element = driver.find_element(webdriver.common.by.By.XPATH,f"/html/body/div[1]/div[1]/div[1]/span/div/div[1]/div[2]/span/span/div/div[3]/div[{day}]/div/div[5]/div[{shift}]/div[2]").text
        if element == 'לא יכול':
            blocked_shift.append(days[day-1]+' '+shifts[shift-1])



# Serializing jsons
schedule_json = json.dumps(schedule_copy, indent=4)
shifts_json = json.dumps(shifts_copy, indent=4)

# Writing to schedule.json
with open("Schedule.json", "w") as outfile:
    outfile.write(schedule_json)        
with open("Shifts.json", "w") as outfile:
    outfile.write(shifts_json) 


