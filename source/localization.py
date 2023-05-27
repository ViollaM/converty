"""Localization module"""
from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from typing import Tuple, Any
import os


supported_languages = ["en", "ru", "fr"]


class Localization(I18nMiddleware):
    """Сlass with custom logic for getting user's locale"""

    async def get_user_locale(self, action: str, args: Tuple[Any]) -> str:
        """User's locale getter for localization, returns locale name

        :param action: event name
        :param args: event arguments
        :rtype: None
        """
        user: types.User = types.User.get_current()

        if get_locale(user.id) is None:
            save_locale(user.id)
        *_, data = args
        language = data['locale'] = get_locale(user.id)
        return language


def save_locale(user_id: str, locale="en"):
    """Saves user's locale to file

    :param user_id: unique identifier for telegram user
    :type user_id: str
    :param locale: user's locale, default = en
    :type user_id: str
    :rtype: None
    """
    path = f"storage/{user_id}/locale/locale.txt"
    file = open(path, "w")
    file.truncate(0)
    file.write(locale)
    file.close()


def get_locale(user_id: str) -> str:
    """Gets user locale from saved file and returns it or return default locale

    :param user_id: unique identifier for telegram user
    :type user_id: str
    :rtype: str
    """
    path = f"storage/{user_id}/locale/locale.txt"
    if os.path.exists(path):
        file = open(path, "r")
        locale = file.read()
        file.close()
    else:
        locale = "en"
    return locale
