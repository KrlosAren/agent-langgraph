import os

import pymysql.cursors

import loguru


class DbService:

    def __init__(self, host: str, port: str, user: str, password: str, db: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db

        self._connection = None

    @property
    def connection(self):
        loguru.logger.info("Connecting to database")
        if self._connection is None:
            loguru.logger.info("Creating new connection")
            self._connection = self.connect()
        loguru.logger.info("Returning connection")
        return self._connection

    def connect(self):
        try:
            connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db,
                port=self.port,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
            return connection
        except Exception as e:
            loguru.logger.error(f"Error connecting to database: {e}")
            raise e

    @classmethod
    def from_env(cls):
        return cls(
            host=os.environ.get("DB_HOST", ""),
            port=int(os.environ.get("DB_PORT", 3306)),
            user=os.environ.get("DB_USER", ""),
            password=os.environ.get("DB_PASSWORD", ""),
            db=os.environ.get("DB_NAME", ""),
        )

    def execute(self, query: str, params: tuple = ()):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()                
                return cursor.fetchall()
        except Exception as e:
            loguru.logger.error(f"Error executing query: {e}")
            raise e
