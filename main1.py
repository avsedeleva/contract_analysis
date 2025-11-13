import json

from bsc import BscScanScraper
from moralis import MoralisScraper

contract = "0xd98438889Ae7364c7E2A3540547Fad042FB24642"
mrl_scraper = MoralisScraper()
bsc_scraper = BscScanScraper()


def analyze(contract):
    holders_list = mrl_scraper.get_top_holders(contract)
    tokens_dict = {}
    for holder_info in holders_list:
        tokens = bsc_scraper.get_wallet_balance(holder_info.get('address'))
        tokens_dict[holder_info.get('address')] = tokens
    print(json.dumps(tokens_dict, indent=4))
    return tokens_dict

analyze(contract)