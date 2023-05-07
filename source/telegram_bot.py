import os
import signal
import shutil
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from converter import (
    convert_images_to_pdf,
    convert_files_to_zip,
    convert_zip_to_files,
    convert_pdf_to_images,
    remove_files,
    supported_pdf_converter_formats
)

file = open(".secret_token", mode='r')
TOKEN = file.read()[:-1]
file.close()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

supported_conversion_formats = ["pdf", "zip", "unzip", "images"]


def signal_handler(signum, frame):
    if signum == signal.SIGTERM:
        os._exit(0)


@dp.message_handler(commands=['start'])
async def handle_start(msg: types.Message):
    try:
        os.mkdir(f"storage/{msg.from_user.id}", mode=0o755)
    except FileExistsError:
        pass
    await msg.answer(f"Hi, dear {msg.from_user.first_name},"
                     "my name is Converty and I am file converter bot 😎\n"
                     "Use /help command to find out what I can do\n")


@dp.message_handler(commands=['stop'])
async def handle_stop(msg: types.Message):
    shutil.rmtree(f"storage/{msg.from_user.id}", ignore_errors=True)
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
    only_images = False
    single_output = True
    try:
        match format:
            case "pdf":
                file_path = convert_images_to_pdf(user_id)
                only_images = True
            case "zip":
                file_path = convert_files_to_zip(user_id)
            case "unzip":
                file_path = convert_zip_to_files(user_id)
                single_output = False
            case "images":
                file_path = convert_pdf_to_images(user_id)
                single_output = False
        if single_output:
            output = open(file_path, "rb")
            await bot.send_document(msg.chat.id, output)
            output.close()
        else:
            media_group = []
            outputs = {}
            for f in os.listdir(file_path):
                if os.path.isfile(os.path.join(file_path, f)):
                    outputs[f] = open(os.path.join(file_path, f), "rb")
                    document = types.InputMediaDocument(type="document", media=outputs[f])
                    media_group.append(document)
            await bot.send_media_group(msg.chat.id, media=media_group)
            for out in outputs.values():
                out.close()
            shutil.rmtree(file_path)
        remove_files(user_id, only_images)
    except ValueError as e:
        await msg.answer(str(e))
    except:  # noqa: E722
        await msg.answer("Something went wrong, please try again later")


@dp.message_handler(commands=['reset'])
async def handle_reset(msg: types.Message):
    remove_files(msg.from_user.id)
    await msg.answer("All uploaded files deleted")


@dp.message_handler(commands=['lang'])
async def handle_lang(msg: types.Message):
    await msg.answer("not implemented")


@dp.message_handler(commands=['help'])
async def handle_help(msg: types.Message):
    text = msg.text.split()
    match len(text):
        case 1:
            message = ("Use commands:\n"
                       "/start to launch the bot\n"
                       "/stop to stop the bot\n"
                       "/make <format> to convert files into format\n"
                       "/reset to forget all uploaded files\n"
                       "/lang to change language\n"
                       "/help to see this message or\n"
                       "/help <command> to see additional information about chosen command\n")
        case 2:
            match text[1]:
                case "make":
                    message = (f"Supported formats: {', '.join(map(str, supported_conversion_formats))}\n\n"
                               "Pdf file will be compiled from files of the following types: "
                               f"{', '.join(map(str, supported_pdf_converter_formats))}, the remaining files "
                               "will be ignored, but will remain among the uploaded ones.\n\n"
                               "Zip file will be compiled from all uploaded files.\n\n"
                               "Unzip option can only unzip one file at a time, will return all files from archive.\n\n"
                               "Images option can only extract images from one pdf file at a time, "
                               "will return all pages as png files.")
                case "start":
                    message = "Launching bot"
                case "stop":
                    message = ("Stopping bot, all uploaded files will be deleted\n"
                               "You'll need to use command start to resume the work with bot")
                case "reset":
                    message = "Delete all uploaded files"
                case _:
                    message = "I don't recognize this command"
        case _:
            message = "Please specify one command"
    await msg.answer(message)


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
    await msg.answer("Photo uploaded!")


@dp.message_handler(content_types=['document'])
async def handle_document_message(msg: types.Message):
    file = msg.document
    file_ID = file.file_id
    file_info = await bot.get_file(file_ID)
    downloaded_file = await bot.download_file(file_info.file_path)
    with open(f"storage/{msg.from_user.id}/{file_ID}={file.file_name}", "wb") as new_file:
        new_file.write(downloaded_file.getvalue())
    await msg.answer("Document uploaded!")


if __name__ == '__main__':
    try:
        os.mkdir("storage", mode=0o755)
    except FileExistsError:
        pass
    signal.signal(signal.SIGTERM, signal_handler)
    executor.start_polling(dp)
