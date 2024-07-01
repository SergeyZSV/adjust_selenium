# Appsflyer Selenium

## Описание

Этот проект автоматизирует авторизацию в Appsflyer и выгрузку отчетов, используя библиотеку Selenium. Скрипт выполняет автоматизацию функций, недоступных через API.

## Основные функции

- **Авторизация**: Выполняет автоматический вход в Appsflyer.
- **Выгрузка отчетов**: Извлекает отчеты "Cohort" и "Retention" с сайта Appsflyer.
- **Обработка данных**: Сохраняет выгруженные данные в локальные файлы CSV и перемещает их в соответствующие папки для дальнейшего использования.

## Установка и настройка

1. **Клонирование репозитория**:
    ```bash
    git clone https://github.com/username/AppsflyerSelenium.git
    cd AppsflyerSelenium
    ```

2. **Создание и активация виртуального окружения (опционально)**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Для Windows: venv\Scripts\activate
    ```

3. **Установка зависимостей**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Настройка Selenium WebDriver**:
    - Убедитесь, что у вас установлен [ChromeDriver](https://sites.google.com/chromium.org/driver/), соответствующий версии вашего браузера Chrome.
    - ChromeDriver должен быть доступен в переменной окружения `PATH`.

5. **Настройка переменных**:
    - Обновите `LOGIN` и `PASSWORD` в скрипте `appsflyer_scraper.py` с вашими учетными данными Appsflyer.
    - Обновите URL и название таблицы в `SPREADSHEET` и `WORKSHEET`.

## Использование

1. **Запуск скрипта для выгрузки отчетов**:
    ```bash
    python appsflyer_scraper.py
    ```

2. **Проверка извлеченных данных**:
    - Данные сохраняются в папки `./cohorts` и `./retention`.

## Структура проекта

```plaintext
AppsflyerSelenium/
│
├── README.md
├── requirements.txt
├── appsflyer_scraper.py
├── cohorts/                 # Папка для сохранения отчетов Cohort
├── retention/               # Папка для сохранения отчетов Retention
└── all_files/               # Папка для загрузки всех файлов перед сортировкой
