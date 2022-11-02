import requests
from bs4 import BeautifulSoup
import csv
import time
from pprint import pprint

url = 'https://jobs.dou.ua/companies/'
current_time = time.strftime("%Y-%m-%d")

headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }

s = requests.Session()

def get_site(url):
    r = s.get(url=url, headers=headers)
    return r.content

def decodeEmail(encodedString):
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email


def get_data(content):
    soup = BeautifulSoup(content, 'lxml')

    company = soup.find_all('div', class_='company')
    new_list = []
    for items in company:
        company_title = items.find('a', class_='cn-a')
        company_url = company_title.get('href')
        company_description = items.find('div', class_='descr').get_text(strip=True).replace('\xa0', ' ')
        if company_description == '':
            company_description = None

        r = s.get(f'{company_url}/offices', headers=headers)
        new_soup = BeautifulSoup(r.content, 'lxml')
        full_info = new_soup.find('div', class_='g-company-wrapper')
        company_site = full_info.find('div', class_='site')
        if company_site is not None:
            company_site = full_info.find('div', class_='site').get_text(strip=True)
        company_size = list(new_soup.find('div', class_='company-info').stripped_strings)[1]
        company_phone = new_soup.find_all('div', class_='phones')
        phones_list = []
        if len(company_phone) > 0:
            for phones in company_phone:
                phones_list.append(phones.get_text(strip=True))
        company_mail = new_soup.find_all('div', class_='mail')
        mails_list = []
        if len(company_mail) > 0:
            for mails in company_mail:
                mails_list.append(decodeEmail(mails.find('span').get('data-cfemail')))
        new_list.append({
            'company_title': company_title.get_text(),
            'company_url': company_url,
            'company_description': company_description,
            'company_site': company_site,
            'company_size': company_size,
            'company_phone': phones_list,
            'company_mails': mails_list,
        })
    return new_list

def main():
    content = get_site(url)
    site_data = get_data(content)
    with open(f'{current_time}_dou_parser.csv', 'w', encoding='utf8', newline='') as output_file:
        fc = csv.DictWriter(output_file, 
                            fieldnames=site_data[0].keys(),

                        )
        fc.writeheader()
        fc.writerows(site_data)

if __name__ == '__main__':
    print('Dou parser started')
    main()
    print('Dour parser finished')