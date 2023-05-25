# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2


class FigurePipeline:
    def __init__(self):
        ## Connection Details
        hostname = 'localhost'
        username = 'innotech'
        password = '' # your password
        database = 'scraping'

        ## Create/Connect to database
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        
        ## Create cursor, used to execute commands
        self.cur = self.connection.cursor()
        
        ## Create quotes table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS figure (
            id SERIAL PRIMARY KEY,
            url VARCHAR(255) NOT NULL UNIQUE,
            name VARCHAR(255) NOT NULL,
            price INTEGER,
            images TEXT[] NOT NULL,
            hash VARCHAR(255) NOT NULL,
            date TIMESTAMP NOT NULL
        )   
        """)
        self.connection.commit()

    def process_item(self, item, spider):
        ## Check to see if name and hash is already in database 
        check_query = "SELECT * FROM figure WHERE url = %s AND hash = %s"
        self.cur.execute(check_query, (item['url'],item['hash']))
        result = self.cur.fetchone()
        if result:
               # The item is already in the database, do not save it again
               print("Item already in database, skipping...")
        else:
            try:
                    ## Define insert statement
                    self.cur.execute("""
                    INSERT INTO figure (url, name, price, images, hash, date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE
                    SET price = EXCLUDED.price, hash = EXCLUDED.hash, date = EXCLUDED.date
                    """, (
                    item["url"],
                    item["name"],
                    item["price"],
                    item["images"],
                    item["hash"],
                    item["date"]
                ))
                    ## Execute insert of data into database
                    self.connection.commit()
            except Exception as e:
                    print(e)
                    self.connection.rollback()
        ## Execute insert of data into database
        self.connection.commit()        
        return item
    
    def close_spider(self, spider):
        ## Close cursor & connection to database 
        self.cur.close()
        self.connection.close()
