
import urllib

import requests
from bs4 import BeautifulSoup



class BscScanScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
})
        '''self.session.proxies.update({
            "http": "http://qWD41r:JdCPrA@196.19.121.132:8000"
        })'''
        self.wallets_dict = {}


    def get_wallet_balance(self, wallet_address):
        html = self.get_wallet_page(wallet_address)
        #print(html)
        if html:
            return self.parse_token_balances(html)


    def get_wallet_page(self, address):
        """Получить HTML страницы кошелька"""
        url = f"https://bscscan.com/address/{address}#asset-tokens"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            print('OK')
            return response.text
        except requests.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return None


    def parse_token_balances(self, html_content):
        """Парсинг балансов токенов из HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        #print(soup)
        tokens = []
        # Поиск таблицы с токенами
        token_table = soup.find_all('tr')
        quantity = None
        usd_value  =None
        for info in token_table:
            #print(info)
            i = info.find('a', class_='link-muted')
            #print(i)
            if not i:
                continue
            chain = i.text
            i = info.find('a', class_='link-dark hash-tag text-truncate')
            if not i:
                continue
            #print(i)
            name = i.text
            if name == 'Visit website extrabnb .net to claim rewards (Visit website extrabnb .net to claim rewards)':
                name = None
            if i and i.has_attr('href'):
                href_value = i['href']
                # Разбираем URL на составляющие
                parsed_url = urllib.parse.urlparse(href_value)
                # Разделяем путь по символу '/' и берем нужную часть
                path_parts = parsed_url.path.split('/')
                # Адрес контракта - это часть пути, идущая после '/token/'
                address = path_parts[2] if len(path_parts) > 2 else None
            number_list = info.find_all('td')
            for n in number_list:
                if not('%' in  n.text or '$' in n.text):
                    try:
                        quantity = round(float(n.text.replace(',', '')), 0)
                    except:
                        continue
                if n.get('data-totalval'):
                    usd_value = int(round(float(n.get('data-totalval')), 0))

            if usd_value > 100:
                tokens.append(
                    {
                        'chain': chain,
                        'name':  name,
                        'token_address': address,
                        'quantity': quantity,
                        'usd_value': usd_value
                    }
                )
        #print(tokens)
        sorted_tokens = sorted(tokens, key=lambda x: x['usd_value'], reverse=True)
        #print(sorted_tokens[0:10])
        if len(sorted_tokens) >= 2:
            self.wallets_dict = sorted_tokens[0:10]
        return self.wallets_dict



# Использование
'''contract = "0xd98438889Ae7364c7E2A3540547Fad042FB24642".lower()
scraper = BscScanScraper()
scraper.analyze(contract)'''
'''html_wallet = scraper.get_wallet_page('0x4858821da3a75c001a895072305b774af7a494d9')
#print(html_wallet)
if html_wallet:
    tokens = scraper.parse_token_balances(html_wallet, 'c')'''
    #print(tokens)
