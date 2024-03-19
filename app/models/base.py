import os
import mysql.connector
from colorama import Fore

'''
    On ne devrait plus y toucher une fois en place.
'''

class Database:
    '''Fourni un accès MySQL.'''
    def __init__(self):
        """Gestion i/o de la base de données."""

        self.mysql_params = {'host': os.getenv('MYSQL_HOST', 'localhost'), 'user': os.getenv('MYSQL_USERNAME', 'root'), 'passwd': os.getenv('MYSQL_PASSWORD', '.Logme1nn'), 'port': os.getenv('MYSQL_PORT', 3306), 'database': os.getenv('MYSQL_DATABASE', 'test'), 'autocommit': True}

        try:
            self._conn = mysql.connector.connect(**self.mysql_params)
            self._cursor = self._conn.cursor(dictionary = True, buffered = True)
            print(Fore.LIGHTGREEN_EX + "Connexion avec la base de données opérationnelle.")
        except Exception as e:
            exit(Fore.RED + f"Le projet a besoin d'une connexion à MySQL pour être opérationnel : {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn: self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor
    
    def create_database(self, name):
        creation = f"CREATE DATABASE IF NOT EXISTS `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        self.execute(creation)

    def use_database(self, name):
        """Bascule vers la base de données spécifiée."""
        self._conn.database = name
    
    def commit(self):
        self.connection.commit()

    def close(self, commit = True):
        if commit: self.commit()
        self.connection.close()

    def execute(self, sql, params = None):
        try: self.cursor.execute(sql, params or ())
        except mysql.connector.errors.IntegrityError as e: print(e); pass

    def fetchone(self):
        return self.cursor.fetchone() 

    def fetchall(self):
        return self.cursor.fetchall()

    def callproc(self, sql, params = []):
        return self.cursor.callproc(sql, params)

    def count(self, table: str):
        self.execute(f'select count(*) as n from `{table}`')
        return self.fetchone(list = True)['n']

    def find_one(self, sql: str):
        self.execute(sql)
        return self.fetchone()

    def find_all(self, sql: str):
        self.execute(sql)
        return self.fetchall()