"""
Item Pipelines for BookScraper

Pipeline order (set in settings.py):
    1. BookscraperPipeline  (300) — cleans and normalizes all fields
    2. SaveToMySQLPipeline  (400) — persists to MySQL (disabled by default)
"""

from itemadapter import ItemAdapter
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


class BookscraperPipeline:
    """Cleans and normalizes scraped book data."""

    RATING_MAP = {
        'zero': 0, 'one': 1, 'two': 2,
        'three': 3, 'four': 4, 'five': 5
    }
    PRICE_FIELDS = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
    LOWERCASE_FIELDS = ['category', 'product_type']

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        self._strip_whitespace(adapter)
        self._lowercase_fields(adapter)
        self._clean_prices(adapter)
        self._clean_availability(adapter)
        self._clean_num_reviews(adapter)
        self._clean_rating(adapter)
        return item

    def _strip_whitespace(self, adapter):
        for field in adapter.field_names():
            if field != 'description':
                value = adapter.get(field)
                if isinstance(value, str):
                    adapter[field] = value.strip()

    def _lowercase_fields(self, adapter):
        for field in self.LOWERCASE_FIELDS:
            value = adapter.get(field)
            if value:
                adapter[field] = value.lower()

    def _clean_prices(self, adapter):
        for field in self.PRICE_FIELDS:
            value = adapter.get(field, '')
            adapter[field] = float(value.replace('£', '').strip())

    def _clean_availability(self, adapter):
        availability = adapter.get('availability', '')
        parts = availability.split('(')
        adapter['availability'] = int(parts[1].split(' ')[0]) if len(parts) >= 2 else 0

    def _clean_num_reviews(self, adapter):
        adapter['num_reviews'] = int(adapter.get('num_reviews', 0))

    def _clean_rating(self, adapter):
        rating_str = adapter.get('rating', '').lower()
        adapter['rating'] = self.RATING_MAP.get(rating_str, 0)


class SaveToMySQLPipeline:
    """Persists scraped book data to a MySQL database."""

    CREATE_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS books (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            url             VARCHAR(500),
            name            VARCHAR(255),
            price           FLOAT,
            rating          INT,
            category        VARCHAR(100),
            description     TEXT,
            product_type    VARCHAR(100),
            price_excl_tax  FLOAT,
            price_incl_tax  FLOAT,
            tax             FLOAT,
            availability    INT,
            num_reviews     INT
        )
    """

    INSERT_SQL = """
        INSERT INTO books (
            url, name, price, rating, category, description,
            product_type, price_excl_tax, price_incl_tax,
            tax, availability, num_reviews
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE', 'books')
        )
        self.cursor = self.connection.cursor()
        self.cursor.execute(self.CREATE_TABLE_SQL)

    def process_item(self, item, spider):
        self.cursor.execute(self.INSERT_SQL, (
            item['url'], item['name'], item['price'],
            item['rating'], item['category'],
            str(item.get('description', [''])[0]),
            item['product_type'], item['price_excl_tax'],
            item['price_incl_tax'], item['tax'],
            item['availability'], item['num_reviews']
        ))
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()