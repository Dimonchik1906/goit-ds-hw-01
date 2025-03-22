# Docker-команда FROM вказує базовий образ контейнера
FROM python:3.13.2

# Встановимо Poetry
RUN pip install poetry

# Встановимо робочу директорію всередині контейнера
WORKDIR /app

# Скопіюємо інші файли в робочу директорію контейнера
COPY pyproject.toml poetry.lock ./
COPY hm08task01.py ./

# Встановимо залежності через Poetry
RUN poetry install --no-root
#Створюємо папку для збереження конннтактів запускаємо контейнер командою
#docker run -it -v $(pwd)/data:/app/data my-assistant
RUN mkdir -p /app/data
VOLUME /app/data
# Відправлляємо команнду запуску
CMD ["poetry", "run", "python", "hm08task01.py"]