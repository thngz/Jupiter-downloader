from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import asyncio
import time
import re
import ffmpeg

t1 = time.time()
url = input("Sisesta Jupiteri URL: ")
#get the file name
filename = input("Sisesta soovitud failinimi (voib tuhjaks jatta) : ")
filepath= input("Sisesta sobiva kausta asukoht (nt C:\Documents\) (voib tuhjaks jatta) : ")
if not filename:
    filename = url.rsplit('/', 1)[-1]

async def get_network_log(headless=True, filter="master.m3u8"):
    while True:
        try:
            # init Chrome driver (Selenium)
            options = Options()
            options.add_experimental_option('w3c', False) ### added this line
            options.headless = headless
            cap = DesiredCapabilities.CHROME
            cap["loggingPrefs"] = {"performance": "ALL"}
            ### installed chromedriver.exe and identify path
            print("Jooksutan Chromedriveri")
            driver = webdriver.Chrome(r"/usr/lib/chromium/chromedriver", desired_capabilities=cap, options=options) ### installed
            # record and parse performance log
            driver.get(url)
            print("Filtreerin sisu")
            if filter:
                log = [item for item in driver.get_log("performance") if filter in str(item)]
            else:
                log = driver.get_log("performance")
            driver.close()
            print("Leiame master.m3u8 urli")
            #regex magic to find urls (returns a list of them, take the last one)
            
            urls  = re.findall('(https.*?[^&"^>?!^$]+)', log[0]["message"])
            return urls[-1]
        except IndexError:
            print("Ei leidnud m3u8 faili, proovin uuesti")
            time.sleep(5)
        
#Convert m3u8 to mp4 using FFMPEG library and download the result
async def m3u8_to_mp4(m3u8_url):
    print("Konventeerin MP4ks")
    print(m3u8_url)
    (
    ffmpeg
    .input(m3u8_url)
    .output(f"{filepath}{filename}.mp4", absf='aac_adtstoasc')
    .run()
    )

async def main():
    m3u8_url = await get_network_log()
    await m3u8_to_mp4(m3u8_url)
    print("Aega kulus", time.time() - t1, "sekundit")
    
loop = asyncio.get_event_loop()
loop.run_until_complete(main())