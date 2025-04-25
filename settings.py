from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

load_dotenv()

BOT_API = os.getenv("BOT_API")
RPC_URL ="https://api.shardeum.org"
bot = Bot(token=BOT_API)
storage: MemoryStorage = MemoryStorage()
dp: Dispatcher = Dispatcher(storage=storage)

CHANNELS = ["@g7team_ru"]
