import requests
import os
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = 'https://mymarketnews.ams.usda.gov/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0'
}

for page_num in range(0,8):
    URL = f'https://mymarketnews.ams.usda.gov/filerepo/reports?name=SJ_LS850&page={page_num}'
    download_folder = 'National_Feeder_Stocker_Cattle_Summary'
    os.makedirs(download_folder, exist_ok=True)

    try:
        db_page = requests.get(URL, headers=headers)
        db_page.raise_for_status()

        soup = BeautifulSoup(db_page.content,'html.parser')
        td_elements = soup.find_all('td', class_='views-field views-field-field-document')

        for td in td_elements:
            hyperlink = td.find('a', href=True)
            RELATIVE_URL = hyperlink['href']

            if hyperlink:
                full_href = urljoin(BASE_URL, RELATIVE_URL)
                try:
                    txt_page =  requests.get(full_href, headers=headers)
                    txt_page.raise_for_status()

                    file_name = os.path.basename(RELATIVE_URL)
                    file_path = os.path.join(download_folder, file_name)

                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(txt_page.text)
                    print(f'Saved {file_name}')
                except HTTPError as err:
                    print(f'HTTP error occurred: {err}')
    except HTTPError as err:
        print(f'HTTP error occurred: {err}')
    

