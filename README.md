# Converty

## Постановка решаемой задачи

Разработать Telegram бота, который позволит конвертировать файлы, присланные пользователем в определенные форматы.

## Описание предполагаемых инструментов решения

Библиотека `aiogram` для создания Telegram бота

Библиотека `zipfile` для работы с архивами

Библиотека `Pillow` для создания pdf из изображений

## Интерфейс

Бот взаимодействует с пользователем через Telegram.
Пользователь отправляет файлы, которые хочет конвертировать и задает желаемый формат.

Примеры команд для бота:

1. `/start`: начало работы, инициализация бота;

2. `/help`: отображение списка доступных команд и их описание;
   `/help`: <команда> чтобы увидеть дополнительную информацию о выбранной команде;

3. `/make <формат>`: создает файл указанного формата из загруженных файлов;
   `/make <формат> mail`: создает файл указанного формата из загруженных файлов и дублирует его на указанную ранее почту;

4. `/reset`: бот забывает загруженные ранее файлы;

5. `/stop`: завершение сеанса;

6. `/lang` смена языка;

7. `/feedback` для отправки нам обратной связи;

8. `/sendmail` для добавления почты;

...

## Статическая документация

https://ViollaM.github.io/converty/

## Документация для разработчиков

Перед коммитом:
1. ```doit codestyle```
2. ```doit docstyle```
3. ```doit docs```

Компиляция .mo файлов для локализации:
```doit mo```

Выгонка документации:
```sphinx-build docs _build```
