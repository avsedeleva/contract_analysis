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
bsc_scraper = BscScanScraper()
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
    contract = message.text
    if '0x' not in contract:
        await message.answer("Контракт не корректный, введи еще раз")
    tokens_dict = await analyze(contract)
    for address, tok_list in tokens_dict.items():
        msg = f"<code>{address}</code>\n<i>Chain    Name    USD value</i>\n"
        for tok in tok_list:
            msg += f"{tok['chain']} <b>{tok['name']}</b> {tok['usd_value']:,.2f}\n"
        await message.answer(msg)


# --- Utilits ---
async def select_option(message: types.Message, state: FSMContext):
    await message.answer('Введи контракт')
    await state.set_state(Data.waiting_for_contract)

async def analyze(contract):
    holders_list = mrl_scraper.get_top_holders(contract)
    tokens_dict = {}
    for holder_info in holders_list:
        tokens = bsc_scraper.get_wallet_balance(holder_info.get('address'))
        tokens_dict[holder_info.get('address')] = tokens
    print(json.dumps(tokens_dict, indent=4))
    return tokens_dict

# Запуск бота
async def main(client_bot, bot):
    global client
    client = client_bot
    await client.connect()
    me = await client.get_me()
    print('START_APP', me.first_name)
    await dp.start_polling(bot)


