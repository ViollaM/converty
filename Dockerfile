FROM python:3.11
# set work directory
WORKDIR /root/converty/
# copy project
# COPY . /usr/src/app/
# install dependencies
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv
RUN pipenv install --dev --system --deploy
# run app
CMD ["python", "telegram_bot.py"]
