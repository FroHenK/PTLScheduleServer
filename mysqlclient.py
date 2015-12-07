import os
import mysql
from mysql.connector import (connection)

MYSQL_HOST = os.environ.get('OPENSHIFT_MYSQL_DB_HOST', '127.0.0.1')
MYSQL_USER = os.environ.get('OPENSHIFT_MYSQL_DB_USERNAME', 'root')
MYSQL_PASSWORD = os.environ.get('OPENSHIFT_MYSQL_DB_PASSWORD', '')
MYSQL_PORT = os.environ.get('OPENSHIFT_MYSQL_DB_PORT', 3306)
MYSQL_DB = 'ptl'

cnx = connection.MySQLConnection(user=MYSQL_USER, password=MYSQL_PASSWORD,
                                 host=MYSQL_HOST,
                                 database=MYSQL_DB,charset='utf8')

curs = cnx.cursor()


def close_connection():
    cnx.close()
