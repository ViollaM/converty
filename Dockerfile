FROM python:3.11
# set work directory
WORKDIR /root/converty/
# install dependencies
COPY Pipfile Pipfile.lock ./
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pip install psycopg2-binary
RUN pip install pyfiglet
RUN pipenv install --dev --system --deploy
COPY locales /etc/locales
RUN pybabel compile -D converty -d /etc/locales -l ru
RUN pybabel compile -D converty -d /etc/locales -l en
RUN pybabel compile -D converty -d /etc/locales -l fr
ENV LOCALES_PATH=/etc/locales
# run app
CMD ["python", "telegram_bot.py"]
