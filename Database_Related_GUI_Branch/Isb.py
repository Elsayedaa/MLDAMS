#https://www.geeksforgeeks.org/scrape-tables-from-any-website-using-python/
#Known issues:
    #Solved: "find_element_by_* commands are deprecated. Please use find_element() instead"
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from html_table_parser import HTMLTableParser
import pandas as pd
import math

def isb(username, password): 
    chromedriver_path = r"\\dm11\mousebrainmicro\Mouselight_Data_Management\Chromdriver\chromedriver.exe"
    ser = Service(chromedriver_path)
    try:
        driver = webdriver.Chrome(service = ser)
    except Exception as e:
        if "Message: session not created: This version of ChromeDriver only supports Chrome version" in str(e):
            bver_s = str(e).index("Current browser version is ")+27
            bver_e = bver_s + str(e)[bver_s:].index(" ")
            chromedriver_version = str(e)[bver_s:bver_e]
            print(f"The Google Chrome webdriver version at '{chromedriver_path}' does not match users version of Google Chrome.")
            print(f"You are currently using Google Chrome version: {chromedriver_version}.")
            print("Please download the appropriate webdriver version from: https://chromedriver.chromium.org/downloads")
            print(f"Then unpack the executable file to {chromedriver_path.replace('chromedriver.exe', '')}")
        if "Message: 'chromedriver.exe' executable needs to be in PATH" in str(e):
            print("chromedriver.exe not found in path. Executable file may have been deleted.")
    try:
        driver.get("http://wiki.int.janelia.org/wiki/pages/viewpage.action?spaceKey=ML&title=Imaged+Samples+Board")

        #u_bar = driver.find_element_by_id("os_username")
        u_bar = driver.find_element(By.ID, "os_username")
        #p_bar = driver.find_element_by_id("os_password")
        p_bar = driver.find_element(By.ID, "os_password")
        #login = driver.find_element_by_id("loginButton")
        login = driver.find_element(By.ID, "loginButton")
        

        u_bar.send_keys(username)
        p_bar.send_keys(password)
        login.click()
    except UnboundLocalError:
        return

    try:
        main = WebDriverWait(driver, math.inf).until(
            EC.presence_of_element_located((By.ID, "main-content"))
        )
        source = driver.page_source
        tableparser = HTMLTableParser()
        tableparser.feed(source)
        df = pd.DataFrame(tableparser.tables[0])
        df.columns = df.loc[0]
        df.drop([0], inplace=True)
        df.set_index("Sample Name (Imaging Date)", inplace=True)
    finally:
        driver.quit()
    return df