# Устанавливаем базовый образ
FROM python:3.10-slim-bullseye

# Копируем файлы проекта в рабочую директорию контейнера
COPY . /GPT_BOT

# Устанавливаем ffmpeg
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg


# Установка curl
#RUN apt-get update && apt-get install -y curl

# Устанавливаем Poetry
#RUN curl -sSL https://install.python-poetry.org | python3 -
RUN pip3 install poetry

# Устанавливаем зависимости проекта
WORKDIR /GPT_BOT
#RUN $HOME/.poetry/bin/poetry install --no-dev
RUN poetry install --no-dev

# Указываем команду запуска приложения
#CMD ["$HOME/.poetry/bin/poetry", "run", "python", "main.py"]
CMD ["poetry", "run", "python3", "gpt_bot/bot.py"]
