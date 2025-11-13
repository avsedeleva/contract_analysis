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

    def get_wallet_balance(self, wallet_address):
        url = f"https://deep-index.moralis.io/api/v2.2/{wallet_address}/erc20?chain=eth"
        response = requests.request("GET", url, headers=self.headers)
        print(json.dumps(response.json(), indent=4))
        return response.json()

    def get_top_holders(self, contract):
        url = f"https://deep-index.moralis.io/api/v2.2/erc20/{contract}/owners?chain=bsc&limit=100&order=DESC"
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
        #print(self.holders)
        return self.holders


wallet_address = '0x4858821da3a75c001a895072305b774af7a494d9'
contract = "0xd98438889Ae7364c7E2A3540547Fad042FB24642"
MoralisScraper().get_top_holders(contract=contract)
#get_wallet_balance(wallet_address)