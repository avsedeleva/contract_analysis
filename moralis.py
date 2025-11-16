import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()


class MoralisScraper:
    def __init__(self):
        API_MORALIS = os.getenv("API_MORALIS")
        self.headers = {
            "Accept": "application/json",
            "X-API-Key": API_MORALIS
        }
        self.holders = []
        #self.token_list = {}
        self.top_tokens= {}
        self.number = 0
        self.contract = None

    def get_wallet_balance(self, wallet_address):
        tokens = []
        #url = f"https://deep-index.moralis.io/api/v2.2/{wallet_address}/erc20?chain=eth"
        #url1 = f"https://deep-index.moralis.io/api/v2.2/wallets/{wallet_address}/tokens?chain=bsc&limit=25"
        #url1 = f"https://deep-index.moralis.io/api/v2.2/wallets/{wallet_address}/tokens"
        #url1 = f""
        url_dict = {
            'eth': f"https://deep-index.moralis.io/api/v2.2/wallets/{wallet_address}/tokens?chain=eth&limit=100",
            'bsc': f"https://deep-index.moralis.io/api/v2.2/wallets/{wallet_address}/tokens?chain=bsc&limit=100",
            #'base': f"https://deep-index.moralis.io/api/v2.2/wallets/{wallet_address}/tokens?chain=base&limit=100"
        }
        for chain, url in url_dict.items():
            response = requests.request("GET", url, headers=self.headers)
            try:
                data = response.json().get('result')
                #print(data)
            except:
                continue
            for info in data:
                #print(info)
                if info['possible_spam'] or info['security_score'] is None:
                    continue
                if info['security_score'] < 50:
                    continue
                if float(info.get('usd_value')) > 100:
                    tokens.append({

                            'chain': chain,
                            'name': info.get('symbol'),
                            'address': info.get('token_address'),
                            'quantity': round(float(info.get('balance_formatted')), 0),
                            'usd_value': round(float(info.get('usd_value')), 0)

                    }
                    )
        sorted_tokens = sorted(tokens, key=lambda x: x['usd_value'], reverse=True)
        # print(sorted_tokens[0:10])
        if len(sorted_tokens) >= 2:
            token_list = sorted_tokens[0:30]
        #print(token_list)
        #print(json.dumps(self.token_list, indent=4))
            for tok in token_list:
                if tok['address'].lower() != self.contract.lower():
                    i = f"{tok['chain']}_{tok['address']}_{tok['name']}"
                    if not self.top_tokens.get(i):
                        self.top_tokens[i] = {
                        'chain': tok['chain'],
                        'address': tok['address'],
                        'name': tok['name'],
                        'number': 1
                        }
                    else:
                        self.top_tokens[i]['number'] += 1

            return token_list
        return

    def get_top_holders(self, contract, input_contract_number):
        self.contract = contract
        url = f"https://deep-index.moralis.io/api/v2.2/erc20/{contract}/owners?chain=bsc&limit={input_contract_number}&order=DESC"
        response = requests.request("GET", url, headers=self.headers)
        count = 0
        for info in response.json().get("result"):
            count += 1

            if info.get("owner_address_label") is None:
                self.holders.append({
                    'address': info.get("owner_address"),
                    'quantity': round(float(info.get("balance_formatted")), 0),
                    'usd_value': round(float(info.get("usd_value")), 0),
                    'number': count
                    #'percent': round(float(info.get("21.253917305601945")), 2)
                })

        return self.holders

    def get_top_tokens(self):
        top_tokens_list = []
        for tok, info in self.top_tokens.items():

            top_tokens_list.append(info)
        sorted_info = sorted(top_tokens_list, key=lambda x: x['number'], reverse=True)
        if len(sorted_info) > 30:
            return sorted_info[0:30]
        return sorted_info

wallet_address = '0x6f6c1073266902197350463620591c0ff9467e85'#'0x7485e27650058d22590ccdee1a86604c71dd8ad8'#'0xd17974cd64ad371b387baeaef2f27c0e8e67f159' #'0x4858821da3a75c001a895072305b774af7a494d9'
contract = "0xd98438889Ae7364c7E2A3540547Fad042FB24642"
#MoralisScraper().get_wallet_balance(wallet_address)
#get_wallet_balance(wallet_address)