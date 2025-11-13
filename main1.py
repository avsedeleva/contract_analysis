from analyze_contract import BscScanScraper

contract = "0xd98438889Ae7364c7E2A3540547Fad042FB24642".lower()
scraper = BscScanScraper()
scraper.analyze(contract)