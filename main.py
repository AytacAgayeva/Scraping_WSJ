import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date,datetime
import os, sys
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

chrome_options = Options()
options = [
    "--headless",
    "--disable-gpu",
    "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage"
]
for option in options:
    chrome_options.add_argument(option)

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
#from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# service = ChromeService(executable_path=ChromeDriverManager().install())

#driver = webdriver.Chrome(executable_path=r'C:\Users\Aytac Agayev\Downloads\chromedriver_win32\chromedriver.exe')
driver.get('https://www.wsj.com/wsjsitemaps/wsj_google_news.xml')
driver

soup = BeautifulSoup(driver.page_source, 'html')
urls = soup.find_all("url")
today=date.today()
now = datetime.now()
current_time = now.strftime("%H_%M")
data = []
for url in urls:
    loc = url.loc.text
    title = url.find("news:title").text
    language = url.find("news:language").text
    publication_date = url.find("news:publication_date").text[:10]
    publication_time = url.find("news:publication_date").text[11:19]
    image_loc_tag = url.find("image:loc")
    keywords_tag=url.find("news:keywords")
    if image_loc_tag and keywords_tag  is not None:
        image_loc = image_loc_tag.text
        keywords=keywords_tag.text
    row_data = {
        "URL": loc,
        "Title": title,
        "Language":language,
        "Publication Date": publication_date,
        "Publication Time": publication_time,
        "Image URL": image_loc,
        }
    data.append(row_data)    
df = pd.DataFrame(data)
path="./json"
df.to_json(os.path.join(path,f'sitemap_wsj_news__{today}_{current_time}.json'))

files = [f for f in os.listdir(path) if f.endswith(".json")]
files.sort()
last_2_files=files[-2:]
if len(last_2_files)==2:
    data_new=pd.read_json(f'./json/{last_2_files[1]}')
    data_old=pd.read_json(f'./json/{last_2_files[0]}')
    news_count = pd.DataFrame({"Time": [last_2_files[1][-10:-5]], "Count": [data_new.shape[0]]})
    old = set(data_old['Title'])
    new = set(data_new['Title'])
    dif_old = old.difference(new)
    dif_new = new.difference(old)
    inter = old.intersection(new)
    all_news = pd.DataFrame({"Time": [f'{last_2_files[0][-10:-5]} - {last_2_files[1][-10:-5]}'], 
                          "NEW": [len(dif_new)], 
                          "SAME": [len(inter)], 
                          "EXCLUDED": [len(dif_old)]})
    all_news.to_csv(f'./all_news/sitemap_wsj_news_{today}__{current_time}.csv',index=False)
    news_count.to_csv(f'./news_count/sitemap_wsj_news_{today}__{current_time}.csv',index=False)
    
    files_news = [f for f in os.listdir("./all_news") if f.endswith(".csv")]
    files_news.sort()
    file_path = os.path.join("./all_news", files_news[0])
    data_all = pd.read_csv(file_path)
    data_all=pd.concat([data_all,all_news],axis=0)
    data_all.to_csv(file_path,index=False)
    
    count_news = [f for f in os.listdir("./news_count") if f.endswith(".csv")]
    count_news.sort()
    count_path = os.path.join("./news_count", count_news[0])
    count_all = pd.read_csv(count_path)
    count_all=pd.concat([count_all,news_count],axis=0)
    count_all.to_csv(count_path,index=False)
    
else:
    data_old=pd.read_json(f'./json/{last_2_files[0]}')
    news_count = pd.DataFrame({"Time": [last_2_files[0][-10:-5]], "Count": [data_old.shape[0]]})
    all_news_ = pd.DataFrame({"Time": [f'{last_2_files[0][-10:-5]}'], 
                          "NEW": [data_old.shape[0]], 
                          "SAME": [0], 
                          "EXCLUDED": [0]})
    all_news_.to_csv(f'./all_news/all_time_news.csv',index=False)
    news_count.to_csv(f'./news_count/all_time_news_count.csv',index=False)
