"""Converter telegram bot, command processing"""
import os
import signal
import shutil
import psycopg2
import configparser
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

from localization import (
    Localization,
    supported_languages,
    save_locale
)

from db_manager import (
    db_connect,
    db_write_feedback,
    db_write_email,
    db_delete_email,
    db_get_email
)

from mailer import (
    smpt_connect,
    send_email,
)

config = configparser.ConfigParser()
config.read("config/converty_config.ini")

db = db_connect(config["Postgres"])
smtp = smpt_connect(config["Smtp"])

bot = Bot(token=config["Converty"]["SecretToken"])
dp = Dispatcher(bot)

locales_path = os.environ.get('LOCALES_PATH')
i18n = Localization("converty", locales_path)
dp.middleware.setup(i18n)
_ = i18n.gettext

supported_conversion_formats = ["pdf", "zip", "unzip", "images"]


def signal_handler(signum, frame):
    """Signal handler"""
    if db:
        db.close()
    if smtp:
        smtp.close()
    if signum == signal.SIGTERM:
        os._exit(0)


@dp.message_handler(commands=['start'])
async def handle_start(msg: types.Message):
    """Processes the start command, creates users' directory and says hi

    :param msg: message from user
    :type msg: aiogram.types.Message
    """
    try:
        os.mkdir(f"storage/{msg.from_user.id}", mode=0o755)
        os.mkdir(f"storage/{msg.from_user.id}/locale", mode=0o755)
    except FileExistsError:
        pass
    await msg.answer(_("Hi, dear {fname}, my name is Converty and I am file converter bot 😎\n"
                     "Use /help command to find out what I can do\n").format(fname=msg.from_user.first_name))


@dp.message_handler(commands=['stop'])
async def handle_stop(msg: types.Message):
    """Processes the stop command, deletes users' directory and says bye

    :param msg: message from user
    :type msg: aiogram.types.Message
    """
    shutil.rmtree(f"storage/{msg.from_user.id}", ignore_errors=True)
    db_delete_email(db, msg.from_user.id)
    await msg.answer(_("Goodbye, dear {fname}").format(fname=msg.from_user.first_name))


@dp.message_handler(commands=['make'])
async def handle_make(msg: types.Message):
    """Processes the make command, parses format and sends user converted file

    :param msg: message from user
    :type msg: aiogram.types.Message
    """
    text = msg.text.split()
    if len(text) < 2:
        return await msg.answer(_("Please specify one convertation format"))
    format = text[1]
    send_on_mail = len(text) > 2 and text[2] == "mail"
    if format not in supported_conversion_formats:
        return await msg.answer(_("Oops, this format is not supported yet 😔️️️\n"
                                  "Choose supported one from: {formats}").format(formats=', '.join(map(str, supported_conversion_formats))))
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
            if send_on_mail:
                email = db_get_email(db, msg.from_user.id)
                if email != "":
                    send_email(smtp, config["Smtp"]["Login"], email, file_path)
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
    except Exception as _ex:  # noqa: E722
        print(f'Exception caught: {_ex}', flush=True)
        await msg.answer(_("Something went wrong, please try again later"))


@dp.message_handler(commands=['reset'])
async def handle_reset(msg: types.Message):
    """Processes the reset command, deletes uploaded files

    :param msg: message from user
    :type msg: aiogram.types.Message
    """
    remove_files(msg.from_user.id)
    await msg.answer(_("All uploaded files deleted"))


@dp.message_handler(commands=['lang'])
async def handle_lang(msg: types.Message):
    """Change bot language"""
    text = msg.text.split()
    if len(text) != 2:
        return await msg.answer(_("Please specify one language"))
    language = text[1]
    if language not in supported_languages:
        return await msg.answer(_("Unfortunately, this language is not supported yet 😔️️️\n"
                                  "Choose supported one from: {langs}").format(langs=', '.join(map(str, supported_languages))))
    save_locale(msg.from_user.id, language)
    await msg.answer(_("Language successfully changed", locale=language))


@dp.message_handler(commands=['help'])
async def handle_help(msg: types.Message):
    """Processes the help command, sends user commands' descriptions

    :param msg: message from user
    :type msg: aiogram.types.Message
    """
    text = msg.text.split()
    match len(text):
        case 1:
            message = (_("Use commands:\n"
                         "/start to launch the bot\n"
                         "/stop to stop the bot\n"
                         "/make <format> to convert files into format\n"
                         "/reset to forget all uploaded files\n"
                         "/lang to change language\n"
                         "/feedback to write us"
                         "/help to see this message or\n"
                         "/help <command> to see additional information about chosen command\n"))
        case 2:
            match text[1]:
                case "make":
                    message = (_("Supported formats: {formats}\n\n"
                                 "Pdf file will be compiled from files of the following types: "
                                 "{pdf_formats}, the remaining files "
                                 "will be ignored, but will remain among the uploaded ones.\n\n"
                                 "Zip file will be compiled from all uploaded files.\n\n"
                                 "Unzip option can only unzip one file at a time, will return all files from archive.\n\n"
                                 "Images option can only extract images from one pdf file at a time, "
                                 "will return all pages as png files.").format(formats=', '.join(map(str, supported_conversion_formats)),
                                                                               pdf_formats=', '.join(map(str, supported_pdf_converter_formats))))
                case "start":
                    message = _("Launching bot")
                case "stop":
                    message = (_("Stopping bot, all uploaded files will be deleted\n"
                               "You'll need to use command /start to resume the work with bot"))
                case "reset":
                    message = _("Delete all uploaded files")
                case "lang":
                    message = _("Changes bot language, supported languages: {langs}").format(langs=', '.join(map(str, supported_languages)))
                case "feedback":
                    message = _("Write a feedback about our service")
                case _:
                    message = _("I don't recognize this command")
        case _:
            message = _("Please specify one command")
    await msg.answer(message)


@dp.message_handler(commands=['feedback'])
async def handle_lang(msg: types.Message):
    """Make feedback about bot"""
    text = msg.text.split()
    if len(text) > 1:
        db_write_feedback(db, " ".join(text[1:]))
        await msg.answer(_("Thanks for your feedback!"))
    else:
        await msg.answer(_("Write something please"))


@dp.message_handler(commands=['sendmail'])
async def handle_lang(msg: types.Message):
    """Make feedback about bot"""
    text = msg.text.split()
    if len(text) > 1:
        db_write_email(db, msg.from_user.id, text[1])
        await msg.answer(_("Email updated!"))
    else:
        await msg.answer(_("Write your email, please"))


@dp.message_handler(content_types=['text'])
async def handle_text_message(msg: types.Message):
    """Text handler"""
    mesg = msg.text[::-1]
    await msg.answer(mesg)


@dp.message_handler(content_types=['photo'])
async def handle_photo_message(msg: types.Message):
    """Handles photo messages and saves it to the users' directory

    :param msg: message from user
    :type msg: aiogram.types.Message
    """
    file_ID = msg.photo[-1].file_id
    file_info = await bot.get_file(file_ID)
    downloaded_file = await bot.download_file(file_info.file_path)
    with open(f"storage/{msg.from_user.id}/{file_ID}.png", "wb") as new_file:
        new_file.write(downloaded_file.getvalue())
    await msg.answer(_("Photo uploaded!"))


@dp.message_handler(content_types=['document'])
async def handle_document_message(msg: types.Message):
    """Handles document messages and saves it to the users' directory

    :param msg: message from user
    :type msg: aiogram.types.Message
    """
    file = msg.document
    file_ID = file.file_id
    file_info = await bot.get_file(file_ID)
    downloaded_file = await bot.download_file(file_info.file_path)
    with open(f"storage/{msg.from_user.id}/{file_ID}={file.file_name}", "wb") as new_file:
        new_file.write(downloaded_file.getvalue())
    await msg.answer(_("Document uploaded!"))


if __name__ == '__main__':
    try:
        os.mkdir("storage", mode=0o755)
    except FileExistsError:
        pass
    signal.signal(signal.SIGTERM, signal_handler)
    executor.start_polling(dp)
