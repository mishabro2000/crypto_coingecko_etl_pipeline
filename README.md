# Crypto Coingecko ETL Pipeline 🚀

[🇺🇸 English Version](#english-version) | [🇷🇺 Русская версия](#русская-версия)

---

## <a name="english-version"></a>🇺🇸 English Version
About the Project:
My name is Mikhail, and I am 14 years old. For the past six months, I have been deeply diving into Data Engineering and development best practices. This project was my personal challenge—a coding sprint that I designed and built from scratch to solidify my knowledge in OOP, API integration, and databases, and to truly test what I am capable of achieving.

An elegant, production-ready, object-oriented ETL (Extract, Transform, Load) pipeline built with clean Python to gather top cryptocurrency metrics from CoinGecko API and save it into a local database.

### 🏗️ Architecture & Component Logic
* **Extract:** Connects to the CoinGecko REST API using dynamic parameters (`per_page`, `vs_currency`) via `sys.argv`. It safely handles authentication headers (`x-cg-demo-api-key`) and checks HTTP status codes.
* **Transform:** Standardizes ISO 8601 timestamps (`last_updated`) into clean SQL format, ensures robust null-handling (replacing missing numeric fields with `0.0`), applies `.upper()` string casing to symbols, and injects metadata tracking the execution time (`extracted_at`).
* **Load:** Implements lightning-fast batch inserts via `executemany` wrapped inside robust transactional context managers (`contextlib.closing`). Uses a **Composite Primary Key** `(coin_id, last_updated)` to systematically prevent data duplication while building clean, immutable price history tables inside a dynamically generated data directory using `os.path`.

### 🚀 Usage & Dynamic CLI Execution
Run the pipeline from your terminal with dynamic parameter replacement:
```bash
python etl_pipeline.py [coins_limit] [currency]
```
Example (fetches top 50 coins in EUR):
```bash
python etl_pipeline.py 50 eur
```

---

## <a name="русская-версия"></a>🇷🇺 Русская версия
О проекте:
Меня зовут Михаил, мне 14 лет. Последние полгода я активно изучаю Data Engineering и лучшие практики разработки. Этот проект — мой личный вызов (забег), который я спроектировал и написал с нуля, чтобы закрепить знания ООП, работы с API и базами данных, а также проверить, на что способны мои силы.

Элегантный, объектно-ориентированный ETL-пайплайн на чистом Python для автоматического сбора и сохранения рыночных метрик криптовалют.

### 🏗️ Архитектура проекта и логика классов
* **Extract:** Отвечает за взаимодействие с REST API CoinGecko. Принимает динамические параметры (`per_page`, `vs_currency`), упаковывает заголовки авторизации и обрабатывает статус-коды ответов сервера.
* **Transform:** Приводит временные метки ISO 8601 к стандартному виду SQL, реализует безопасную обработку пустых значений (Null Handling), переводит тикеры к верхнему регистру и генерирует метаданные времени работы скрипта (`extracted_at`).
* **Load:** Реализует пакетную загрузку данных (Batch Load) высокой скорости с помощью метода `executemany`, обернутого в контекстные менеджеры транзакций (`contextlib.closing`). Наличие **составного первичного ключа** `(coin_id, last_updated)` на корню исключает дублирование записей, позволяя эффективно копить историю курсов монет внутри папки, создаваемой модулем `os.path`.

### 🚀 Запуск и передача аргументов через терминал
Пайплайн поддерживает полную кастомизацию объема выгрузки прямо из командной строки с помощью встроенных проверок `sys.argv`:
```bash
python etl_pipeline.py [кол-во_монет] [валюта]
```
Пример запуска (выгрузит топ-50 монет в евро):
```bash
python etl_pipeline.py 50 eur
```

