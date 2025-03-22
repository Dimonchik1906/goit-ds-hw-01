# Docker-команда FROM вказує базовий образ контейнера

FROM python:3.13.2

# Устанавливаем Poetry
RUN pip install poetry
# Встановимо робочу директорію всередині контейнера
WORKDIR /app

# Скопіюємо інші файли в робочу директорію контейнера
COPY pyproject.toml poetry.lock ./
COPY hm08task01.py ./
# Встановимо залежності всередині контейнера
# Устанавливаем зависимости через Poetry
RUN poetry install --no-dev --no-root

# Определяем команду запуска
CMD ["poetry", "run", "python", "hm08task01.py"]