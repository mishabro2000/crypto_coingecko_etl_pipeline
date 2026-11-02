# импортируем библиотеки
import sqlite3
import sys
import os
import logging
import requests
import datetime
from contextlib import closing
# настройка базового конфига 
logging.basicConfig(
    level = logging.INFO,
    filename = 'history_ETL.log',
    filemode = 'a',
    encoding = 'utf-8',
    format='%(asctime)s - %(levelname)s - %(message)s'
    )

# т.к метод конвертации datetime признан устаревшим то делаем адаптер
#Адаптер: как превратить объект datetime из Python в строку/число для SQLite
def adapt_datetime(dt):
    return dt.isoformat()

#Конвертер: как превратить строку из SQLite обратно в объект datetime в Python
def convert_datetime(val):
    return datetime.datetime.fromisoformat(val.decode())

# Регистрируем их в sqlite3
sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter("timestamp", convert_datetime)

class Extract:
    def __init__(self,API_KEY,per_page = 10,vs_currency = 'usd'):

        self.URL = "https://api.coingecko.com/api/v3/coins/markets"
        self.API_KEY = API_KEY
        self.per_page = per_page
        self.vs_currency = vs_currency

    def extract_data(self):
        # расставление параметров запроса документации
        params = {
            'vs_currency': self.vs_currency,
            'order': 'market_cap_desc',
            'per_page': self.per_page,
            'page': 1,
            'sparkline': 'false',

    }
            
    # передача ключа (CoinGecko требует передавать его в заголовке x-cg-demo-api-key)
        headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": self.API_KEY
    }
        # запрос данных
        response = requests.get(self.URL,params = params,headers = headers)

        if response.status_code == 200:
            logging.info("Данные были успешно извлечены и передаються в следующий класс для их обработки")
            if response is not None:
                return response.json()
        else:
            logging.error(f"Ошибка запроса: {response.status_code}")

class Transform:
    # инициализировать общие настройки для будующего масштабирования и создание модуля по принципу ООП
    def __init__(self):
        pass

    def transform_data(self,raw_data):
        try:
            # получение времени перед циклом
            extracted_at = datetime.datetime.now()
            # создание списка
            clean_data = []

            logging.info("Начало очистки данных")
            #начало цикла
            for coin in raw_data:
            # берем и извлекаем данные из класса Extract
                coin_id = coin.get('id')

                symbol = coin.get('symbol','').upper()

                name = coin.get('name')

                current_price = coin.get('current_price')

                if current_price is None:
                    current_price = 0.0
                else:
                    current_price = float(current_price)

                market_cap = coin.get('market_cap')

                if market_cap is not None:
                    market_cap = int(market_cap)

                last_update = coin.get('last_updated')
                last_update = last_update.replace('T','')
                last_update = last_update.replace('Z','')
                # упаковываем данные в кортеж и добавляем в список
                coin_tuple = (coin_id,symbol,name,current_price,market_cap,last_update,extracted_at)
                clean_data.append(coin_tuple)
            logging.info("Данные были успешно очищены и передаються в следующий класс для их загрузки в базу данных")

            return clean_data

        except Exception as e:
            logging.error(f"Ошибка очистки данных: {e}")

class Load:
    def __init__(self,db_path='crypto_database.db',detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES):
        
        self.db_path = db_path
        self.detect_types = detect_types
        self.db_dir = "data_etl"

        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
            logging.info(f"Директория {self.db_dir} была успешно создана")

        self.db_path = os.path.join(self.db_dir,self.db_path)

    def load_data(self,clean_data):
        with closing(sqlite3.connect(self.db_path,detect_types = self.detect_types)) as conn:
            with conn:
                cur = conn.cursor()

                cur.execute("""
                CREATE TABLE IF NOT EXISTS crypto(
                COIN_ID TEXT,
                SYMBOL TEXT,
                NAME TEXT,
                CURRENT_PRICE REAL,
                MARKET_CAP INTEGER,
                LAST_UPDATE TEXT,
                EXTRACTED_AT TEXT,
                
                PRIMARY KEY(COIN_ID,LAST_UPDATE)
            )
    """)


                try:
                    cur.executemany("""
                    INSERT OR IGNORE INTO crypto(COIN_ID,SYMBOL,NAME,CURRENT_PRICE,MARKET_CAP,LAST_UPDATE,EXTRACTED_AT) VALUES(?,?,?,?,?,?,?)
                    """,clean_data)
                    logging.info("Данные были успешно загружены в базу данных")

                except:
                    logging.error(f"Ошибка загрузки данных в базу данных")
                    pass

                
                cur.execute("SELECT * FROM crypto")
                rows = cur.fetchall()
                for row in rows:
                    logging.info(row)


if __name__ == '__main__':

    coins_limit = 10
    currency = "usd"

    if len(sys.argv) > 1:
        try:
            # т.к в модуле sys всегда все передается в тексте
            coins_limit = int(sys.argv[1])

        except ValueError:
            logging.warning("будет использовано дефолтное кол-во монет: 10")

    if len(sys.argv) > 2:
        currency = sys.argv[2].lower()

    logging.info(f"Запуск ETL со следующими параметрами: кол-во монет {coins_limit}, валюта:{currency}")

    # инициализируем все классы в ETL
    E = Extract(API_KEY ='into_Key',per_page = 10,vs_currency = 'usd')
    T = Transform()
    L = Load(db_path = "crypto_database.db")

    # запуск конвейера
    try:
        
        raw_data = E.extract_data()
        clean_data = T.transform_data(raw_data)
        L.load_data(clean_data)

        logging.info("ETL-пайплан завершен успешно!")

    except Exception as e:
        logging.error(f"!!! ПАЙПЛАЙН УПАЛ С ОШИБКОЙ: {e} !!!")

        