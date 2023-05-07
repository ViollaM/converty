import os
import signal
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from PIL import Image

from converter import convert_images_to_pdf, convert_images_to_zip, remove_files

file = open(".secret_token", mode='r')
TOKEN = file.read()[:-1]
file.close()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

supported_conversion_formats = ["pdf", "zip"]

def signal_handler(signum, frame):
    if signum == signal.SIGTERM:
        os._exit(1)


@dp.message_handler(commands=['start'])
async def handle_start(msg: types.Message):
    try:
        os.mkdir(f"storage/{msg.from_user.id}", mode=0o755)
    except FileExistsError:
        pass
    await msg.answer(f"Hello, dear {msg.from_user.first_name}😊\n"
                     "My name is Converty, I am file converter bot 😎\n")


@dp.message_handler(commands=['stop'])
async def handle_stop(msg: types.Message):
    await msg.answer(f"Goodbye, dear {msg.from_user.first_name}")


@dp.message_handler(commands=['make'])
async def handle_make(msg: types.Message):
    text = msg.text.split()
    if len(text) != 2:
        await msg.answer("Please specify one convertation format")
    format = text[1]
    if format not in supported_conversion_formats:
        await msg.answer("Oops, this format is not supported yet 😔️️️\n"
                         f"Choose supported one from: {', '.join(map(str, supported_conversion_formats))}")
    user_id = msg.from_user.id
    try:
        match format:
            case "pdf":
                file_path = convert_images_to_pdf(user_id)
            case "zip":
                file_path = convert_images_to_zip(user_id)
        
        output = open(file_path, "rb")
        await bot.send_document(msg.chat.id, output)
        output.close()
        remove_files(user_id)
    except Exception as e:
        await msg.answer(str(e))


@dp.message_handler(commands=['reset'])
async def handle_reset(msg: types.Message):
    path = f"storage/{msg.from_user.id}/"
    uploadedFiles = [f for f in os.listdir(path)
                     if os.path.isfile(os.path.join(path, f))]
    for f in uploadedFiles:
        os.remove(os.path.join(path, f))
    await msg.answer("OK!")


@dp.message_handler(commands=['lang'])
async def handle_lang(msg: types.Message):
    await msg.answer("not implemented")


@dp.message_handler(commands=['help'])
async def handle_help(msg: types.Message):
    await msg.answer("Use commands:\n"
                     "/start to launch the bot\n"
                     "/stop to stop the bot\n"
                     "/make to convert files\n"
                     "/reset to forget all uploaded files\n"
                     "/lang to change language\n"
                     "/help to see this message\n")


@dp.message_handler(content_types=['text'])
async def handle_text_message(msg: types.Message):
    mesg = msg.text[::-1]
    await msg.answer(mesg)


@dp.message_handler(content_types=['photo'])
async def handle_photo_message(msg: types.Message):
    file_ID = msg.photo[-1].file_id
    file_info = await bot.get_file(file_ID)
    downloaded_file = await bot.download_file(file_info.file_path)
    with open(f"storage/{msg.from_user.id}/{file_ID}.png", "wb") as new_file:
        new_file.write(downloaded_file.getvalue())
    await msg.answer("OK!")


if __name__ == '__main__':
    try:
        os.mkdir("storage", mode=0o755)
    except FileExistsError:
        pass
    signal.signal(signal.SIGTERM, signal_handler)
    executor.start_polling(dp)
