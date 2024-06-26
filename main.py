import logging
import os
from aiogram import Bot, Dispatcher, types
import g4f
from aiogram.utils import executor

from dotenv import load_dotenv
load_dotenv()

current_provider = g4f.Provider.Blackbox	
current_model = "gpt-3.5-turbo"

# Включите логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=os.getenv("API_TOKEN"))
dp = Dispatcher(bot)

# Словарь для хранения истории разговоров
conversation_history = {}

# Функция для обрезки истории разговора
def trim_history(history, max_length=4096):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    return history


@dp.message_handler(commands=['clear'])
async def process_clear_command(message: types.Message):
    user_id = message.from_user.id
    conversation_history[user_id] = []
    await message.reply("История диалога очищена.")

# Обработчик для каждого нового сообщения
@dp.message_handler()
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    user_input = message.text

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({"role": "user", "content": user_input})
    conversation_history[user_id] = trim_history(conversation_history[user_id])

    # chat_history = conversation_history[user_id]

    try:
        response = await g4f.ChatCompletion.create_async(
            model =  current_model,
            messages = [{"role": "system", "content": """Use only English language. Your name is Mr.Constantin.You are an AI acting as  STEM coordinator of an International school. 
            You help your colleagues with lesson plans. You speak English. The lesson plan should include the following parts:
            Vocabulary， Teacher’s questions， forms of lessons (e.g. lecture, conversation, presentation, excursion, research, 
            drafting, laboratory work, quiz, conference, seminar, written work)，lesson structure, Transdisciplinary connections, 
            activities and assessment. The total lesson duration is 40 minutes."""}, {'role': 'user', 'content': message.text}],
            provider = current_provider,
        )
        chat_gpt_response = response
    except Exception as e:
        print(f"{current_provider.__name__}:", e)
        chat_gpt_response = "Извините, произошла ошибка. Обратитесь к настоящему Mr.Constantin"

    conversation_history[user_id].append({"role": "assistant", "content": chat_gpt_response})
    print(conversation_history)
    length = sum(len(message["content"]) for message in conversation_history[user_id])
    print(length)
    await message.answer(chat_gpt_response)


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
