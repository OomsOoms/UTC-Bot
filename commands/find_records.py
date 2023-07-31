import asyncio
import concurrent.futures
import time

import aiohttp
import nextcord
from nextcord import Embed
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
sent_embed_titles = []



async def send_to_webhook(webhookURL, embed):
    async with aiohttp.ClientSession() as session:
        webhook = nextcord.Webhook.from_url(webhookURL, session=session)
        await webhook.send(embed=embed)


def scrape():
    while True:
        url = "https://live.worldcubeassociation.org"

        options = Options()
        options.add_argument("--headless")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        service = Service('chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)

        # Wait for the page to load and JavaScript to execute
        time.sleep(1)  # Adjust the waiting time as needed
        # Get the page's HTML after JavaScript execution
        page_html = driver.page_source

        driver.quit()

        html_soup = BeautifulSoup(page_html, 'html.parser')

        items = html_soup.find_all('ul', class_="MuiList-root MuiList-dense css-1uzmcsd")

        # Define a dictionary to map the class names to their corresponding record types
        record_types = {
            'MuiBox-root css-flgzw': ['WR', 0xFF3131, "https://cdn.discordapp.com/attachments/1133464859644788758/1133782837452083210/WR.png"], # World Record
            'MuiBox-root css-1hstzf1': ['CR', 0xFFEE59, "https://cdn.discordapp.com/attachments/1133464859644788758/1133782837720522792/CR.png"],   # Continental Record
            'MuiBox-root css-k2529z': ['NR', None, None]    # National Record
        }

        # Iterate through each <ul> element
        ul_element = items[1]
        # Find all <a> elements within the <ul>
        a_elements = ul_element.find_all('a', class_='MuiButtonBase-root MuiListItem-root MuiListItem-dense MuiListItem-gutters MuiListItem-padding MuiListItem-button css-1wxv7rq')

        # Iterate through each <a> element
        for a_element in a_elements:
            # Check if the <a> element represents any record type (WR, CR, or NR)
            for class_name, record_data in record_types.items():
                is_record = a_element.find('span', class_=class_name)

                if is_record:
                    link = a_element['href']
                    event_info = a_element.find('span', class_='MuiListItemText-primary').text.strip()
                    participant_info = a_element.find('p', class_='MuiListItemText-secondary').text.strip()

                    # If the record type is 'NR', stop the loop
                    if record_data[0] == 'NR':
                        break

                    if [event_info, participant_info] in sent_embed_titles:
                        continue

                    else:
                        record_embed = Embed(title=event_info, description=participant_info, url=f"{url}{link}", color=record_data[1])
                        record_embed.set_thumbnail(url=record_data[2])

                        asyncio.run(send_to_webhook(WEBHOOK_URL, record_embed))

                        sent_embed_titles.append([event_info, participant_info])

            else:
                continue  # If the inner loop did NOT break, continue with the next iteration of the outer loop
            break  # If the inner loop did break, break out of the outer loop as well
        time.sleep(10)


async def scrape_records():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        await asyncio.get_event_loop().run_in_executor(executor, scrape)
