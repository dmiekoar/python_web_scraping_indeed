import bs4
import selenium
import numpy as np
import pandas as pd
import datetime as dt
import re
import os
from selenium import webdriver
from bs4 import BeautifulSoup

get_all = False
published_days_ago = 3
filename = 'job_positions_indeed.csv'
number = 300

if os.path.exists(filename):
    df = pd.read_csv(filename)
    print('Loading existing data')
else:
    df = pd.DataFrame(columns = ["Title", "Location", "Company", "Summary", "Search_type", "Date", "Link", 'Extraction_date'])
    print('New df created')


driver = webdriver.Chrome("./chromedriver")

main_link = "https://se.indeed.com"

number = (number//15 + 1)*10
# The total number of ads distributed through the pages. Seems a bit strange. It shows 15 per page, while each page number changes each 10.
# Even if we scrap the total number correctly, the pages displayed are different.
# So probably better to set up a number and then drop duplicates registers.
page_range = np.arange(0,number,10)
print(number)
print(page_range)

# We will browse every page
for page in page_range:

    if page == 0:
        if get_all == True:
            driver.get("https://se.indeed.com/jobb?q=data+science%2C+data+analyst%2C+data+engineer%2C+machine+learning+engineer%2C+artificial+intelligence&l=Sverige")
        else:
            driver.get('https://se.indeed.com/jobs?q=data+science%2C+data+analyst%2C+data+engineer%2C+machine+learning+engineer%2C+artificial+intelligence&l=Sverige&fromage='+published_days_ago.astype(str))
    else:
        if get_all == True:
            driver.get("https://se.indeed.com/jobb?q=data+science%2C+data+analyst%2C+data+engineer%2C+machine+learning+engineer%2C+artificial+intelligence&l=Sverige&start="+page.astype(str))
        else:
            driver.get('https://se.indeed.com/jobs?q=data+science%2C+data+analyst%2C+data+engineer%2C+machine+learning+engineer%2C+artificial+intelligence&l=Sverige&fromage='+published_days_ago.astype(str)+ '&start='+page.astype(str))
    
    driver.implicitly_wait(15)

    result = driver.find_elements_by_class_name("result")


    # Loop through each position to extract its data
    for position in result:

        result_html = position.get_attribute('innerHTML')
        
        soup = BeautifulSoup(result_html, 'html.parser')

        # Job title
        try:
            title = soup.find("a", class_ = "jobtitle").text.replace('\n', '')
        except:
            title = 'None'
        
        # Location
        try:
            location = soup.find(class_ = "location").text
        except:
            location = 'None'
        
        # Company
        try:
            company = soup.find(class_ = "company").text.replace('\n', '').strip()
        except:
            company = 'None'
        
        # Summary
        try:
            summary = soup.find( class_ = "summary").text.replace('\n', '').strip()
        except:
            summary = 'None'
        
        # Whether the position is organic or sponsored
        try:
            sponsored = soup.find("a", class_ = "sponsoredGray").text
            sponsored = "Sponsored"
        except:
            sponsored = 'Organic'
            
        # How long it has been released
        try:
            date = soup.find("span", class_ = "date").text
        except:
            date = 'None'

        # Link to the job position
        try:
            relative_link = soup.find("a", class_="jobtitle")['href']
            link = main_link + relative_link
        except:
            link = 'None'
        
        # Check if job position gathered already exists in our df,
        # and only add it if it is a new record
        if link not in df['Link']:
            # Finally we append the extracted data into a df
            df = df.append({"Title":title, 
                                "Location":location, 
                                "Company":company, 
                                "Summary":summary, 
                                "Search_type":sponsored,
                                "Date":date,
                                "Link": link,
                                "Extraction_date": dt.date.today().isoformat()
                                }, 
                                ignore_index = True)
        else:
            print('Ignoring duplicated record')

    print(df.shape)

df.drop_duplicates(subset = ['Link'], inplace = True)
print(df.shape)
print(df.head().append(df.tail()))
df.to_csv('job_positions_indeed.csv', index = False)