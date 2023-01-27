#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 13:15:16 2023

@author: ayalo
"""
import os
import json
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

shifts = ["Morning", "Evening", "Night"]

# List of days
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

employees_list = json.load(open("Employees.json"))

restrictions = {}

blocked_shift = []

# Get environment variables
username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')

options = webdriver.chrome.options.Options()
options.add_argument("--window-size=1920,1080")
options.add_argument("start-maximized")
options.add_argument('--headless')
options.add_argument("disable-infobars");  # disabling infobars
options.add_argument("--disable-extensions");  # disabling extensions
options.add_argument("--disable-dev-shm-usage");  # overcome limited resource problems
options.add_argument("--no-sandbox");  # Bypass OS security model

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
options.add_argument(f'user-agent={user_agent}')

driver = webdriver.Chrome(options=options)

driver.get("https://www.timetable.co.il/")

# Get the location of the fill boxes of username and password on TimeTable
userNameTextBox = driver.find_element(By.ID, "ctl00_ContentPlaceHolderMain_MultiLogin1_txtUsername")
passwordTextBox = driver.find_element(By.ID, "ctl00_ContentPlaceHolderMain_MultiLogin1_txtPass")

# Clear the fill boxes of username and password on TimeTable
userNameTextBox.clear()
passwordTextBox.clear()

# Set the fill boxes of username and password on TimeTable
userNameTextBox.send_keys(username)
passwordTextBox.send_keys(password)
passwordTextBox.send_keys(Keys.RETURN)

driver.implicitly_wait(5)

# enter requests on TimeTable
driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[1]/span/div/div[3]/div/div[3]/div[2]/span[8]/div").click()
driver.implicitly_wait(5)


# # Serializing jsons
# restrictions_json = json.dumps(restrictions, indent=4)

# # Writing to schedule.json
# with open("Restrictions.json", "w") as outfile:
#     outfile.write(restrictions_json)  


# enter requests control
driver.find_element(By.XPATH,
                    "/html/body/div[1]/div[1]/div[3]/span[2]/div/div/table/tbody/tr[1]/td[1]/span/div/div/span[1]/span/div").click()
driver.implicitly_wait(5)
# enter employees that sent requests
driver.find_element(By.XPATH,
                    "/html/body/div[1]/div[1]/div[1]/span/div/div[2]/div[2]/div/div[4]/div/div[1]/div/span[1]/span[3]/div").click()
driver.implicitly_wait(5)

num = driver.find_element(By.XPATH,
                          "/html/body/div[1]/div[1]/div[1]/span/div/div[2]/div[2]/div/div[4]/div/div[1]/div/span[1]/span[3]/div/div/div[5]/div/div[2]").text
count = int(re.findall("\d+", num)[0])
name = driver.find_element(By.XPATH,
                           "/html/body/div[1]/div[1]/div[1]/span/div/div[2]/div[2]/div/div[4]/div/div[2]/div[2]/div/span/div[2]/div/table/tbody/tr[1]/td[2]/span").text

for i in range(1, count):
    # enter employee section
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                     f"/html/body/div[1]/div[1]/div[1]/span/div/div[2]/div[2]/div/div[4]/div/div[2]/div[2]/div/span/div[2]/div/table/tbody/tr[{i}]/td[1]/img")))
    driver.find_element(By.XPATH,
                        f"/html/body/div[1]/div[1]/div[1]/span/div/div[2]/div[2]/div/div[4]/div/div[2]/div[2]/div/span/div[2]/div/table/tbody/tr[{i}]/td[1]/img").click()
    driver.implicitly_wait(5)

    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                     "/html/body/div[1]/div[1]/div[1]/span/div/div[3]/div[2]/div/div[2]/div[1]/div/div[2]/div[1]/table[1]/tbody/tr[2]/td[3]/div")))
    # get employee name
    employee = driver.find_element(By.XPATH,
                                   "/html/body/div[1]/div[1]/div[1]/span/div/div[3]/div[2]/div/div[2]/div[1]/div/div[2]/div[1]/table[1]/tbody/tr[2]/td[3]/div").text
    print(employee)

    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                     "/html/body/div[1]/div[1]/div[1]/span/div/div[3]/div[2]/div/div[2]/div[1]/div/div[1]/div[1]/span/span[3]/div")))
    # enter employees requests
    driver.find_element(By.XPATH,
                        "/html/body/div[1]/div[1]/div[1]/span/div/div[3]/div[2]/div/div[2]/div[1]/div/div[1]/div[1]/span/span[3]/div").click()

    driver.implicitly_wait(5)

    restrictions[employee] = []
    # manually block shifts by location
    if employee in employees_list['Portugees']:
        # block Saturday night
        restrictions[employee].append("Saturday Night")
        # block Sunday
        # restrictions[employee].extend(["Sunday " + shift for shift in shifts])
        # block Monday morning and evening
        restrictions[employee].extend(["Monday Morning", "Monday Evening"])

    elif employee in employees_list['Israelis']:
        # block Monday night
        restrictions[employee].append("Monday Night")
        # block Tuesday to Friday
        restrictions[employee].extend(
            [day + ' ' + shift for day in days if day not in ["Sunday", 'Monday', 'Saturday'] for shift in shifts])
        # block Saturday morning and evening
        restrictions[employee].extend(["Saturday Morning", "Saturday Evening"])
    else:
        continue

    # add the employee submitted requests
    for day in range(1, 8):
        for shift in range(1, 4):
            curr_shift = days[day - 1] + ' ' + shifts[shift - 1]
            if curr_shift not in restrictions[employee]:
                element = driver.find_element(By.XPATH,
                                              f"/html/body/div[1]/div[1]/div[1]/span/div/div[1]/div[2]/span/span/div/div[3]/div[{day}]/div/div[5]/div[{shift}]/div[2]").text
                if element == 'לא יכול':
                    restrictions[employee].append(curr_shift)

    wait = WebDriverWait(driver, 30)
    element = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                     "/html/body/div[1]/div[1]/div[1]/span/div/div[3]/div[1]/img")))
    # close request
    driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[1]/span/div/div[3]/div[1]/img").click()
    driver.implicitly_wait(5)
# except:
#     break


print(restrictions)

# Serializing jsons
restrictions_json = json.dumps(restrictions, indent=4)

# Writing to schedule.json
with open("Restrictions.json", "w") as outfile:
    outfile.write(restrictions_json)