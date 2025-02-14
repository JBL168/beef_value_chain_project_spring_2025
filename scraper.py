import requests
import os
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = 'https://mymarketnews.ams.usda.gov/'

# User Agent because MMN AMS blocks GET requests that look like bots
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0'
}

# Loop through each page in the database
for page_num in range(0,8):
    url = f'https://mymarketnews.ams.usda.gov/filerepo/reports?name=SJ_LS850&page={page_num}'
    download_folder = 'National_Feeder_Stocker_Cattle_Summary'
    os.makedirs(download_folder, exist_ok=True)

    try:
        # GET request for the database page
        db_page = requests.get(url, headers=headers)
        db_page.raise_for_status()

        soup = BeautifulSoup(db_page.content,'html.parser')

        # Find each element that contains the hyperlink
        td_elements = soup.find_all('td', class_='views-field views-field-field-document')

        for td in td_elements:
            hyperlink = td.find('a', href=True)
            relative_url = hyperlink['href']

            if hyperlink:
                full_href = urljoin(BASE_URL, relative_url)
                try:
                    # GET request for the .txt page
                    txt_page =  requests.get(full_href, headers=headers)
                    txt_page.raise_for_status()

                    file_name = os.path.basename(relative_url)
                    file_path = os.path.join(download_folder, file_name)

                    # Download the .txt from the page
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(txt_page.text)
                    print(f'Saved {file_name}')
                except HTTPError as err:
                    print(f'HTTP error occurred: {err}')
    except HTTPError as err:
        print(f'HTTP error occurred: {err}')
    

