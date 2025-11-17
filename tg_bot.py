import json

from dotenv import load_dotenv
from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bsc import BscScanScraper
from moralis import MoralisScraper

load_dotenv()

dp = Dispatcher()
mrl_scraper = MoralisScraper()

# Определение состояний
class Data(StatesGroup):
    waiting_for_contract = State()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await select_option(message, state)

# --- Опросная часть ---
@dp.message(Data.waiting_for_contract)
async def process_contract(message: types.Message, state: FSMContext):
    input_number_contract =100
    contract = message.text
    if '0x' not in contract:
        await message.answer("Контракт не корректный, введи еще раз")
    tokens_dict = await analyze(contract, input_number_contract)
    top_tokens = mrl_scraper.get_top_tokens()
    name = mrl_scraper.get_name()
    msg_general = (
        f'<a href="https://bscscan.com/address/{contract}"><b>{name}</b></a>\n'
        f'{len(tokens_dict)}/{input_number_contract} holders\n'
        f'TOP 30 TOKENS\n'
                   )

    for tok in top_tokens:
        if tok["chain"] == 'bsc':
            msg_general += f'{tok["chain"]} <a href="https://bscscan.com/address/{tok["address"]}"><b>{tok["name"]}</b></a>: {tok["number"]}\n'
        else:
            msg_general += f'{tok["chain"]} <a href="https://etherscan.io/address/{tok["address"]}"><b>{tok["name"]}</b></a>: {tok["number"]}\n'
    await message.answer(msg_general, disable_web_page_preview=True)
    for address, tok_list in tokens_dict.items():
        tokens = tok_list['tokens']
        number = tok_list['number']
        usd_value = f"{tok_list['usd_value']:,.2f}"
        msg = f'{number}  <a href="https://bscscan.com/address/{address}#asset-tokens">BSC {address}</a>\n<a href="https://etherscan.io/address/{address}#asset-tokens">ETH {address}</a>\n<i>USD VALUE:</i> {usd_value}\n<i>Chain    Name    USD value</i>\n'
        for tok in tokens:
            if tok["chain"] == 'bsc':
                msg += f'{tok["chain"]} <a href="https://bscscan.com/address/{tok["address"]}"><b>{tok["name"]}</b></a> {tok["usd_value"]:,.2f}\n'
            else:
                msg += f'{tok["chain"]} <a href="https://etherscan.io/address/{tok["address"]}"><b>{tok["name"]}</b></a> {tok["usd_value"]:,.2f}\n'
        await message.answer(msg, disable_web_page_preview=True)


# --- Utilits ---
async def select_option(message: types.Message, state: FSMContext):
    await message.answer('Введи контракт')
    await state.set_state(Data.waiting_for_contract)

async def analyze(contract, input_contract_number):
    holders_list = mrl_scraper.get_top_holders(contract, input_contract_number)
    tokens_dict = {}
    for holder_info in holders_list:
        tokens = mrl_scraper.get_wallet_balance(holder_info.get('address'))
        if tokens:
            tokens_dict[holder_info.get('address')] = {}
            tokens_dict[holder_info.get('address')]['tokens'] = tokens
            tokens_dict[holder_info.get('address')]['number'] = holder_info.get('number')
            tokens_dict[holder_info.get('address')]['usd_value'] = holder_info.get('usd_value')
            tokens_dict[holder_info.get('address')]['stat_number'] = len(tokens)
    #print(json.dumps(tokens_dict, indent=4))
    return tokens_dict

# Запуск бота
async def main(client_bot, bot):
    global client
    client = client_bot
    await client.connect()
    me = await client.get_me()
    print('START_APP', me.first_name)
    await dp.start_polling(bot)


