FROM python:3.11
# set work directory
WORKDIR /root/converty/
# install dependencies
COPY Pipfile Pipfile.lock ./
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --dev --system --deploy
COPY locales /etc/locales
RUN pybabel compile -D converty -d /etc/locales
ENV LOCALES_PATH=/etc/locales
# run app
CMD ["python", "telegram_bot.py"]
