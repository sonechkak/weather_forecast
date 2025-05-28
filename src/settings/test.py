from .base import *

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': True,
        'OPTIONS': {
            'timeout': 20,
        },
        'TEST': {
            'NAME': ':memory:',
        },
    }
}

# Ускоряем хеширование паролей в тестах
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Отключаем кеширование в тестах
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Настройки сессий для тестов
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400
SESSION_SAVE_EVERY_REQUEST = True

# Отключаем CSRF для тестов
CSRF_COOKIE_SECURE = False
CSRF_USE_SESSIONS = False

# Медиа файлы для тестов
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'test_media'

# Тестовые URL для внешних API
GEOCODING_API_URL = 'https://test-geocoding-api.example.com/v1/search'
WEATHER_API_BASE_URL = 'https://test-weather-api.example.com/v1/forecast'
