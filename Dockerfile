FROM python:3.11
# set work directory
WORKDIR /root/converty/
# copy project
# COPY . /usr/src/app/
# install dependencies
RUN pip install aiogram Pillow PyMuPDF
# run app
CMD ["python", "telegram_bot.py"]
