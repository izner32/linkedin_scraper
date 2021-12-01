# for scraping 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup as bs

# misc
import re as re # regex 
import time
import pandas as pd

# accesing env file 
import os 
from dotenv import load_dotenv # to access the secret keys we've hidden in a separate file 
load_dotenv() # grab values inside env file

PATH = os.getenv("WEBDRIVER_PATH")
USERNAME = os.getenv("LI_USERNAME")
PASSWORD = os.getenv("LI_PASS")

# initialize web driver that would control the web browser
ser = Service(PATH)
op = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=ser, options=op)

# website we wanted to access 
driver.get("https://www.linkedin.com/uas/login")
time.sleep(3) # added a pause to avoid getting marked as bot 

# login in linkedin
email=driver.find_element(By.ID,"username")
email.send_keys(USERNAME)
password=driver.find_element(By.ID,"password")
password.send_keys(PASSWORD)
time.sleep(3)
password.send_keys(Keys.RETURN)

# Creating lists
post_links = []
post_texts = []
post_names = []

def Scrape_func(post_links,post_texts,post_names):
    name = post_links[28:-1]
    page = post_links
    time.sleep(10)

    driver.get(page + 'detail/recent-activity/shares/')  
    start=time.time()
    lastHeight = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        newHeight = driver.execute_script("return document.body.scrollHeight")
        if newHeight == lastHeight:
            break
        lastHeight = newHeight
        end=time.time()
        if round(end-start)>20: # how long the webdriver gets to collect posts, in this case 20 seconds 
            break

    company_page = driver.page_source   

    linkedin_soup = bs(company_page.encode("utf-8"), "html")
    linkedin_soup.prettify()
    containers = linkedin_soup.findAll("div",{"class":"occludable-update ember-view"})
    print("Fetching data from account: "+ name)
    iterations = 0
    nos = int(input("Enter number of posts: "))
    for container in containers:

        try:
            text_box = container.find("div",{"class":"feed-shared-update-v2__description-wrapper ember-view"})
            text = text_box.find("span",{"dir":"ltr"})
            post_texts.append(text.text.strip())
            post_names.append(name)
            iterations += 1
            print(iterations)
            
            if(iterations==nos):
                break

        except:
            pass 

# Using recursion with our function
n = int(input("Enter the number of entries: "))
for i in range(n):
    post_links.append(input("Enter the link: "))
for j in range(n):
    Scrape_func(post_links[j],post_texts,post_names)

driver.quit()

data = {
    "Name": post_names,
    "Content": post_texts,
}

# save to csv 
df = pd.DataFrame(data)
df.to_csv("user_posts.csv", encoding='utf-8', index=False)

# save to excel 
writer = pd.ExcelWriter("user_posts.xlsx", engine='xlsxwriter')
df.to_excel(writer, index =False)
writer.save()