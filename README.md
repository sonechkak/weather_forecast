# 🌤️ Weather Forecast Service

Веб-приложение для получения прогноза погоды по городам мира с использованием Open-Meteo API.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)

## 📋 Описание

Сервис предоставляет актуальную информацию о погоде для любого города мира. Пользователи могут:
- Получать текущую погоду и прогноз на 7 дней
- Использовать автодополнение при вводе названия города
- Просматривать историю своих поисков
- Получать доступ к данным через REST API

## ✨ Реализованные функции

### Основной функционал
- ✅ **Поиск погоды по городу** - введите название города и получите актуальный прогноз
- ✅ **Текущая погода** - температура, влажность, скорость ветра, описание
- ✅ **Прогноз на 7 дней** - максимальная и минимальная температура, погодные условия
- ✅ **Удобный интерфейс** - адаптивный дизайн с Bootstrap 5

### Дополнительные возможности  
- ✅ **Автодополнение городов** - умные подсказки при вводе с использованием Open-Meteo Geocoding API
- ✅ **История поиска** - сохранение последних поисков в cookies и полная история в базе данных
- ✅ **Предложение повторного поиска** - быстрый доступ к ранее искомым городам
- ✅ **Статистика популярных городов** - аналитика по всем поискам пользователей
- ✅ **REST API** - программный доступ к функциям сервиса
- ✅ **Docker контейнеризация** - легкое развертывание и масштабирование
- ✅ **Тесты** - покрытие основного функционала тестами

## 🛠️ Технологии

### Backend
- **Django 4.2+** - веб-фреймворк
- **PostgreSQL** - основная база данных
- **Python Decouple** - управление конфигурацией
- **Requests** - HTTP клиент для API запросов
- **Poetry** - управление зависимостями

### Frontend
- **Bootstrap 5.3** - CSS фреймворк
- **Bootstrap Icons** - иконки
- **Vanilla JavaScript** - интерактивность и AJAX
- **Django Templates** - серверный рендеринг

### Внешние API
- **Open-Meteo Weather API** - данные о погоде
- **Open-Meteo Geocoding API** - геокодинг и автодополнение городов

### Инфраструктура
- **Docker & Docker Compose** - контейнеризация
- **Poetry** - управление Python зависимостями

## 🚀 Быстрый старт

### Предварительные требования
- Python 3.11+
- Poetry
- Docker & Docker Compose (для контейнерного запуска)
- PostgreSQL (для локального запуска без Docker)

### Установка и запуск

#### Вариант 1: Docker Compose (рекомендуемый)

```bash
# Клонируем репозиторий
git clone git@github.com:sonechkak/weather_forecast.git
cd weather-forecast

# Копируем настройки окружения
cp .env.example .env

# Запускаем через Docker Compose
docker-compose up --build
```

Приложение будет доступно по адресу: http://localhost:8000

#### Вариант 2: Локальная установка

```bash
# Клонируем репозиторий
git clone git@github.com:sonechkak/weather_forecast.git
cd weather-forecast

# Устанавливаем зависимости
poetry install

# Активируем виртуальное окружение
poetry shell

# Копируем и настраиваем переменные окружения
cp .env.example .env
# Отредактируйте .env файл с вашими настройками БД

# Применяем миграции
python manage.py migrate

# Создаем суперпользователя (опционально)
python manage.py createsuperuser

# Запускаем сервер разработки
python manage.py runserver
```

### Настройки окружения (.env)

```env
# Database
DATABASE_NAME=weather_db
DATABASE_USER=weather_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Open-Meteo API URLs (опционально)
GEOCODING_API_URL=https://geocoding-api.open-meteo.com/v1/search
WEATHER_API_BASE_URL=https://api.open-meteo.com/v1/forecast
```

## 📖 Использование

### Веб-интерфейс

1. **Поиск погоды**: Перейдите на главную страницу и введите название города
2. **Автодополнение**: При вводе появятся подсказки с названиями городов
3. **История**: Просмотрите свои недавние поиски на странице "История"
4. **Быстрый доступ**: Используйте сохраненные города для повторного поиска

### REST API

#### Автодополнение городов
```http
GET /api/v1/autocomplete/?q=Моск
```

#### Статистика популярных городов
```http
GET /api/v1/stats/
```

#### История поиска пользователя
```http
GET /api/v1/user-history/
```

Подробная документация API доступна по адресу: `/about-api/`

## 🧪 Тестирование

```bash
# Запуск всех тестов
cd src
pytest
```

## 🐳 Docker

### Структура контейнеров
- **web** - Django приложение
- **db** - PostgreSQL база данных

### Основные команды

```bash
# Сборка и запуск
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f web

# Выполнение команд Django
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Остановка
docker-compose down
```

## 🔧 Архитектура

### Компоненты системы
1. **WeatherService** - интеграция с Open-Meteo API
2. **HistoryService** - управление историей поиска
3. **Models** - City, WeatherSearch для хранения данных
4. **Views** - обработка HTTP запросов
5. **Templates** - пользовательский интерфейс
6. **API Views** - REST endpoints

### Потоки данных
```
Пользователь → Frontend (JS) → Django Views → Services → External API
                                    ↓
                               Database ← Models
```

## 🤝 Разработка

### Стек технологий
- Python 3.11+ с Poetry для управления зависимостями
- Django 4.2+ как основной веб-фреймворк
- PostgreSQL для надежного хранения данных
- Bootstrap 5 для современного UI
- Docker для консистентного развертывания

## 📄 Лицензия

Этот проект создан в рамках тестового задания.

## 📞 Контакты

При возникновении вопросов или предложений по улучшению проекта, создайте issue в репозитории.

---

**Версия:** 1.0.0  
**Последнее обновление:** Май 2025