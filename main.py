import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import database  # Импорт модуля базы данных

API_TOKEN = 'Your Token'

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Список админов
ADMINS = ['admin_username1', 'admin_username2', 'admin_username3']

# Инициализация базы данных
database.init_db()

# Переменная для хранения текущей категории и вопроса
user_category = {}
admin_question = {}

# Хендлер для команды /start
@dp.message(Command(commands=['start']))
async def send_welcome(message: types.Message):
    if message.from_user.username in ADMINS:
        # Сообщение и кнопка для админов
        await message.answer("Добро пожаловать Администратор!")
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Посмотреть непрочитанные вопросы и предложения \U0001F5C4 \U0001F50D",
                                  callback_data="view_unread")]
        ])
        await message.answer("\U000023EC\U000023EC\U000023EC \U0001F440 \U000023EC\U000023EC\U000023EC",
                             reply_markup=markup)
    else:
        # Сообщение и инлайн-кнопка для пользователей
        await message.answer("Привет! Это бот \U0001F916 обратной связи.\n"
                             "Здесь вы можете анонимно задать вопрос команде обучения, "
                             "оставить свои пожелания и предложения.")
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Start", callback_data="start")]
        ])
        await message.answer("Нажмите 'Start' для продолжения", reply_markup=markup)

# Обработка нажатия инлайн-кнопки "Start"
@dp.callback_query(F.data == "start")
async def process_start(call: types.CallbackQuery):
    logging.info(f"Processing start callback: {call.data}")
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вопросы по каналу для СМЗ", callback_data="question_smz")],
        [InlineKeyboardButton(text="Проблемы с обучением для стажеров", callback_data="problem_training")],
        [InlineKeyboardButton(text="Идеи и темы для обучения", callback_data="ideas_training")]
    ])
    await call.message.edit_text("Выберите категорию вашего вопроса или предложения", reply_markup=markup)
    await call.answer()

# Обработка выбора категории
@dp.callback_query(F.data.in_(["question_smz", "problem_training", "ideas_training"]))
async def category_selected(call: types.CallbackQuery):
    logging.info(f"Category selected: {call.data}")
    user_category[call.from_user.id] = call.data
    await call.message.edit_text("Задайте ваш вопрос или опишите проблему \U0001F4DD")
    await call.answer()

# Обработка получения вопроса
@dp.message(F.text)
async def receive_question(message: types.Message):
    if message.from_user.id in user_category:
        category = user_category.pop(message.from_user.id)
        categories = {
            "question_smz": "Вопросы по каналу для СМЗ",
            "problem_training": "Проблемы с обучением для стажеров",
            "ideas_training": "Идеи и темы для обучения"
        }
        category_name = categories.get(category, "Неизвестная категория")
        database.save_question(message.from_user.id, message.from_user.username, category_name, message.text)
        await message.answer("Спасибо за ваше обращение!\n"
                             "Мы рассмотрим его и постараемся ответить, как можно быстрее.")

# Обработка нажатия кнопки "Посмотреть непрочитанные вопросы и предложения" для администраторов
@dp.callback_query(F.data == "view_unread")
async def show_unread_questions(call: types.CallbackQuery):
    if call.from_user.username in ADMINS:
        questions = database.get_unread_questions()
        if not questions:
            await call.message.answer("Нет непрочитанных вопросов.")
        else:
            for question in questions:
                question_id, user_id, username, category, text = question
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Ответить", callback_data=f"answer_{question_id}")]
                ])
                await call.message.answer(f"Категория: {category}\n"
                                          f"Вопрос: {text}", reply_markup=markup)
        await call.answer()

# Обработка нажатия кнопки "Ответить"
@dp.callback_query(F.data.startswith('answer_'))
async def answer_question(call: types.CallbackQuery):
    question_id = call.data.split('_')[1]
    user_category[call.from_user.id] = question_id
    await call.message.answer("Пожалуйста, введите ваш ответ.")
    await call.answer()

# Обработка ответа администратора
@dp.message(F.text)
async def receive_answer(message: types.Message):
    if message.from_user.id in user_category:
        question_id = user_category.pop(message.from_user.id)
        database.save_answer(question_id, message.text)

        # Уведомление администратора
        await message.answer("Ваш ответ отправлен.")

        # Получение ID пользователя и отправка ему ответа
        user_id = database.get_user_id_by_question_id(question_id)
        if user_id:
            await bot.send_message(user_id, f"Вы получили ответ на Ваше обращение: {message.text}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())