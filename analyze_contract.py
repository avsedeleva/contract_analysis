import json
import urllib

import requests
from bs4 import BeautifulSoup
import time
import re
import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


class BscScanScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.session.proxies.update({
            "http": "http://qWD41r:JdCPrA@196.19.121.132:8000"
        })
        self.tokens_dict = {}

    def analyze(self, contract):
        html_top_holders = self.get_top_holders_page(contract)
        if html_top_holders:
            holders_list = self.parse_top_holders(html_top_holders)
            #print(holders_list)
            for holder_info in holders_list:
                html_wallet = self.get_wallet_page(holder_info.get('address'))
                #print(html_wallet)
                if html_wallet:
                    self.parse_token_balances(html_wallet, holder_info.get('address'))
        print(json.dumps(self.tokens_dict, indent=4))
        return self.tokens_dict

    def get_wallet_page(self, address):
        """Получить HTML страницы кошелька"""
        url = f"https://bscscan.com/address/{address}#asset-tokens"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return None

    def get_top_holders_page(self, contract):


        """Обход Cloudflare с помощью undetected-chromedriver"""
        try:
            url = f"https://bscscan.com/token/tokenholderchart/{contract}"

            options = uc.ChromeOptions()

            # Настройки для скрытия автоматизации
            options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')

            # Для сервера
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')

            # Реалистичный user-agent
            options.add_argument(
                '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            print("🔄 Запускаем undetected-chromedriver...")

            driver = uc.Chrome(
                options=options,
                driver_executable_path='/usr/bin/chromedriver'
            )

            # Устанавливаем таймауты
            driver.set_page_load_timeout(30)

            print(f"🌐 Открываем: {url}")
            driver.get(url)

            # Ждем загрузки контента
            wait = WebDriverWait(driver, 20)

            # Проверяем разные элементы которые должны быть на странице
            content_indicators = [
                (By.XPATH, "//table//tr"),
                (By.XPATH, "//div[contains(@class, 'card')]"),
                (By.XPATH, "//a[contains(@href, 'address')]"),
                (By.TAG_NAME, "table")
            ]

            content_loaded = False
            for by, selector in content_indicators:
                try:
                    wait.until(EC.presence_of_element_located((by, selector)))
                    print(f"✅ Найден контент: {selector}")
                    content_loaded = True
                    break
                except:
                    continue

            if not content_loaded:
                print("⚠ Контент не найден, проверяем что загрузилось...")
                '''# Сохраняем для отладки
                with open('/tmp/debug_page.html', 'w') as f:
                    f.write(driver.page_source)
                print("💾 HTML сохранен в /tmp/debug_page.html")'''
                print(driver.page_source)

            # Дополнительное время для JS
            time.sleep(3)

            html_content = driver.page_source

            # Проверяем успешность
            if "Holders" in html_content and len(html_content) > 10000:
                print("✅ Страница успешно загружена!")
                return html_content
            else:
                print("❌ Контент не содержит нужных данных")
                return None

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
        finally:
            try:
                driver.quit()
            except:
                pass
            '''options = webdriver.ChromeOptions()
            options.add_argument('--headless=new')  # Новый headless режим
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--remote-debugging-port=9222')

            # Опции для обхода защиты
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # Реалистичный user-agent
            options.add_argument(
                '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Дополнительные опции для скрытия
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            options.add_argument('--blink-settings=imagesEnabled=false')

            # Язык и регион
            options.add_argument('--lang=en-US,en;q=0.9')

            # Указываем браузер
            options.binary_location = '/usr/bin/chromium-browser'

            service = Service('/usr/bin/chromedriver')

            driver = webdriver.Chrome(service=service, options=options)

            # Удаляем свойства webdriver ДО загрузки страницы
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 
                           Object.defineProperty(navigator, 'webdriver', {
                               get: () => undefined
                           });
                           Object.defineProperty(navigator, 'plugins', {
                               get: () => [1, 2, 3, 4, 5]
                           });
                           Object.defineProperty(navigator, 'languages', {
                               get: () => ['en-US', 'en']
                           });
                       
            })

            print(f"🔄 Opening BSCscan: {url}")

            try:
                driver.get(url)

                # Ждем загрузки с проверками
                wait = WebDriverWait(driver, 15)

                # Проверяем разные элементы которые должны быть на странице
                selectors_to_check = [
                    "//div[contains(@class, 'card')]",
                    "//table",
                    "//div[contains(text(), 'Holders')]",
                    "//body"
                ]

                page_loaded = False
                for selector in selectors_to_check:
                    try:
                        wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                        print(f"✓ Found element: {selector}")
                        page_loaded = True
                        break
                    except:
                        continue

                if not page_loaded:
                    print("⚠ No expected elements found, but continuing...")

                # Дополнительное время для JS
                time.sleep(3)

                # Проверяем содержимое страницы
                html = driver.page_source
                current_url = driver.current_url

                print(f"📊 Page source length: {len(html)}")
                print(f"🌐 Current URL: {current_url}")

                # Проверяем не попали ли мы на капчу или блокировку
                if "captcha" in html.lower() or "cloudflare" in html.lower():
                    print("❌ CAPTCHA or Cloudflare detected")
                    return None

                if "access denied" in html.lower():
                    print("❌ Access denied by BSCscan")
                    return None

                if len(html) < 1000:
                    print("❌ Page content too short")
                    return None

                print("✅ Page loaded successfully")
                return html

            except Exception as page_error:
                print(f"❌ Page loading error: {page_error}")
                return None

            finally:
                driver.quit()

        except Exception as e:
            print(f"❌ Selenium setup error: {e}")'''


        """Получить HTML страницы контракта
        url = f"https://bscscan.com/token/tokenholderchart/{contract}"
        '''options = Options()
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        options.add_argument('--disable-blink-features=AutomationControlled')'''
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--remote-debugging-port=9222')

        # Явно укажите путь к Chrome
        #options.binary_location = '/usr/bin/google-chrome'
        options.binary_location = '/usr/bin/chromium-browser'
        # Для Selenium 4.x и выше
        from selenium.webdriver.chrome.service import Service
        service = Service('/usr/bin/chromedriver')

        driver = webdriver.Chrome(service=service, options=options)
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )



        #driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(8)
        html = driver.page_source
        driver.quit()
        #print(html)
        return html"""

    def parse_top_holders(self, html_content):
        """Парсинг топ холдеров из HTML"""
        holders = []
        address = None
        soup = BeautifulSoup(html_content, 'html.parser')
        #print(soup)
        holder_rows = soup.find_all('tr')
        #print(holder_rows)
        for info in holder_rows:

            link = info.find('a')


            if link:

                name = link.get_text(strip=True)
                #address = link.get('data-highlight-target')
                if link and link.has_attr('href'):
                    href_value = link['href']
                    # Разбираем URL на составляющие
                    parsed_url = urllib.parse.urlparse(href_value)
                    # Разделяем путь по символу '/' и берем нужную часть
                    address = parsed_url.query[2:]

            quantity_list = info.find_all('td')
            if quantity_list:
                for q in quantity_list:
                    q = q.get_text(strip=True)
                    try:
                        quantity = float(q.replace(',',''))
                    except:
                        if '%' in q:
                            percent = float(q.replace(',', '').replace('%', ''))


            if address:
                #print('address', address, 'name', name, 'quantity', quantity, 'percent', percent)
                if '0x' in name:
                    holders.append({
                        'address': address,
                        'name': name,
                        'quantity': quantity,
                        'percent': percent
                    })
        return holders

    def parse_token_balances(self, html_content, holder_address):
        """Парсинг балансов токенов из HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        #print(soup)
        tokens = []

        # Поиск таблицы с токенами
        token_table = soup.find_all('tr')
        count = 0
        quantity = None
        usd_value  =None
        #print(token_table)
        for info in token_table:
            #print(info)
            i = info.find('a', class_='link-muted')
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


            '''token_table = soup.find_all('li',  class_='nav-item list-custom-ERC20')
        count = 0
        for info in token_table:
            #print(info)
            name = info.find('span', class_='list-name hash-tag text-truncate').find('span').get('data-bs-title')
            if name == 'Visit website extrabnb .net to claim rewards (Visit website extrabnb .net to claim rewards)':
                name = None

            link = info.find('a')

            if link and link.has_attr('href'):
                href_value = link['href']
                # Разбираем URL на составляющие
                parsed_url = urllib.parse.urlparse(href_value)
                # Разделяем путь по символу '/' и берем нужную часть
                path_parts = parsed_url.path.split('/')
                # Адрес контракта - это часть пути, идущая после '/token/'
                address = path_parts[2] if len(path_parts) > 2 else None


            quantity = info.find('span', class_='text-muted').get_text(strip=True).split(' ')[0]
            usd_value = info.find('div', class_='list-usd-value').get_text(strip=True)
            usd_value = 0 if usd_value == '' else float(usd_value.replace(',', '')[1:])'''


            #print(name, address, quantity, usd_value)
            if usd_value > 100:
                tokens.append(
                    {
                        'chain': chain,
                        'name':  name,
                        'address': address,
                        'quantity': quantity,
                        'usd_value': usd_value
                    }
                )
        #print(tokens)
        sorted_tokens = sorted(tokens, key=lambda x: x['usd_value'], reverse=True)
        #print(sorted_tokens[0:10])
        if len(sorted_tokens) >= 2:
            self.tokens_dict[holder_address] = sorted_tokens[0:10]
        return tokens



# Использование
'''contract = "0xd98438889Ae7364c7E2A3540547Fad042FB24642".lower()
scraper = BscScanScraper()
scraper.analyze(contract)'''
'''html_wallet = scraper.get_wallet_page('0x4858821da3a75c001a895072305b774af7a494d9')
#print(html_wallet)
if html_wallet:
    tokens = scraper.parse_token_balances(html_wallet, 'c')'''
    #print(tokens)
