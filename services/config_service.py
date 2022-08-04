from database import database
from models.config import Config


class ConfigService:
    def __init__(self):
        self.connection = database.open()

    def get_all_configs(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT key, value FROM config")

        data = []
        for row in cursor.fetchall():
            item = Config(row[0], row[1])
            data.append(item)

        return data
    
    def get_by(self, key):
        cursor = self.connection.cursor()
        cursor.execute("SELECT key, value FROM config WHERE key = '{}' ".format(key))
        row = cursor.fetchone()

        if row is None:
            return None
        return Config(row[0], row[1])

    def update_config(self, config):
        
        sql_query = """
        UPDATE config SET value = '{}'
        WHERE key = '{}';
        """.format(config.value, config.key)
        
        cursor = self.connection.cursor()
        cursor.execute(sql_query)
        self.connection.commit()
