import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, MessageReactionUpdated
from aiogram.enums import ReactionTypeEmoji
from aiogram.filters import Command
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from config import BOT_TOKEN
from cipher import encode
from storage import add_pending, get_pending, remove_pending, set_locked

WAIT_TIME = 5

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_new_message(message: Message):
    if message.from_user.id == bot.id:
        return
    if message.text and message.text.startswith('/'):
        return
    
    original_text = message.text
    if not original_text:
        return
    
    
    try:
        await message.delete()
    except:
        return
    
    
    placeholder = await message.answer(
        f"⏳ {message.from_user.first_name} пишет секретное сообщение..."
    )
    
    add_pending(placeholder.message_id, original_text, message.from_user.id, message.chat.id)
    
    
    asyncio.create_task(wait_and_process(placeholder))

async def wait_and_process(placeholder: Message):
    await asyncio.sleep(WAIT_TIME)
    
    data = get_pending(placeholder.message_id)
    if not data:
        return
    
    chat_id = data["chat_id"]
    original_text = data["original_text"]
    
    if data["locked"]:
        encrypted = encode(original_text)
        await bot.send_message(chat_id, f"🔐 {encrypted}")
    else:
        await bot.send_message(chat_id, original_text)
    
    try:
        await placeholder.delete()
    except:
        pass
    
    remove_pending(placeholder.message_id)


@dp.message_reaction()
async def handle_reaction(reaction: MessageReactionUpdated):
    data = get_pending(reaction.message_id)
    if not data:
        return
    
    if reaction.user.id != data["original_sender_id"]:
        return
    
    has_lock = any(
        r.emoji == "🔒" for r in reaction.new_reaction 
        if isinstance(r, ReactionTypeEmoji)
    )
    
    if has_lock:
        set_locked(reaction.message_id)
        await bot.send_message(reaction.user.id, "🔒 Сообщение зашифровано!")


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("🔐 Я бот-шифровальщик! Добавь меня в группу и сделай админом. Потом просто пиши сообщения и ставь 🔒 на временное сообщение.")

@dp.message(Command("help"))
async def help(message: Message):
    await message.answer("1. Напиши сообщение в группу\n2. Оно исчезнет\n3. Появится ⏳ сообщение\n4. Поставь на него 🔒 (5 секунд)\n5. Бот отправит зашифрованную версию")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())