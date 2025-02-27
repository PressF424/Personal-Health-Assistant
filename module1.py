import logging
import asyncio  # Импортируем asyncio для запуска асинхронного кода
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ctransformers import AutoModelForCausalLM  # Используем ctransformers

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
API_TOKEN = '7813631986:AAGPnTeJWyCexp1x8ZrjeMS-tbG2iHtgs8g'  # Замени на свой токен
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # Указываем parse_mode через DefaultBotProperties
)
dp = Dispatcher()  # Теперь Dispatcher не принимает bot в качестве аргумента

# Подключение моделей ИИ
symptom_analyzer = AutoModelForCausalLM.from_pretrained(
    "C:/Users/asazo/.lmstudio/models/mradermacher/Symptom-detector-v0.1-GGUF/Symptom-detector-v0.1.Q4_K_S.gguf",
    model_type="llama"
)

mental_health_analyzer = AutoModelForCausalLM.from_pretrained(
    "C:/Users/asazo/.lmstudio/models/QuantFactory/Mental-Health-FineTuned-Mistral-7B-Instruct-v0.2-GGUF/Mental-Health-FineTuned-Mistral-7B-Instruct-v0.2.Q4_K_S.gguf",
    model_type="llama"
)

# Состояния для диалога
class UserState(StatesGroup):
    waiting_for_symptoms = State()
    waiting_for_mental_health = State()

# Команда /start
@dp.message(Command("start"))  # Используем Command для обработки команд
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я твой персональный помощник по здоровью. Чем могу помочь?")

# Обработка симптомов
@dp.message(Command("analyze_symptoms"))  # Используем Command для обработки команд
async def analyze_symptoms(message: types.Message, state: FSMContext):
    await state.set_state(UserState.waiting_for_symptoms)
    await message.reply("Опишите свои симптомы:")

@dp.message(UserState.waiting_for_symptoms)  # Обработка состояния
async def process_symptoms(message: types.Message, state: FSMContext):
    symptoms = message.text
    # Анализ симптомов с помощью модели
    result = symptom_analyzer(f"Analyze the following symptoms: {symptoms}")
    await message.reply(f"Результат анализа симптомов: {result}")
    await state.clear()  # Завершаем состояние

# Обработка ментального здоровья
@dp.message(Command("analyze_mental_health"))  # Используем Command для обработки команд
async def analyze_mental_health(message: types.Message, state: FSMContext):
    await state.set_state(UserState.waiting_for_mental_health)
    await message.reply("Как вы себя чувствуете сегодня?")

@dp.message(UserState.waiting_for_mental_health)  # Обработка состояния
async def process_mental_health(message: types.Message, state: FSMContext):
    feelings = message.text
    # Анализ ментального здоровья с помощью модели
    result = mental_health_analyzer(f"Analyze the following feelings: {feelings}")
    await message.reply(f"Результат анализа ментального здоровья: {result}")
    await state.clear()  # Завершаем состояние

# Напоминания
scheduler = AsyncIOScheduler()

async def send_reminder(chat_id):
    await bot.send_message(chat_id, "Не забудьте выпить стакан воды!")

@dp.message(Command("start_reminders"))  # Используем Command для обработки команд
async def start_reminders(message: types.Message):
    scheduler.add_job(send_reminder, 'interval', hours=2, args=(message.chat.id,))
    scheduler.start()
    await message.reply("Напоминания включены!")

# Запуск бота
async def main():
    await dp.start_polling(bot)  # Используем await для запуска бота

if __name__ == '__main__':
    asyncio.run(main())  # Запускаем асинхронный код с помощью asyncio.run