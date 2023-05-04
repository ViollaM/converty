import os
import signal
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from PIL import Image

file = open(".secret_token", mode='r')
TOKEN = file.read()[:-1]
file.close()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


def signal_handler(signum, frame):
    if signum == signal.SIGTERM:
        os.exit()


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
    path = f"storage/{msg.from_user.id}"
    uploadedFiles = [f for f in os.listdir(path)
                     if os.path.isfile(os.path.join(path, f))]
    pdf_path = os.path.join(path, "output.pdf")
    if len(uploadedFiles) == 0:
        await msg.answer("No files uploaded")
        return
    await msg.answer("Processing...")
    images = [Image.open(os.path.join(path, f)) for f in uploadedFiles]
    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    output = open(pdf_path, "rb")
    await bot.send_document(msg.chat.id, output)
    output.close()
    for f in uploadedFiles:
        os.remove(os.path.join(path, f))
    os.remove(os.path.join(path, "output.pdf"))


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
    fileID = msg.photo[-1].file_id
    file_info = await bot.get_file(fileID)
    downloaded_file = await bot.download_file(file_info.file_path)
    with open(f"storage/{msg.from_user.id}/{fileID}", "wb") as new_file:
        new_file.write(downloaded_file.getvalue())
    await msg.answer("OK!")


if __name__ == '__main__':
    try:
        os.mkdir("storage", mode=0o755)
    except FileExistsError:
        pass
    signal.signal(signal.SIGTERM, signal_handler)
    executor.start_polling(dp)
