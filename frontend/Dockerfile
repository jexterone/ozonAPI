# Базовый образ Node.js
FROM node:16-alpine

# Установка рабочей директории
WORKDIR /app

# Копирование зависимостей
COPY package.json .
RUN npm install

# Копирование исходного кода
COPY . .

# Команда запуска
CMD ["npm", "start"]